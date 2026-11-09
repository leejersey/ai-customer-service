# -*- coding: utf-8 -*-
"""把「猜对了几条」算成一个比例，并数每种标准答案被猜成了什么。"""


def accuracy(gold: list[str], predicted: list[str]) -> float:
    """gold 是标准答案，predicted 是程序的判断。两者必须一样长。"""
    if len(gold) == 0 or len(gold) != len(predicted):
        raise ValueError("两份标签必须一样长，而且不能是空的")
    correct = 0
    for index, expected in enumerate(gold):
        if predicted[index] == expected:
            correct = correct + 1
    return correct / len(gold)


def confusion(gold: list[str], predicted: list[str]) -> dict:
    """外层键是标准答案，内层键是预测，值是出现次数。"""
    if len(gold) != len(predicted):
        raise ValueError("两份标签必须一样长")
    counts: dict[str, dict[str, int]] = {}
    for index, expected in enumerate(gold):
        guess = predicted[index]
        if expected not in counts:
            counts[expected] = {}
        row = counts[expected]
        # 没有这个预测过，就从 0 开始加，避免 KeyError。
        row[guess] = row.get(guess, 0) + 1
    return counts
