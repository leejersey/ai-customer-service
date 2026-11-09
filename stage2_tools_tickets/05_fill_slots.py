# -*- coding: utf-8 -*-
"""阶段 2 · 示例 5：没给订单号就先追问，补上之后才建工单。不需要密钥。

反复运行会重建 shop.db。

    python stage2_tools_tickets/05_fill_slots.py

导读：stage2_tools_tickets/docs/05_slots.md
"""

from db import count_tickets, reset_database
from service import handle_turn


def show_turn(label: str, text: str, session: dict) -> dict:
    outcome = handle_turn(text, session)
    print(label)
    print(f"顾客：{text}")
    print(f"小星：{outcome['reply']}")
    print(f"意图={outcome['intent']} 来源={outcome['source']} 工具={outcome['tool']}")
    print(f"正在等待的槽位：{session.get('pending')}")
    print(f"当前工单张数：{count_tickets()}")
    print()
    return outcome


def main() -> None:
    print("这一步会重建 shop.db，工单编号从 1 重新开始。")
    path = reset_database()
    print(f"数据库文件：{path}")
    print()
    session = {"pending": None}
    show_turn("第 1 轮：只有退款，没有订单号。", "我要退款", session)
    show_turn("第 2 轮：补上订单号，才写入工单。", "订单号 10086", session)
    print("两轮用的是同一个 session。第 1 轮若换一个新字典，第 2 轮就不知道还在办退款。")


if __name__ == "__main__":
    main()
