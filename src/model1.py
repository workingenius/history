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

from collections import defaultdict, OrderedDict
from itertools import count, cycle, islice
from math import fabs
from random import randint, shuffle as _shuffle
from typing import Optional

import numpy as np
import pandas as pd
from tqdm import tqdm
from neo4j_example import myneo4j

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

class Characteristic(object):
    """属性"""
    def __init__(self, tongshuai, wuli, zhili, zhengzhi):
        self.tongshuai = tongshuai
        self.wuli = wuli
        self.zhili = zhili
        self.zhengzhi = zhengzhi
        self.heji = tongshuai + wuli + zhili + zhengzhi

    @staticmethod
    def pk(c1, c2) -> int:
        """
        两个人物相互pk
        胜率取决于4维之和
        c1赢返回1
        c2赢返回-1
        平手返回0
        """
        r = np.random.rand()
        if r < (c1.heji/(c1.heji+c2.heji)):
            return 1
        elif r > (c1.heji/(c1.heji+c2.heji)):
            return -1
        else:
            return 0

class Hobby(object):
    """相性"""
    def __init__(self, wuju, shuji, baowu, shijiu):
        self.wuju = self.convert(wuju)
        self.shuji = self.convert(shuji)
        self.baowu = self.convert(baowu)
        self.shijiu = self.convert(shijiu)
        # 将字符串转化为数字

    def convert(self, c):
        if c == '×':
            return -1
        elif c == '●':
            return 1
        else:
            return 0

    @staticmethod
    def similarity(h1, h2) -> int:
        """和另外一个 hobby 的相似程度"""
        s = h1.wuju * h2.wuju + h1.shuji * h2.shuji + h1.baowu * h2.baowu + h1.shijiu * h2.shijiu
        return s

class Individual(object):
    """个人"""

    def __init__(self, id, df):
        self.id = id
        self.name = df['武將']
        self._nation = None
        self._dengchangnian = df['登場年']
        self._characteristic = Characteristic(df['統率'], df['武力'], df['智力'], df['政治'])
        self._hobby = Hobby(df['武具'], df['書籍'], df['寶物'], df['嗜酒'])
        # self.qiang = df['槍']
        # self.qi = df['騎']
        # self.gong = df['弓']
        # self.zhanfa = df['戰法']
        # self.chuanshouteji = df['傳授特技']
        # self.zhongchentexing = df['重臣特性']

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        if self._nation:
            return '{0} 的 {1}'.format(self._nation, self.name)
        else:
            return '{0}'.format(self.name)

    @property
    def hobby(self) -> Hobby:
        return self._hobby

    def prop2dict(self):
        return {'name':self.name, '登场年':self._dengchangnian}

def shuffle(l):
    """有返回值的 shuffle 函数"""
    l1 = list(l)
    _shuffle(l1)
    return l1


