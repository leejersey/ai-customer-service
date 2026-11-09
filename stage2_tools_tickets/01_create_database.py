# -*- coding: utf-8 -*-
"""阶段 2 · 示例 1：创建 SQLite 数据库，并放入示例订单。

反复运行会删掉旧的 shop.db 再重建，已经记下的工单也会被清空。

    python stage2_tools_tickets/01_create_database.py

导读：stage2_tools_tickets/docs/01_database.md
"""

from db import count_tickets, fetch_orders, list_tables, reset_database


def main() -> None:
    print("这一步会重建 shop.db。以前记下的工单会被清空。")
    path = reset_database()
    print(f"数据库文件：{path}")
    names = list_tables()
    print("表：" + "、".join(names))
    print()
    orders = fetch_orders()
    for order in orders:
        print(
            f"订单 {order['order_id']}｜{order['user_name']}｜{order['product']}｜"
            f"{order['amount_yuan']} 元｜{order['status']}｜{order['created_at']}"
        )
    print()
    print(f"共 {len(orders)} 张订单。工单 {count_tickets()} 张。")
    print("新建时工单是 0 张。工单要到示例 3 之后才会出现。")


if __name__ == "__main__":
    main()
