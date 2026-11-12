# -*- coding: utf-8 -*-
"""阶段 3 · 示例 5：按 session_id 保存消息、摘要和槽位，并在访问时续期。

    python stage3_memory/05_session_store.py

导读：stage3_memory/docs/05_session_store.md
"""

import time

from backend import explain, open_client
from store import SessionStore
from working import WorkingMemory

SESSION_ID = "stage3-lesson"
OTHER_ID = "stage3-lesson-other"


def main() -> None:
    connected = open_client(prefer_real=True)
    explain(connected)
    print()
    # 演示用 30 秒，方便看见 TTL。命令行客服默认 1800 秒，也就是 30 分钟。
    store = SessionStore(connected.client, ttl_seconds=30)
    store.clear_session(SESSION_ID)
    store.clear_session(OTHER_ID)

    print("== 消息写成 JSON，放进 LIST ==")
    store.append_message(SESSION_ID, {"role": "user", "content": "我要退款"})
    store.append_message(SESSION_ID, {"role": "assistant", "content": "请告诉我订单号。"})
    store.append_message(SESSION_ID, {"role": "user", "content": "订单号 10086"})
    recent = store.recent_messages(SESSION_ID, limit=2)
    print("最近 2 条：")
    for message in recent:
        print(f"  {message['role']}：{message['content']}")
    print("全部仍是 3 条，最近这一读没有把更早的删掉。")
    print("条数 =", len(store.all_messages(SESSION_ID)))
    print()

    print("== 摘要和槽位 ==")
    store.save_summary(SESSION_ID, "顾客要退款，订单号 10086。")
    memory = WorkingMemory(
        intent="退款",
        slots={"order_id": "10086"},
        ticket_id="1",
        task_status="done",
    )
    store.save_working(SESSION_ID, memory)
    print("摘要 =", store.load_summary(SESSION_ID))
    print("工作记忆 =", store.load_working(SESSION_ID))
    print()

    print("== 换一个 SessionStore 对象，还是同一个客户端 ==")
    again = SessionStore(connected.client, ttl_seconds=30)
    loaded = again.load_working(SESSION_ID)
    print("读回的订单号 =", loaded.slots.get("order_id"))
    print("另一个 session 的订单号 =", again.load_working(OTHER_ID).slots.get("order_id"))
    print("新的 Python 对象不是新的记忆。记忆在客户端对面的键上，键按 session_id 分开。")
    print()

    print("== 读一次就续期 ==")
    summary_key = store.key(SESSION_ID, "summary")
    print("现在 TTL =", connected.client.ttl(summary_key))
    time.sleep(1)
    print("等 1 秒 TTL =", connected.client.ttl(summary_key))
    again.load_summary(SESSION_ID)
    print("再读一次 TTL =", connected.client.ttl(summary_key))
    print("第二次应比等完那一次更接近 30。空闲才开始倒计时，说话就会把 30 秒拨满。")
    print()
    connected.client.close()


if __name__ == "__main__":
    main()
