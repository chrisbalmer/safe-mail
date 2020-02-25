import zipfile
from os.path import basename
import json

import pdfkit
import os
from werkzeug.utils import secure_filename
from pantomime import FileName, normalize_mimetype, mimetype_extension
from oletools.olevba import VBA_Parser, TYPE_OLE, TYPE_OpenXML, TYPE_Word2003_XML, TYPE_MHTML

from .documentconverter import DocumentConverter

from .msgconverter import MsgConverter

from .emlrender import EmlRender

class SafeMail(object):

    #os.path.join(dir_path, 'static'),
    _output_path = '/static'
    _output_file = 'output.zip'
    _output = '/tmp/{}.pdf'
    _msg_dict = {}

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
    
    def convert_msg(self, file_obj):
        return_file = MsgConverter(filename_or_stream=file_obj).get()
        z = zipfile.ZipFile(self._output_path + '/' + self._output_file, 'w')
        if 'attachments' in return_file:
            if return_file['attachments']:
                for attachment in return_file['attachments']:
                    dc = DocumentConverter()
                    dc.convert_file(attachment, 100)
                    converted_file = dc.get()
                    z.write(converted_file, basename(converted_file))
                    try:
                        self.__detect_vba_macro(converted_file)
                    except:
                        pass


        msg_dict = {}
        msg = return_file['msg']
        image = EmlRender().process(msg)
        if image:
            z.write(image, basename(image))
        for item in msg.keys():
            msg_dict[item] = msg[item]
        with open('/tmp/message.json', 'w+') as f:
            f.write(json.dumps(msg_dict))
        z.write('/tmp/message.json', basename('/tmp/message.json'))
  
        z.close()
        return self._output_file

    def convert_eml(self, file_obj):
        pass

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
            print(vba)
          #  z.write
        z.close()
        return self._output_file
     #   pass
    