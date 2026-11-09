# -*- coding: utf-8 -*-
"""阶段 0 · 示例 2：三种角色，以及为什么第二轮要把历史再发一遍。

先运行，再读教程：stage0_basics/docs/02_messages_roles.md

    python stage0_basics/02_messages_roles.py
"""

from config import create_client, describe_settings, print_api_error, require_settings

# 这一课要比较的是「列表变长了没有」，不是文采。温度放低，避免两轮回答飘得无法对照。
TEMPERATURE = 0.3
# 回复太长时，打印出来的历史会把角色结构淹没掉。
MAX_TOKENS = 200

# 规则放在每一轮都会重发的第 0 条里。删掉它，模型更容易编出具体退款金额。
SYSTEM_PROMPT = (
    "你是「星河数码」的客服。用简体中文回答，不超过 80 个字。"
    "不要编造具体的退款金额或物流单号。不确定的规则，就说需要人工确认。"
)


def show_messages(messages: list[dict[str, str]]) -> None:
    """请求前把整份列表打出来，让两次发送的差别肉眼可见。"""
    print("即将发送的 messages：")
    for index, message in enumerate(messages):
        print(f"  [{index}] {message['role']}: {message['content']}")


def request_reply(client, model: str, messages: list[dict[str, str]]) -> tuple[str, object]:
    """发一次非流式请求。

    两次调用共用它，是为了保证除了 messages 以外的参数不会一次一个样。
    这个参数是整份历史。函数看不见调用者手里另有一份更全的列表。
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            # 这一课要看完整 JSON 对应的整段结果。流式放到下一课，避免两件事叠在一起。
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
    """并排比较两轮的 prompt token。第二轮变大，才说明历史真的被重新发送了。"""
    if usage is None:
        print(f"{turn_name} 没有返回 token 用量。")
        return
    print(
        f"{turn_name} token：prompt={usage.prompt_tokens}, "
        f"completion={usage.completion_tokens}, total={usage.total_tokens}"
    )


def main() -> None:
    settings = require_settings()
    describe_settings(settings)
    client = create_client(settings)

    # 对话状态只活在这个列表里。进程退出后它就没了，服务器也不会替我们留底。
    messages: list[dict[str, str]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]

    print()
    print("========== 第 1 轮 ==========")
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

    # 不把模型刚说的话写回列表，下一轮就看不到它自己承诺过什么。
    messages.append({"role": "assistant", "content": reply})

    print()
    print("========== 第 2 轮 ==========")
    # 「上面这个订单」本身没有订单号。只有整份历史一起送出去，这句话才有所指。
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
    # 本课到此结束。若要第三轮，同样得先把这句回复写回列表，否则第三句也接不上。
    messages.append({"role": "assistant", "content": reply})

    print()
    print("请对比两次打印出来的 messages。")
    print("第二次比第一次多了：第 1 轮的 assistant，以及第 2 轮的 user。")
    print("接口没有保存第 1 轮。是这个 Python 列表被我们重新发送了出去。")
    print(f"脚本结束时，本地历史一共 {len(messages)} 条。")


if __name__ == "__main__":
    # 防止这个文件被 import 时连打两次付费请求。
    try:
        main()
    except KeyboardInterrupt:
        print("\n已手动中断。")
