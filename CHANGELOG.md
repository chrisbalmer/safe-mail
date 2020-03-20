# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [1.0.0] - 2020-03-20
    
    - Upload EML and MSG mail messages as well as Microsoft Office documents themselves
    - .MSG mail messages are Microsoft binary email format
    - Generates a PNG of the message itself named {file_name}.png
    - Extracts all embedded & attached images/attachments within the email message
    - Provides a OCR text file of the generated mail message
    - Generates a JSON file representing the mail message headers
    - Extracts attachments of mail messages 
    - Generates an image & PDF of each attachment
    - Attempts to extract any identified Macros within attachments and creates a JSON file representing the Macro code base
    - PDF Documents will generate output from [pdfid](https://blog.didierstevens.com/2009/03/31/pdfid/) & [pdfparser](https://blog.didierstevens.com/programs/pdf-tools/) tools
    - ZIP attachments will extract the zip and return any files within the zip