from oletools.olevba import VBA_Parser, TYPE_OLE, TYPE_OpenXML, TYPE_Word2003_XML, TYPE_MHTML

class Macros(object):

    def detect(self, filename):
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