# 低效率版本，全部使用我写的标准化接口
# 由于高额的通信成本导致效率较低
# 由于shema设计的不完善，导致查询复杂
if __name__ == '__main__':
    # 读取三国人物数据库
    heros = pd.read_excel('../data/heros.xlsx')
    # 参数
    TIME_PERIOD = range(180, 205, 5) # 事件发生的时间
    NATIONS = ['魏', '蜀', '吴']  # 势力数量和名称
    INIT_NATION_COUNT = 30  # 给前若干个人依次设置初始势力
    BE_FRIEND_IF = 1
    JOIN_IF = 2
    BE_ENEMY_IF = -2

    # 数据服务器
    database = myneo4j()
    database.delete_all() # 清空数据库(可以通过增加版本label的方式，在保留历史数据的情况下进行新实验)

    print('-------------- 人物初始化 --------------')
    # 人物登场
    indv_dict = OrderedDict()
    for i, idx in enumerate(heros.index):
        # 创建人物
        p = Individual(i, heros.loc[idx])
        # 保存人物
        uid = database.add_node(['individual'], p.prop2dict())[0]
        indv_dict[uid] = p
        # 打印
        print(f'{p.name} 登场于 {p._dengchangnian}')
    indv_list = list(indv_dict.keys())

    print('-------------- 初始势力分配 --------------')
    # 势力登场
    nati_dict = OrderedDict()
    for i in NATIONS:
        # 创建势力
        n = Nation(i)
        # 保存势力
        uid = database.add_node(['nation'], n.prop2dict())[0]
        nati_dict[uid] = n
    nati_list = list(nati_dict.keys())
    # 随机分配初始势力
    t_indv_list = shuffle(indv_list)
    for i, n in enumerate(islice(cycle(nati_list), 0, INIT_NATION_COUNT)):
        print(f'{indv_dict[t_indv_list[i]].name} 加入了 {nati_dict[n].id}')
        database.add_relation(t_indv_list[i], n, ['in'])

    def is_friend(a, b):
        res = database.get_relation(a, b)
        if len(list(res)) > 0:
            return True
        return False

    def become_friend(a, b):
        database.add_relation(a, b, ['friend'], bidiriction=True)

    # 世界开始运转
    # 若干次机会随机相遇
    for x in TIME_PERIOD:
        print(f'-------------- {x}年 --------------')
        # 打印当前状态
        t_indv_list = [indv_dict[a]._dengchangnian <= x for a in indv_list]
        # 随机相遇
        meetings = list(zip(shuffle(indv_list), shuffle(indv_list)))
        # 相遇最多100次
        meetings = meetings[:100]
        for ind, ind2 in meetings:
            # 去掉自己遇到自己的情况
            if ind == ind2:
                continue

            a = indv_dict[ind]
            b = indv_dict[ind2]

            print(f'{a.name} 遇到了 {b.name},', end='')
            if is_friend(ind, ind2):
                print('故交重逢，把酒言欢。')
                continue

            # 获取两人势力
            c = list(database.cypher('MATCH (n)-[r:in]->(m:nation) WHERE ID(n)={id} RETURN ID(m)'.format(id=ind)))
            n1 = c[0]['ID(m)'] if len(c) > 0 else None
            d = list(database.cypher('MATCH (n)-[r:in]->(m:nation) WHERE ID(n)={id} RETURN ID(m)'.format(id=ind2)))
            n2 = d[0]['ID(m)'] if len(d) > 0 else None

            # 两人开始接触
            s = Hobby.similarity(a._hobby, b._hobby)

            # 如果比较投缘
            if s >= BE_FRIEND_IF:
                # 则结交
                become_friend(ind, ind2)
                print('酒逢知己千杯少，羁绊等级上升。'.format(ind, ind2))
                # 如果十分投缘
                if s >= JOIN_IF:
                    # 没阵营的 会 加入另外一个人的阵营
                    if n1 and not n2:
                        database.add_relation(ind2, n1, ['in'])
                        print(f'{b.name} 因为 {a.name} 加入 {nati_dict[n1].id}')
                    if not n1 and n2:
                        database.add_relation(ind, n2, ['in'])
                        print(f'{a.name} 因为 {b.name} 加入 {nati_dict[n2].id}')
            elif s <= BE_ENEMY_IF:
                # 则交手一场
                res = Characteristic.pk(a._characteristic, b._characteristic)
                if res == 1:
                    print(f'{a.name} 教训了 {b.name}。')
                elif res == -1:
                    print(f'{b.name} 教训了 {a.name}。')
                else:
                    become_friend(ind, ind2)
                    print(f'不打不相识，两人成为了好友。')
            else:
                print('君子之交淡如水，有缘江湖再会。')

        print(f'-------------- {x}年 终 --------------')

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
                print('{0}：{1}'.format(indv_dict[ind].name, '，'.join(['{0} 国 {1} 个朋友'.format(x,y) for y, x in zip(friend_num, [nati_dict[x].id for x in nati_list])])))
                print('{0} 选择加入 {1} 国'.format(indv_dict[ind].name, nati_dict[max_nati].id))
                database.add_relation(ind, max_nati, ['in'])

    # 世界运转完毕 进入结算环节
    for nati in nati_list:
        # 获取国家属性
        a = database.get_node(id=nati).properties['name']
        # 获取国家内人员数量
        b = list(database.cypher('MATCH (n)-[r:in]->(m) WHERE ID(m)={nati} RETURN count(n)'.format(nati=nati)))[0]['count(n)']
        print('{name} 国 共计 {num} 人'.format(name=a, num=b))
