# -*- coding: utf-8 -*-
"""输出是否越出店铺政策：乱答应赔钱、索要密码、背出系统提示、说出别人的号码。

金额的位数写不进词表，所以这一条用正则。词仍放在 rules.json 的 policy 里，方便改说法。
回复里的号码只有「这一句顾客的话里没出现过」才算泄露他人。顾客自己的号码打码即可。
"""

import re

from pii import find_emails, find_id_cards, find_phones, mask_text

# 必须连着数字和「元」。单独的「运费 8 元」对不上，正常的运费说明不会被当成赔款。
_AMOUNT = re.compile(r"(?:赔偿|赔你|赔您|退你|退您|退款)\s*\d+\s*元")


def _hit(category: str, word: str, level: str, action: str) -> dict:
    return {"category": category, "word": word, "level": level, "action": action}


def policy_hits(user_text: str, reply: str, book: dict) -> list[dict]:
    policy = book["policy"]
    found = []
    for word in policy["compensation_words"]:
        if word and word in reply:
            found.append(_hit("越权承诺", word, "高", "转人工"))
    if _AMOUNT.search(reply):
        found.append(_hit("越权承诺", "具体金额", "高", "转人工"))
    for word in policy["ask_secret_words"]:
        if word and word in reply:
            found.append(_hit("索要密码", word, "高", "拦截"))
    for word in policy["system_markers"]:
        if word and word in reply:
            found.append(_hit("泄露系统提示", "系统提示片段", "高", "拦截"))
    for word in policy["other_user_words"]:
        if word and word in reply:
            found.append(_hit("泄露他人信息", word, "高", "拦截"))
    for phone in find_phones(reply):
        if phone not in user_text:
            found.append(_hit("泄露他人信息", mask_text(phone), "高", "拦截"))
    for card in find_id_cards(reply):
        if card not in user_text:
            found.append(_hit("泄露他人信息", mask_text(card), "高", "拦截"))
    for email in find_emails(reply):
        if email not in user_text:
            found.append(_hit("泄露他人信息", mask_text(email), "高", "拦截"))
    return found


def before_tool_hits(text: str, book: dict) -> list[dict]:
    """建工单会写入数据库。要求打款、赔钱或动别人的订单时，不要调用工具。

    「我要退款」不在这份词里，仍会进入阶段 2，并且只登记工单，不会打款。
    """
    policy = book["policy"]
    found = []
    for word in policy["compensation_words"]:
        if word and word in text:
            found.append(_hit("越权打款", word, "高", "转人工"))
    if _AMOUNT.search(text):
        found.append(_hit("越权打款", "具体金额", "高", "转人工"))
    for word in policy["other_user_words"]:
        if word and word in text:
            found.append(_hit("越权打款", word, "高", "转人工"))
    return found
