# -*- coding: utf-8 -*-
"""用正则把手机号、身份证号、银行卡号、邮箱和口令打码。

先打短的、形状明确的，再打更宽的数字。顺序反了，身份证会被银行卡规则整段吃掉。
打码函数交给 re.sub，是为了按分组保留前后几位，而不是整段换成同一个词。
"""

import re

# 11 位、1 开头、第二位 3 到 9。前后不能再贴着数字，避免从更长的一串里截一段。
PHONE_RE = re.compile(r"(?<!\d)(1[3-9]\d)\d{4}(\d{4})(?!\d)")
# 正好 18 位。末位可以是 X。15 位的老号码这一条认不出，这是漏报，文档里单独说。
ID_RE = re.compile(r"(?<!\d)(\d{3})\d{11}(\d{3}[\dXx])(?!\d)")
# 去掉手机号和 18 位证件之后，剩下的 13 到 19 位连续数字当卡号。
# 单独拿去搜原文时，18 位身份证也会符合这个形状，所以必须排在 ID_RE 后面。
BANK_RE = re.compile(r"(?<!\d)(\d{4})\d{5,11}(\d{4})(?!\d)")
EMAIL_RE = re.compile(r"([A-Za-z0-9])[A-Za-z0-9._%+-]*@([A-Za-z0-9.-]+\.[A-Za-z]{2,})")
# 只抹「密码是 abc123」这种紧挨着的口令。问「密码是怎么设置的」对不上，避免误伤。
SECRET_RE = re.compile(r"(密码\s*[:：]?\s*(?:是|为)?\s*)([A-Za-z0-9]{6,})")


def _mask_phone(match: re.Match) -> str:
    return match.group(1) + "****" + match.group(2)


def _mask_id(match: re.Match) -> str:
    return match.group(1) + "***********" + match.group(2)


def _mask_bank(match: re.Match) -> str:
    hidden = "*" * len(match.group(0)[4:-4])
    return match.group(1) + hidden + match.group(2)


def _mask_email(match: re.Match) -> str:
    return match.group(1) + "***@" + match.group(2)


def _mask_secret(match: re.Match) -> str:
    return match.group(1) + "[已省略]"


def mask_text(text: str) -> str:
    """同一串字打两次码，结果应和一次相同。日志里可以放心再走一遍。"""
    text = PHONE_RE.sub(_mask_phone, text)
    text = ID_RE.sub(_mask_id, text)
    text = BANK_RE.sub(_mask_bank, text)
    text = EMAIL_RE.sub(_mask_email, text)
    text = SECRET_RE.sub(_mask_secret, text)
    return text


def find_phones(text: str) -> list[str]:
    return [item.group(0) for item in PHONE_RE.finditer(text)]


def find_id_cards(text: str) -> list[str]:
    return [item.group(0) for item in ID_RE.finditer(text)]


def find_emails(text: str) -> list[str]:
    return [item.group(0) for item in EMAIL_RE.finditer(text)]


def mask_value(value):
    """字典和列表里的每段文本都打码。数字和布尔值原样留下。"""
    if isinstance(value, str):
        return mask_text(value)
    if isinstance(value, list):
        return [mask_value(item) for item in value]
    if isinstance(value, dict):
        copied = {}
        for key, item in value.items():
            copied[key] = mask_value(item)
        return copied
    return value
