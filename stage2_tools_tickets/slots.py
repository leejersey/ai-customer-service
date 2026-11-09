# -*- coding: utf-8 -*-
"""哪些意图还缺槽位，以及缺了之后问哪一句。

槽位是办成这件事必须先知道的一项事实。阶段 1 已经会从句子里抽订单号。
抽到的是 None 时，不能编一个号码去查库，要先问顾客。
"""

# 投诉和转人工不在这张表里：没有订单号也可以建工单。
REQUIRED_SLOTS = {
    "查订单": ("order_id",),
    "退款": ("order_id",),
}

QUESTIONS = {
    "order_id": "请告诉我订单号。它一般是一串数字，例如 10086。",
}


def missing_slots(intent: str, slots: dict) -> list[str]:
    """按固定顺序检查。这一阶段每条意图最多缺订单号一项。"""
    missing = []
    for name in REQUIRED_SLOTS.get(intent, ()):
        value = slots.get(name)
        if value is None or str(value).strip() == "":
            missing.append(name)
    return missing


def question_for(slot_name: str) -> str:
    """追问的句子写在程序里。缺订单号时不让模型现编一个号码。"""
    return QUESTIONS.get(slot_name, f"还需要补充：{slot_name}")
