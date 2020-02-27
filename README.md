# safe-mail

safe-mail is a Docker service to help security teams safely interact with msg, eml, and documents

## Synopsis

safe-mail is a Docker service to help security teams safely interact with msg, eml, and documents

safe-mail has the following features and functionality:

* Upload EML and MSG mail messages as well as Microsoft Office documents themselves
* Generates a PNG of the message itself
* Provides a OCR text file of the generated mail message
* Extracts attachments of mail messages and generates a image of the document itself
* Attempts to extract any identified Macros within attachments and creates a JSON file representing the Macro code base
* Extracts any .ZIP attachments
* Generates a JSON file representing the mail message headers
* Returns all this in a .zip file

## Installation

First you can download safe-mail by cloning the repository:

```bash
git clone git@github.com:swimlane/safe-mail.git
```

## Building Docker Image

You first need to build the Docker image:

```bash
docker build --force-rm -t safe-mail .
```

## Running the Docker Image

You can run the docker image using the following command:

```bash
docker run -p 7001:7001 -ti safe-mail 
```

## USAGE

You can use this docker image to upload via the API or the minimal front-end

### Using the Front End

You can upload files using the front-end by dragging and dropping or uploading by select the drag and drop zone.

You can access this front-end at the provided port number you selected when running the container.  

```
http://0.0.0.0:7001
```

Once the files are uploaded, you can then select to process the files using the `Process Files` button and it should return a `output.zip` file which contains the processed items details.

### Using the API

You can also upload mail messages (MSG & EML) and documents (see list below) using the API.

#### Uploading Messages

```python
import requests
import os

path = './my_message.msg'
outpath = './Downloads/output.zip'

url = 'http://0.0.0.0:7001/email'

files = {'file': open(path, 'rb')}
data = {'extension': 'msg'}
res = requests.post(url, files=files, data=data)
f = open(outpath, 'w+')
f.write(res.content)
```

##### Upload Documents & Files

```python
import requests
import os

path = './my_doc.docm'
outpath = './Downloads/output.zip'

url = 'http://0.0.0.0:7001/document'

files = {'file': open(path, 'rb')}
data = {'extension': 'docm'}
res = requests.post(url, files=files, data=data)
f = open(outpath, 'w+')
f.write(res.content)
```

## Supported Extensions

You can upload both MSG & EML files to either the front-end or to the `email` endpoint using the API.

Additionally, if you are using the `document` endpoint (or the UI front-end) safe-mail currently supports the following extensions but can possibly support additional files with testing.

* doc
* dot
* wbk
* docx
* docm
* dotx
* dotm
* docb
* xls
* xlt
* xlm
* xlsx
* xlsm
* xltx
* xltm
* xlsb
* xla
* xlam
* xll
* ppt
* pptx

## Notes
```yaml
   Name: safe-mail
   Created by: Josh Rickard
   Created Date: 02/25/2020
```