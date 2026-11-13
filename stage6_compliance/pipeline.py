# -*- coding: utf-8 -*-
"""输入审核、工具前审核、生成、输出审核、审计日志。

answer_fn 和 tool_fn 由调用方交进来。离线演示交假的，命令行交阶段 5 和阶段 2。
judge_fn 为 None 时这一轮不请模型当裁判，词表和正则仍然生效。
"""

from pathlib import Path

from audit import append_audit
from judge import hits_from_verdict
from pii import mask_text
from policy import before_tool_hits, policy_hits
from result import ComplianceResult, decide
from rules import injection_hits, load_rules, sensitive_hits


def review_input(text: str, book: dict) -> ComplianceResult:
    found = []
    found.extend(injection_hits(text, book))
    found.extend(sensitive_hits(text, book, "input"))
    # 不管放不放行，往下传和写日志的都是打过码的句子。
    return decide(found, mask_text(text))


def review_before_tool(text: str, book: dict) -> ComplianceResult:
    return decide(before_tool_hits(text, book), mask_text(text))


def review_output(user_text: str, reply: str, book: dict, judge_fn) -> ComplianceResult:
    """先按原文查政策和号码，再把打码后的回复交给裁判。裁判看不到完整号码。"""
    found = []
    found.extend(sensitive_hits(reply, book, "output"))
    found.extend(policy_hits(user_text, reply, book))
    masked = mask_text(reply)
    if judge_fn is not None:
        try:
            judged = judge_fn(masked)
        except Exception:
            # 裁判函数自己抛错时，不能当成「没意见」然后放行。
            judged = {"verdict": "拒绝", "reason": "审核结果无法解析，默认拒绝，不放行", "ok": False}
        found.extend(hits_from_verdict(judged))
    return decide(found, masked)


def run_turn(
    user_text: str,
    answer_fn,
    tool_fn,
    route: str,
    judge_fn,
    audit_path: Path,
    book: dict | None = None,
) -> dict:
    """route 为 tool 时才可能调用 tool_fn。被输入审核拦住时，两个函数都不调用。

    被拦住的顾客原句不返回给调用方去写入对话历史。注入句子留在历史里，下一轮仍会进模型。
    """
    book = book if book is not None else load_rules()
    incoming = review_input(user_text, book)
    append_audit(audit_path, incoming, "input")
    if incoming.action != "放行":
        return {
            "answer": incoming.text,
            "input": incoming,
            "before_tool": None,
            "output": None,
            "ran_tool": False,
            "ran_model": False,
        }

    # 要求打款或动别人的订单时，不管路由器把这句话分到哪，都不生成、也不调用工具。
    gate = review_before_tool(user_text, book)
    if gate.action != "放行":
        append_audit(audit_path, gate, "before_tool")
        return {
            "answer": gate.text,
            "input": incoming,
            "before_tool": gate,
            "output": None,
            "ran_tool": False,
            "ran_model": False,
        }

    reported_gate = None
    ran_tool = False
    ran_model = False
    if route == "tool":
        append_audit(audit_path, gate, "before_tool")
        reported_gate = gate
        reply = tool_fn(incoming.text)
        ran_tool = True
    else:
        reply = answer_fn(incoming.text)
        ran_model = True

    outgoing = review_output(user_text, reply, book, judge_fn)
    append_audit(audit_path, outgoing, "output")
    return {
        "answer": outgoing.text,
        "input": incoming,
        "before_tool": reported_gate,
        "output": outgoing,
        "ran_tool": ran_tool,
        "ran_model": ran_model,
    }
