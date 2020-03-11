import zipfile
from os.path import basename


class OutputZip(object):

    _output = '/tmp/output.zip'

    def __init__(self):
        self.zip = zipfile.ZipFile(self._output, 'w')

    def add_json(self, json_data, filename):
        json_file_path = '/tmp/{}.json'.format(filename)
        with open(json_file_path, 'w+') as f:
            f.write(json_data)
        self.zip.write(json_file_path, basename(json_file_path))

    def add_image(self, image):
        pass

    def add_text(self, text):
        self.zip.write
        pass

    def add_file(self, file_path):
        if basename(file_path) not in self.zip.namelist():
            self.zip.write(file_path, basename(file_path))

    def close(self):
        self.zip.close()
