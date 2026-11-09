# -*- coding: utf-8 -*-
"""阶段 2 · 示例 3：四个工具函数。不调用大模型。

反复运行会重建 shop.db，工单编号重新从 1 开始，方便和教程对照。

    python stage2_tools_tickets/03_tool_functions.py

导读：stage2_tools_tickets/docs/03_tools.md
"""

import json

from db import reset_database
from tools import create_ticket, get_ticket, query_order, update_ticket_status


def show(title: str, result: dict) -> None:
    print(title)
    print(json.dumps(result, ensure_ascii=False))
    print()


def main() -> None:
    print("这一步会重建 shop.db。以前用命令行客服记下的工单会被清空。")
    path = reset_database()
    print(f"数据库文件：{path}")
    print()
    show("查得到的订单", query_order("10086"))
    show("查不到的订单", query_order("99999"))
    created = create_ticket(
        ticket_type="退款",
        description="耳机不想要了",
        order_id="10086",
    )
    show("创建退款工单", created)
    ticket_id = created["ticket"]["id"]
    show("读出这张工单", get_ticket(ticket_id))
    show("推进到处理中", update_ticket_status(ticket_id, "处理中"))
    show("跳到已关闭（应被拒绝）", update_ticket_status(ticket_id, "已关闭"))
    show("拒绝之后再读，状态应仍是处理中", get_ticket(ticket_id))
    show(
        "没有订单号的投诉",
        create_ticket(ticket_type="投诉", description="包装破了"),
    )
    show(
        "没有订单号的退款",
        create_ticket(ticket_type="退款", description="我要退款"),
    )
    show(
        "订单不存在的退款",
        create_ticket(ticket_type="退款", description="我要退款", order_id="99999"),
    )


if __name__ == "__main__":
    main()
