# -*- coding: utf-8 -*-
"""阶段 2 · 示例 7：不调用模型，用假的 tool_calls 跑通数据库和状态流转。

使用单独的数据库文件，不会清空命令行客服用的 shop.db。

    python stage2_tools_tickets/07_offline_demo.py

导读：stage2_tools_tickets/docs/07_offline.md
"""

import json
from pathlib import Path

import db
from calling import append_tool_results, run_tool
from schema import TOOLS
from service import handle_turn
from states import StatusMachine
from tools import (
    TOOL_FUNCTIONS,
    create_ticket,
    get_ticket,
    query_order,
    update_ticket_status,
)


def show(title: str, payload) -> None:
    print(title)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    print()


def check_states() -> None:
    print("== 状态机 ==")
    machine = StatusMachine()
    print(machine.chain_text())
    assert machine.move("待处理", "处理中") == "处理中"
    try:
        machine.move("待处理", "已关闭")
    except ValueError as error:
        print(f"跳步被拒绝：{error}")
    else:
        raise AssertionError("待处理不能直接到已关闭")
    try:
        machine.move("已关闭", "处理中")
    except ValueError as error:
        print(f"关闭之后被拒绝：{error}")
    else:
        raise AssertionError("已关闭不能再改")
    print()


def check_orders_and_tickets() -> None:
    print("== 订单和工单 ==")
    found = query_order("10086")
    show("query_order 10086", found)
    assert found["ok"] is True
    assert found["order"]["product"] == "星河蓝牙耳机"
    assert found["order"]["order_id"] == "10086"
    missing = query_order("99999")
    show("query_order 99999", missing)
    assert missing["ok"] is False

    created = create_ticket(
        ticket_type="退款",
        description="耳机不想要了",
        order_id="10086",
    )
    show("create_ticket 退款", created)
    assert created["ok"] is True
    ticket_id = created["ticket"]["id"]
    assert ticket_id == 1
    assert created["ticket"]["status"] == "待处理"
    assert created["ticket"]["user_name"] == "演示用户"

    step = update_ticket_status(ticket_id, "处理中")
    assert step["ok"] is True
    assert step["ticket"]["status"] == "处理中"
    step = update_ticket_status(ticket_id, "已解决")
    assert step["ok"] is True
    step = update_ticket_status(ticket_id, "已关闭")
    show("走到已关闭", step)
    assert step["ok"] is True
    assert step["ticket"]["status"] == "已关闭"
    again = update_ticket_status(ticket_id, "处理中")
    show("已关闭再改", again)
    assert again["ok"] is False
    current = get_ticket(ticket_id)
    assert current["ticket"]["status"] == "已关闭"

    fresh = create_ticket(ticket_type="投诉", description="包装破了", order_id="30021")
    assert fresh["ok"] is True
    assert fresh["ticket"]["id"] == 2
    assert fresh["ticket"]["status"] == "待处理"
    skipped = update_ticket_status(fresh["ticket"]["id"], "已关闭")
    show("新建后直接关闭", skipped)
    assert skipped["ok"] is False
    stayed = get_ticket(fresh["ticket"]["id"])
    assert stayed["ticket"]["status"] == "待处理"

    shipped = update_ticket_status(fresh["ticket"]["id"], "已发货")
    assert shipped["ok"] is False
    no_order = create_ticket(ticket_type="退款", description="我要退款")
    assert no_order["ok"] is False
    unknown_order = create_ticket(
        ticket_type="退款",
        description="我要退款",
        order_id="99999",
    )
    assert unknown_order["ok"] is False
    print("订单、建单、逐步流转、非法流转都符合预期。")
    print()


