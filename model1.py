from collections import defaultdict
from itertools import count, cycle, islice
from math import fabs
from random import randint, shuffle as _shuffle
from typing import Optional


id_iter = count()


class Nation(object):
    """势力"""
    def __init__(self, _id):
        self.id = _id

    def __str__(self):
        return self.id

    def __hash__(self):
        return hash(self.id)


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
        self._nation = None

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

    @property
    def nation(self) -> Optional[Nation]:
        return self._nation

    @nation.setter
    def nation(self, n: Nation) -> None:
        assert isinstance(n, Nation)
        self._nation = n


# ### helpers ###


def shuffle(l):
    """有返回值的 shuffle 函数"""
    l1 = list(l)
    _shuffle(l1)
    return l1


if __name__ == '__main__':

    # 参数
    INDIVIDUAL_COUNT = 1000  # 登场人物数量
    MEET_TIMES = 5  # 随机相遇次数
    NATIONS = ['魏', '蜀', '吴']  # 势力数量和名称
    INIT_NATION_COUNT = 30  # 给前若干个人依次设置初始势力
    BE_FRIEND_IF = 5000
    JOIN_IF = 2000

    # 人物登场
    INDIVIDUAL_COUNT = INDIVIDUAL_COUNT
    inds = [Individual() for i in range(INDIVIDUAL_COUNT)]

    # 分配初始势力
    nations = [Nation(n) for n in NATIONS]
    for i, n in enumerate(islice(cycle(nations), 0, INIT_NATION_COUNT)):
        inds[i].nation = n

    # 朋友关系
    # 用集合表示无向图
    # 节点连接表示朋友，否则表示不相识
    friends = set()

    def is_friend(a: Individual, b: Individual) -> bool:
        return (a, b) in friends


    def become_friend(a: Individual, b: Individual) -> None:
        friends.add((a, b))
        friends.add((b, a))

    # 世界开始运转
    # 若干次机会随机相遇
    MEET_TIMES = MEET_TIMES

    for x in range(MEET_TIMES):

        # 随机相遇
        meetings = zip(shuffle(inds), shuffle(inds))

        for ind, ind2 in meetings:
            # 去掉自己遇到自己的情况
            if ind == ind2:
                continue

            # print('{0} 遇到了 {1}'.format(ind, ind2))
            if is_friend(ind, ind2):
                continue

            # 两人开始接触
            s = Hobby.similarity(ind.hobby, ind2.hobby)

            # 如果比较投缘
            if s < BE_FRIEND_IF:
                # 则结交
                become_friend(ind, ind2)
                print('{0} 与 {1} 成为好友'.format(ind, ind2))

            # 如果十分投缘
            if s < JOIN_IF:
                # 没阵营的 会 加入另外一个人的阵营
                n1, n2 = ind.nation, ind2.nation
                if n1 and not n2:
                    ind2.nation = ind.nation
                    print('{0} 因为 {1} 加入 {2}'.format(ind2, ind, ind.nation))
                if not n1 and n2:
                    ind.nation = ind2.nation
                    print('{0} 因为 {1} 加入 {2}'.format(ind, ind2, ind2.nation))

    # 结交过后 每个没势力的人自主选择势力
    for ind in inds:
        if ind.nation is None:
            # 哪个势力中自己的朋友最多，就加入哪个

            # 自己的朋友们
            my_friends = [ind2 for ind2 in inds if (ind2 is not ind) and (is_friend(ind, ind2))]

            # 如果没朋友就不管了
            if not my_friends:
                print('不管了')
                continue

            # 统计自己哪个势力里朋友最多
            count_nation = defaultdict(int)
            for ind2 in my_friends:
                count_nation[ind2.nation] += 1
            # 没势力的朋友不算
            if None in count_nation:
                count_nation.pop(None)

            # 朋友势力汇总排序
            nation_sort = sorted(list(count_nation.items()), key=lambda item: item[1], reverse=True)
            # 自己要加入的
            if nation_sort:
                the_nation = nation_sort[0][0]
                print('{0} 选择加入 {1}'.format(ind, the_nation))
                ind.nation = the_nation

    # 结交过后 进入 结算环节
    stats = {str(n): len([1 for i in inds if i.nation is n]) for n in nations}
    print(stats)
