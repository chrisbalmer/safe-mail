import zipfile
from os.path import basename
import json

import pdfkit
import os
import glob
from werkzeug.utils import secure_filename
from pantomime import FileName, normalize_mimetype, mimetype_extension
from oletools.olevba import VBA_Parser, TYPE_OLE, TYPE_OpenXML, TYPE_Word2003_XML, TYPE_MHTML

try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
from .documentconverter import DocumentConverter
from .msgconverter import MsgConverter
from .emlrender import EmlRender

class SafeMail(object):

    _output_path = '/downloads'
    _output_file = 'output.zip'
    _output = '/tmp/{}.pdf'
    _msg_dict = {}
    
    def __init__(self):
        self.zip = None

    def __detect_vba_macro(self, filename):
        return_list = []
        vbaparser = VBA_Parser(filename)
        if vbaparser.detect_vba_macros():
            for (filename, stream_path, vba_filename, vba_code) in vbaparser.extract_macros():
                return_list.append({
                    'filename': filename,
                    'ole_stream': stream_path,
                    'vba_filename': vba_filename,
                    'vba_code': vba_code
                })
            results = vbaparser.analyze_macros()
            for kw_type, keyword, description in results:
                return_list.append({
                    'type': kw_type,
                    'keyword': keyword,
                    'description': description
                })
            return_list.append({
                'revealed_macro': vbaparser.reveal()
            })
            return return_list
        else:
            return None

    def __add_to_zip(self, file_obj):
        self.zip.write(file_obj, basename(file_obj))

    def __extract_zip(self, path):
        path = path.split('.zip')[0]
        with zipfile.ZipFile('{}.zip'.format(path), 'r') as zipObj:
            # Extract all the contents of zip file in current directory
            path = path.split('.')[0]
            zipObj.extractall('/tmp/eml/zip/{}'.format(path))
            for file in glob.glob("/tmp/eml/zip/{}/*".format(path)):
                self.zip.write(file, basename(file))
            
    def _generate_ocr_text(self, file_obj):
        ocr = pytesseract.image_to_string(Image.open(file_obj))
        with open('/tmp/ocr.txt', 'w+') as f:
            f.write(ocr)
        self.zip.write('/tmp/ocr.txt', basename('ocr.txt'))
        
    def _generate_json(self, file_obj):
        msg_dict = {}
        for item in file_obj.keys():
            msg_dict[item] = file_obj[item]
        with open('/tmp/message.json', 'w+') as f:
            f.write(json.dumps(msg_dict))
        self.zip.write('/tmp/message.json', basename('/tmp/message.json'))

    def convert_msg(self, file_obj):
        if not self.zip:
            self.zip = zipfile.ZipFile(self._output_path + '/' + self._output_file, 'w')
        return_file = MsgConverter(filename_or_stream=file_obj).get()
        if 'attachments' in return_file:
            if return_file['attachments']:
                for attachment in return_file['attachments']:
                    dc = DocumentConverter()
                    dc.convert_file(attachment, 100)
                    converted_file = dc.get()
                    self.__add_to_zip(converted_file)
                    try:
                        self.__detect_vba_macro(converted_file)
                    except:
                        pass
                    os.remove(converted_file)

        msg = return_file['msg']
        self._generate_json(msg)

        with open('/tmp/mail_message.msg', 'w+') as f:
            f.write(str(msg))
        self.convert_eml('/tmp/mail_message.msg', close=False)
        self.zip.close()
        return self._output_file

    def convert_eml(self, file_obj, close=True):
        if not self.zip:
            self.zip = zipfile.ZipFile(self._output_path + '/' + self._output_file, 'w')
        eml = EmlRender()
        f = open(file_obj, "rb")
        return_file = eml.process(f.read())
        if return_file:
            self.zip.write(return_file['result'], basename(return_file['result']))
           # self._generate_json(return_file['result'])
            if return_file['attachments']:
                for attachment in return_file['attachments']:
                    if '.zip' in attachment:
                        self.__extract_zip(attachment)
                    self.zip.write(attachment, basename(attachment))
                    os.remove(attachment)
            if return_file['images']:
                for image in return_file['images']:
                    self.zip.write(image, basename(image))
                    os.remove(image)
            self._generate_ocr_text(return_file['result'])
            os.remove(return_file['result'])
        if close:
            self.zip.close()
            return self._output_file


    def convert_document(self, file_obj):
        z = zipfile.ZipFile(self._output_path + '/' + self._output_file, 'w')
        dc = DocumentConverter()
        dc.convert_file(file_obj, 100)
        converted_file = dc.get()
        z.write(converted_file, basename(converted_file))
        vba = self.__detect_vba_macro(file_obj)
        if vba:
            with open('/tmp/macro.json', 'w+') as f:
                f.write(json.dumps(vba))
            z.write('/tmp/macro.json', basename('/tmp/macro.json'))
        z.close()
        return self._output_file
    