# -*- coding: utf-8 -*-
"""决定一句话值不值得放进长期记忆，并先抹掉手机号和卡号。

规则不联网，离线演示锁的就是它。有对话客户端时再请模型抽一条 JSON。
模型没按格式写，就退回规则。记一笔记忆不应当把客服打崩。
"""

import json
import re

# 问句里的这些字说明人在打听，不是在告诉你一个事实。「我住在哪」不该被记成住址。
QUESTION_MARKS = ("哪", "吗", "什么", "多少", "几天", "多久", "几点", "如何", "怎么", "？", "?")

# 这些说法多半是偏好、城市、以前的事。闲聊「今天天气不错」一条都对不上，就不记。
KEEP_CUES = (
    "我住",
    "我喜欢",
    "我不喜欢",
    "不要放",
    "偏好",
    "上次",
    "以前",
    "记得我",
    "收货",
    "请记住",
)

# 先换手机号（11 位），再换身份证（18 位），最后换银行卡（更宽的一长串数字）。
# 顺序反过来的话，11 位手机号不会被 13 位以上的规则吃掉，但 18 位证件会被当成卡号。
_PHONE = re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")
_ID_CARD = re.compile(r"(?<!\d)\d{17}[\dXx](?!\d)")
_BANK_CARD = re.compile(r"(?<!\d)\d{13,19}(?!\d)")

_EXTRACT_SYSTEM = """你从顾客的一句话里抽出值得长期记住的事实。
只输出一个 JSON 数组，例如 ["住在杭州","收货喜欢放门口"]。
没有就输出 []。
不要写入完整手机号、银行卡号、身份证号、密码。
不要把退货天数、运费、保修期写进记忆，那些在知识库里。"""


def redact_secrets(text: str) -> str:
    """完整号码不进索引。留下占位，是为了让人看见「这里本来有一串数字，被拿掉了」。"""
    text = _PHONE.sub("[手机号已省略]", text)
    text = _ID_CARD.sub("[证件号已省略]", text)
    text = _BANK_CARD.sub("[卡号已省略]", text)
    return text


def _looks_sensitive(text: str) -> bool:
    if _PHONE.search(text):
        return True
    if _ID_CARD.search(text):
        return True
    if _BANK_CARD.search(text):
        return True
    return False


def _clip(text: str, limit: int = 80) -> str:
    if len(text) <= limit:
        return text
    return text[:limit]


def facts_from_rules(text: str) -> list[str]:
    """有线索、并且不是问句，才留下整句。没有线索就空列表，调用方什么都不写。"""
    cleaned = text.strip()
    if cleaned == "":
        return []
    matched = False
    for cue in KEEP_CUES:
        if cue in cleaned:
            matched = True
            break
    if not matched:
        return []
    for mark in QUESTION_MARKS:
        if mark in cleaned:
            return []
    redacted = _clip(redact_secrets(cleaned))
    if redacted.strip() == "":
        return []
    if _looks_sensitive(redacted):
        return []
    return [redacted]


def _parse_fact_list(content: str) -> list[str]:
    """从模型原文里剪出 JSON 数组。前后若有废话，只取第一对方括号。"""
    start = content.find("[")
    end = content.rfind("]")
    if start < 0 or end <= start:
        raise ValueError("模型没有交回 JSON 数组")
    data = json.loads(content[start : end + 1])
    if not isinstance(data, list):
        raise ValueError("模型交回的不是数组")
    facts = []
    for item in data:
        if not isinstance(item, str):
            continue
        redacted = _clip(redact_secrets(item.strip()))
        if redacted == "" or _looks_sensitive(redacted):
            continue
        facts.append(redacted)
    return facts


def facts_from_llm(client, model: str, text: str) -> list[str]:
    """请模型抽事实。异常交给调用方，由调用方退回规则。"""
    response = client.chat.completions.create(
        model=model,
        temperature=0,
        max_tokens=200,
        messages=[
            {"role": "system", "content": _EXTRACT_SYSTEM},
            {"role": "user", "content": text},
        ],
    )
    content = response.choices[0].message.content or ""
    return _parse_fact_list(content)


def select_facts(text: str, client=None, model: str | None = None) -> list[str]:
    """有客户端就先问模型。问失败就用规则。没有客户端就只用规则。"""
    if client is not None and model:
        try:
            return facts_from_llm(client, model, text)
        except Exception:
            return facts_from_rules(text)
    return facts_from_rules(text)
