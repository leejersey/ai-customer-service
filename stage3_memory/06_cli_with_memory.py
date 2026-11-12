# -*- coding: utf-8 -*-
"""阶段 3 · 示例 6：阶段 2 的客服加上会话记忆。

传入 session_id 后，同一编号在 Redis 里接得上：订单号、没问完的槽位和最近几句还在。
本机没有 Redis 时会改用 fakeredis，屏幕会说明退出后记不住。

    python stage3_memory/06_cli_with_memory.py
    python stage3_memory/06_cli_with_memory.py demo-1

导读：stage3_memory/docs/06_cli.md
"""

import json
import sys

import stage3_link

stage3_link.enable()

from config import create_client, describe_settings, print_api_error, require_settings
from db import ensure_database
from llm_intent import api_key_ready, classify_by_llm
from backend import configured_session_id, configured_ttl, explain, open_client
from bridge import run_turn
from session_flow import record_exchange
from speak import build_model_messages, phrase
from store import SessionStore
from window import copy_messages
from working import WorkingMemory

EXIT_COMMANDS = {"quit", "exit", "q", "退出"}


def choose_session_id(argv: list[str]) -> str:
    """命令行第 2 个词优先。没有的话再看环境变量，最后用 local。"""
    if len(argv) >= 2 and argv[1].strip() != "":
        return argv[1].strip()
    return configured_session_id()


def greet(session_id: str, memory: WorkingMemory, transcript: list[dict], ttl_seconds: int) -> None:
    print(f"会话编号：{session_id}")
    print(f"空闲 {ttl_seconds} 秒后过期。每次发言都会重新计时。")
    if transcript or memory.slots or memory.pending_slot or memory.ticket_id:
        print(f"已恢复对话 {len(transcript)} 条。")
    order_id = memory.slots.get("order_id", "")
    if order_id:
        print(f"记得的订单号：{order_id}")
    if memory.ticket_id:
        print(f"手头的工单：{memory.ticket_id}")
    if memory.pending_slot:
        print(f"上次还在等{memory.pending_slot}。上一句是：{memory.pending_text}")
    print()


def reply_for(user_text: str, outcome: dict, summary: str, transcript: list[dict], client, settings) -> str:
    if client is None or outcome.get("asked") is not None:
        return outcome["reply"]
    fact = outcome["reply"]
    if outcome.get("result") is not None:
        fact = fact + "\n" + json.dumps(outcome["result"], ensure_ascii=False)
    draft = copy_messages(build_model_messages(summary, transcript))
    try:
        return phrase(client, settings.model, draft, user_text, fact)
    except Exception as error:
        print_api_error(error)
        print("这一轮没有改用模型润色。下面仍显示程序自己的句子。")
        return outcome["reply"]


def main() -> None:
    session_id = choose_session_id(sys.argv)
    connected = open_client(prefer_real=True)
    explain(connected)
    print()
    ttl_seconds = configured_ttl()
    store = SessionStore(connected.client, ttl_seconds=ttl_seconds)
    path = ensure_database()
    print(f"工单保存在：{path}")
    print("这一步不会清空已有工单。阶段 2 的示例 1、示例 3、示例 5 会重建数据库。")
    use_model = api_key_ready()
    client = None
    settings = None
    if use_model:
        settings = require_settings()
        describe_settings(settings)
        client = create_client(settings)
    else:
        print("没有可用的 API 密钥。意图用规则，回复是程序写的。工单和会话记忆仍会写。")
    memory = store.load_working(session_id)
    transcript = store.all_messages(session_id)
    summary = store.load_summary(session_id)
    print()
    print("星河数码在线客服（阶段 3：会话记在 Redis）")
    greet(session_id, memory, transcript, ttl_seconds)
    print("可以试这些句子：")
    print("  我要退款")
    print("  订单号 10086")
    print("退出后再用同一个会话编号启动，应能沿用这个订单号。")
    print("输入 退出 或 quit 结束。退款只会写成工单，不会打款。")
    print()
    while True:
        try:
            user_text = input("你：").strip()
        except EOFError:
            print("\n输入结束，再见。")
            break
        except KeyboardInterrupt:
            print("\n已退出。")
            break
        if user_text.lower() in EXIT_COMMANDS:
            print("小星：感谢咨询，再见。")
            break
        if user_text == "":
            print("请输入内容。想结束时，整行输入：退出")
            continue
        classification = None
        if use_model and not memory.pending_slot:
            try:
                classification = classify_by_llm(client, settings.model, user_text)
            except Exception as error:
                print_api_error(error)
                print("这一句改用规则。")
                classification = None
        outcome = run_turn(user_text, memory, classification)
        reply = reply_for(user_text, outcome, summary, transcript, client, settings)
        folded = record_exchange(
            store,
            session_id,
            memory,
            transcript,
            summary,
            user_text,
            reply,
            client=client if use_model else None,
            model=settings.model if use_model else None,
        )
        transcript = folded["messages"]
        summary = folded["summary"]
        if folded["source"] != "none":
            print(f"（更早的对话已收成摘要，来源={folded['source']}）")
            if folded["note"]:
                print(folded["note"])
        print(f"（意图={outcome['intent']} 来源={outcome['source']}）")
        print(f"小星：{reply}")
        print()
    connected.client.close()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n已退出。")
