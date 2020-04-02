import os, tempfile
import requests
from io import BytesIO
from zipfile import ZipFile

def test_doc_upload_via_api_zip_file_size(docker_hello_world):
    """Test if the container is reachable.
    The docker_hello_world fixture is used, so the container will start on test
    startup. Do a request to the docker service and read the body.
    """
    file_path = os.path.dirname(os.path.abspath(__file__)) + '/files/Should_open_calc.docm'
    output_path = tempfile.mkstemp(suffix='.zip', prefix='output')

    files = {'file': open(file_path, 'rb')}
    data = {'extension': 'docm'}
    res = requests.post(docker_hello_world + '/document', files=files, data=data)
    f = open(output_path[1], 'wb+')
    f.write(res.content)
    assert os.path.getsize(output_path[1]) > 0

def test_doc_upload_via_api_zip_content_contains_pdf(docker_hello_world):
    """Test if the container is reachable.
    The docker_hello_world fixture is used, so the container will start on test
    startup. Do a request to the docker service and read the body.
    """
    name = 'Should_open_calc'
    file_path = os.path.dirname(os.path.abspath(__file__)) + '/files/{name}.docm'.format(name=name)

    files = {'file': open(file_path, 'rb')}
    data = {'extension': 'docm'}
    res = requests.post(docker_hello_world + '/document', files=files, data=data)
    file_found = False
    with BytesIO(res.content) as zip_file:
        with ZipFile(zip_file) as zip_file:
            for zip_info in zip_file.infolist():
                if zip_info.filename in name.replace('-','_').replace(' ','_') + '.pdf':
                    file_found = True
    if file_found:
        assert True
    else:
        assert False


def test_doc_upload_via_api_zip_content_contains_macro_json_file(docker_hello_world):
    """Test if the container is reachable.
    The docker_hello_world fixture is used, so the container will start on test
    startup. Do a request to the docker service and read the body.
    """
    name = 'Should_open_calc'
    file_path = os.path.dirname(os.path.abspath(__file__)) + '/files/{name}.docm'.format(name=name)

    files = {'file': open(file_path, 'rb')}
    data = {'extension': 'docm'}
    res = requests.post(docker_hello_world + '/document', files=files, data=data)
    file_found = False
    with BytesIO(res.content) as zip_file:
        with ZipFile(zip_file) as zip_file:
            for zip_info in zip_file.infolist():
                if zip_info.filename in 'uploads - macro.json':
                    file_found = True
    if file_found:
        assert True
    else:
        assert False

