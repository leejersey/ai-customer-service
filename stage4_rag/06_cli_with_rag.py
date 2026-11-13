# -*- coding: utf-8 -*-
"""阶段 4 · 示例 6：政策走检索，订单和工单仍走阶段 2。

没有密钥时，检索到的资料会被原样复述，方便看见召回了哪一段。
工单回复始终由程序写成句子。退款只记工单，不会打款。

    python stage4_rag/06_cli_with_rag.py

导读：stage4_rag/docs/06_cli.md
"""

import stage4_link

stage4_link.enable()

from answering import answer_question
from config import create_client, describe_settings, print_api_error, require_settings
from llm_intent import api_key_ready
from prompting import SCORE_THRESHOLD
from retrieve import build_index
from routing import choose_path
import db
import service

EXIT_COMMANDS = {"quit", "exit", "q", "退出"}


def reply_with_rag(user_text: str, index, client, model: str | None) -> str:
    """够分才生成。模型失败时改复述资料，不改口编一条政策。"""
    if client is None or model is None:
        result = answer_question(user_text, index)
        return result["answer"]
    try:
        result = answer_question(user_text, index, client=client, model=model)
    except Exception as error:
        print_api_error(error)
        print("这一轮没有用模型，改为复述检索到的资料。")
        result = answer_question(user_text, index)
    return result["answer"]


def main() -> None:
    index = build_index()
    path = db.ensure_database()
    print(f"工单保存在：{path}")
    print("问政策不会写工单。说「我要退款」才会走阶段 2 的工具。")
    print(f"检索阈值：{SCORE_THRESHOLD}。索引 {len(index.chunks)} 块，启动时建好，不每问一次重读文件。")
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
    print("星河数码在线客服（阶段 4：政策先检索）")
    print("可以试这些句子：")
    print("  退货政策是几天")
    print("  耳机保修多久")
    print("  我要退款")
    print("  订单号 10086")
    print("  你们今年招实习生吗")
    print("输入 退出 或 quit 结束。")
    print()
    session = {"pending": None}
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
            print(f"路径：阶段 2 工具    意图：{outcome['intent']}")
            print(f"小星：{outcome['reply']}")
            continue
        hits = index.search(user_text, top_k=3)
        print("路径：检索知识库")
        for hit in hits:
            print(f"  {hit.score:.4f}  {hit.source} 第{hit.index}段")
        answer = reply_with_rag(user_text, index, client, model)
        print(f"小星：{answer}")


if __name__ == "__main__":
    main()
