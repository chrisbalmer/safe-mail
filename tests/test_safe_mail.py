import requests


def test_title(docker_hello_world):
    """Test if the container is reachable.
    The docker_hello_world fixture is used, so the container will start on test
    startup. Do a request to the docker service and read the body.
    """
    response = requests.get(docker_hello_world)
    assert b'<title>safe-mail</title>' in response.content