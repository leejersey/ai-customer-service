# -*- coding: utf-8 -*-
"""把阶段 2 的一轮处理写进工作记忆。

阶段 2 的 session 只活在那一次函数调用里。这里负责在调用前后翻译。
顾客没再说订单号、但小表里已经有，就沿用，避免每次重启都重新追问。
"""

import stage3_link

stage3_link.enable()

from rule_intent import extract_order_id
from service import handle_turn
from working import WorkingMemory


def run_turn(text: str, memory: WorkingMemory, classification: dict | None = None) -> dict:
    """处理一句顾客的话，并更新同一份 WorkingMemory。"""
    found = extract_order_id(text)
    if found:
        # 这句话里的号码优先。沿用旧号码只发生在这句话抽不到号码的时候。
        memory.slots["order_id"] = found
    session = memory.to_stage2_session()
    outcome = handle_turn(text, session, classification)
    remembered = memory.slots.get("order_id", "")
    if outcome.get("asked") == "order_id" and remembered != "" and found is None:
        outcome = handle_turn(f"订单号 {remembered}", session, None)
        outcome = dict(outcome)
        outcome["reply"] = f"沿用你之前提供的订单号 {remembered}。" + outcome["reply"]
        outcome["source"] = "memory"
    memory.observe(session, outcome)
    if found:
        memory.slots["order_id"] = found
    return outcome
