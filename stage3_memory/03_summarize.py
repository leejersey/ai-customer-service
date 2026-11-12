# -*- coding: utf-8 -*-
"""阶段 3 · 示例 3：历史太长时，用摘要换掉旧消息。

没有密钥时只用假摘要。有密钥时再请 DeepSeek 写一段，失败也退回假摘要。

    python stage3_memory/03_summarize.py

导读：stage3_memory/docs/03_summarize.md
"""

import json

import stage3_link

stage3_link.enable()

from config import create_client, describe_settings, require_settings
from llm_intent import api_key_ready
from summary import compress_messages


def show(title: str, messages: list[dict]) -> None:
    print(title)
    print(json.dumps(messages, ensure_ascii=False, indent=2))
    print()


def build_messages() -> list[dict]:
    return [
        {"role": "system", "content": "你是星河数码的客服。不要编造订单号。"},
        {"role": "user", "content": "我要退款"},
        {"role": "assistant", "content": "请告诉我订单号。"},
        {"role": "user", "content": "紫色包装破了，订单号 10086"},
        {"role": "assistant", "content": "已记下退款工单 1。钱还没有退。"},
        {"role": "user", "content": "谢谢"},
        {"role": "assistant", "content": "不客气。"},
        {"role": "user", "content": "还在吗"},
        {"role": "assistant", "content": "在的，我在。"},
    ]


def main() -> None:
    messages = build_messages()
    show("== 压缩之前 ==", messages)
    short = compress_messages(messages, keep_turns=2, threshold_turns=4)
    print(f"只有 4 轮，阈值也是 4，来源={short['source']}。消息条数仍是 {len(short['messages'])}。")
    print("阈值用的是「超过才压缩」。刚好等于阈值时还保留原文。")
    print()

    packed = compress_messages(messages, keep_turns=1, threshold_turns=2)
    print(f"来源={packed['source']}")
    print(f"说明：{packed['note']}")
    print(f"摘要：{packed['summary']}")
    print()
    show("== 假摘要替换旧消息之后 ==", packed["messages"])

    if not api_key_ready():
        print("没有可用的 DEEPSEEK_API_KEY，不再请求模型。")
        print("上面这段假摘要就是兜底。它只拼接旧句子的开头，不会自己发现没写出来的事实。")
        return

    settings = require_settings()
    describe_settings(settings)
    client = create_client(settings)
    produced = compress_messages(
        messages,
        keep_turns=1,
        threshold_turns=2,
        client=client,
        model=settings.model,
    )
    print(f"模型摘要来源={produced['source']}")
    if produced["note"]:
        print(f"说明：{produced['note']}")
    print(f"摘要：{produced['summary']}")
    print()
    show("== 模型摘要替换旧消息之后 ==", produced["messages"])


if __name__ == "__main__":
    main()
