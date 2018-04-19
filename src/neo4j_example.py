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
        # 去除value为空的
        keys = list(properties.keys())
        for k in keys:
            if properties[k] is None:
                properties.pop(k)
        return '{'+', '.join(['{}:"{}"'.format(k, v) if type(v) == str else '{}:{}'.format(k, v) for k, v in properties.items()])+'}' 

    @staticmethod
    def label2str(labels):
        if labels:
            return ':'+':'.join(labels) if type(labels)==list else labels
        else:
            return ''

    # 新增节点
    def add_node(self, labels='', properties={}):
        '''
        labels: str or list of str
        properties: dict
        '''
        label_str = self.label2str(labels)
        property_str = self.dict2str(properties)
        statement = 'CREATE (n{labels} {properties}) with n match (n) return ID(n)'.format(labels=label_str, properties=property_str)    
        res = self.cypher(statement)
        return [x['ID(n)'] for x in res]

    # 获取单个节点
    def get_node(self, id=None):
        statement = 'MATCH (a) where ID(a)={id} RETURN a'.format(id=id)  
        res = list(self.cypher(statement))
        if len(res) == 0:
            return None  
        return res[0]['a']
    # 获取众多节点
    def get_nodes(self, labels='', properties={}):
        '''
        name: 
        labels: str or list of str
        properties: dict
        '''        
        label_str = self.label2str(labels)
        property_str = self.dict2str(properties)
        statement = 'MATCH (a{labels} {properties}) RETURN a'.format(labels=label_str, properties=property_str)
        return self.cypher(statement)



    # 新增关系
    # 关系暂时只能有一个label
    def add_relation(self, id1, id2, labels='', properties={}, bidiriction=False):
        '''
        id1, id2: find by `match (n) return ID(n)`
        labels: str or list of str
        properties: dict
        bidiriction: if create bidiriction relations
        '''        
        label_str = self.label2str(labels)
        property_str = self.dict2str(properties)
        if not bidiriction:
            statement = 'MATCH (n), (m) where ID(n)={id1} and ID(m)={id2} CREATE (n)-[r{labels} {properties}]->(m)'.format(labels=label_str, properties=property_str, id1=id1, id2=id2)
        else:
            statement = 'MATCH (n), (m) where ID(n)={id1} and ID(m)={id2} CREATE (n)-[r{labels} {properties}]->(m)'.format(labels=label_str, properties=property_str, id1=id1, id2=id2)
            statement = 'MATCH (n), (m) where ID(n)={id1} and ID(m)={id2} CREATE (n)<-[r{labels} {properties}]-(m)'.format(labels=label_str, properties=property_str, id1=id1, id2=id2)           
        return self.cypher(statement)

    # 查询关系
    def get_relation(self, id1, id2, labels='', properties={}, bidiriction=False):
        '''
        id1, id2: find by `match (n) return ID(n)`
        labels: str or list of str
        properties: dict
        bidiriction: if get bidiriction relations
        '''            
        label_str = self.label2str(labels)
        property_str = self.dict2str(properties)
        if not bidiriction:
            statement = 'MATCH (n)-[r{labels} {properties}]->(m) where ID(n)={id1} and ID(m)={id2} RETURN r'.format(labels=label_str, properties=property_str, id1=id1, id2=id2)
        else:
            statement = 'MATCH (n)-[r{labels} {properties}]-(m) where ID(n)={id1} and ID(m)={id2} RETURN r'.format(labels=label_str, properties=property_str, id1=id1, id2=id2)            
        return self.cypher(statement)

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
    for i in foo.get_relation(79, 6602):
        print(i)

