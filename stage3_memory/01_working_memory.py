# -*- coding: utf-8 -*-
"""阶段 3 · 示例 1：工作记忆和对话历史是两份东西。

不连接 Redis，也不调用模型。只在这一进程里把小表填出来。

    python stage3_memory/01_working_memory.py

导读：stage3_memory/docs/01_working_memory.md
"""

from working import WorkingMemory


def show_history(messages: list[dict]) -> None:
    print(f"对话历史 {len(messages)} 条：")
    for index, message in enumerate(messages):
        print(f"  [{index}] {message['role']}：{message['content']}")
    print()


def main() -> None:
    memory = WorkingMemory()
    messages: list[dict] = []
    print("== 一开始 ==")
    print(memory)
    show_history(messages)
    print("历史是一个列表，里面还没有句子。")
    print("工作记忆是另一张小表：意图、槽位、正在等的项、工单编号、办到哪一步。")
    print()

    print("== 顾客说：我要退款 ==")
    messages.append({"role": "user", "content": "我要退款"})
    messages.append({"role": "assistant", "content": "请告诉我订单号。它一般是一串数字，例如 10086。"})
    memory.intent = "退款"
    memory.pending_slot = "order_id"
    memory.pending_text = "我要退款"
    memory.task_status = "waiting"
    print(memory)
    show_history(messages)
    print("这两句话已经在历史里。订单号还不在历史的结构外面单独放好，小表上 pending_slot 是 order_id。")
    print()

    print("== 顾客说：订单号 10086 ==")
    messages.append({"role": "user", "content": "订单号 10086"})
    messages.append({"role": "assistant", "content": "已记下退款工单 1，当前状态是待处理。钱还没有退。"})
    memory.slots["order_id"] = "10086"
    memory.pending_slot = None
    memory.pending_text = ""
    memory.ticket_id = "1"
    memory.task_status = "done"
    print(memory)
    show_history(messages)
    print()

    print("== 丢掉最早的两句历史 ==")
    # 这里还不用切片。下一课才把「留下最近几句」写成窗口。
    shortened = []
    for message in messages:
        if message["content"] == "我要退款":
            continue
        if message["content"].startswith("请告诉我订单号"):
            continue
        shortened.append(message)
    show_history(shortened)
    print(f"工作记忆里的订单号仍是：{memory.slots['order_id']}")
    print(f"手头的工单编号仍是：{memory.ticket_id}")
    print()
    print("历史回答「说过什么」。工作记忆回答「这一单办到哪了」。")
    print("切掉旧句子，不会自动把订单号一起忘掉。后面的窗口和摘要都靠这个差别。")


if __name__ == "__main__":
    main()
