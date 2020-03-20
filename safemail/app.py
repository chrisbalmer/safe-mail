import os
import secrets
import logging
import traceback
from threading import RLock
from flask import Flask, flash, request, redirect, url_for, send_file, render_template, send_from_directory, session
from tempfile import mkstemp
from werkzeug.wsgi import ClosingIterator
from werkzeug.exceptions import HTTPException
from werkzeug.utils import secure_filename
from pantomime import FileName, normalize_mimetype, mimetype_extension
from flask_dropzone import Dropzone

from .formats import load_mime_extensions
from .safemail import SafeMail

class ShutdownMiddleware:
    def __init__(self, application):
        self.application = application

    def post_request(self):
        if app.is_dead:
            os._exit(127)

    def __call__(self, environ, after_response):
        iterator = self.application(environ, after_response)
        try:
            return ClosingIterator(iterator, [self.post_request])
        except Exception:
            traceback.print_exc()
            return iterator


ALLOWED_MS_EXTENSIONS = ['.doc', '.dot', '.wbk', '.docx', '.docm', '.dotx', '.dotm', '.docb', '.xls', '.xlt', '.xlm', '.xlsx', '.xlsm', '.xltx', '.xltm', '.xlsb', '.xla', '.xlam', '.xll', '.ppt', '.pptx']
ALLOWED_MAIL_EXTENSIONS = ['.msg', '.eml']
UPLOAD_FOLDER = '/uploads/'


lock = RLock()
extensions = load_mime_extensions()


app = Flask("safe-mail")
app.config['SECRET_KEY'] = secrets.token_hex(32)

app.config.update(
    UPLOAD_FOLDER=UPLOAD_FOLDER,
    DROPZONE_ALLOWED_FILE_CUSTOM=True,
    DROPZONE_ALLOWED_FILE_TYPE=', '.join('{}'.format(x) for x in ALLOWED_MS_EXTENSIONS + ALLOWED_MAIL_EXTENSIONS),
    DROPZONE_IN_FORM=True,
    DROPZONE_UPLOAD_ON_CLICK=True,
    DROPZONE_UPLOAD_ACTION='handle_upload',  # URL or endpoint
    DROPZONE_UPLOAD_BTN_ID='submit'
)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
# dropzone extension
dropzone = Dropzone(app)

app.is_dead = False
app.wsgi_app = ShutdownMiddleware(app.wsgi_app)

def get_safe_file_obj(uploaded_file):
    file_name = FileName(uploaded_file.filename)
    mime_type = normalize_mimetype(uploaded_file.mimetype)
    if not file_name.has_extension:
        file_name.extension = extensions.get(mime_type)
    if not file_name.has_extension:
        file_name.extension = mimetype_extension(mime_type)
    fd, upload_file = mkstemp(suffix=file_name.safe())
    os.close(fd)
    log.info('PDF convert: %s [%s]', upload_file, mime_type)
    uploaded_file.save(upload_file)
    return {
        'file_obj': upload_file,
        'file_name': file_name.safe()
    }

def process_uploads(file_name):
    if file_name:
        safemail = SafeMail(file_name)
        if '.msg' in file_name:
            converted_file, image = safemail.convert_msg(file_name)
        elif '.eml' in file_name:
            converted_file, image = safemail.convert_eml(file_name)
        else:
            for item in ALLOWED_MS_EXTENSIONS:
                if item in file_name:
                    converted_file, image = safemail.convert_document(file_name)
                    break
        session['file_urls'].append({
            'url': converted_file,
            'image': '' if not image else image})


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def handle_upload():
    if request.method == 'POST':
        if 'file_urls' not in session:
            session['file_urls'] = []
        else:
            if session['file_urls']:
                session['file_urls'] = []
        file_obj = request.files
        for f in file_obj:
            file = request.files.get(f)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            process_uploads(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        return '', 204

@app.route('/form', methods=['POST'])
def handle_form():
    if request.method == 'POST':
        if 'file_urls' not in session or session['file_urls'] == []:
            return redirect(url_for('handle_upload'))

        file_urls = session['file_urls']
        session.pop('file_urls', None)
        return render_template('results.html', file_urls=file_urls)

@app.route('/tmp/<filename>')
def download(filename):
    if '/tmp/' in filename:
        filename = filename.replace('/tmp/','')
    return send_from_directory('/tmp', filename)

@app.route('/email', methods=['POST'])
@app.route('/document', methods=['POST'])
def upload():
    if 'file_urls' not in session:
        session['file_urls'] = []
    else:
        if session['file_urls']:
            session['file_urls'] = []
    for key, f in request.files.items():
        if key.startswith('file'):
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
            process_uploads(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))

    return send_file(session['file_urls'][0]['url'])

@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-store'
    return response