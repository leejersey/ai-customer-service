# -*- coding: utf-8 -*-
"""阶段 1 · 示例 5：先识别意图，再决定怎么答。

没有密钥时，只用规则和写死的回复，仍然可以对话。
有密钥时，先分类，再把意图写进一条开发者消息，然后才让客服模型说话。

    python stage1_intent/05_cli_with_intent.py

导读：stage1_intent/docs/05_cli.md
"""

import stage0_link

stage0_link.enable()

from config import create_client, describe_settings, print_api_error, require_settings
from llm_intent import api_key_ready, classify_by_llm
from router import route, route_by_rules

EXIT_COMMANDS = {"quit", "exit", "q", "退出"}

SYSTEM_PROMPT = """你是「星河数码」的在线客服，名字叫小星。
请用简体中文回答，语气礼貌，句子短。
你现在只能聊天，还不能查询真实订单、库存或物流。
不要编造物流单号、到货时间或退款金额。
不要索要密码、短信验证码或完整银行卡号。
如果对话里出现「意图识别结果」，按那个意图回答，不要改口说自己查到了数据库。"""


def request_reply(client, model: str, messages: list[dict[str, str]]) -> str:
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


def main() -> None:
    # 没有密钥也要能练习意图。此时不创建客户端，避免看起来像已经连上了模型。
    use_model = api_key_ready()
    client = None
    settings = None
    if use_model:
        settings = require_settings()
        describe_settings(settings)
        client = create_client(settings)
    else:
        print("没有可用的 API 密钥。这一轮只用规则识别意图，回复是写死的。")
        print("配好 .env 之后，同一条命令会先分类，再让客服模型按意图说话。")

    messages: list[dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]
    print()
    print("星河数码在线客服（阶段 1：先看意图）")
    print("输入 退出 或 quit 结束。")
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

        if use_model:
            try:
                result = classify_by_llm(client, settings.model, user_text)
            except Exception as error:
                print_api_error(error)
                result = route_by_rules(user_text)[0]
                result = dict(result)
                result["source"] = "rules-after-error"
            reply_plan = route(user_text, result)
            order_id = result["slots"].get("order_id")
            note = (
                f"意图识别结果：{result['intent']}。"
                f"订单号：{order_id or '无'}。"
                f"来源：{result['source']}。"
                f"处理函数建议：{reply_plan}"
            )
            messages.append({"role": "user", "content": user_text})
            # 单独一条开发者消息，避免把意图说明混进顾客原话，以后回看历史时还能分清谁说的。
            messages.append({"role": "system", "content": note})
            try:
                reply = request_reply(client, settings.model, messages)
            except Exception as error:
                print_api_error(error)
                if messages and messages[-1]["role"] == "system":
                    messages.pop()
                if messages and messages[-1]["role"] == "user":
                    messages.pop()
                print("这一轮没有写入历史。")
                continue
            messages.append({"role": "assistant", "content": reply})
        else:
            result, reply = route_by_rules(user_text)

        print(f"（意图={result['intent']} 来源={result['source']}）")
        print(f"小星：{reply}")
        print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n已退出。")
