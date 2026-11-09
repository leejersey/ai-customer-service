# -*- coding: utf-8 -*-
"""阶段 0 · 示例 3：流式输出。

先运行，再读教程：stage0_basics/docs/03_streaming.md

    python stage0_basics/03_streaming.py
"""

from config import create_client, describe_settings, print_api_error, require_settings

TEMPERATURE = 0.7
# 回复故意留得长一些。太短的话，片段会在你眨眼之前全部到齐，看不出「陆续出现」。
MAX_TOKENS = 400

SYSTEM_PROMPT = "你是「星河数码」的客服。用简体中文分步骤回答，每一步单独成行。"
USER_PROMPT = "顾客要申请退货。请按顺序写出：需要准备的信息、大致流程、以及我们现在还查不到真实订单时应该怎么说。写详细一点。"


def main() -> None:
    settings = require_settings()
    describe_settings(settings)
    client = create_client(settings)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT},
    ]

    print()
    print("开始流式输出。文字会一段段出现；网络很快时，也可能几乎连在一起：")
    print()
    # 前缀先打出来。后面的片段不换行，才会接在「模型：」后面，而不是各自占一行。
    print("模型：", end="", flush=True)

    # 屏幕上的字不是数据。不另存一份，这一轮就没有可以放进历史的 assistant 消息。
    pieces: list[str] = []
    finish_reason = None

    try:
        # 返回值不是整段回复，而是「再要下一段才继续」的流。网络读取发生在 for 循环里。
        stream = client.chat.completions.create(
            model=settings.model,
            messages=messages,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=True,
        )
        for chunk in stream:
            # 有的包只带用量、没有 choices。把它当成正文去取 delta，会在中途崩溃。
            if not chunk.choices:
                continue
            choice = chunk.choices[0]
            # delta 是这一包新增加的一点点，不是到目前为止的累计全文。
            delta = choice.delta
            piece = delta.content if delta is not None else None
            if isinstance(piece, str) and piece != "":
                pieces.append(piece)
                # 不刷新缓冲区的话，片段可能攒在内存里，人还是要等到最后才看见字。
                print(piece, end="", flush=True)
            if choice.finish_reason:
                finish_reason = choice.finish_reason
    except Exception as error:
        # 中断前屏幕上可能已经有半句话。那不是完整回复，也不能写进历史。
        print()
        print_api_error(error)
        print("如果上面已经冒出半句话，那是中断前收到的片段，不能当作完整答案。")
        raise SystemExit(1)

    # 流式打印故意不换行，这里补一个换行，避免说明文字粘在回复末尾。
    print()

    full_reply = "".join(pieces)
    print()
    if full_reply.strip() == "":
        print("没有收到任何文本片段。请检查模型名、余额和网络后重试。")
        raise SystemExit(1)

    print("把片段拼回去的完整回复：")
    print(full_reply)
    print()
    print(f"共收到 {len(pieces)} 个非空片段。结束原因：{finish_reason}")
    print("如果要做多轮对话，下一步是：")
    print('    messages.append({"role": "assistant", "content": full_reply})')
    print("只把片段打印到屏幕、却不保存 full_reply，下一轮模型就不知道自己说过什么。")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # 人按下中断时，已经打印的片段没有被保存。这是故意让现象和「没写入历史」一致。
        print("\n已手动中断。已经打印出来的文字不会被保存。")
