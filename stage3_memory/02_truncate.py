# -*- coding: utf-8 -*-
"""阶段 3 · 示例 2：按轮数或按字符数切短 messages，开头的 system 留下。

不需要 API 密钥，也不需要 Redis。

    python stage3_memory/02_truncate.py

导读：stage3_memory/docs/02_truncate.md
"""

from window import content_length, truncate_by_chars, truncate_by_turns


def show(title: str, messages: list[dict]) -> None:
    total = 0
    print(title)
    for index, message in enumerate(messages):
        total = total + content_length(message)
        content = message.get("content")
        print(f"  [{index}] {message.get('role')}：{content}")
    print(f"  字数（只算 content）= {total}")
    print()


def build_messages() -> list[dict]:
    return [
        {"role": "system", "content": "你是星河数码的客服。不要编造订单号。"},
        {"role": "user", "content": "第一句很旧：我想问问保修。"},
        {"role": "assistant", "content": "保修一般是一年。"},
        {"role": "user", "content": "第二句：帮我查一下订单。"},
        {"role": "assistant", "content": "请提供订单号。"},
        {"role": "user", "content": "第三句要留下：订单号 10086。"},
        {"role": "assistant", "content": "订单 10086 已发货。"},
    ]


def main() -> None:
    messages = build_messages()
    show("== 切之前 ==", messages)
    print("一次请求能放下的 token 有上限，叫上下文窗口。")
    print("本课用字数代替 token：汉字和 token 不是一比一，但太长就要丢，这件事是一样的。")
    print("岗位说明是列表最前面的 system。它不占「一轮」，窗口不能把它切掉。")
    print()

    by_turns = truncate_by_turns(messages, max_turns=1)
    show("== 只留最近 1 轮 ==", by_turns)

    # 70 能放下岗位说明和后两轮（67 字），放不下把第一轮也算进去（88 字）。
    by_chars = truncate_by_chars(messages, max_chars=70)
    show("== 字数上限 70，按整轮从旧到新丢 ==", by_chars)

    try:
        truncate_by_turns(messages, 0)
    except ValueError as error:
        print(f"0 轮被拒绝：{error}")
    print()
    print("旧列表没有被改短。窗口交回的是一份新列表。")
    print(f"原列表仍是 {len(messages)} 条。")


if __name__ == "__main__":
    main()
