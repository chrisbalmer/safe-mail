import zipfile
from os.path import basename


class OutputZip(object):

    _output = '/tmp/{}.zip'
    count = 0

    def __init__(self, zip_name):
        self.__zip_name = zip_name.split('/')[2].split('.')[0]
        self.zip = zipfile.ZipFile(self._output.format(self.__zip_name), 'w')

    @property
    def filename(self):
        return self.zip.filename

    def add_json(self, json_data, filename):
        json_file_path = '/tmp/{}.json'.format(filename)
        if basename(json_file_path) not in self.zip.namelist():
            with open(json_file_path, 'w+') as f:
                f.write(json_data)
            self.zip.write(json_file_path, basename(json_file_path))
        else:
            self.count += 1
            new_json_file_path = '/tmp/{}_{}.json'.format(filename, self.count)
            with open(new_json_file_path, 'w+') as f:
                f.write(json_data)
            self.zip.write(new_json_file_path, basename(new_json_file_path))

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