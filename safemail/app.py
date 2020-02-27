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


ALLOWED_MS_EXTENSIONS = ['doc', 'dot', 'wbk', 'docx', 'docm', 'dotx', 'dotm', 'docb', 'xls', 'xlt', 'xlm', 'xlsx', 'xlsm', 'xltx', 'xltm', 'xlsb', 'xla', 'xlam', 'xll', 'ppt', 'pptx']
ALLOWED_MAIL_EXTENSIONS = ['msg', 'eml']
UPLOAD_FOLDER = '/uploads/'
DOWNLOAD_FOLDER = '/downloads/'

lock = RLock()
extensions = load_mime_extensions()


app = Flask("safe-mail")
app.config['SECRET_KEY'] = secrets.token_hex(32)

app.config.update(
    UPLOAD_FOLDER=UPLOAD_FOLDER,
    DOWNLOAD_FOLDER=DOWNLOAD_FOLDER,
    DROPZONE_ALLOWED_FILE_CUSTOM=True,
    DROPZONE_ALLOWED_FILE_TYPE=', '.join('.{}'.format(x) for x in ALLOWED_MS_EXTENSIONS + ALLOWED_MAIL_EXTENSIONS),
    DROPZONE_IN_FORM=True,
    DROPZONE_UPLOAD_ON_CLICK=True,
    DROPZONE_UPLOAD_ACTION='handle_upload',  # URL or endpoint
    DROPZONE_UPLOAD_BTN_ID='submit'
)
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
    safemail = SafeMail()
    if file_name:
        if '.msg' in file_name:
            converted_file = safemail.convert_msg(file_name)
        elif '.eml' in file_name:
            converted_file = safemail.convert_eml(file_name)
        else:
            for item in ALLOWED_MS_EXTENSIONS:
                if item in file_name:
                    converted_file = safemail.convert_document(file_name)
        session['zip'] = converted_file


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def handle_upload():
    for key, f in request.files.items():
        if key.startswith('file'):
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
            process_uploads(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
    return '', 204

@app.route('/form', methods=['POST'])
def handle_form():
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], session['zip'], as_attachment=True)


@app.route('/email', methods=['POST'])
@app.route('/document', methods=['POST'])
def upload():
    for key, f in request.files.items():
        if key.startswith('file'):
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
            process_uploads(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
    
    return send_file(app.config['DOWNLOAD_FOLDER'] + session['zip'])