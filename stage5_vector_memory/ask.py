# -*- coding: utf-8 -*-
"""政策走向量检索。长期记忆只补充偏好和城市，不拿来编造天数。

没有客户端时，政策题复述资料原文。记忆题用固定句式说「你以前提过」或「我记下了」。
"""

import stage5_link

stage5_link.enable()

from answering import complete_with_client, echo_retrieved
from prompting import NOT_FOUND

from embedder import backend_name
from knowledge_index import search_knowledge
from memory_store import UserMemory
from remember import facts_from_rules

# 阶段 4 的 0.15 只属于二字词余弦。向量的分数是另一把尺子，还要按模型分开。
# 0.22 对着这份知识库的假向量试过：原词问句里最低的「营业到几点」大约 0.23，
# 「我住在杭州」这种偏好句大约 0.20，门放在中间，避免把住址当成运费规定来念。
FAKE_VECTOR_THRESHOLD = 0.22
BGE_VECTOR_THRESHOLD = 0.45


def vector_threshold() -> float:
    if backend_name() == "bge":
        return BGE_VECTOR_THRESHOLD
    return FAKE_VECTOR_THRESHOLD


def _format_context(hits: list) -> str:
    blocks = []
    for hit in hits:
        blocks.append(f"[来源：{hit.source} 第{hit.index}段]\n{hit.text}")
    return "\n\n".join(blocks)


def build_messages(question: str, hits: list, memories: list, recent: list) -> list[dict]:
    """资料放在问题前面，记忆和短期对话放在问题后面。

    阶段 4 的假模型只复述「顾客的问题」之前的来源块。
    记忆放在后面，复述才不会把「我住在杭州」说成一条退货规定。
    """
    system = (
        "你是「星河数码」的客服。\n"
        "只能根据用户消息里资料下面的段落回答政策，不要用资料以外的常识补充天数、金额或价格。\n"
        f"资料没有写到的，只回答这一句：{NOT_FOUND}\n"
        "顾客以前提过的偏好和城市，可以用来称呼和选择说法，不能用来编造政策数字。\n"
        "用简体中文。回答政策时，最后一行以「来源：」开头，写上你用到的文件名。"
    )
    user = (
        "请只根据下面的资料回答。资料没写到的，回答「知识库里没有找到」。\n\n"
        f"{_format_context(hits)}\n\n"
        f"顾客的问题：{question}"
    )
    notes = []
    if memories:
        lines = []
        for item in memories:
            lines.append("- " + item.text)
        notes.append("长期记忆（不是店铺规定）：\n" + "\n".join(lines))
    if recent:
        lines = []
        for item in recent:
            lines.append(item["role"] + "：" + item["content"])
        notes.append("这一次进程里刚说过的几句：\n" + "\n".join(lines))
    if notes:
        user = user + "\n\n" + "\n\n".join(notes)
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def _memory_sentence(memories: list) -> str:
    parts = []
    for item in memories:
        parts.append(item.text)
    return "（根据长期记忆，没有调用模型）你以前提过：" + "；".join(parts)


def _saved_sentence(saved: list[str]) -> str:
    return "（记下长期记忆，没有调用模型）我记下了：" + "；".join(saved)


def answer_question(
    question: str,
    store,
    memory: UserMemory | None = None,
    client=None,
    model: str | None = None,
    recent: list | None = None,
    top_k: int = 3,
    remember: bool = True,
) -> dict:
    """先回忆，再检索政策。这一句要记的事实在回答决定之后写入，避免刚说的话立刻被当成旧记忆。"""
    memories = []
    if memory is not None:
        memories = memory.recall(question, top_k=3)
    hits = search_knowledge(store, question, top_k=top_k)
    threshold = vector_threshold()
    best = hits[0].score if hits else 0.0
    chosen = []
    for hit in hits:
        if hit.score >= threshold:
            chosen.append(hit)
    recent_turns = recent or []
    saved: list[str] = []
    # 规则认定这是偏好或住址时，不再把擦边的知识库段落当成回答。
    # 真模型里「请记住我的手机号」也会靠近「短信、订单号」那一段。
    preference = facts_from_rules(question) if remember else []

    if chosen and not preference:
        messages = build_messages(question, chosen, memories, recent_turns)
        if client is None or model is None:
            answer = echo_retrieved(messages)
            source = "echo"
        else:
            answer = complete_with_client(client, model, messages)
            source = "model"
        if remember and memory is not None:
            memory.remember_exchange(question, chosen[0].source)
        if remember and memory is not None:
            saved = memory.add_text(question, client=client, model=model)
        return {
            "question": question,
            "hits": hits,
            "memories": memories,
            "saved": saved,
            "best_score": best,
            "messages": messages,
            "answer": answer,
            "source": source,
        }

    if remember and memory is not None:
        saved = memory.add_text(question, client=client, model=model)
    if saved:
        answer = _saved_sentence(saved)
        source = "saved"
    elif memories:
        answer = _memory_sentence(memories)
        source = "memory"
    else:
        answer = NOT_FOUND
        source = "missing"
    return {
        "question": question,
        "hits": hits,
        "memories": memories,
        "saved": saved,
        "best_score": best,
        "messages": None,
        "answer": answer,
        "source": source,
    }
