# -*- coding: utf-8 -*-
"""把一轮对话写回会话库：先追加，超长再摘要，然后保存工作记忆。

命令行和离线演示走同一个函数，避免一边续期、另一边忘记保存槽位。
"""

from summary import fold_transcript
from window import copy_messages

# 课堂默认：超过 6 轮就把更早的收成摘要，手头仍留 4 轮。
# 短对话不会触发，避免一开口就把两句话变成摘要。
KEEP_TURNS = 4
THRESHOLD_TURNS = 6


def record_exchange(
    store,
    session_id: str,
    memory,
    transcript: list[dict],
    summary: str,
    user_text: str,
    reply: str,
    client=None,
    model: str | None = None,
    keep_turns: int = KEEP_TURNS,
    threshold_turns: int = THRESHOLD_TURNS,
) -> dict:
    """返回折叠之后的 summary、messages、source、note。store 里已经是这一份。"""
    updated = copy_messages(transcript)
    updated.append({"role": "user", "content": user_text})
    updated.append({"role": "assistant", "content": reply})
    folded = fold_transcript(
        summary,
        updated,
        keep_turns=keep_turns,
        threshold_turns=threshold_turns,
        client=client,
        model=model,
    )
    store.replace_messages(session_id, folded["messages"])
    store.save_summary(session_id, folded["summary"])
    store.save_working(session_id, memory)
    return folded
