import datetime
import json
import eml_parser


class EmlToDict(object):

    def __init__(self):
        self.parsed_eml = None

    def json_serial(self, obj):
        if isinstance(obj, datetime.datetime):
            serial = obj.isoformat()
            return serial

    def process(self, eml_path):
        with open(eml_path, 'rb') as fhdl:
            raw_email = fhdl.read()
        parsed_eml = eml_parser.eml_parser.decode_email_b(raw_email)
        eml_dict = json.loads(json.dumps(parsed_eml, default=self.json_serial))
        return eml_dict

#print(json.dumps(parsed_eml, default=json_serial))

#render = RenderEml()
#render.process('/Users/josh.rickard/Downloads/2019-10-15-Shade-ransomware-malspam-1502-UTC.eml')