# -*- coding: utf-8 -*-
"""按意图选一个处理函数。阶段 1 的处理函数只回话，还不查数据库。"""

from rule_intent import classify_by_rules


def handle_consult(text: str, result: dict) -> str:
    return "我可以先讲一般用法和保修。你想问的是哪一类产品？"


def handle_order(text: str, result: dict) -> str:
    order_id = result["slots"].get("order_id")
    if not order_id:
        return "我现在还查不到真实物流。请发订单号，我先替你记下来。"
    # 报出订单号是为了证明槽位被接住了。后面没有数据库查询。
    return f"订单 {order_id} 我先记下了。真正去数据库查，要到阶段 2 的工具调用。"


def handle_refund(text: str, result: dict) -> str:
    order_id = result["slots"].get("order_id")
    if order_id:
        return f"退款申请我先记下订单 {order_id}。阶段 2 才会写成工单，现在还不会打款。"
    return "可以说明退款一般要准备什么。请补充订单号。我现在还不能直接退钱。"


def handle_complaint(text: str, result: dict) -> str:
    return "抱歉让你有不好的体验。我先记下这是投诉。阶段 2 才会把它写成工单交给人工。"


def handle_human(text: str, result: dict) -> str:
    return "好的，这一轮按转人工处理。阶段 2 才会真正建立工单并通知同事。"


def handle_other(text: str, result: dict) -> str:
    return "我主要处理购物咨询、订单、退款和投诉。这句话我先归到其他。"


# 值是函数本身，没有括号。加了括号就会立刻执行，而不是等到选中它。
HANDLERS = {
    "咨询": handle_consult,
    "查订单": handle_order,
    "退款": handle_refund,
    "投诉": handle_complaint,
    "转人工": handle_human,
    "其他": handle_other,
}


def route(text: str, result: dict) -> str:
    """按结果里的意图挑选函数。不认识的意图走「其他」，避免 KeyError 把对话打死。"""
    handler = HANDLERS.get(result.get("intent"), handle_other)
    return handler(text, result)


def route_by_rules(text: str) -> tuple[dict, str]:
    """没有模型时的整条小路：规则分类，再交给对应的处理函数。"""
    result = classify_by_rules(text)
    return result, route(text, result)
