# -*- coding: utf-8 -*-
"""阶段 0 · 示例 4：一个还不能查订单的命令行客服。

它已经具备后面智能体的最小对话外壳：

- 一条固定的系统提示，规定身份和不能做的事
- 一个 messages 列表，保存本次运行中的全部历史
- 一个循环：读入用户输入，请求模型，再把回复追加进历史
- 一个退出命令

它还没有工具、数据库和记忆服务。问具体物流时，它只能按系统提示承认查不到。
那些能力留在后续阶段。

在项目根目录运行：

    python stage0_basics/04_cli_chatbot.py

输入 quit、exit、q 或「退出」结束。这几个词必须是整行内容，写在句子里面不会触发。
"""

from config import create_client, describe_settings, print_api_error, require_settings

# 客服回答希望稳定，比前几个演示更低的温度更合适。
TEMPERATURE = 0.3
MAX_TOKENS = 512

# 整行匹配才算退出，所以大小写先统一成小写再比较。中文「退出」没有大小写问题。
EXIT_COMMANDS = {"quit", "exit", "q", "退出"}

# 系统提示一直放在 messages[0]，清空练习如果要做，也应该保留这一条。
SYSTEM_PROMPT = """你是「星河数码」的在线客服，名字叫小星。
请用简体中文回答，语气礼貌，句子短。
你现在只能聊天，还不能查询真实订单、库存或物流。
如果顾客追问具体订单状态，请说明目前查不到真实数据，并告诉对方需要准备订单号和收货手机号后四位。
不要编造物流单号、到货时间或退款金额。
不要索要密码、短信验证码或完整银行卡号。
不确定的政策，就说需要人工客服再确认。"""


def request_reply(client, model: str, messages: list[dict[str, str]]) -> str:
    """把当前全部历史发给模型，返回这一轮的完整回复。"""
    response = client.chat.completions.create(
        model=model,
        # 这里传的是整个列表，不是只传最新一句。这就是多轮能接上的原因。
        messages=messages,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        stream=False,
    )
    if not response.choices:
        # 用普通异常抛出，外层循环会翻译成中文并继续等待下一次输入。
        raise RuntimeError("响应里没有 choices。")
    reply = response.choices[0].message.content
    if not isinstance(reply, str) or reply.strip() == "":
        raise RuntimeError("模型没有返回文本内容。")
    return reply


def main() -> None:
    settings = require_settings()
    describe_settings(settings)
    # 客户端可以反复使用，不必每说一句就新建一个。
    client = create_client(settings)

    # 历史从系统提示开始。之后用户和助手的话都追加在后面。
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
            # input 读到一行就返回，不含末尾换行。strip 去掉用户多打的空格。
            user_text = input("你：").strip()
        except EOFError:
            # 管道结束或 Ctrl+D 时没有下一行。当作正常告别，而不是异常崩溃。
            print("\n输入结束，再见。")
            return
        except KeyboardInterrupt:
            print("\n已退出。")
            return

        # 先判断退出，再判断空行。这样单独输入 quit 不会被当成一句顾客的话发给模型。
        if user_text.lower() in EXIT_COMMANDS:
            print("小星：感谢咨询，再见。")
            return
        if user_text == "":
            print("请输入内容。想结束时，整行输入：退出")
            continue

        # 先放进历史，请求失败时再拿出来。不这么做的话，失败的半句话会留在下一轮里。
        messages.append({"role": "user", "content": user_text})
        try:
            reply = request_reply(client, settings.model, messages)
        except Exception as error:
            print_api_error(error)
            if messages and messages[-1]["role"] == "user":
                messages.pop()
            print("这一轮没有写入历史。你可以修改问题或检查配置后再发。")
            continue

        messages.append({"role": "assistant", "content": reply})
        print(f"小星：{reply}")
        # 条数包含最前面那条 system。它提醒你：聊天越长，下一次请求的提示 token 越多。
        print(f"（当前 messages 共 {len(messages)} 条，下一次会全部重新发送。）")
        print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n已退出。")
