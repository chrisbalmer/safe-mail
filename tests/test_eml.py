import os, tempfile
import requests


def test_eml_upload_via_api(docker_hello_world):
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
    assert os.path.getsize(file_path) > 0
