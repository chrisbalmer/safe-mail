from setuptools import setup, find_packages

def parse_requirements(requirement_file):
    with open(requirement_file) as f:
        return f.readlines()

setup(
    name='safe-mail',
    version='0.0.1',
    packages=find_packages(exclude=['tests*']),
    license='MIT',
    description='safe-mail is a python Docker image that can be used to convert emails, documents, and attachments to PDFs using a provided API',
    long_description=open('README.md').read(),
    install_requires=parse_requirements('./requirements.txt'),
    keywords='',
    url='https://github.com/swimlane/safe-mail',
    author='Josh Rickard',
    author_email='josh.rickard@swimlane.com'
)