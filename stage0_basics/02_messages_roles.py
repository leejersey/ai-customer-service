# -*- coding: utf-8 -*-
"""阶段 0 · 示例 2：三种角色，以及为什么第二轮要把历史再发一遍。

脚本会连续做两次请求：

1. 顾客说明自己要退耳机，订单尾号是 86。
2. 顾客追问「那上面这个订单，拆封了还能退吗？」

第二句里的「上面这个订单」只有带着第一轮的问答才有所指。
聊天接口不会替你记住第一轮，所以 messages 列表要由我们自己保存并整包重发。

在项目根目录运行：

    python stage0_basics/02_messages_roles.py
"""

from config import create_client, describe_settings, print_api_error, require_settings

# 这一课重点看消息列表，不看文采，所以温度低一些，回复更稳。
TEMPERATURE = 0.3
# 每轮回复限制短一点，打印历史时才看得清。
MAX_TOKENS = 200

# system：开发者设定的规则，一般在列表的第 0 条，并且每一轮都保留。
SYSTEM_PROMPT = (
    "你是「星河数码」的客服。用简体中文回答，不超过 80 个字。"
    "不要编造具体的退款金额或物流单号。不确定的规则，就说需要人工确认。"
)


def show_messages(messages: list[dict[str, str]]) -> None:
    """把即将发出去的历史原样打印出来。"""
    print("即将发送的 messages：")
    for index, message in enumerate(messages):
        # role 只能是我们约定的三种：system、user、assistant。
        # content 是这句的正文。
        print(f"  [{index}] {message['role']}: {message['content']}")


def request_reply(client, model: str, messages: list[dict[str, str]]) -> tuple[str, object]:
    """发一次非流式请求，返回回复文本和整段响应。

    两次调用共用这个函数，因为参数形式一样。真正变化的是 messages 里有几条。
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            # 仍然一次拿回整段。流式是下一课的主题。
            stream=False,
        )
    except Exception as error:
        print_api_error(error)
        raise SystemExit(1)

    if not response.choices:
        print("接口没有返回 choices。")
        raise SystemExit(1)

    reply = response.choices[0].message.content
    if not isinstance(reply, str) or reply.strip() == "":
        print("模型没有返回文本。")
        raise SystemExit(1)
    return reply, response


def print_usage(turn_name: str, usage: object) -> None:
    """打印这一轮的 token 用量，用来和下一轮对比。"""
    if usage is None:
        print(f"{turn_name} 没有返回 token 用量。")
        return
    # prompt_tokens 会随着历史变长而变大，因为上一轮的问答又被放进了新请求。
    print(
        f"{turn_name} token：prompt={usage.prompt_tokens}, "
        f"completion={usage.completion_tokens}, total={usage.total_tokens}"
    )


def main() -> None:
    settings = require_settings()
    describe_settings(settings)
    client = create_client(settings)

    # 对话状态只存在于这个列表。程序一退出，列表就没了，服务端也不会帮我们留着。
    messages: list[dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    print()
    print("========== 第 1 轮 ==========")
    # 追加用户的第一句话。现在列表是 [system, user]。
    messages.append(
        {
            "role": "user",
            "content": "我买的耳机想退货，订单尾号是 86。",
        }
    )
    show_messages(messages)
    reply, response = request_reply(client, settings.model, messages)
    print("模型回复：")
    print(reply)
    print_usage("第 1 轮", response.usage)

    # assistant 表示「这是模型说过的话」。
    # 不把这句追加进去，下一轮模型就看不到自己刚才承诺过什么。
    messages.append({"role": "assistant", "content": reply})

    print()
    print("========== 第 2 轮 ==========")
    # 第二句故意使用「上面这个订单」。如果请求里没有第一轮，这句话是不完整的。
    messages.append(
        {
            "role": "user",
            "content": "那上面这个订单，如果已经拆封了，还能退吗？",
        }
    )
    show_messages(messages)
    reply, response = request_reply(client, settings.model, messages)
    print("模型回复：")
    print(reply)
    print_usage("第 2 轮", response.usage)
    # 如果还要第 3 轮，同样要把这句 assistant 再放回列表。本示例到此停止。
    messages.append({"role": "assistant", "content": reply})

    print()
    print("请对比两次打印出来的 messages。")
    print("第二次比第一次多了：第 1 轮的 assistant，以及第 2 轮的 user。")
    print("接口没有保存第 1 轮。是这个 Python 列表被我们重新发送了出去。")
    print(f"脚本结束时，本地历史一共 {len(messages)} 条。")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n已手动中断。")
