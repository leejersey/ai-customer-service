# -*- coding: utf-8 -*-
"""阶段 2 · 示例 4：请模型决定调用哪一个工具，程序执行后再要最终回复。

没有密钥时只打印 tools 说明书，然后说明跳过，不会假装已经调用过模型。
有密钥时只演示一轮工具调用。

    python stage2_tools_tickets/04_function_calling.py

导读：stage2_tools_tickets/docs/04_function_calling.md
"""

import json

import stage2_link

stage2_link.enable()

from calling import append_tool_results, request_with_tools
from config import create_client, describe_settings, print_api_error, require_settings
from db import ensure_database
from llm_intent import api_key_ready
from schema import TOOLS

# 这句话里已经有订单号，所以正常情况是一轮 query_order，而不是先追问。
USER_TEXT = "请帮我查一下订单 10086 的状态。"

SYSTEM_PROMPT = """你是「星河数码」的客服。
需要订单或工单的事实时，调用给定的工具，不要编造。
顾客没提供订单号就不要猜一个。
工具结果返回之后，用简体中文短句回复。
不要说已经打款。"""


def show_messages(title: str, messages: list) -> None:
    print(title)
    print(json.dumps(messages, ensure_ascii=False, indent=2))
    print()


def main() -> None:
    print("下面这份 JSON 就是请求里的 tools。它描述函数，它不是函数。")
    print(json.dumps(TOOLS, ensure_ascii=False, indent=2))
    print()
    path = ensure_database()
    print(f"查询会用这个数据库：{path}")
    print("这一步不会清空已有工单。还没有文件时，会先建库并放入示例订单。")
    print()
    if not api_key_ready():
        print("没有可用的 DEEPSEEK_API_KEY，跳过真正的模型调用。")
        print("同一套执行函数在示例 7 里用假的 tool_calls 跑通，不需要密钥。")
        return
    settings = require_settings()
    describe_settings(settings)
    client = create_client(settings)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_TEXT},
    ]
    try:
        assistant, finish_reason = request_with_tools(client, settings.model, messages)
    except Exception as error:
        print_api_error(error)
        return
    messages.append(assistant)
    print(f"第一轮结束原因：{finish_reason}")
    show_messages("模型决定之后的 messages：", messages)
    if not assistant.get("tool_calls"):
        print("这一次模型没有调用工具，上面的 content 就是它的直接回复。")
        print("可以把 USER_TEXT 换成更明确的一句，或先看示例 7 的假响应。")
        return
    results = append_tool_results(messages, assistant)
    print("本地函数已经执行。结果如下：")
    print(json.dumps(results, ensure_ascii=False, indent=2))
    print()
    try:
        final, final_reason = request_with_tools(client, settings.model, messages)
    except Exception as error:
        print_api_error(error)
        print("工具已经执行。最终回复这一轮没有拿到。")
        show_messages("目前的 messages：", messages)
        return
    messages.append(final)
    print(f"第二轮结束原因：{final_reason}")
    if final.get("tool_calls"):
        # 本示例只执行一轮。再调用就停下来，避免不知不觉打很多轮。
        print("模型还想再调用工具。本示例只做一轮，到这里停。")
    show_messages("加上最终回复之后的 messages：", messages)
    print(f"小星：{final.get('content')}")


if __name__ == "__main__":
    main()
