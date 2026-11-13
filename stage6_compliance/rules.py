# -*- coding: utf-8 -*-
"""从 rules.json 读取词表。敏感词和提示注入都是「整段短语」，不是单个字。

单个字太容易误报：「垃圾」会命中「垃圾分类」，「忽略」会命中「忽略之前的订单」。
短语仍会漏报：中间插一个空格，或者换一种说法，就对不上。这是规则的边界，不是疏忽。
"""

import json
from pathlib import Path

RULES_PATH = Path(__file__).resolve().parent / "rules.json"


def load_rules(path: Path | None = None) -> dict:
    """文件坏了就停下来说明，不要带着空词表继续，空词表会把所有句子放行。"""
    path = path or RULES_PATH
    if not path.is_file():
        print(f"找不到规则文件：{path}")
        print("阶段 6 的词表在 stage6_compliance/rules.json。")
        raise SystemExit(1)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        print(f"规则文件不是合法的 JSON：{path}")
        print(error)
        raise SystemExit(1)
    for key in ("sensitive", "injection", "policy"):
        if key not in data:
            print(f"规则文件缺少「{key}」。")
            raise SystemExit(1)
    return data


def has_word(text: str, words: list[str]) -> bool:
    """有一个非空词出现就停。空字符串会命中每一句，所以先看 word 自己。"""
    return any(word and word in text for word in words)


def _collect(text: str, rules: list[dict]) -> list[dict]:
    found = []
    for rule in rules:
        for word in rule.get("words") or []:
            if word and word in text:
                found.append(
                    {
                        "category": rule["category"],
                        "word": word,
                        "level": rule["level"],
                        "action": rule["action"],
                    }
                )
    return found


def sensitive_hits(text: str, book: dict, where: str) -> list[dict]:
    """where 是 input 或 output。绝对化承诺只查输出，避免「你们保证100%吗」误伤顾客的提问。"""
    chosen = []
    for rule in book["sensitive"]:
        places = rule.get("where") or []
        if where in places:
            chosen.append(rule)
    return _collect(text, chosen)


def injection_hits(text: str, book: dict) -> list[dict]:
    """只用于顾客的输入。模型的回复里出现这些字，另由输出审核处理。"""
    return _collect(text, book["injection"])
