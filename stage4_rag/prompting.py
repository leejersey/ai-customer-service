# -*- coding: utf-8 -*-
"""把检索到的段拼进发给模型的消息。

岗位规则放在 system，这一次的资料和问题放在 user。
资料每问一次都会变，规则不变。来源标签写在每段前面，回答才知道引用哪一个文件。
"""

NOT_FOUND = "知识库里没有找到"

# 分数低于这个数就不要请模型说话。模型会用它自己记得的「一般退货规定」把空当填上。
# 0.15 是对着本知识库的二字词余弦调的：政策问句通常更高，知识库没写的话题通常更低。
# 它不是概率。0.15 不是「15% 的把握」。
SCORE_THRESHOLD = 0.15

_SYSTEM_PROMPT = """你是「星河数码」的客服。
只能根据用户消息里给出的资料回答，不要用资料以外的常识补充天数、金额、地址或价格。
资料没有写到的，只回答这一句：知识库里没有找到
用简体中文。最后一行以「来源：」开头，写上你用到的文件名。"""


def format_context(hits: list) -> str:
    """每段前面写文件名和段号。模型要引用时有标签可抄，人也看得清来源。"""
    blocks = []
    for hit in hits:
        label = f"[来源：{hit.source} 第{hit.index}段]"
        blocks.append(label + "\n" + hit.text)
    return "\n\n".join(blocks)


def build_messages(question: str, hits: list) -> list[dict]:
    """拼出 messages。调用方要先确认最高分过了阈值，再把这份列表交给模型。"""
    context = format_context(hits)
    user = (
        "请只根据下面的资料回答。资料没写到的，回答「知识库里没有找到」。\n\n"
        f"{context}\n\n"
        f"顾客的问题：{question}"
    )
    return [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]


def best_score(hits: list) -> float:
    if not hits:
        return 0.0
    return float(hits[0].score)


def covered(hits: list, threshold: float = SCORE_THRESHOLD) -> bool:
    """最高分够不到阈值时，视为知识库没有写到。不要把勉强相关的段交给模型。"""
    return best_score(hits) >= threshold


def hits_for_prompt(hits: list, threshold: float = SCORE_THRESHOLD) -> list:
    """屏幕上可以列出 top-k。送进提示的只留达到阈值的段，避免半句噪音。"""
    chosen = []
    for hit in hits:
        if hit.score >= threshold:
            chosen.append(hit)
    return chosen
