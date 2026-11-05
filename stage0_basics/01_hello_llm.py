# -*- coding: utf-8 -*-
"""阶段 0 · 示例 1：一次请求，一次回复。

先运行，再读教程：stage0_basics/docs/01_hello_llm.md

    python stage0_basics/01_hello_llm.py
"""

# 读密钥、建客户端、翻译错误都放在 config.py。这一课只保留「发一次、看懂结果」。
from config import create_client, describe_settings, print_api_error, require_settings

# 第一课不用 0。温度太低时，两次回答几乎一样，容易误以为模型在背固定句子。
TEMPERATURE = 0.7

# 练习请求把回复封顶，避免一句问候换回很长的文本、多花额度。
MAX_TOKENS = 256

# 身份先于问题。后面的智能体也靠这种系统消息规定「我是谁、不能做什么」。
SYSTEM_PROMPT = "你是「星河数码」的客服助手。请用简体中文回答，语气礼貌，控制在两句话以内。"

# 问题写成常量，是为了改问题做实验时不用钻进函数里面找。
USER_PROMPT = "你好，请用两句话介绍你能帮顾客做什么。"


def main() -> None:
    # 密钥不可用就停在这里。继续往下只会得到难读的 401，而不是这份中文说明。
    settings = require_settings()
    # 把地址和模型打出来，用来核对 .env 有没有生效。密钥不能出现在屏幕上。
    describe_settings(settings)
    # 准备电话号码和钥匙。真正拨号、也是可能产生费用的，是下面的 create。
    client = create_client(settings)

    # 用带角色的列表，而不是拼成一大段字符串。接口要的是这个形状，以后追加历史也不必重拼全文。
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT},
    ]

    # 发送前把列表打出来。否则看起来像程序在别的地方还藏着记忆。
    print()
    print("即将发送的消息：")
    for index, message in enumerate(messages):
        # 下标从 0 开始，和后面取 choices[0] 是同一种数法。第一条就是第 0 条。
        print(f"[{index}] {message['role']}: {message['content']}")

    print()
    print("正在请求模型，请稍等……")
    try:
        # stream 写明为 False，是为了和第三课对照。不写也会整段返回，但默认值在代码里看不见。
        # base_url 不要自己加上 /chat/completions，SDK 会拼这条路径。
        response = client.chat.completions.create(
            model=settings.model,
            messages=messages,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
    except Exception as error:
        # 这一课失败就结束。命令行客服那一课才会捕获错误后继续等下一句。
        print_api_error(error)
        raise SystemExit(1)

    # 先确认列表非空再取第 0 项。空列表时的 IndexError 看起来像 messages 写错了，其实不是。
    if not response.choices:
        print("接口返回成功，但里面没有任何回复。可以重试一次。")
        raise SystemExit(1)

    reply = response.choices[0].message.content
    # 调用成功和「有可显示的正文」不是一回事。空正文要单独说明，不要一律当成密钥错误。
    if not isinstance(reply, str) or reply.strip() == "":
        print("模型没有返回文本。如果刚把模型换成带「思考」的型号，请稍后再试，或改回 .env 里的模型名。")
        raise SystemExit(1)

    print()
    print("模型回复：")
    print(reply)

    # 同样一段短文字，可能是说完了，也可能是被 max_tokens 切断。只看正文分不出来。
    finish_reason = response.choices[0].finish_reason
    print()
    print(f"结束原因（finish_reason）：{finish_reason}")
    if finish_reason == "length":
        print("回复是因为碰到 MAX_TOKENS 被截断的。把 MAX_TOKENS 调大可以看完，但会多花一点额度。")
    elif finish_reason == "stop":
        print("stop 表示模型自己把话说完了，不是被字数上限切断的。")

    # 用量是「历史变长就会更贵」的第一份证据。有的响应不带 usage，没有就不拆。
    usage = response.usage
    print()
    if usage is None:
        print("这次响应没有附带 token 用量。")
    else:
        print(f"提示 token（prompt_tokens）：{usage.prompt_tokens}")
        print(f"回复 token（completion_tokens）：{usage.completion_tokens}")
        print(f"合计 token（total_tokens）：{usage.total_tokens}")
        print("提示 token 里包含系统消息和用户消息。回复 token 只计算模型新写出来的部分。")

    # 服务端实际使用的名字有时比请求里的名字更具体。两边不一致时，以这一行为准排查模型。
    print(f"服务端报告的模型：{response.model}")


if __name__ == "__main__":
    # 这个守卫把「运行本文件」和「被别的文件 import」分开。
    # 没有它的话，将来谁借用这里的函数，都会顺便打出一次付费请求。
    try:
        main()
    except KeyboardInterrupt:
        # 人按了 Ctrl+C，不是接口拒绝。不要走 print_api_error 那套说明。
        print("\n已手动中断。")
