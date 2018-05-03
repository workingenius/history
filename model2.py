"""
模型 2

针对 模型 1 在人物关系方面有所改动

两人除了"认识"关系，增加了"友好度"的概念
"""

from collections import defaultdict
from itertools import islice, cycle
from statistics import mean

from helpers import shuffle
from model1 import Individual, Nation, Hobby


friends = defaultdict(int)


def feel_better(a, b, value):
    """{a} 对 {b} 的好感提升 {value}"""
    assert isinstance(a, Individual)
    assert isinstance(b, Individual)
    friends[(a, b)] += value


feel_change = feel_better


def feel_worse(a, b, value):
    """{a} 对 {b} 的好感下降 {value}"""
    assert isinstance(a, Individual)
    assert isinstance(b, Individual)
    friends[(a, b)] -= value


def set_feeling(a, b, value):
    u"""设置 {a} 对 {b} 的友好度"""
    assert isinstance(a, Individual)
    assert isinstance(b, Individual)
    friends[(a, b)] = value


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


# hobby -> feeling


def hobby_feeling(h1, h2):
    u"""相性对友好度的影响"""
    s = Hobby.similarity(h1, h2)
    return int(10000 - s) / 100


# helpers with log

def act_join(ind, nation):
    if ind.nation:
        n0 = ind.nation
        if n0 != nation:
            ind.nation = nation
            print('{0} 从 {1} 变为 {2}'.format(ind, n0, nation))
    else:
        ind.nation = nation
        print('{0} 加入 {1}'.format(ind, nation))


def act_feel(ind1, ind2, feeling):
    if acquaintance_p(ind1, ind2):
        f0, f1 = feeling_of(ind1, ind2), feeling
        if f0 == f1:
            return

        cap = '{0} 对 {1} 的友好'.format(ind1, ind2)
        if f1 > f0:
            cap += '提升了'
        elif f1 < f0:
            cap += '下降了'

        if f1 > 10:
            cap += ', 现在有好高'
        if 10 >= f1 >= -20:
            cap += ', 现在没感觉'
        if f1 < -20:
            cap += ', 现在很讨厌'
        print(cap)
    else:
        if feeling > 10:
            print('{0} 开始对 {1} 有好感'.format(ind1, ind2))
        if 10 >= feeling >= -20:
            print('{0} 开始对 {1} 无所谓'.format(ind1, ind2))
        if feeling < -20:
            print('{0} 开始对 {1} 很讨厌'.format(ind1, ind2))
            
    set_feeling(ind1, ind2, feeling)


if __name__ == '__main__':
    # 参数
    INDIVIDUAL_COUNT = 1000
    MEET_TIMES = 10
    NATIONS = ['魏', '蜀', '吴']  # 势力数量和名称
    INIT_NATION_COUNT = 40  # 给前若干个人依次设置初始势力

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

    def meet():
        u"""随机相遇"""

        # 随机相遇 不算遇到自己
        meetings = islice(filter(lambda i: i[0] is not i[1],
                                 zip(shuffle(inds), shuffle(inds))),
                          0, int(len(inds) / 1.1))

        for ind1, ind2 in meetings:
            # 相遇后 二者的互相影响是对等的
            change = hobby_feeling(ind1.hobby, ind2.hobby)
            act_feel(ind1, ind2, change)
            act_feel(ind2, ind1, change)

    def hear_about():
        u"""一部分人听说别人"""
        # 一部分人成为名人，被人听说
        famous_persons = shuffle(inds)[0:int(len(inds) / 10)]

        # 一部分人听别人
        # "the masses" for "群众"
        the_masses = shuffle(inds)[0:int(len(inds) / 3)]

        # news for "新闻"
        news = zip(cycle(famous_persons), the_masses)
        news = [(ind1, ind2) for ind1, ind2 in news if ind1 and ind2]

        for ind1, ind2 in news:
            # 好感度单向变化
            act_feel(ind2, ind1, hobby_feeling(ind1.hobby, ind2.hobby))

    def join_nation():
        u"""加入势力"""
        for ind in inds:
            acqs = [acq for acq in acquaintance_of(ind)]
            # 按好感从高到低排列
            acqs = sorted(acqs, key=lambda acq: -feeling_of(ind, acq))
            # 加入好感度最高的人的势力
            if acqs:
                if acqs[0].nation:
                    act_join(ind, acqs[0].nation)

    def close_up():
        u"""相同势力的人相性相互靠拢"""

        def _move_toward(ind, target, k):
            u"""{ind} 这个人的相性向着 {target} 靠拢 以 k 为靠近程度"""
            v = ind.hobby + int((target - ind.hobby) * k)
            ind.hobby = v

        for nation in nations:
            # compatriot for "同胞"
            compatriots = filter(lambda ind: ind.nation == nation, inds)

            avg_hobby = mean([i.hobby for i in compatriots])
            for ind in compatriots:
                _move_toward(ind, avg_hobby, 0.2)

    def recalc_feeling():
        u"""重算友好度"""
        for ind1, ind2 in friends:
            act_feel(ind1, ind2, hobby_feeling(ind1.hobby, ind2.hobby))

    # ####### GO !!!!! ########
    for x in range(MEET_TIMES):
        meet()
        hear_about()
        join_nation()
        close_up()
        recalc_feeling()

    # ### 结算 ###
    stats = {str(n): len([1 for i in inds if i.nation is n]) for n in nations}
    print(stats)
