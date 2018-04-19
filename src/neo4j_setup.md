### Docker
Docker version 17.12.0-ce, build c97c6d6

### Neo4j
[readme here](https://hub.docker.com/_/neo4j/)

#### Install
docker pull registry.docker-cn.com/library/neo4j:3.3

#### Start
```
docker run \
    --publish=7474:7474 --publish=7687:7687 \
    --volume=$HOME/neo4j/data:/data \
    --volume=$HOME/neo4j/logs:/logs \
    --env=NEO4J_dbms_memory_pagecache_size=4G \
    --env=NEO4J_AUTH=none \
    neo4j:3.3
```

### PyNeo4j
[readme here](https://neo4j.com/developer/python/)
[and here](https://neo4j.com/docs/api/python-driver/current/)

#### Neo4j Python driver
pip install neo4j-driver

try this out:
```
from neo4j.v1 import GraphDatabase

class HelloWorldExample(object):

    def __init__(self, uri, user, password):
        # by default uri should be `bolt://localhost:7687`
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def print_greeting(self, message):
        with self._driver.session() as session:
            greeting = session.write_transaction(self._create_and_return_greeting, message)
            print(greeting)

    @staticmethod
    def _create_and_return_greeting(tx, message):
        result = tx.run("CREATE (a:Greeting) "
                        "SET a.message = $message "
                        "RETURN a.message + ', from node ' + id(a)", message=message)
        return result.single()[0]

if __name__ == '__main__':
    Hello = HelloWorldExample('bolt://localhost:7687', 'neo4j', 'neo4j')
    Hello.print_greeting('Hello 357!')        
```

By using cypher `match (n) return n` in http://localhost:7474/browser/
you should see something like this:![picture](http://i1.bvimg.com/641642/cbfa9c7e5edd6147.png)
