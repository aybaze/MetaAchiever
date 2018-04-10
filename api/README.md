# API

## Install requirements

```
pip install -r requirements.txt
```

## Launch neo4j

```
docker run -d -p=7474:7474 -p=7687:7687 -v $HOME/neo4j/data:/data -v $HOME/neo4j/logs:/logs neo4j
```

Login to neoj4 admin console at http://localhost:7474 and change the password to `password`

## Run API Server

```
./main.py
```
