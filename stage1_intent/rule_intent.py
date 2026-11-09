# -*- coding: utf-8 -*-
"""用关键词判断顾客想干什么。

不调用模型，所以没有密钥也能运行。
局限写在这个文件的规则顺序里：先匹配到的词赢，句子里有那个词就算，不管是不是在否定。
"""

import re

# 六个意图用固定字符串，避免有的文件写成「退货」、有的写成「退款」，后面的准确率会对不上。
INTENTS = ("咨询", "查订单", "退款", "投诉", "转人工", "其他")

# 列表的顺序就是优先级。越靠前越先检查。
# 不用字典，是为了让「谁先被看见」直接等于从上往下读，不用再记字典的顺序规则。
# 「转人工」放在最前：一句里同时有「退款」和「人工」时，人是在要求换人，不是只要退款说明。
RULES = [
    ("转人工", ("人工", "真人", "客服电话")),
    ("投诉", ("投诉", "差评", "骗子")),
    ("退款", ("退款", "退货", "退钱")),
    ("查订单", ("订单", "物流", "快递", "单号")),
    ("咨询", ("怎么", "如何", "多少钱", "保修", "发票")),
]

# 原始字符串：反斜杠要交给正则，不要先被 Python 字符串吃掉一层。
_ORDER_WITH_LABEL = re.compile(r"(?:订单号|订单|单号)\s*[:：]?\s*(\d{4,})")
_LONG_NUMBER = re.compile(r"\d{5,}")


def extract_order_id(text: str) -> str | None:
    """尽量从这句话里取出订单号。没有就交回 None，不要编一个。"""
    labeled = _ORDER_WITH_LABEL.search(text)
    if labeled:
        return labeled.group(1)
    # 顾客有时只丢一串数字。要求至少 5 位，避免把「用了 2 天」里的 2 当成订单。
    bare = _LONG_NUMBER.search(text)
    if bare:
        return bare.group(0)
    return None


def classify_by_rules(text: str) -> dict:
    """返回一份结果字典。调用方用键取意图，而不是靠记住返回值的位置。"""
    order_id = extract_order_id(text)
    slots = {"order_id": order_id}
    for intent, keywords in RULES:
        for keyword in keywords:
            # 子串就算命中。这正是规则的局限：「不想退款」里也有「退款」。
            if keyword in text:
                return {
                    "intent": intent,
                    "confidence": 0.6,
                    "slots": slots,
                    "source": "rules",
                }
    return {
        "intent": "其他",
        "confidence": 0.2,
        "slots": slots,
        "source": "rules",
    }
