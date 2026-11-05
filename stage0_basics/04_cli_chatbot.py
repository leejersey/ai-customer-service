# -*- coding: utf-8 -*-
"""阶段 0 · 示例 4：一个还不能查订单的命令行客服。

先运行，再读教程：stage0_basics/docs/04_cli_chatbot.md

    python stage0_basics/04_cli_chatbot.py

输入 quit、exit、q 或「退出」结束。这几个词必须是整行内容。
"""

from config import create_client, describe_settings, print_api_error, require_settings

# 客服希望前后说法稳定。这里比前几课更低，是产品选择，不是接口的默认要求。
TEMPERATURE = 0.3
MAX_TOKENS = 512

# 用集合做整行匹配。写在句子中间的 quit 不会命中，避免顾客一提到这个词就被踢出对话。
EXIT_COMMANDS = {"quit", "exit", "q", "退出"}

# 这条提示会留在列表第 0 条，每一轮都重发。它只约束模型的说法，并不真的查数据库或拦截敏感信息。
SYSTEM_PROMPT = """你是「星河数码」的在线客服，名字叫小星。
请用简体中文回答，语气礼貌，句子短。
你现在只能聊天，还不能查询真实订单、库存或物流。
如果顾客追问具体订单状态，请说明目前查不到真实数据，并告诉对方需要准备订单号和收货手机号后四位。
不要编造物流单号、到货时间或退款金额。
不要索要密码、短信验证码或完整银行卡号。
不确定的政策，就说需要人工客服再确认。"""


def request_reply(client, model: str, messages: list[dict[str, str]]) -> str:
    """把当前整份历史发给模型，拿回这一轮的完整回复。"""
    response = client.chat.completions.create(
        model=model,
        # 传整个列表，对话才能接上。只传最新一句的话，模型看不见前面的订单和自己的承诺。
        messages=messages,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        stream=False,
    )
    if not response.choices:
        # 抛给外层循环。在这里直接退出的话，一次空响应就会把整个客服进程打死。
        raise RuntimeError("响应里没有 choices。")
    reply = response.choices[0].message.content
    if not isinstance(reply, str) or reply.strip() == "":
        raise RuntimeError("模型没有返回文本内容。")
    return reply


def main() -> None:
    settings = require_settings()
    describe_settings(settings)
    # 客户端可以反复拨号。每说一句就新建一个，只会让人误以为连接里保存着记忆。
    client = create_client(settings)

    # 进程内的全部记忆就是这个列表。程序一退出，小星就不记得这次对话了。
    messages: list[dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    print()
    print("星河数码在线客服（阶段 0 练习）")
    print("输入问题后回车。输入 退出 或 quit 结束本次对话。")
    print("小星还查不到真实订单。连续提问时，上一句会留在本地历史里再发给模型。")
    print()

    while True:
        try:
            user_text = input("你：").strip()
        except EOFError:
            # 输入被管道关掉或按下 Ctrl+D 时，没有下一行。这是正常结束，不是接口故障。
            print("\n输入结束，再见。")
            return
        except KeyboardInterrupt:
            print("\n已退出。")
            return

        # 先认退出命令，再发给模型。否则「退出」两个字会变成一次付费请求。
        if user_text.lower() in EXIT_COMMANDS:
            print("小星：感谢咨询，再见。")
            return
        if user_text == "":
            print("请输入内容。想结束时，整行输入：退出")
            # continue 回到循环开头。用 return 的话，一次误触回车就会结束客服。
            continue

        messages.append({"role": "user", "content": user_text})
        try:
            reply = request_reply(client, settings.model, messages)
        except Exception as error:
            print_api_error(error)
            # 失败的用户句如果留在列表里，下一轮会变成「两句 user 中间没有 assistant」。
            if messages and messages[-1]["role"] == "user":
                messages.pop()
            print("这一轮没有写入历史。你可以修改问题或检查配置后再发。")
            continue

        messages.append({"role": "assistant", "content": reply})
        print(f"小星：{reply}")
        # 条数含系统提示。它一直涨，是在提醒：下一次请求会把这些全部再付一次 token。
        print(f"（当前 messages 共 {len(messages)} 条，下一次会全部重新发送。）")
        print()


if __name__ == "__main__":
    # 没有这个守卫，别的文件一旦 import 本模块，就会立刻进入客服循环。
    try:
        main()
    except KeyboardInterrupt:
        print("\n已退出。")
