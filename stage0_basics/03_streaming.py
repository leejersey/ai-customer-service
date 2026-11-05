# -*- coding: utf-8 -*-
"""阶段 0 · 示例 3：流式输出。

非流式请求要等模型把整段话写完才返回，所以终端会先停一会儿，然后一下子刷出全文。
流式请求则是每生成一小段就发回来。总等待时间差不多，但人可以更早开始读。

注意：流式时接口不会替你把片段收成一条完整消息。
如果这是聊天机器人，你必须自己把片段拼好，再作为 assistant 放进历史。
本脚本只演示拼接，不进入多轮。

在项目根目录运行：

    python stage0_basics/03_streaming.py
"""

from config import create_client, describe_settings, print_api_error, require_settings

TEMPERATURE = 0.7
# 这段回复故意稍长，这样即使网络很快，也更容易看出文字是陆续出现的。
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
    # 先打印说话人前缀。后面的片段用 end=""，所以会接在这一行后面。
    print("模型：", end="", flush=True)

    # 接口只给片段。完整回复要靠这个列表自己攒。
    pieces: list[str] = []
    # 结束原因通常出现在最后一个有内容的片段上，先留空。
    finish_reason = None

    try:
        # stream=True 时，返回值不是完整回复，而是一个可以逐段迭代的对象。
        # 真正的网络读取发生在下面的 for 循环里，所以异常也可能在循环中途抛出。
        stream = client.chat.completions.create(
            model=settings.model,
            messages=messages,
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=True,
        )
        for chunk in stream:
            # 有的包没有 choices，例如个别实现把用量单独放在最后一包。没有文本就跳过。
            if not chunk.choices:
                continue
            choice = chunk.choices[0]
            # delta 是「相对于上一包新增加的那一点」，不是累计全文。
            delta = choice.delta
            piece = delta.content if delta is not None else None
            # 只收下文本片段。空包和个别非文本增量都跳过，避免把 None 拼进回复。
            if isinstance(piece, str) and piece != "":
                pieces.append(piece)
                # end="" 避免每个片段都换行。flush=True 立刻刷到屏幕，不然可能攒一批才显示。
                print(piece, end="", flush=True)
            if choice.finish_reason:
                finish_reason = choice.finish_reason
    except Exception as error:
        # 失败前可能已经打印了一部分。那部分不是完整回复，本脚本也没有写进历史。
        print()
        print_api_error(error)
        print("如果上面已经冒出半句话，那是中断前收到的片段，不能当作完整答案。")
        raise SystemExit(1)

    # 流式打印没有在结尾换行，这里补一行，让后面的说明另起一行。
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
        print("\n已手动中断。已经打印出来的文字不会被保存。")