def check_slots() -> None:
    print("== 追问补槽位 ==")
    session = {"pending": None}
    first = handle_turn("我要退款", session)
    show("第 1 轮", first)
    assert first["tool"] is None
    assert first["asked"] == "order_id"
    assert session["pending"]["intent"] == "退款"
    assert db.count_tickets() == 2
    second = handle_turn("订单号 10086", session)
    show("第 2 轮", second)
    assert second["tool"] == "create_ticket"
    assert second["result"]["ok"] is True
    assert second["source"] == "slots"
    assert second["result"]["ticket"]["order_id"] == "10086"
    assert second["result"]["ticket"]["description"] == "我要退款"
    assert session["pending"] is None
    assert db.count_tickets() == 3

    direct = handle_turn("订单 20001888 到哪了", {"pending": None})
    assert direct["tool"] == "query_order"
    assert direct["result"]["order"]["product"] == "星河机械键盘"
    complaint = handle_turn("我要投诉，耳机有杂音", {"pending": None})
    assert complaint["tool"] == "create_ticket"
    assert complaint["result"]["ticket"]["ticket_type"] == "投诉"
    looked = handle_turn("查询工单 2", {"pending": None})
    assert looked["tool"] == "get_ticket"
    assert looked["result"]["ticket"]["id"] == 2
    moved = handle_turn("把工单 2 改为处理中", {"pending": None})
    assert moved["result"]["ok"] is True
    assert moved["result"]["ticket"]["status"] == "处理中"
    print("追问、查询、投诉、工单命令都符合预期。")
    print()


def check_fake_model() -> None:
    print("== 假的模型响应 ==")
    messages = [
        {"role": "system", "content": "你是星河数码的客服。"},
        {"role": "user", "content": "请帮我查一下订单 10086 的状态。"},
    ]
    # 形状和在线接口的 tool_calls 相同。arguments 故意用文本，因为接口给的就是文本。
    fake = {
        "role": "assistant",
        "content": None,
        "tool_calls": [
            {
                "id": "call_offline_query",
                "type": "function",
                "function": {
                    "name": "query_order",
                    "arguments": json.dumps({"order_id": "10086"}, ensure_ascii=False),
                },
            }
        ],
    }
    messages.append(fake)
    results = append_tool_results(messages, fake)
    show("执行假 tool_calls 之后的 messages", messages)
    assert [item["role"] for item in messages] == ["system", "user", "assistant", "tool"]
    assert messages[-1]["tool_call_id"] == "call_offline_query"
    body = json.loads(messages[-1]["content"])
    assert body["ok"] is True
    assert body["order"]["order_id"] == "10086"
    assert results[0]["name"] == "query_order"

    bad_name = run_tool("delete_all", "{}")
    assert bad_name["ok"] is False
    bad_json = run_tool("query_order", "订单 10086")
    assert bad_json["ok"] is False
    # 不传 user_name、不传 order_id，走函数定义里的默认值。
    omitted = run_tool(
        "create_ticket",
        json.dumps({"ticket_type": "转人工", "description": "请转人工"}, ensure_ascii=False),
    )
    assert omitted["ok"] is True
    assert omitted["ticket"]["user_name"] == "演示用户"
    assert omitted["ticket"]["order_id"] == ""
    blank_name = run_tool(
        "create_ticket",
        json.dumps(
            {"ticket_type": "投诉", "description": "包装破了", "user_name": "  "},
            ensure_ascii=False,
        ),
    )
    assert blank_name["ok"] is True
    assert blank_name["ticket"]["user_name"] == "演示用户"
    print("假响应、未知工具、坏 JSON、默认参数都符合预期。")
    print()


def check_schema_matches_functions() -> None:
    print("== 说明书和登记表 ==")
    names = []
    for item in TOOLS:
        names.append(item["function"]["name"])
    assert set(names) == set(TOOL_FUNCTIONS)
    print("tools 里的名字：" + "、".join(names))
    print()


def main() -> None:
    demo_path = Path(__file__).resolve().parent / "data" / "offline_demo.db"
    db.use_database(demo_path)
    path = db.reset_database()
    print(f"离线演示使用单独的文件：{path}")
    print("不会改动 shop.db。")
    print()
    check_states()
    check_orders_and_tickets()
    check_slots()
    check_fake_model()
    check_schema_matches_functions()
    print("离线演示通过")


if __name__ == "__main__":
    main()
