import pytest


@pytest.fixture(scope='session')
def docker_hello_world(docker_services):
    """Fixture for the specific Hello World container.
    Depends on the `docker_services` fixture and returns the public url for the
    docker container's service.
    """
    docker_services.start('safe-mail')
    public_port = docker_services.wait_for_service("safe-mail", 7001)
    url = "http://{docker_services.docker_ip}:{public_port}".format(**locals())
    return url


@pytest.fixture(scope='session')
def docker_hello_world2(docker_services):
    """Fixture for the second Hello World container.
    Depends on the `docker_services` fixture and returns the public url for the
    docker container's service.
    """
    docker_services.start('safe-mail')
    public_port = docker_services.wait_for_service("safe-mail", 7001)
    url = "http://{docker_services.docker_ip}:{public_port}".format(**locals())
    return url


@pytest.fixture(scope='session')
def docker_services_project_name():
    return "safe-mail"
