"""
# 模型 1
一些特点（可以针对改进之处）
1. 人物间的关系
    + 是不带属性的 即两人之间只有"有关系"和"没关系"两种 且描述的是"朋友"关系
    + 是无向的 即 A对B 和 B对A 是完全相等的
        也就是说 若A是B的朋友 则 B一定是A的朋友
2. 决定关系
    + 除初始值，势力完全由人物间关系决定
    + 人物间关系完全由相性决定
    + 相性完全随机指定
3. 事件
    + 只有完全随机的"相遇"事件，触发"结交"或者"加入"
4. 人物
    + 一旦初始化，人物没有生、老、死
    + 势力不会反覆 即一旦加入了某个势力就再也不会退出 或加入其它势力
    + 相性用一个数字表达，且固定不变
    + 所有人物完全平等
        + 平均每人获得行动的机会相同
        + 每人可以作出的选择相同
        + 平均每人的影响力相同
"""

from collections import defaultdict
from itertools import count, cycle, islice
from math import fabs
from random import randint, shuffle as _shuffle
from typing import Optional

import numpy as np
from tqdm import tqdm
from neo4j_example import myneo4j

id_iter = count()

class Nation(object):
    """势力"""
    def __init__(self, _id):
        self.id = _id

    def __str__(self):
        return self.id

    def __hash__(self):
        return hash(self.id)

    def prop2dict(self):
        return {'name':self.id}        

class Hobby(int):
    """相性"""

    @classmethod
    def rand(cls):
        return cls(randint(-10000, 10000))

    @staticmethod
    def similarity(h1, h2) -> int:
        """和另外一个 hobby 的相似程度"""
        return fabs(int(h1) - int(h2))

class Individual(object):
    """个人"""

    def __init__(self, hobby: Optional[Hobby]=None):
        self.id = next(id_iter)
        if hobby is None:
            hobby = Hobby.rand()
        self._hobby = hobby

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        if self._nation:
            return '{0} 的 人物{1}'.format(self._nation, self.id)
        else:
            return '人物{0}'.format(self.id)

    @property
    def hobby(self) -> Hobby:
        return self._hobby

    def prop2dict(self):
        return {'hobby':self._hobby}

def shuffle(l):
    """有返回值的 shuffle 函数"""
    l1 = list(l)
    _shuffle(l1)
    return l1


# 低效率版本，全部使用我写的标准化接口
# 由于高额的通信成本导致效率较低
# 由于shema设计的不完善，导致查询复杂
if __name__ == '__main__':
    # 参数
    INDIVIDUAL_COUNT = 100  # 登场人物数量
    MEET_TIMES = 1  # 随机相遇次数
    NATIONS = ['魏', '蜀', '吴']  # 势力数量和名称
    INIT_NATION_COUNT = 30  # 给前若干个人依次设置初始势力
    BE_FRIEND_IF = 5000
    JOIN_IF = 2000

    # 数据服务器
    database = myneo4j()
    database.delete_all() # 清空数据库(可以通过增加版本label的方式，在保留历史数据的情况下进行新实验)

    # 人物登场
    indv_list = []
    for i in tqdm(range(INDIVIDUAL_COUNT)):
        # 创建人物
        p = Individual()
        # 保存人物
        indv_list.extend(database.add_node(['individual'], p.prop2dict()))
    # 势力登场
    nati_list = []
    for i in tqdm(NATIONS):
        # 创建势力
        n = Nation(i)
        # 保存势力
        nati_list.extend(database.add_node(['nation'], n.prop2dict()))
    # 分配初始势力
    for i, n in enumerate(islice(cycle(nati_list), 0, INIT_NATION_COUNT)):
        database.add_relation(indv_list[i], n, ['in'])

    def is_friend(a, b):
        res = database.get_relation(a, b)
        if len(list(res)) > 0:
            return True
        return False

    def become_friend(a, b):
        database.add_relation(a, b, ['friend'], bidiriction=True)

    # 世界开始运转
    # 若干次机会随机相遇
    for x in range(MEET_TIMES):

        # 随机相遇
        meetings = zip(shuffle(indv_list), shuffle(indv_list))

        for ind, ind2 in meetings:
            # 去掉自己遇到自己的情况
            if ind == ind2:
                continue

            print('{0} 遇到了 {1}'.format(ind, ind2))
            if is_friend(ind, ind2):
                continue
            
            # 获取两人属性
            a = database.get_node(id=ind)
            b = database.get_node(id=ind2)

            # 获取两人势力
            c = list(database.cypher('MATCH (n)-[r:in]->(m:nation) WHERE ID(n)={id} RETURN ID(m)'.format(id=ind)))
            n1 = c[0]['ID(m)'] if len(c) > 0 else None
            d = list(database.cypher('MATCH (n)-[r:in]->(m:nation) WHERE ID(n)={id} RETURN ID(m)'.format(id=ind2)))
            n2 = d[0]['ID(m)'] if len(d) > 0 else None

            # 两人开始接触
            s = Hobby.similarity(a.properties['hobby'], b.properties['hobby'])

            # 如果比较投缘
            if s < BE_FRIEND_IF:
                # 则结交
                become_friend(ind, ind2)
                print('{0} 与 {1} 成为好友'.format(ind, ind2))

            # 如果十分投缘
            if s < JOIN_IF:
                # 没阵营的 会 加入另外一个人的阵营
                if n1 and not n2:
                    database.add_relation(ind2, n1, ['in'])
                    print('{0} 因为 {1} 加入 {2}'.format(ind2, ind, n1))
                if not n1 and n2:
                    database.add_relation(ind, n2, ['in'])
                    print('{0} 因为 {1} 加入 {2}'.format(ind, ind2, n2))

    # 结交过后 每个没势力的人自主选择势力
    for ind in indv_list:
        a = list(database.cypher('MATCH (n)-[r:in]->(m:nation) WHERE ID(n)={id} RETURN ID(m)'.format(id=ind)))
        n = a[0]['ID(m)'] if len(a) > 0 else None        
        if n is None:
            max_c = 0
            max_nati = None
            # 统计各个势力里面的朋友数量
            friend_num = []
            for nati in nati_list:
                c = database.cypher('MATCH (n)-[r:in]->(m) WHERE ID(m)={nati} WITH n MATCH (ind)-[r:friend]-(n) WHERE ID(ind)={ind} RETURN count(n)'.format(nati=nati, ind=ind))
                c = list(c)[0]['count(n)']
                friend_num.append(c)
                if c > max_c:
                    max_c = c
                    max_nati = nati
            if max_nati:
                print('{0}：{1}'.format(ind, '，'.join(['{0} 国 {1} 个朋友'.format(x,y) for y, x in zip(friend_num, nati_list)])))
                print('{0} 选择加入 {1}'.format(ind, nati))
                database.add_relation(ind, max_nati, ['in'])

    # 世界运转完毕 进入结算环节
    for nati in nati_list:
        # 获取国家属性
        a = database.get_node(id=nati).properties['name']
        # 获取国家内人员数量
        b = list(database.cypher('MATCH (n)-[r:in]->(m) WHERE ID(m)={nati} RETURN count(n)'.format(nati=nati)))[0]['count(n)']
        print('{name} 国 共计 {num} 人'.format(name=a, num=b))
