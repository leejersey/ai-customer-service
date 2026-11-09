# -*- coding: utf-8 -*-
"""阶段 2 · 示例 6：先识别意图，再调用工具，工单写进 SQLite。

没有密钥时，用规则分类，回复是程序拼出来的句子，工单仍然会写进去。
有密钥时，工具照样由程序执行；模型只负责把结果说成客服的话。

    python stage2_tools_tickets/06_cli_with_tools.py

导读：stage2_tools_tickets/docs/06_cli.md
"""

import json

import stage2_link

stage2_link.enable()

from config import create_client, describe_settings, print_api_error, require_settings
from db import ensure_database
from llm_intent import api_key_ready, classify_by_llm
from service import handle_turn

EXIT_COMMANDS = {"quit", "exit", "q", "退出"}

SYSTEM_PROMPT = """你是「星河数码」的在线客服，名字叫小星。
请用简体中文回答，语气礼貌，句子短。
程序会在系统消息里给你工具的真实结果。金额、订单状态、工单编号只能引用结果里有的内容。
不要编造物流单号、到货时间或退款金额。
不要索要密码、短信验证码或完整银行卡号。
退款只是记下工单，不要说已经打款。"""


def request_reply(client, model: str, messages: list[dict]) -> str:
    """和阶段 0 一样，一次把整份历史发出去。这里不再附带 tools。

    工具已经由意图路由执行过了。再把 tools 交给模型，它可能再要一轮调用。
    """
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.3,
        max_tokens=512,
        stream=False,
    )
    if not response.choices:
        raise RuntimeError("响应里没有 choices。")
    reply = response.choices[0].message.content
    if not isinstance(reply, str) or reply.strip() == "":
        raise RuntimeError("模型没有返回文本内容。")
    return reply


def phrase(client, model: str, messages: list[dict], user_text: str, fact: str) -> str:
    messages.append({"role": "user", "content": user_text})
    note = (
        "下面是程序刚刚得到的结果。请只根据这些内容回复顾客，"
        "不要补充结果里没有的单号、金额或时间。\n"
        + fact
    )
    messages.append({"role": "system", "content": note})
    try:
        reply = request_reply(client, model, messages)
    except Exception:
        # 先弹出这一轮的说明，再弹出顾客的话。顺序反了会把更早的回复弹掉。
        if messages and messages[-1]["role"] == "system":
            messages.pop()
        if messages and messages[-1]["role"] == "user":
            messages.pop()
        raise
    messages.append({"role": "assistant", "content": reply})
    return reply


def main() -> None:
    path = ensure_database()
    print(f"工单保存在：{path}")
    print("这一步不会清空已有工单。示例 1、示例 3、示例 5 会重建数据库。")
    use_model = api_key_ready()
    client = None
    settings = None
    messages: list[dict] = []
    if use_model:
        settings = require_settings()
        describe_settings(settings)
        client = create_client(settings)
        messages.append({"role": "system", "content": SYSTEM_PROMPT})
    else:
        print("没有可用的 API 密钥。意图用规则，回复是程序写的。工单仍会写入数据库。")
        print("配好 .env 之后，同一条命令会让模型把工具结果说成客服的话。")
    session = {"pending": None}
    print()
    print("星河数码在线客服（阶段 2：意图之后调用工具）")
    print("可以试这些句子：")
    print("  订单号 10086 到哪了")
    print("  我要退款")
    print("  我要投诉，耳机有杂音")
    print("  查询工单 1")
    print("  把工单 1 改为处理中")
    print("输入 退出 或 quit 结束。退款只会写成工单，不会打款。")
    print()
    while True:
        try:
            user_text = input("你：").strip()
        except EOFError:
            print("\n输入结束，再见。")
            return
        except KeyboardInterrupt:
            print("\n已退出。")
            return
        if user_text.lower() in EXIT_COMMANDS:
            print("小星：感谢咨询，再见。")
            return
        if user_text == "":
            print("请输入内容。想结束时，整行输入：退出")
            continue
        classification = None
        # 正在追问订单号时不再请模型分类。缺口要补上，这一步用规则就够，也省一次请求。
        if use_model and not session.get("pending"):
            try:
                classification = classify_by_llm(client, settings.model, user_text)
            except Exception as error:
                print_api_error(error)
                print("这一句改用规则。")
                classification = None
        outcome = handle_turn(user_text, session, classification)
        reply = outcome["reply"]
        if use_model and outcome["asked"] is None:
            fact = outcome["reply"]
            if outcome["result"] is not None:
                fact = fact + "\n" + json.dumps(outcome["result"], ensure_ascii=False)
            try:
                reply = phrase(client, settings.model, messages, user_text, fact)
            except Exception as error:
                print_api_error(error)
                reply = outcome["reply"]
                print("这一轮没有写入历史。下面仍显示程序自己的句子。")
        elif use_model:
            # 追问也放进历史。下一轮模型才看得见自己问过订单号。
            messages.append({"role": "user", "content": user_text})
            messages.append({"role": "assistant", "content": outcome["reply"]})
        print(f"（意图={outcome['intent']} 来源={outcome['source']}）")
        print(f"小星：{reply}")
        print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n已退出。")
