#!/usr/bin/python3
#
# api.py - Flask REST API to render EML files
#
# Author: Xavier Mertens <xavier@rootshell.be>
# Copyright: GPLv3 (http://gplv3.fsf.org)
# Fell free to use the code, but please share the changes you've made
#
# Todo
# - "offline" mode when rendering HTML code
#__author__     = "Xavier Mertens"
#__license__    = "GPL"
#__version__    = "1.0"
#__maintainer__ = "Xavier Mertens"
#__email__      = "xavier@erootshell.be"
#__name__       = "EMLRender"
#

import os
import re
import sys
import email
import email.header
import quopri
import hashlib
import logging
import base64
import zipfile
import string
import random
import json
from time import strftime
from logging.handlers import RotatingFileHandler

from json import dumps



try:
    import imgkit
except:
    print('[ERROR] imgkit module not installed ("pip install imgkit")')
    sys.exit(1)

try:
    from PIL import Image
except:
    print('[ERROR] pillow module not installed ("pip install pillow")')
    sys.exit(1)



dumpDir    = 'dumps'
textTypes  = [ 'text/plain', 'text/html' ]
imageTypes = [ 'image/gif', 'image/jpeg', 'image/png' ]


class EmlRender(object):

    _temp_dir = '/tmp/eml'

    def __init__(self):
        self.image_list = []
        self.attachments = []
        self.msg = None

    def __append_images(self, images):
        bgColor=(255,255,255)
        widths, heights = zip(*(i.size for i in images))

        new_width = max(widths)
        new_height = sum(heights)
        new_im = Image.new('RGB', (new_width, new_height), color = bgColor)
        offset = 0
        for im in images:
            # x = int((new_width - im.size[0])/2)
            x = 0
            new_im.paste(im, (x, offset))
            offset += im.size[1]
        return new_im

    def __extract_email(self, string):
        match = re.match(r'.*\<(\S+)\>.*', string)
        if match:
            return match.group(1)
        else:
            return None

    def process(self, data):
        '''
        Process the email (bytes), extract MIME parts and useful headers.
        Generate a PNG picture of the mail
        '''

        # Create the dump directory if not existing yet
        if not os.path.isdir(self._temp_dir):
            os.makedirs(self._temp_dir)

        self.msg = email.message_from_bytes(data)
        try:
            decode = email.header.decode_header(self.msg['Date'])[0]
            dateField = str(decode[0])
        except:
            dateField = '&lt;Unknown&gt;'

        try:
            decode = email.header.decode_header(self.msg['From'])[0]
            fromField = str(decode[0])
        except:
            fromField = '&lt;Unknown&gt;'
        fromField = fromField.replace('<', '&lt;').replace('>', '&gt;')

        try:
            decode = email.header.decode_header(self.msg['To'])[0]
            toField = str(decode[0])
        except:
            toField = '&lt;Unknown&gt;'
        toField = toField.replace('<', '&lt;').replace('>', '&gt;')

        try:
            decode = email.header.decode_header(self.msg['Subject'])[0]
            subjectField = str(decode[0])
        except:
            subjectField = '&lt;Unknown&gt;'
        subjectField = subjectField.replace('<', '&lt;').replace('>', '&gt;')

        try:
            decode = email.header.decode_header(self.msg['Message-Id'])[0]
            idField = str(decode[0])
        except:
            idField = '&lt;Unknown&gt;'
        idField = idField.replace('<', '&lt;').replace('>', '&gt;')    

        imgkitOptions = { 'load-error-handling': 'skip' }
        # imgkitOptions.update({ 'quiet': None })
        imagesList = []

        # Build a first image with basic mail details
        headers = '''
        <table width="100%%">
        <tr><td align="right"><b>Date:</b></td><td>{date}</td></tr>
        <tr><td align="right"><b>From:</b></td><td>{fromm}</td></tr>
        <tr><td align="right"><b>To:</b></td><td>{to}</td></tr>
        <tr><td align="right"><b>Subject:</b></td><td>{subject}</td></tr>
        <tr><td align="right"><b>Message-Id:</b></td><td>{id}</td></tr>
        </table>
        <hr></p>
        '''.format(
            date=dateField, 
            fromm=fromField, 
            to=toField, 
            subject=subjectField, 
            id=idField)
        m = hashlib.md5()
        m.update(headers.encode('utf-8'))
        imagePath = m.hexdigest() + '.png'

        try:
            imgkit.from_string(headers, self._temp_dir + '/' + imagePath, options = imgkitOptions)
            self.image_list.append(self._temp_dir + '/' + imagePath)
        except:
            pass

        #
        # Main loop - process the MIME parts
        #
        for part in self.msg.walk():
            mimeType = part.get_content_type()
            if part.is_multipart():
                continue
            if mimeType in textTypes:
                try:
                    payload = quopri.decodestring(part.get_payload(decode=True)).decode('utf-8')
                except:
                    payload = str(quopri.decodestring(part.get_payload(decode=True)))[2:-1]
                
                # Cleanup dirty characters
                dirtyChars = [ '\n', '\\n', '\t', '\\t', '\r', '\\r']
                for char in dirtyChars:
                    payload = payload.replace(char, '')
                
                # Generate MD5 hash of the payload
                m = hashlib.md5()
                m.update(payload.encode('utf-8'))
                imagePath = m.hexdigest() + '.png'
                try:
                    imgkit.from_string(payload, self._temp_dir + '/' + imagePath, options = imgkitOptions)
                    self.image_list.append(self._temp_dir + '/' + imagePath)
                except:
                    pass
                
            elif mimeType in imageTypes:
                payload = part.get_payload(decode=False)
                imgdata = base64.b64decode(payload)
                # Generate MD5 hash of the payload
                m = hashlib.md5()
                m.update(payload.encode('utf-8'))
                imagePath = m.hexdigest() + '.' + mimeType.split('/')[1]
                try:
                    with open(self._temp_dir + '/' + imagePath, 'wb') as f:
                        f.write(imgdata)
                    self.image_list.append(self._temp_dir + '/' + imagePath)
                except:
                    pass
            else:
                fileName = part.get_filename()
                payload = part.get_payload(decode=False)
                payload_data = base64.b64decode(payload)
           
                # Generate MD5 hash of the payload
                m = hashlib.md5()
                m.update(payload.encode('utf-8'))
               
                if 'zip' in mimeType.split('/')[1]:
                    filePath = m.hexdigest() + '.zip'
                else:
                    filePath = m.hexdigest() + '.' + mimeType.split('/')[1]

                if not fileName:
                    fileName = "Unknown"
                with open(self._temp_dir + '/' + filePath, 'wb') as f:
                    f.write(payload_data)
                self.attachments.append(self._temp_dir + '/' + filePath)
            

        if len(self.attachments):
            footer = '<p><hr><p><b>Attached Files:</b><p><ul>'
            for a in self.attachments:
                footer = footer + '<li>' + a + '</li>'
            footer = footer + '</ul><p><br>Generated by EMLRender v1.0'
            m = hashlib.md5()
            m.update(footer.encode('utf-8'))
            imagePath = m.hexdigest() + '.png'
            try:
                imgkit.from_string(footer, self._temp_dir + '/' + imagePath, options = imgkitOptions)
                self.image_list.append(self._temp_dir + '/' + imagePath)
            except:
                pass
            
        resultImage = self._temp_dir + '/' + 'new.png'
        if len(self.image_list) > 0:
            images = list(map(Image.open, self.image_list))
            combo = self.__append_images(images)
            combo.save(resultImage)
        return {
            'result': resultImage,
            'images': self.image_list,
            'attachments': self.attachments
        }
        