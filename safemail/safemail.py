import zipfile
from os.path import basename
import json
import subprocess
import tempfile, base64

import pdfkit
import os
import glob
from werkzeug.utils import secure_filename
from pantomime import FileName, normalize_mimetype, mimetype_extension
from pdf2image import convert_from_path

try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
from .documentconverter import DocumentConverter
from .msgconverter import MsgConverter
from .emlrender import EmlRender
from .emltodict import EmlToDict
from .macros import Macros
from .outputzip import OutputZip

class SafeMail(object):

    _output_path = '/downloads'
    _output = '/tmp/{}.pdf'
    _msg_dict = {}
    
    def __init__(self, input_name):
        self.__document_upload = []
        self.zip = OutputZip(input_name)

    def __extract_zip(self, path):
        path = path.split('.zip')[0]
        with zipfile.ZipFile('{}.zip'.format(path), 'r') as zipObj:
            # Extract all the contents of zip file in current directory
            path = path.split('.')[0]
            zipObj.extractall('/tmp/eml/zip/{}'.format(path))
            for file in glob.glob("/tmp/eml/zip/{}/*".format(path)):
                self.zip.add_file(file)
            
    def _generate_ocr_text(self, file_obj):
        ocr = pytesseract.image_to_string(Image.open(file_obj))
        with open('/tmp/ocr.txt', 'w+') as f:
            f.write(ocr)
        self.zip.add_file('/tmp/ocr.txt')

    def __convert_document_private(self, document):
        dc = DocumentConverter()
        dc.convert_file(document, 100)
        converted_file = dc.get()
        if converted_file:
            self.__convert_pdf_to_image(converted_file)
            self.zip.add_file(converted_file)

    def __detect_macros(self, document):
        macros = None
        try:
            macros = Macros().detect(document)
        except:
            pass
        if macros:
            self.zip.add_json(json.dumps(macros), '{} - macro'.format(document.split('/')[1]))

    def __add_pdf_analysis_to_zip(self, pdf):
        pdfid = subprocess.check_output(['python', '/app/safemail/pdfid.py', '{}'.format(pdf)])
        pdfid_output = '/tmp/pdfid_output.txt'
        with open(pdfid_output, 'w+') as f:
            f.write(pdfid.decode('utf-8'))
        self.zip.add_file(pdfid_output)
        os.remove(pdfid_output)
        pdfparser = subprocess.check_output(['python', '/app/safemail/pdfparser.py', '-a','{}'.format(pdf)])
        pdfparser += subprocess.check_output(['python', '/app/safemail/pdfparser.py', '-w','{}'.format(pdf)])
        pdfparser_output = '/tmp/pdfparser_output.txt'
        with open(pdfparser_output, 'w+') as f:
            f.write(pdfparser.decode('utf-8'))
        self.zip.add_file(pdfparser_output)
        os.remove(pdfparser_output)

    def __convert_pdf_to_image(self, pdf):
        images_from_path = None
        file_name = os.path.basename(pdf).split('.')[0] + '.ppm'
        with tempfile.TemporaryDirectory() as path:
            try:
                images_from_path = convert_from_path(pdf, output_folder=path, output_file=file_name, size=(500, None))
            except:
                # TODO: Add error logs are part of output
                pass
            if images_from_path:
                for image in images_from_path:
                    self.zip.add_file(image.filename)
                    self.__document_upload.append(image.filename)

    def convert_msg(self, file_obj):
        # Convert msg file
        return_file = None
        return_file = MsgConverter(filename_or_stream=file_obj).get()
        if 'attachments' in return_file:
            if return_file['attachments']:
                for attachment in return_file['attachments']:
                    if '.zip' in attachment:
                        self.__extract_zip(attachment)
                    elif '.pdf' in attachment:
                        self.__add_pdf_analysis_to_zip(attachment)
                        self.__convert_pdf_to_image(attachment)
                    else:
                        try:
                            self.__convert_document_private(attachment)
                        except:
                            pass
                            # TODO: Add any errors to error file which is added to returned zip
                    self.zip.add_file(attachment)
                    self.__detect_macros(attachment)
                    os.remove(attachment)
        msg = return_file['msg']
        msg_dict = {}
        for item in msg.keys():
            msg_dict[item] = msg[item]
        self.zip.add_json(json.dumps(msg_dict), 'msg')

        image_name = file_obj.split('/',2)[1].replace('.msg','')
        with open('/tmp/{}.eml'.format(image_name), 'w+') as f:
            f.write(str(msg))
        msg_image = None
        zip_file, msg_image = self.convert_eml('/tmp/{}.eml'.format(image_name), image_name=image_name, close=False)
        self.zip.close()
        return self.zip.filename, msg_image


    def convert_eml(self, file_obj, image_name=None, close=True):
        if not image_name:
            image_name = file_obj.split('/',2)[1].replace('.eml','')
        eml = EmlRender()
        f = open(file_obj, "rb")
        return_file = None
        return_file = eml.process(f.read(), image_name)
        if return_file:
            self.zip.add_file(return_file['result'])
            if return_file['attachments']:
                for attachment in return_file['attachments']:
                    if '.zip' in attachment:
                        self.__extract_zip(attachment)
                    elif '.pdf' in attachment:
                        self.__add_pdf_analysis_to_zip(attachment)
                        self.__convert_pdf_to_image(attachment)
                    else:
                        try:
                            self.__convert_document_private(attachment)
                        except:
                            pass
                            # TODO: Add any errors to error file which is added to returned zip
                    self.zip.add_file(attachment)
                    self.__detect_macros(attachment)
                    os.remove(attachment)
            self._generate_ocr_text(return_file['result'])
            eml_dict = EmlToDict().process(file_obj)
            if eml_dict:
                eml_json = '/tmp/eml.json'
                with open(eml_json, 'w+') as eml:
                    eml.write(json.dumps(eml_dict))
                self.zip.add_file(eml_json)
                os.remove(eml_json)
            #os.remove(return_file['result'])
        if close:
            self.zip.close()
        os.remove(file_obj)
        return self.zip.filename,return_file['result']


    def convert_document(self, document):
        if '.zip' in document:
            self.__extract_zip(document)
        elif '.pdf' in document:
            self.__add_pdf_analysis_to_zip(document)
            self.__convert_pdf_to_image(document)
        else:
            try:
                self.__convert_document_private(document)
            except:
                pass
                # TODO: Add any errors to error file which is added to returned zip
        self.zip.add_file(document)
        self.__detect_macros(document)
        self.zip.close()
        if os.path.exists(document):
            os.remove(document)
        if self.__document_upload:
            return self.zip.filename, self.__document_upload[0]
        return self.zip.filename, None