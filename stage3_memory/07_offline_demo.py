# -*- coding: utf-8 -*-
"""阶段 3 · 示例 7：不调用模型，也不连接本机 Redis。

fakeredis 提供一台假的服务器，两个客户端共用它，用来模拟重新连上。
内存实现再跑一遍过期和槽位，证明 Redis 不可用时练习仍能通过。

    python stage3_memory/07_offline_demo.py

导读：stage3_memory/docs/07_offline.md
"""

import json
import time
from pathlib import Path

import stage3_link

stage3_link.enable()

import db
from backend import InMemoryRedis, client_on_fake_server, open_fake_server
from bridge import run_turn
from session_flow import record_exchange
from store import SessionStore
from summary import compress_messages, fake_summary
from window import truncate_by_chars, truncate_by_turns
from working import WorkingMemory


def contents(messages: list[dict]) -> str:
    parts = []
    for message in messages:
        content = message.get("content")
        if content is None:
            continue
        parts.append(str(content))
    return "\n".join(parts)


def check_working_memory() -> None:
    print("== 工作记忆和历史 ==")
    memory = WorkingMemory(intent="退款", slots={"order_id": "10086"}, ticket_id="1")
    messages = [
        {"role": "user", "content": "我要退款"},
        {"role": "assistant", "content": "已记下"},
    ]
    text = json.dumps(memory.to_dict(), ensure_ascii=False)
    restored = WorkingMemory.from_dict(json.loads(text))
    assert restored.intent == "退款"
    assert restored.slots["order_id"] == "10086"
    assert "10086" in text
    messages.clear()
    assert restored.slots["order_id"] == "10086"
    assert messages == []
    print("历史清空后，订单号还在工作记忆里。")
    print()


def check_truncate() -> None:
    print("== 截断 ==")
    messages = [
        {"role": "system", "content": "你是客服"},
        {"role": "user", "content": "第一句很旧"},
        {"role": "assistant", "content": "旧的回复"},
        {"role": "user", "content": "第二句"},
        {"role": "assistant", "content": "第二回复"},
        {"role": "user", "content": "第三句要留下"},
        {"role": "assistant", "content": "第三回复"},
    ]
    kept = truncate_by_turns(messages, max_turns=1)
    text = contents(kept)
    assert kept[0]["role"] == "system"
    assert kept[0]["content"] == "你是客服"
    assert "第一句很旧" not in text
    assert "第三句要留下" in text
    assert len(messages) == 7
    try:
        truncate_by_turns(messages, 0)
    except ValueError:
        print("0 轮被拒绝。")
    else:
        raise AssertionError("0 轮必须拒绝")

    short = [
        {"role": "system", "content": "岗位"},
        {"role": "user", "content": "这是一段比较旧的话要被丢掉"},
        {"role": "assistant", "content": "好的"},
        {"role": "user", "content": "留"},
        {"role": "assistant", "content": "在"},
    ]
    clipped = truncate_by_chars(short, max_chars=4)
    clipped_text = contents(clipped)
    assert clipped[0]["content"] == "岗位"
    assert "留" in clipped_text
    assert "在" in clipped_text
    assert "比较旧" not in clipped_text
    tiny = truncate_by_chars(short, max_chars=2)
    assert "留" in contents(tiny)
    assert "比较旧" not in contents(tiny)
    print("按轮数和按字符数都留下了 system，并丢掉了更旧的一轮。")
    print()


def check_summary() -> None:
    print("== 假摘要 ==")
    messages = [
        {"role": "system", "content": "你是星河数码的客服。"},
        {"role": "user", "content": "我要退款"},
        {"role": "assistant", "content": "请告诉我订单号。"},
        {"role": "user", "content": "紫色包装破了，订单号 10086"},
        {"role": "assistant", "content": "已记下退款工单 1。"},
        {"role": "user", "content": "还在吗"},
        {"role": "assistant", "content": "在的"},
    ]
    same = compress_messages(messages, keep_turns=2, threshold_turns=4)
    assert same["source"] == "none"
    assert len(same["messages"]) == len(messages)
    packed = compress_messages(messages, keep_turns=1, threshold_turns=2)
    assert packed["source"] == "fake"
    assert "紫色包装" in packed["summary"]
    assert "10086" in packed["summary"]
    body = contents(packed["messages"])
    assert body.startswith("你是星河数码的客服。")
    assert "此前对话摘要：" in body
    assert "还在吗" in body
    assert "紫色包装" not in body.replace(packed["summary"], "")
    assert fake_summary([]) == "没有更早的对话。"
    print("旧句子进了摘要，最近一轮还在列表里。")
    print()


