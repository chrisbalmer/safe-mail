import os, tempfile
import requests
from io import BytesIO
from zipfile import ZipFile

def test_eml_upload_via_api_zip_file_size(docker_hello_world):
    """Test if the container is reachable.
    The docker_hello_world fixture is used, so the container will start on test
    startup. Do a request to the docker service and read the body.
    """
    file_path = os.path.dirname(os.path.abspath(__file__)) + '/files/Phish Test - 1.eml'
    output_path = tempfile.mkstemp(suffix='.zip', prefix='output')

    files = {'file': open(file_path, 'rb')}
    data = {'extension': 'eml'}
    res = requests.post(docker_hello_world + '/email', files=files, data=data)
    f = open(output_path[1], 'wb+')
    f.write(res.content)
    assert os.path.getsize(output_path[1]) > 0

def test_eml_upload_via_api_zip_content_contains_png(docker_hello_world):
    """Test if the container is reachable.
    The docker_hello_world fixture is used, so the container will start on test
    startup. Do a request to the docker service and read the body.
    """
    name = 'Phish Test - 1'
    file_path = os.path.dirname(os.path.abspath(__file__)) + '/files/{name}.eml'.format(name=name)

    files = {'file': open(file_path, 'rb')}
    data = {'extension': 'eml'}
    res = requests.post(docker_hello_world + '/email', files=files, data=data)
    file_found = False
    with BytesIO(res.content) as zip_file:
        with ZipFile(zip_file) as zip_file:
            for zip_info in zip_file.infolist():
                if zip_info.filename in name.replace('-','_').replace(' ','_') + '.png':
                    file_found = True
    if file_found:
        assert True
    else:
        assert False


def test_eml_upload_via_api_zip_content_contains_ocr_text_file(docker_hello_world):
    """Test if the container is reachable.
    The docker_hello_world fixture is used, so the container will start on test
    startup. Do a request to the docker service and read the body.
    """
    name = 'Phish Test - 1'
    file_path = os.path.dirname(os.path.abspath(__file__)) + '/files/{name}.eml'.format(name=name)

    files = {'file': open(file_path, 'rb')}
    data = {'extension': 'eml'}
    res = requests.post(docker_hello_world + '/email', files=files, data=data)
    file_found = False
    with BytesIO(res.content) as zip_file:
        with ZipFile(zip_file) as zip_file:
            for zip_info in zip_file.infolist():
                if zip_info.filename in 'ocr.txt':
                    file_found = True
    if file_found:
        assert True
    else:
        assert False


def test_eml_upload_via_api_zip_content_contains_eml_json_file(docker_hello_world):
    """Test if the container is reachable.
    The docker_hello_world fixture is used, so the container will start on test
    startup. Do a request to the docker service and read the body.
    """
    name = 'Phish Test - 1'
    file_path = os.path.dirname(os.path.abspath(__file__)) + '/files/{name}.eml'.format(name=name)

    files = {'file': open(file_path, 'rb')}
    data = {'extension': 'eml'}
    res = requests.post(docker_hello_world + '/email', files=files, data=data)
    file_found = False
    with BytesIO(res.content) as zip_file:
        with ZipFile(zip_file) as zip_file:
            for zip_info in zip_file.infolist():
                if zip_info.filename in 'eml.json':
                    file_found = True
    if file_found:
        assert True
    else:
        assert False


import os, tempfile
import requests
from io import BytesIO
from zipfile import ZipFile

def test_eml_upload_via_api_zip_file_size(docker_hello_world):
    """Test if the container is reachable.
    The docker_hello_world fixture is used, so the container will start on test
    startup. Do a request to the docker service and read the body.
    """
    file_path = os.path.dirname(os.path.abspath(__file__)) + '/files/Phish Test - 1.eml'
    output_path = tempfile.mkstemp(suffix='.zip', prefix='output')

    files = {'file': open(file_path, 'rb')}
    data = {'extension': 'eml'}
    res = requests.post(docker_hello_world + '/email', files=files, data=data)
    f = open(output_path[1], 'wb+')
    f.write(res.content)
    assert os.path.getsize(output_path[1]) > 0

def test_ransomware_eml_upload_via_api_zip_content_contains_png(docker_hello_world):
    """Test if the container is reachable.
    The docker_hello_world fixture is used, so the container will start on test
    startup. Do a request to the docker service and read the body.
    """
    name = '2019-10-15-Shade-ransomware-malspam-1502-UTC'
    file_path = os.path.dirname(os.path.abspath(__file__)) + '/files/{name}.eml'.format(name=name)

    files = {'file': open(file_path, 'rb')}
    data = {'extension': 'eml'}
    res = requests.post(docker_hello_world + '/email', files=files, data=data)
    file_found = False
    with BytesIO(res.content) as zip_file:
        with ZipFile(zip_file) as zip_file:
            for zip_info in zip_file.infolist():
                if zip_info.filename in name.replace('-','_').replace(' ','_') + '.png':
                    file_found = True
                    file_found = True
    if file_found:
        assert True
    else:
        assert False


def test_ransomware_eml_upload_via_api_zip_content_contains_ocr_text_file(docker_hello_world):
    """Test if the container is reachable.
    The docker_hello_world fixture is used, so the container will start on test
    startup. Do a request to the docker service and read the body.
    """
    name = '2019-10-15-Shade-ransomware-malspam-1502-UTC'
    file_path = os.path.dirname(os.path.abspath(__file__)) + '/files/{name}.eml'.format(name=name)

    files = {'file': open(file_path, 'rb')}
    data = {'extension': 'eml'}
    res = requests.post(docker_hello_world + '/email', files=files, data=data)
    file_found = False
    with BytesIO(res.content) as zip_file:
        with ZipFile(zip_file) as zip_file:
            for zip_info in zip_file.infolist():
                if zip_info.filename in 'ocr.txt':
                    file_found = True
    if file_found:
        assert True
    else:
        assert False


def test_ransomware_eml_upload_via_api_zip_content_contains_eml_json_file(docker_hello_world):
    """Test if the container is reachable.
    The docker_hello_world fixture is used, so the container will start on test
    startup. Do a request to the docker service and read the body.
    """
    name = '2019-10-15-Shade-ransomware-malspam-1502-UTC'
    file_path = os.path.dirname(os.path.abspath(__file__)) + '/files/{name}.eml'.format(name=name)

    files = {'file': open(file_path, 'rb')}
    data = {'extension': 'eml'}
    res = requests.post(docker_hello_world + '/email', files=files, data=data)
    file_found = False
    with BytesIO(res.content) as zip_file:
        with ZipFile(zip_file) as zip_file:
            for zip_info in zip_file.infolist():
                if zip_info.filename in 'eml.json':
                    file_found = True
    if file_found:
        assert True
    else:
        assert False