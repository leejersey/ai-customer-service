# -*- coding: utf-8 -*-
"""阶段 5 · 示例 7：政策走 FAISS，订单和工单走阶段 2，长期记忆写在磁盘上。

这一次进程里的最近几句只放在列表里，退出就没了。那是为了读得懂。
阶段 3 的 Redis 能在进程外面再留大约 30 分钟，这里不把 Redis 再讲一遍。
没有密钥时，政策题复述资料。退款只记工单，不会打款。

    USE_FAKE_EMBEDDING=1 python stage5_vector_memory/07_cli_with_vector.py

导读：stage5_vector_memory/docs/07_cli.md
"""

import os

import stage5_link

stage5_link.enable()

import service
from config import create_client, describe_settings, print_api_error, require_settings
from llm_intent import api_key_ready
from prompting import NOT_FOUND
from routing import choose_path

import db
from ask import answer_question, vector_threshold
from embedder import backend_name, describe_backend
from knowledge_index import build_knowledge_store
from memory_store import UserMemory, safe_user_id

EXIT_COMMANDS = {"quit", "exit", "q", "退出"}


def current_user_id() -> str:
    raw = os.environ.get("STAGE5_USER_ID", "").strip()
    if raw == "":
        return "local"
    return safe_user_id(raw)


def trim_recent(recent: list) -> None:
    """只留最近 6 条。这是这一次进程里的短期对话，不是长期记忆。"""
    if len(recent) > 6:
        del recent[:-6]


def main() -> None:
    user_id = current_user_id()
    memory = UserMemory(user_id)
    store = build_knowledge_store()
    path = db.ensure_database()
    print(describe_backend())
    print(f"工单保存在：{path}")
    print(f"长期记忆：{memory.folder}  已有 {len(memory.store.records)} 条")
    print(f"向量阈值：{vector_threshold()}  后端：{backend_name()}  知识库 {len(store.records)} 条")
    print("问政策不会写工单。说「我要退款」才会走阶段 2 的工具。")
    print("短期对话只留在这次运行的列表里，退出就没了。阶段 3 的 Redis 能再留大约 30 分钟。")
    print("长期记忆写在磁盘上。手机号和卡号不会原样保存。")
    client = None
    model = None
    if api_key_ready():
        settings = require_settings()
        describe_settings(settings)
        client = create_client(settings)
        model = settings.model
        print("政策问题会调用模型，并且只能根据检索到的资料回答。")
    else:
        print("没有可用的 API 密钥。政策问题会复述资料原文，不联网。")
    print()
    print("星河数码在线客服（阶段 5：向量检索和长期记忆）")
    print("可以试这些句子：")
    print("  退货政策是几天")
    print("  退钱一般是几天")
    print("  我住在杭州，收货喜欢放门口")
    print("  我住在哪")
    print("  我要退款")
    print("  订单号 10086")
    print("输入 退出 或 quit 结束。")
    print()
    session = {"pending": None}
    recent = []
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
        path_name = choose_path(user_text)
        if path_name == "tools":
            outcome = service.handle_turn(user_text, session)
            saved = memory.add_text(user_text, client=client, model=model)
            print(f"路径：阶段 2 工具    意图：{outcome['intent']}")
            if saved:
                print(f"长期记忆记下了：{saved[0]}")
            print(f"小星：{outcome['reply']}")
            recent.append({"role": "顾客", "content": user_text})
            recent.append({"role": "小星", "content": outcome["reply"]})
            trim_recent(recent)
            continue
        try:
            result = answer_question(
                user_text,
                store,
                memory=memory,
                client=client,
                model=model,
                recent=recent,
            )
        except Exception as error:
            print_api_error(error)
            print("这一轮没有用模型。")
            result = answer_question(
                user_text,
                store,
                memory=memory,
                recent=recent,
            )
        print("路径：向量检索")
        for hit in result["hits"]:
            mark = "达到阈值" if hit.score >= vector_threshold() else "低于阈值"
            print(f"  {hit.score:.4f} {mark} {hit.source} 第{hit.index}段")
        if result["memories"]:
            print("长期记忆召回：")
            for item in result["memories"]:
                print(f"  {item.score:.4f}  {item.text}")
        if result["saved"]:
            print(f"长期记忆记下了：{result['saved'][0]}")
        if result["answer"] == NOT_FOUND:
            print("小星：" + NOT_FOUND)
        else:
            print(f"小星：{result['answer']}")
        recent.append({"role": "顾客", "content": user_text})
        recent.append({"role": "小星", "content": result["answer"]})
        trim_recent(recent)


if __name__ == "__main__":
    main()
