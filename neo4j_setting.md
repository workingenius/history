### Docker
Docker version 17.12.0-ce, build c97c6d6

### Neo4j

#### Install
docker pull registry.docker-cn.com/library/neo4j
currently, the version of neo4j should be 3.3.4

#### Start
docker run \
    --publish=7474:7474 --publish=7687:7687 \
    --volume=$HOME/neo4j/data:/data \
    neo4j

#### Change Password
Inital password: neo4j
Change to any password you like

### PyNeo4j
https://neo4j.com/developer/python/

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
you should see something like this:
