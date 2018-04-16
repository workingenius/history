from neo4j.v1 import GraphDatabase

class myneo4j(object):
    ''' 
    play with the movie-graph
    using it like this:

    > 
    > 
    > 
    > 
    '''
    def __init__(self, uri="bolt://localhost:7687", user=None, password=None):
        if user is None:
            self._driver = GraphDatabase.driver(uri, auth=None)
        else:
            self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def __del__(self):
        self._driver.close()

    # ------------ 标准化接口 ------------
    @staticmethod
    def dict2str(properties):
        return '{'+', '.join(['{}:"{}"'.format(k, v) if type(v) == str else '{}:{}'.format(k, v) for k, v in properties.items()])+'}' 

    @staticmethod
    def label2str(labels):
        return ':'.join(labels) if type(labels)==list else labels

    # 新增节点
    def add_node(self, labels='', properties={}):
        '''
        name: 
        labels: str or list of str
        properties: dict
        '''
        label_str = self.label2str(labels)
        property_str = self.dict2str(properties)
        statement = 'CREATE (n:{labels} {properties})'.format(labels=label_str, properties=property_str)
        print(statement)        
        return self.cypher(statement)

    # 获取节点
    def get_nodes(self, labels='', properties={}):
        '''
        name: 
        labels: str or list of str
        properties: dict
        '''        
        label_str = self.label2str(labels)
        property_str = self.dict2str(properties)        
        statement = 'MATCH (a:{labels} {properties}) RETURN a'.format(labels=label_str, properties=property_str)
        print(statement)
        return self.cypher(statement)

    # 新增关系
    def add_relations(self, node_id1, node_id2, labels='', properties={}):
        pass

    # 修改节点
    def set_nodes(self, ):
        pass

    # 修改关系
    def set_relations(self, ):
        pass

    # 删除全部节点
    def delete_all(self):
        '''
        delete all data
        '''
        print('match (n) detach delete n')
        self.cypher('match (n) detach delete n')
        return

    # ------------ 自定义cypher ------------
    def cypher(self, statement, parameters=None, **kwparameters):
        '''
        Parameters: 
            statement – template Cypher statement
            parameters – dictionary of parameters
            kwparameters – additional keyword parameters
        Returns:    
            StatementResult object
        '''
        with self._driver.session() as session:
            with session.begin_transaction() as tx:
                result = tx.run(statement, parameters=parameters, **kwparameters)
        return result

if __name__ == '__main__':
    foo = myneo4j()
