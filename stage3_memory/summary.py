# -*- coding: utf-8 -*-
"""历史超过阈值时，用一段摘要换掉旧消息。

没有模型客户端时，用旧消息拼一段假摘要。假摘要能让练习跑完，
它不会理解对话，只是把每句的开头剪下来。
"""

from window import (
    copy_messages,
    flatten_turns,
    group_turns,
    leading_system,
)

SUMMARY_PREFIX = "此前对话摘要："
# 摘要本身太长，就失去了压缩的意义。多出来的字直接切掉。
SUMMARY_CHAR_LIMIT = 200

SUMMARY_SYSTEM = """你是对话记录员，不是客服。
把下面的旧对话压成一段简体中文摘要，不超过 120 字。
必须保留：顾客意图、出现过的订单号、工单编号、已经答应过的事。
不要编造原文里没有的订单号或金额。
只输出摘要正文，不要加标题，不要使用 Markdown。"""


def is_summary_message(message: dict) -> bool:
    """只认我们自己加上的前缀。岗位说明里如果提到摘要这两个字，不能被当成旧摘要删掉。"""
    if message.get("role") != "system":
        return False
    content = message.get("content")
    if content is None:
        return False
    return str(content).startswith(SUMMARY_PREFIX)


def fake_summary(old_messages: list[dict]) -> str:
    """没有密钥时的兜底。每句只留开头，避免把整段历史又原样贴回去。"""
    parts = []
    for message in old_messages:
        content = message.get("content")
        if content is None:
            continue
        text = str(content).replace("\n", " ").strip()
        if text == "":
            continue
        role = message.get("role") or "unknown"
        parts.append(f"{role}：{text[:30]}")
    if not parts:
        return "没有更早的对话。"
    joined = "；".join(parts)
    if len(joined) > 180:
        joined = joined[:180] + "…"
    return joined


def summarize_old(old_messages: list[dict], client=None, model: str | None = None) -> dict:
    """返回 summary、source、note。source 是 llm 或 fake。"""
    if client is None or model is None or str(model).strip() == "":
        return {
            "summary": fake_summary(old_messages),
            "source": "fake",
            "note": "没有模型客户端，使用截断拼接的假摘要。",
        }
    lines = []
    for message in old_messages:
        role = message.get("role") or "unknown"
        content = message.get("content")
        if content is None:
            content = ""
        lines.append(f"{role}：{content}")
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SUMMARY_SYSTEM},
                {"role": "user", "content": "\n".join(lines)},
            ],
            temperature=0.0,
            max_tokens=200,
            stream=False,
        )
    except Exception as error:
        # 摘要失败不应该让客服退出。旧消息用假摘要换掉，这一轮仍然能回复。
        return {
            "summary": fake_summary(old_messages),
            "source": "fake",
            "note": f"{type(error).__name__}: {error}",
        }
    text = ""
    if response.choices:
        text = response.choices[0].message.content or ""
    text = _strip_fence(text).strip()
    if text == "":
        return {
            "summary": fake_summary(old_messages),
            "source": "fake",
            "note": "模型没有返回摘要正文。",
        }
    if len(text) > SUMMARY_CHAR_LIMIT:
        text = text[:SUMMARY_CHAR_LIMIT] + "…"
    return {"summary": text, "source": "llm", "note": ""}


def compress_messages(
    messages: list[dict],
    keep_turns: int,
    threshold_turns: int,
    client=None,
    model: str | None = None,
) -> dict:
    """超过 threshold_turns 才压缩，压缩后保留最近 keep_turns 轮。

    没超过阈值时 summary 是空字符串、source 是 none，消息原样抄一份。
    """
    if keep_turns < 1:
        raise ValueError("至少保留 1 轮")
    if threshold_turns < keep_turns:
        raise ValueError("阈值不能小于保留轮数")
    head, body = leading_system(messages)
    turns = group_turns(body)
    if len(turns) <= threshold_turns:
        return {
            "messages": copy_messages(messages),
            "summary": "",
            "source": "none",
            "note": "",
        }
    old = flatten_turns(turns[:-keep_turns])
    recent = flatten_turns(turns[-keep_turns:])
    prior = []
    persona = []
    for message in head:
        if is_summary_message(message):
            # 上一次的摘要也要送进这一次，否则更早的订单号会在第二次压缩时消失。
            prior.append(message)
        else:
            persona.append(message)
    produced = summarize_old(prior + old, client=client, model=model)
    summary_message = {
        "role": "system",
        "content": SUMMARY_PREFIX + produced["summary"],
    }
    packed = copy_messages(persona) + [summary_message] + copy_messages(recent)
    return {
        "messages": packed,
        "summary": produced["summary"],
        "source": produced["source"],
        "note": produced["note"],
    }


def fold_transcript(
    summary: str,
    messages: list[dict],
    keep_turns: int,
    threshold_turns: int,
    client=None,
    model: str | None = None,
) -> dict:
    """会话库把摘要单独存成一条字符串，对话列表里只留最近几轮。"""
    packaged = []
    if summary.strip() != "":
        packaged.append({"role": "system", "content": SUMMARY_PREFIX + summary.strip()})
    for message in messages:
        packaged.append(message)
    result = compress_messages(
        packaged,
        keep_turns=keep_turns,
        threshold_turns=threshold_turns,
        client=client,
        model=model,
    )
    if result["source"] == "none":
        return {
            "summary": summary,
            "messages": copy_messages(messages),
            "source": "none",
            "note": "",
        }
    recent = []
    for message in result["messages"]:
        if is_summary_message(message):
            continue
        recent.append(message)
    return {
        "summary": result["summary"],
        "messages": recent,
        "source": result["source"],
        "note": result["note"],
    }


def _strip_fence(text: str) -> str:
    """模型有时用 Markdown 代码块把摘要包起来。记号不是对话内容。"""
    stripped = text.strip()
    if not stripped.startswith("```"):
        return stripped
    lines = stripped.split("\n")
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].startswith("```"):
        lines = lines[:-1]
    return "\n".join(lines).strip()
