# safe-mail

safe-mail is a Docker service to help security teams safely interact with msg, eml, and documents

## Synopsis

safe-mail is a Docker service to help security teams safely interact with msg, eml, and documents

### Installation

First you can download safe-mail by cloning the repository:


```bash
git clone git@github.com:swimlane/safe-mail.git
```

### Building Docker Image

You first need to build the Docker image:

```bash
docker build --force-rm -t safe-mail .
```

### Running the Docker Image

You can run the docker image in a few different ways:

#### Running the CLI tool 

```bash
docker run -p 7001:7001 -ti safe-mail 
```

#### Running the API 

If you want to run the API, then simply emit the value you want to search:

**NOTE**: You must now use docker-compose to expose the api directly

```bash

```

#### API ENDPOINTS

There are several new API endpoints available:

##### Upload MSG & EML Files

```bash

```

##### Upload Documents & Files

```bash

```

## Notes
```yaml
   Name: safe-mail
   Created by: Josh Rickard
   Created Date: 02/25/2020
```