import os
import logging
import traceback
from threading import RLock
from flask import Flask, flash, request, redirect, url_for, send_file, render_template, send_from_directory, session
#from flask_uploads import UploadSet, configure_uploads, patch_request_class, ALL
from tempfile import mkstemp
from werkzeug.wsgi import ClosingIterator
from werkzeug.exceptions import HTTPException
from werkzeug.utils import secure_filename
from pantomime import FileName, normalize_mimetype, mimetype_extension
from flask_dropzone import Dropzone

#from .documentconverter import DocumentConverter, ConversionFailure
from .formats import load_mime_extensions

from .safemail import SafeMail

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('convert')
lock = RLock()
extensions = load_mime_extensions()
#converter = DocumentConverter()


os.path.abspath('/static')

UPLOAD_FOLDER = os.path.abspath('/static')
ALLOWED_EXTENSIONS = set(['msg', 'eml', 'doc', 'xls', 'xlsx', 'ppt'])
UPLOADED_FILE_NAME = None

safemail = SafeMail()


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


app = Flask("safe-mail")


app.config['SECRET_KEY'] = 'supersecretkeygoeshere'

app.config.update(
    UPLOAD_FOLDER=UPLOAD_FOLDER,
    # Flask-Dropzone config:
    DROPZONE_ALLOWED_FILE_CUSTOM=True,
    DROPZONE_ALLOWED_FILE_TYPE='.msg, .doc, .eml, .xls',
   # DROPZONE_REDIRECT_VIEW='static/output.zip'
    #DROPZONE_ALLOWED_FILE_TYPE='image',
    #DROPZONE_MAX_FILE_SIZE=3,
   # DROPZONE_MAX_FILES=30,
)

## flask-uploads extension
#ploaded_files = UploadSet('files', ALL)
#configure_uploads(app, uploaded_files)
#patch_request_class(app)

# dropzone extension
dropzone = Dropzone(app)

#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.is_dead = False
app.wsgi_app = ShutdownMiddleware(app.wsgi_app)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
        if '.msg' in file_name:
          #  safe_file = get_safe_file_obj(file_name)
            converted_file = safemail.convert_msg(file_name)
        elif '.eml' in file_name:
           # safe_file = get_safe_file_obj(file_name)
            converted_file = safemail.convert_eml(file_name)
        else:
            pass
        session['zip'] = UPLOAD_FOLDER + '/' + converted_file
       # return converted_file 

@app.route('/', methods=['POST','GET'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            process_uploads(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            #return render_template('process.html', file_name=process_uploads(os.path.join(app.config['UPLOAD_FOLDER'], filename)))
            return redirect(url_for('results', filename='output.zip'))
       # f = request.files.get('file')
       # global UPLOADED_FILE_NAME
       # file = None
       # file = f.save(app.config['UPLOADED_PATH'] + '/' + secure_filename(f.filename))
       # UPLOADED_FILE_NAME = app.config['UPLOADED_PATH'] + '/' + secure_filename(f.filename)
    return render_template('upload.html')

@app.route('/static/<filename>', methods=['POST','GET'])
def results(filename):
    if request.method == 'GET':
        if 'zip' not in session or session['zip'] == []:
            return redirect(url_for('upload'))
        # set the file_urls and remove the session variable
        file_urls = session['zip']
        session.pop('zip', None)
        return render_template('process.html', file_urls=file_urls)
    return render_template('process.html')
  #  return send_from_directory(app.config['UPLOAD_FOLDER'],
  #                             filename)
  #  return render_template('process.html', filename=file_urls)
    #return render_template('process.html', filename=filename)#send_from_directory(app.config['UPLOAD_FOLDER'],filename, as_attachment=True))

#@app.route("/")
#def info():
#    if app.is_dead:
#        return ("BUSY", 503)
#    return ("OK", 200)

@app.route('/static', methods=['POST', 'GET'])
def process():
    global UPLOADED_FILE_NAME
    #if request.method == 'POST':
    timeout = int(request.args.get('timeout', 100))

   # if 'file' not in request.files:
    #    return 'No file provided.  Please provide a file when calling email POST method'
    
    #uploaded_file = UPLOAD_FOLDER + '/' + UPLOADED_FILE_NAME

    #if uploaded_file.filename == '':
   #     return 'No filename provided.  Please provide a filename when calling email POST method'
    if '.msg' in UPLOADED_FILE_NAME:
        #safe_file = get_safe_file_obj(UPLOADED_FILE_NAME)
        converted_file = safemail.convert_msg(UPLOADED_FILE_NAME)
    elif '.eml' in UPLOADED_FILE_NAME:
       # safe_file = get_safe_file_obj(UPLOADED_FILE_NAME)
        converted_file = safemail.convert_eml(UPLOADED_FILE_NAME)
    else:
        pass


  #  return send_from_directory(directory='static', filename=converted_file)
    return render_template("process.html", file_name = converted_file)
    #return send_file(converted_file,
    #                mimetype='application/pdf',
    #                attachment_filename='output.pdf')

@app.route('/email', methods=['POST'])
def email():
    if request.method == 'POST':
        timeout = int(request.args.get('timeout', 100))

        if 'file' not in request.files:
            return 'No file provided.  Please provide a file when calling email POST method'
        
        uploaded_file = request.files['file']

        if uploaded_file.filename == '':
            return 'No filename provided.  Please provide a filename when calling email POST method'
        elif '.msg' in uploaded_file.filename:
            safe_file = get_safe_file_obj(uploaded_file)
            converted_file = safemail.convert_msg(safe_file['file_name'], safe_file['file_obj'])
        elif '.eml' in uploaded_file.filename:
            safe_file = get_safe_file_obj(uploaded_file)
            converted_file = safemail.convert_eml(safe_file['file_name'], safe_file['file_obj'])
        else:
            pass

    
        return send_file(converted_file,
                        mimetype='application/pdf',
                        attachment_filename='output.pdf')


@app.route('/document', methods=['POST'])
def document():
    if request.method == 'POST':
        timeout = int(request.args.get('timeout', 100))

        if 'file' not in request.files:
            return 'No file provided.  Please provide a file when calling email POST method'
        
        uploaded_file = request.files['file']

        if uploaded_file.filename == '':
            return 'No filename provided.  Please provide a filename when calling email POST method'
        safe_file = get_safe_file_obj(uploaded_file)
        converted_file = safemail.convert_document(safe_file['file_name'], safe_file['file_obj'])
        return send_file(converted_file,
                        mimetype='application/pdf',
                        attachment_filename='output.pdf')