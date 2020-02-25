import requests
import os

path = '/Users/josh.rickard/Downloads/test-convertor/Should open calc.docm'

outpath = '/Users/josh.rickard/Downloads/test-convertor/output.zip'
url = 'http://0.0.0.0:7001/document'

files = {'file': open(path, 'rb')}
data = {'extension': 'msg'}
# print('send request')
res = requests.post(url, files=files, data=data)
# message = res.text if res.status_code != 200 else ''
print(res.status_code)
f = open(outpath, 'w+')
#print(res.content)
f.write(res.content)
