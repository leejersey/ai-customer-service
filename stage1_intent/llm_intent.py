# -*- coding: utf-8 -*-
"""让模型只交回一份 JSON，再由我们检查。模型没按格式写时，退回「其他」，不要让程序崩溃。"""

import json
import os

# enable() 必须写在 import config 之前。顺序反了，config 已经查找失败，不会再找一次。
import stage0_link

stage0_link.enable()
from config import ENV_PATH, _clean, _is_placeholder
from rule_intent import INTENTS

# 温度压低：我们要的是一份稳定的表格，不是发挥文采。
CLASSIFY_TEMPERATURE = 0.0
CLASSIFY_MAX_TOKENS = 200

_CLASSIFY_SYSTEM = """你是意图分类器，不是客服。
只输出一个 JSON 对象，不要写解释，不要使用 Markdown。
格式固定为：
{"intent":"咨询","confidence":0.8,"slots":{"order_id":null}}
intent 只能是：咨询、查订单、退款、投诉、转人工、其他。
confidence 是 0 到 1 的小数。
没有订单号时 order_id 用 null。不要编造订单号。"""


def api_key_ready() -> bool:
    """只回答有没有可用密钥。

    不调用 require_settings，也不调用 _load_dotenv。
    那两个函数在失败时会打印说明并结束整个程序。
    规则打分必须在「没装 dotenv」或「没有密钥」时继续。
    """
    try:
        from dotenv import load_dotenv
    except ImportError:
        return False
    try:
        load_dotenv(ENV_PATH, override=False, encoding="utf-8")
    except UnicodeError:
        return False
    api_key = _clean(os.environ.get("DEEPSEEK_API_KEY", ""))
    if not api_key or _is_placeholder(api_key):
        return False
    return True


def _fallback(reason: str) -> dict:
    """解析失败时的统一结果。调用方仍然能用同样的键，不用再写一套分支。"""
    return {
        "intent": "其他",
        "confidence": 0.0,
        "slots": {"order_id": None},
        "source": "fallback",
        "error": reason,
    }


def _extract_json_text(raw: str) -> str:
    """模型有时会在 JSON 前后加废话或代码围栏。先把花括号那一段剪出来。"""
    text = raw.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end <= start:
        return text
    return text[start : end + 1]


def parse_model_output(raw: str) -> dict:
    """把模型的原文收成结果字典。任何格式问题都变成 fallback，不往外抛。"""
    if not isinstance(raw, str) or raw.strip() == "":
        return _fallback("模型没有返回文本")
    snippet = _extract_json_text(raw)
    try:
        data = json.loads(snippet)
    except json.JSONDecodeError as error:
        return _fallback(f"JSON 无法解析：{error}")
    if not isinstance(data, dict):
        return _fallback("JSON 不是对象")
    intent = data.get("intent")
    if intent not in INTENTS:
        return _fallback(f"意图不在允许列表里：{intent}")
    confidence = data.get("confidence")
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
        return _fallback(f"置信度不是数字：{confidence}")
    if not 0 <= float(confidence) <= 1:
        return _fallback(f"置信度超出 0 到 1：{confidence}")
    slots = data.get("slots")
    if not isinstance(slots, dict):
        return _fallback("slots 不是对象")
    order_id = slots.get("order_id")
    if order_id is not None and not isinstance(order_id, str):
        return _fallback("order_id 必须是字符串或 null")
    if isinstance(order_id, str) and order_id.strip() == "":
        order_id = None
    return {
        "intent": intent,
        "confidence": float(confidence),
        "slots": {"order_id": order_id},
        "source": "llm",
    }


def classify_by_llm(client, model: str, text: str) -> dict:
    """请模型分类。网络失败仍然抛出，让调用方决定是退出还是换规则。"""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": _CLASSIFY_SYSTEM},
            {"role": "user", "content": text},
        ],
        temperature=CLASSIFY_TEMPERATURE,
        max_tokens=CLASSIFY_MAX_TOKENS,
        stream=False,
    )
    if not response.choices:
        return _fallback("响应里没有 choices")
    content = response.choices[0].message.content
    if not isinstance(content, str):
        return _fallback("模型没有返回文本")
    return parse_model_output(content)


