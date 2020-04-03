# portions of this Dockerfile are from this repository https://github.com/alephdata/convert-document
FROM ubuntu:19.10

# Declare Enviorment Variables
ENV DEBIAN_FRONTEND 'noninteractive' \
    LANG='en_US.UTF-8' \
    LC_ALL='en_US.UTF-8'

# Set up the locale and make sure the system uses unicode for the file system.
RUN apt-get -qq -y update \
    && apt-get -q -y install locales \
    && sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen \
    && dpkg-reconfigure locales \
    && update-locale LANG=en_US.UTF-8

# Install/Setup Dependencies
# "libreoffice" is a meta package which will pull all other libreoffice needed packages and basic fonts
# "hyphen-*" will pull all hyphen packages instead of listing each package
RUN apt-get -qq -y update \
    && apt-get -q -y --no-install-recommends install \
	libreoffice \
        libreoffice-java-common openjdk-11-jre-headless \
        hyphen-* \
        python3-pip python3-uno python3-lxml python3-icu \
        unoconv wkhtmltopdf \
        tesseract-ocr libtesseract-dev poppler-utils \ 
    && apt-get -qq -y autoremove \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# RUN echo ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true | debconf-set-selections
# RUN apt-get -q -y install ttf-mscorefonts-installer

# Install Python Requirments
COPY requirements.txt /tmp/requirements.txt
RUN ln -s /usr/bin/python3 /usr/bin/python \
    && pip3 install --no-cache-dir -q --upgrade setuptools \
    && pip3 install --no-cache-dir -q -r /tmp/requirements.txt

# create user "app" with GID of 1000 and set its default shell to false
RUN groupadd -g 1000 -r app \
    && useradd -m -u 1000 -s /bin/false -g app app

# Setup Caching Directories
RUN mkdir -p /uploads \
    && chown app:app /uploads \
    && mkdir -p /downloads \
    && chown app:app /downloads

# Copy Entire Repo Contents inside docker
COPY . /app
WORKDIR /app

# Setup Python Enviorment
RUN python setup.py install
USER app

#ENTRYPOINT [ "/bin/ash", "/app/entrypoint.sh" ]
CMD ["gunicorn", \
     "--threads", "3", \
     "--bind", "0.0.0.0:7001", \
     # "--max-requests", "100", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--timeout", "600", \
     "--graceful-timeout", "500", \
     "safemail.app:app"]
