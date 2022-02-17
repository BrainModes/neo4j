# Neo4j Api Service

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg?style=for-the-badge)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.9](https://img.shields.io/badge/python-3.9-green?style=for-the-badge)](https://www.python.org/)

the service wrap up some basic neo4j query into API for further usage.

The service will running at `<host>:6062`

## Installation

follow the step below to setup the service

### Clone

- Clone this repo to machine using `https://git.indocresearch.org/platform/dataset_neo4j.git`

### Setup:

> To run the service as dev mode

```
python3 -m pip install -r requirement.txt
python3 app.py
```

> To run the service as production in docker and gunicorn

```
docker build . -t neo4j/latest
docker run neo4j/latest -d
```

## Features:

the service uses the swagger to make the api documents: see the detailed [doc](localhost:6062/v1/api-doc)

### Node Related API:

 - Retrieve node by id

 - Retrieve node by relationship

 - Query node by input payload

 - Add new nodes

 - Update nodes attributes

 - Retrieve nodes beyond the relationship

### Relation Related API:

 - Retrive the relation between nodes

 - Add new relationship between nodes

 - Update the relationship between nodes



