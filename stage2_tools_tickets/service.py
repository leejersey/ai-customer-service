# -*- coding: utf-8 -*-
"""阶段 1 的意图决定调用哪一个工具。工具本身在 tools.py。

订单号只用原话里的数字。分类器若另外填了一个号，可能是编的，不能拿去查库。
"""

import re

import stage2_link

stage2_link.enable()

from rule_intent import INTENTS, classify_by_rules, extract_order_id
from slots import missing_slots, question_for
from tools import create_ticket, get_ticket, query_order, update_ticket_status

# 句式写死，是为了没有模型时也能改状态、查工单。闲聊里随便出现「工单」两个字不会命中。
_STATUS_UPDATE = re.compile(
    r"工单\s*(\d+)\s*(?:改为|改成|更新为|设为|标记为)\s*(待处理|处理中|已解决|已关闭)"
)
_TICKET_LOOKUP = re.compile(r"(?:查询|查看|看看)\s*工单\s*(\d+)")


def _pack(
    intent: str,
    source: str,
    reply: str,
    tool: str | None = None,
    result: dict | None = None,
    asked: str | None = None,
) -> dict:
    return {
        "reply": reply,
        "intent": intent,
        "source": source,
        "tool": tool,
        "result": result,
        "asked": asked,
    }


def render(tool: str | None, result: dict | None) -> str:
    """把工具字典说成一句顾客能读的话。模型在线时可以再润色，事实以这句为准。"""
    if result is None:
        return "没有拿到工具结果。"
    if not result.get("ok"):
        return str(result.get("error") or "没有完成。")
    if tool == "query_order":
        order = result["order"]
        return (
            f"订单 {order['order_id']}：{order['product']}，"
            f"{order['amount_yuan']} 元，状态 {order['status']}，"
            f"下单人 {order['user_name']}。"
        )
    if tool == "create_ticket":
        ticket = result["ticket"]
        kind = ticket["ticket_type"]
        base = f"已记下{kind}工单 {ticket['id']}，当前状态是{ticket['status']}。"
        if kind == "退款":
            return base + "钱还没有退，这一步只是记录。"
        if kind == "转人工":
            return base + "同事会按这张工单接手。"
        return base
    if tool == "update_ticket_status":
        ticket = result["ticket"]
        return (
            f"工单 {ticket['id']} 已从{result['previous_status']}改为{ticket['status']}。"
        )
    if tool == "get_ticket":
        ticket = result["ticket"]
        order_text = ticket["order_id"] or "无"
        return (
            f"工单 {ticket['id']}，类型 {ticket['ticket_type']}，"
            f"状态 {ticket['status']}，订单号 {order_text}。"
            f"描述：{ticket['description']}"
        )
    return "工具已经执行。"


def _classification_for(text: str, classification: dict | None) -> dict:
    """意图可以来自模型。订单号始终来自阶段 1 的正则。"""
    if classification is None or classification.get("source") == "fallback":
        # 模型没交出合法 JSON 时会被收成「其他」。那种结果不能用来决定是否建工单。
        result = classify_by_rules(text)
    else:
        result = classification
    intent = result.get("intent")
    if intent not in INTENTS:
        intent = "其他"
    return {
        "intent": intent,
        "confidence": result.get("confidence"),
        "source": result.get("source") or "rules",
        "slots": {"order_id": extract_order_id(text)},
    }


def _run_tool(intent: str, text: str, order_id: str | None) -> dict:
    if intent == "查订单":
        result = query_order(order_id or "")
        reply = render("query_order", result)
        return _pack(intent, "rules", reply, tool="query_order", result=result)
    if intent == "退款":
        result = create_ticket(ticket_type="退款", description=text, order_id=order_id or "")
        reply = render("create_ticket", result)
        return _pack(intent, "rules", reply, tool="create_ticket", result=result)
    if intent == "投诉":
        result = create_ticket(ticket_type="投诉", description=text, order_id=order_id or "")
        reply = render("create_ticket", result)
        return _pack(intent, "rules", reply, tool="create_ticket", result=result)
    if intent == "转人工":
        result = create_ticket(ticket_type="转人工", description=text, order_id=order_id or "")
        reply = render("create_ticket", result)
        return _pack(intent, "rules", reply, tool="create_ticket", result=result)
    if intent == "咨询":
        return _pack(intent, "rules", "我可以先讲一般用法和保修。你想问的是哪一类产品？")
    return _pack(intent, "rules", "我主要处理查订单、退款和投诉。这句话没有写入工单。")


def _with_source(outcome: dict, source: str) -> dict:
    copied = dict(outcome)
    copied["source"] = source
    return copied


def _command(text: str) -> dict | None:
    """工单编号命令不属于阶段 1 的六个意图。认的是句式，不是闲聊。"""
    updating = _STATUS_UPDATE.search(text)
    if updating:
        ticket_id = int(updating.group(1))
        status = updating.group(2)
        result = update_ticket_status(ticket_id, status)
        reply = render("update_ticket_status", result)
        return _pack("更新工单", "command", reply, tool="update_ticket_status", result=result)
    looking = _TICKET_LOOKUP.search(text)
    if looking:
        ticket_id = int(looking.group(1))
        result = get_ticket(ticket_id)
        reply = render("get_ticket", result)
        return _pack("查询工单", "command", reply, tool="get_ticket", result=result)
    return None


def _start_turn(text: str, session: dict, classification: dict | None) -> dict:
    judged = _classification_for(text, classification)
    intent = judged["intent"]
    source = judged["source"]
    order_id = judged["slots"].get("order_id")
    if missing_slots(intent, judged["slots"]):
        # 先记住原话。下一句只补订单号时，描述仍然用这一句，而不是只用数字。
        session["pending"] = {"intent": intent, "text": text}
        return _pack(intent, source, question_for("order_id"), asked="order_id")
    session["pending"] = None
    outcome = _run_tool(intent, text, order_id)
    return _with_source(outcome, source)


def _continue_pending(text: str, session: dict, pending: dict) -> dict:
    judged = classify_by_rules(text)
    # 投诉和转人工即使带着订单号，也表示人已经改口，不再把数字填进上一张退款单。
    if judged["intent"] in {"投诉", "转人工"}:
        session["pending"] = None
        return _start_turn(text, session, None)
    order_id = extract_order_id(text)
    if order_id:
        session["pending"] = None
        description = pending["text"]
        if pending["intent"] == "查订单":
            result = query_order(order_id)
            reply = render("query_order", result)
            return _pack(pending["intent"], "slots", reply, tool="query_order", result=result)
        result = create_ticket(ticket_type="退款", description=description, order_id=order_id)
        reply = render("create_ticket", result)
        return _pack(pending["intent"], "slots", reply, tool="create_ticket", result=result)
    if judged["intent"] in {"查订单", "退款"} and judged["intent"] != pending["intent"]:
        session["pending"] = None
        return _start_turn(text, session, None)
    return _pack(pending["intent"], "slots", question_for("order_id"), asked="order_id")


def handle_turn(text: str, session: dict, classification: dict | None = None) -> dict:
    """处理一句顾客的话。session["pending"] 记住还缺的槽位，调用方要留着同一个字典。"""
    command = _command(text)
    if command is not None:
        session["pending"] = None
        return command
    pending = session.get("pending")
    if pending:
        return _continue_pending(text, session, pending)
    return _start_turn(text, session, classification)
