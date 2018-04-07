from random import shuffle as _shuffle


def shuffle(l):
    """有返回值的 shuffle 函数"""
    l1 = list(l)
    _shuffle(l1)
    return l1
