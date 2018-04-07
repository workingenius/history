"""
模型 2

针对 模型 1 在人物关系方面有所改动

两人除了"认识"关系，增加了"友好度"的概念
"""

from collections import defaultdict
from itertools import islice, cycle

from helpers import shuffle
from model1 import Individual, Nation, Hobby

friends = defaultdict(int)


def feel_better(a, b, value):
    """{a} 对 {b} 的好感提升 {value}"""
    assert isinstance(a, Individual)
    assert isinstance(b, Individual)
    friends[(a, b)] += value


def feel_worse(a, b, value):
    """{a} 对 {b} 的好感下降 {value}"""
    assert isinstance(a, Individual)
    assert isinstance(b, Individual)
    friends[(a, b)] -= value


def acquaintance_p(a, b):
    """{a} 是否知道 {b}"""
    assert isinstance(a, Individual)
    assert isinstance(b, Individual)
    return (a, b) in friends


def acquaintance_of(a):
    """{a} 的所有认识的人"""
    assert isinstance(a, Individual)
    for rel in filter(lambda i: i[0] == a, friends.keys()):
        yield rel[1]


def feeling_of(a, b):
    """{a} 对 {b} 的感觉如何"""
    assert isinstance(a, Individual)
    assert isinstance(b, Individual)
    return friends[(a, b)]


if __name__ == '__main__':
    # 参数
    INDIVIDUAL_COUNT = 1000
    MEET_TIMES = 10
    NATIONS = ['魏', '蜀', '吴']  # 势力数量和名称
    INIT_NATION_COUNT = 30  # 给前若干个人依次设置初始势力

    # 人物登场
    INDIVIDUAL_COUNT = INDIVIDUAL_COUNT
    inds = [Individual() for i in range(INDIVIDUAL_COUNT)]

    # 分配初始势力
    nations = [Nation(n) for n in NATIONS]
    for i, n in enumerate(islice(cycle(nations), 0, INIT_NATION_COUNT)):
        inds[i].nation = n

    # 世界开始运转
    # 若干次机会随机相遇
    MEET_TIMES = MEET_TIMES

    for x in range(MEET_TIMES):

        # 随机相遇 不算遇到自己
        meetings = filter(lambda i: i[0] is not i[1],
                          zip(shuffle(inds), shuffle(inds)))

        for ind1, ind2 in meetings:
            pass