def check_shared_server() -> None:
    print("== fakeredis 上的会话 ==")
    server, first_client = open_fake_server()
    store = SessionStore(first_client, ttl_seconds=30)
    session_id = "offline-demo"
    store.clear_session(session_id)
    store.append_message(session_id, {"role": "user", "content": "订单号 10086"})
    store.append_message(session_id, {"role": "assistant", "content": "记下了"})
    store.append_message(session_id, {"role": "user", "content": "谢谢"})
    recent = store.recent_messages(session_id, 2)
    assert [item["content"] for item in recent] == ["记下了", "谢谢"]
    assert "10086" in store.all_messages(session_id)[0]["content"]
    memory = WorkingMemory(
        intent="退款",
        slots={"order_id": "10086"},
        pending_slot="order_id",
        pending_text="我要退款",
        ticket_id="1",
        task_status="waiting",
    )
    store.save_working(session_id, memory)
    store.save_summary(session_id, "顾客要退订单 10086")

    second = SessionStore(client_on_fake_server(server), ttl_seconds=30)
    loaded = second.load_working(session_id)
    assert loaded.slots["order_id"] == "10086"
    assert loaded.pending_text == "我要退款"
    assert loaded.ticket_id == "1"
    assert second.load_summary(session_id) == "顾客要退订单 10086"
    assert second.load_working("nobody").intent is None
    print("新的客户端连上同一台假服务器，订单号还在。另一个 session 是空的。")

    summary_key = store.key(session_id, "summary")
    time.sleep(2)
    before = first_client.ttl(summary_key)
    second.load_summary(session_id)
    after = first_client.ttl(summary_key)
    assert before <= 28
    assert after >= 29
    print(f"续期前 TTL={before}，读一次之后 TTL={after}。")

    short = SessionStore(client_on_fake_server(server), ttl_seconds=1)
    short.save_summary("expire-me", "一会儿就没了")
    time.sleep(1.3)
    assert short.load_summary("expire-me") == ""
    print("1 秒 TTL 到期后，摘要读回来是空字符串。")
    print()


def check_memory_backend() -> None:
    print("== 内存替身 ==")
    client = InMemoryRedis()
    client.set("stage3:demo:order", "10086", ex=30)
    assert client.get("stage3:demo:order") == "10086"
    assert client.get("missing") is None
    assert client.ttl("stage3:demo:order") > 0
    client.rpush("stage3:demo:turns", "甲", "乙", "丙")
    client.ltrim("stage3:demo:turns", -2, -1)
    assert client.lrange("stage3:demo:turns", 0, -1) == ["乙", "丙"]
    client.hset("stage3:demo:slots", mapping={"order_id": "10086"})
    assert client.hget("stage3:demo:slots", "order_id") == "10086"
    store = SessionStore(client, ttl_seconds=30)
    memory = WorkingMemory(intent="退款", slots={"order_id": "10086"}, task_status="done")
    store.save_working("local", memory)
    other = SessionStore(client, ttl_seconds=30)
    assert other.load_working("local").slots["order_id"] == "10086"
    fresh = InMemoryRedis()
    assert SessionStore(fresh, ttl_seconds=30).load_working("local").slots == {}
    client.set("gone", "x", ex=1)
    time.sleep(1.2)
    assert client.get("gone") is None
    print("同一份内存客户端能读回槽位。新的一份是空的，所以它不能代替重启后的 Redis。")
    print()


def check_stage2_resume() -> None:
    print("== 接上阶段 2，重启后沿用订单号 ==")
    demo_path = Path(__file__).resolve().parent / "data" / "offline_demo.db"
    db.use_database(demo_path)
    db.reset_database()
    server, client = open_fake_server()
    store = SessionStore(client, ttl_seconds=60)
    session_id = "shopper"
    memory = WorkingMemory()
    transcript: list[dict] = []
    summary = ""

    first = run_turn("我要退款", memory)
    assert first["asked"] == "order_id"
    assert memory.pending_text == "我要退款"
    record_exchange(
        store,
        session_id,
        memory,
        transcript,
        summary,
        "我要退款",
        first["reply"],
        keep_turns=2,
        threshold_turns=3,
    )
    assert db.count_tickets() == 0

    resumed = SessionStore(client_on_fake_server(server), ttl_seconds=60)
    memory = resumed.load_working(session_id)
    transcript = resumed.all_messages(session_id)
    summary = resumed.load_summary(session_id)
    assert memory.pending_slot == "order_id"
    second = run_turn("订单号 10086", memory)
    assert second["tool"] == "create_ticket"
    assert second["result"]["ticket"]["order_id"] == "10086"
    assert second["result"]["ticket"]["description"] == "我要退款"
    record_exchange(
        resumed,
        session_id,
        memory,
        transcript,
        summary,
        "订单号 10086",
        second["reply"],
        keep_turns=2,
        threshold_turns=3,
    )
    assert memory.slots["order_id"] == "10086"
    assert db.count_tickets() == 1

    restarted = SessionStore(client_on_fake_server(server), ttl_seconds=60)
    memory = restarted.load_working(session_id)
    assert memory.slots["order_id"] == "10086"
    third = run_turn("耳机坏了，我要退款", memory)
    assert third["source"] == "memory"
    assert third["result"]["ok"] is True
    assert third["result"]["ticket"]["order_id"] == "10086"
    assert "10086" in third["reply"]
    record_exchange(
        restarted,
        session_id,
        memory,
        restarted.all_messages(session_id),
        restarted.load_summary(session_id),
        "耳机坏了，我要退款",
        third["reply"],
        keep_turns=1,
        threshold_turns=2,
    )
    assert db.count_tickets() == 2
    saved = restarted.load_summary(session_id)
    assert saved != ""
    assert "10086" in saved or "退款" in saved
    recent = restarted.recent_messages(session_id, 2)
    assert recent[-1]["role"] == "assistant"
    print("同一 session 在新的客户端上沿用了订单号，并写成了第二张工单。")
    print(f"离线库：{demo_path}")
    print("没有改动 shop.db。")
    print()


def main() -> None:
    print("离线演示不读取 API 密钥，也不连接本机 Redis。")
    print("fakeredis 活在这个进程里。两个客户端共用一台 FakeServer，才像重新连上。")
    print("真正的重启要另开进程，那需要一台还在跑的 Redis。原因见屏幕后半和导读。")
    print()
    check_working_memory()
    check_truncate()
    check_summary()
    check_shared_server()
    check_memory_backend()
    check_stage2_resume()
    print("离线演示通过")


if __name__ == "__main__":
    main()
