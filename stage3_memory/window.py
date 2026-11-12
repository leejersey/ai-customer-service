# -*- coding: utf-8 -*-
"""把过长的 messages 切短。系统岗位说明留在列表最前面。

按轮数切，是为了不把「问」和「答」拆开。
按字符数切，是因为这一课没有分词器，用字数代替 token 做上限演示。
"""


def content_length(message: dict) -> int:
    """只数字符，不数 token。token 要分词器，字数足够说明「太长就要丢」。"""
    content = message.get("content") if isinstance(message, dict) else ""
    if content is None:
        return 0
    return len(str(content))


def copy_messages(messages: list[dict]) -> list[dict]:
    """新列表、新字典。调用方继续改旧列表时，窗口结果不会跟着变。"""
    copied = []
    for message in messages:
        item = {}
        if isinstance(message, dict):
            for key, value in message.items():
                item[key] = value
        copied.append(item)
    return copied


def leading_system(messages: list[dict]) -> tuple[list[dict], list[dict]]:
    """开头连续的 system 留下来。夹在对话中间的 system 算进那一轮，可以一起被切掉。"""
    index = 0
    while index < len(messages) and messages[index].get("role") == "system":
        index = index + 1
    return messages[:index], messages[index:]


def group_turns(messages: list[dict]) -> list[list[dict]]:
    """一轮从一条 user 开始，直到下一条 user 之前。

    这样工具结果或紧跟的回复会和那句问话留在一起。
    """
    turns = []
    current: list[dict] = []
    for message in messages:
        if message.get("role") == "user" and current:
            turns.append(current)
            current = [message]
        else:
            current.append(message)
    if current:
        turns.append(current)
    return turns


def flatten_turns(turns: list[list[dict]]) -> list[dict]:
    flat = []
    for turn in turns:
        for message in turn:
            flat.append(message)
    return flat


def truncate_by_turns(messages: list[dict], max_turns: int) -> list[dict]:
    """保留开头的 system，再保留最近 max_turns 轮。"""
    if max_turns < 1:
        raise ValueError("至少保留 1 轮")
    head, body = leading_system(messages)
    turns = group_turns(body)
    kept = turns[-max_turns:]
    return copy_messages(head) + copy_messages(flatten_turns(kept))


def truncate_by_chars(messages: list[dict], max_chars: int) -> list[dict]:
    """按整轮从旧到新丢，直到字数放进上限。

    岗位说明和最新一轮即使超标也留下。丢掉最新一句，模型就看不见顾客刚刚问了什么。
    """
    if max_chars < 1:
        raise ValueError("字符上限至少是 1")
    head, body = leading_system(messages)
    budget = max_chars - _total_length(head)
    if budget < 0:
        budget = 0
    turns = group_turns(body)
    used = 0
    kept_count = 0
    index = len(turns) - 1
    while index >= 0:
        size = _total_length(turns[index])
        # 最新一轮即使超标也留下。再往前的轮，放不下就停。
        if kept_count > 0 and used + size > budget:
            break
        used = used + size
        kept_count = kept_count + 1
        index = index - 1
    kept = turns[len(turns) - kept_count :]
    return copy_messages(head) + copy_messages(flatten_turns(kept))


def _total_length(messages: list[dict]) -> int:
    total = 0
    for message in messages:
        total = total + content_length(message)
    return total
