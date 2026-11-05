# -*- coding: utf-8 -*-
"""阶段 0 · 示例 1：一次请求，一次回复。

这个脚本只做一件事：把一条用户消息发给 DeepSeek，再把模型的回复打印出来。
它是后面三个脚本的基础。先跑通它，再读注释。

在项目根目录运行：

    python stage0_basics/01_hello_llm.py
"""

# config.py 和本文件在同一个目录。直接运行本文件时，Python 会把该目录放进搜索路径。
from config import create_client, describe_settings, print_api_error, require_settings

# 温度越高，用词越发散；越低，越倾向于每次都给出差不多的说法。
# 客服场景通常用偏低的值。0.7 足够稳定，又不是完全背固定答案。
TEMPERATURE = 0.7

# 只限制「模型这次最多生成多少 token」，不限制我们发出去的提示有多长。
# 设小一点，是为了让第一次练习又短又省。
MAX_TOKENS = 256

# 系统消息：规定说话人的身份。用户在终端里看不到我们把它发给了接口，但模型会遵守它。
SYSTEM_PROMPT = "你是「星河数码」的客服助手。请用简体中文回答，语气礼貌，控制在两句话以内。"

# 用户消息：这一轮真正的问题。换成你自己的句子，就是这个示例的第一个练习。
USER_PROMPT = "你好，请用两句话介绍你能帮顾客做什么。"


def main() -> None:
    # 读取 .env。没有密钥时，require_settings 会打印中文说明并结束，不会继续联网。
    settings = require_settings()
    # 让运行的人确认模型名和地址。函数内部不会打印密钥。
    describe_settings(settings)
    # 创建客户端只是在内存里备好地址和密钥，此时还没有发出请求。
    client = create_client(settings)

    # messages 是一个列表，里面每一项都是一条「谁说了什么」。
    # 这一次只有两条：开发者写的 system，和顾客说的 user。还没有历史。
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT},
    ]

    print()
    print("即将发送的消息：")
    for index, message in enumerate(messages):
        # index 从 0 数起。打印出来是为了让你看见：请求正文就是这个列表，没有别的隐藏记忆。
        print(f"[{index}] {message['role']}: {message['content']}")

    print()
    print("正在请求模型，请稍等……")
    try:
        # chat.completions.create 会发起一次 HTTP 请求。
        # SDK 实际访问的是：{base_url}/chat/completions
        # 所以 base_url 保持 https://api.deepseek.com ，不要自己把路径加进去。
        # stream=False 表示等整段回复生成完再一次性返回。流式输出在 03_streaming.py。
        response = client.chat.completions.create(
            model=settings.model,
            messages=messages,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
    except Exception as error:
        # 网络、密钥、余额、模型名等问题都到这里。翻译成中文后退出。
        print_api_error(error)
        raise SystemExit(1)

    # choices 是候选回复列表。我们没有要求多份草稿，所以正常情况下只有第 0 项。
    if not response.choices:
        print("接口返回成功，但里面没有任何回复。可以重试一次。")
        raise SystemExit(1)

    reply = response.choices[0].message.content
    # content 正常是字符串。空字符串或别的类型都当成「这次没有可用文本」。
    if not isinstance(reply, str) or reply.strip() == "":
        print("模型没有返回文本。如果刚把模型换成带「思考」的型号，请稍后再试，或改回 .env 里的模型名。")
        raise SystemExit(1)

    print()
    print("模型回复：")
    print(reply)

    # finish_reason 告诉你这段文字为什么停下来。
    finish_reason = response.choices[0].finish_reason
    print()
    print(f"结束原因（finish_reason）：{finish_reason}")
    if finish_reason == "length":
        print("回复是因为碰到 MAX_TOKENS 被截断的。把 MAX_TOKENS 调大可以看完，但会多花一点额度。")
    elif finish_reason == "stop":
        print("stop 表示模型自己把话说完了，不是被字数上限切断的。")

    # usage 是这次计费和长度的依据。接口没返回时不要勉强拆它。
    usage = response.usage
    print()
    if usage is None:
        print("这次响应没有附带 token 用量。")
    else:
        print(f"提示 token（prompt_tokens）：{usage.prompt_tokens}")
        print(f"回复 token（completion_tokens）：{usage.completion_tokens}")
        print(f"合计 token（total_tokens）：{usage.total_tokens}")
        print("提示 token 里包含系统消息和用户消息。回复 token 只计算模型新写出来的部分。")

    # 服务端回显的模型名，有时会带具体版本，不一定和请求里的字符串逐字相同。
    print(f"服务端报告的模型：{response.model}")


if __name__ == "__main__":
    # 只有「python 01_hello_llm.py」这种直接运行才会进到这里。
    # 被别的文件 import 时不会自动发请求。
    try:
        main()
    except KeyboardInterrupt:
        # Ctrl+C 是人主动停下，不算接口失败。
        print("\n已手动中断。")
