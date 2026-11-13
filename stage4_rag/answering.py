# -*- coding: utf-8 -*-
"""有分数才生成。不够分时直接说知识库里没有，避免模型编政策。

没有客户端时用 echo_retrieved：把已经检索到的第一段原文说出来。
那不是模型，只是为了让人看见「检索到的字」确实进了回答。
"""

from prompting import (
    NOT_FOUND,
    SCORE_THRESHOLD,
    best_score,
    build_messages,
    covered,
    hits_for_prompt,
)


def echo_retrieved(messages: list[dict]) -> str:
    """假模型。不联网。把 user 消息里每一段资料原样复述出来，并带上来源标签。"""
    user_text = ""
    for message in messages:
        if message.get("role") == "user":
            user_text = str(message.get("content") or "")
    if "[来源：" not in user_text:
        return NOT_FOUND
    # 问题写在资料后面。复述资料，不把问题再贴回去。
    material, _sep, _question = user_text.partition("顾客的问题：")
    blocks = []
    for part in material.split("[来源：")[1:]:
        source_line, _sep2, body = part.partition("\n")
        source_line = source_line.strip()
        if source_line.endswith("]"):
            source_line = source_line[:-1]
        body = body.strip()
        if body == "":
            continue
        blocks.append(f"{body}\n来源：{source_line}")
    if not blocks:
        return NOT_FOUND
    return "（离线复述，没有调用模型）\n" + "\n\n".join(blocks)


def prepare(question: str, hits: list, threshold: float = SCORE_THRESHOLD) -> dict:
    """决定这一问要不要请模型。不够分时 answer 已经是那句固定的话。"""
    score = best_score(hits)
    if not covered(hits, threshold):
        return {
            "question": question,
            "hits": hits,
            "best_score": score,
            "call_model": False,
            "messages": None,
            "answer": NOT_FOUND,
        }
    return {
        "question": question,
        "hits": hits,
        "best_score": score,
        "call_model": True,
        "messages": build_messages(question, hits_for_prompt(hits, threshold)),
        "answer": None,
    }


def complete_with_client(client, model: str, messages: list[dict]) -> str:
    """真正调用对话接口。温度压低，是为了少改资料里的数字。"""
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.1,
        max_tokens=400,
    )
    content = response.choices[0].message.content
    if content is None or content.strip() == "":
        return NOT_FOUND
    return content.strip()


def answer_question(
    question: str,
    index,
    client=None,
    model: str | None = None,
    top_k: int = 3,
    threshold: float = SCORE_THRESHOLD,
) -> dict:
    """检索，再按阈值决定复述、调用模型，或直接说没有找到。"""
    hits = index.search(question, top_k=top_k)
    plan = prepare(question, hits, threshold)
    if not plan["call_model"]:
        return plan
    messages = plan["messages"]
    if client is None or model is None:
        plan["answer"] = echo_retrieved(messages)
        plan["call_model"] = False
        plan["source"] = "echo"
        return plan
    plan["answer"] = complete_with_client(client, model, messages)
    plan["source"] = "model"
    return plan
