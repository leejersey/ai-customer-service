# -*- coding: utf-8 -*-
"""阶段 5 · 示例 6：按顾客把值得留的事实写进 FAISS，下一句再找回来。

不调用政策模型。有密钥时，多打印一次模型抽出的 JSON；失败不影响规则。
记忆在 stage5_vector_memory/data/memory/demo_reader/。不要提交。

    USE_FAKE_EMBEDDING=1 python stage5_vector_memory/06_long_term_memory.py

导读：stage5_vector_memory/docs/06_memory.md
"""

import stage5_link

stage5_link.enable()

from llm_intent import api_key_ready

from embedder import describe_backend
from memory_store import UserMemory, memory_threshold
from remember import facts_from_llm, facts_from_rules, redact_secrets

TURNS = (
    "我住在杭州，收货喜欢放门口，不要放驿站",
    "上次问耳机保修，客服说是一年",
    "请记住我的手机号13800138000和卡号6222021234567890",
    "今天天气不错",
)

QUERIES = (
    "我住在哪",
    "放门口还是驿站",
    "收货放哪里",
    "我的手机号是多少",
    "以前问过保修吗",
)


def main() -> None:
    print(describe_backend())
    print("阶段 3 的短期记忆：最近几句对话，放 Redis，空闲大约 30 分钟就过期，过期就找不回那几句。")
    print("阶段 5 的长期记忆：偏好、城市、以前的问题和结果。写成向量，存在这位顾客自己的文件夹里。")
    print("下次再运行，只要还是这个顾客编号，就能按意思找回来。这里不用 Redis。")
    print("完整手机号、银行卡号、身份证号不入库。")
    print()

    memory = UserMemory("demo_reader")
    memory.reset()
    print(f"顾客文件夹：{memory.folder}")
    print(f"回忆门槛：{memory_threshold()}")
    print()

    client = None
    model = None
    if api_key_ready():
        from config import create_client, require_settings

        settings = require_settings()
        client = create_client(settings)
        model = settings.model
        print("有密钥。每一句会额外请模型抽一次 JSON。规则的结果仍然会写下来。")
    else:
        print("没有可用的 API 密钥。这一课只用规则决定记什么。")
    print()

    for text in TURNS:
        print(f"顾客：{text}")
        print(f"  抹掉号码之后：{redact_secrets(text)}")
        print(f"  规则留下：{facts_from_rules(text)}")
        if client is not None and model is not None:
            try:
                print(f"  模型留下：{facts_from_llm(client, model, text)}")
            except Exception as error:
                print(f"  模型这一句没有抽成 JSON（{type(error).__name__}），不影响规则。")
        saved = memory.add_text(text)
        if saved:
            print(f"  写入：{saved[0]}")
        else:
            print("  没有写入。要么没有线索，要么只剩不该保存的号码。")
        print()

    exchange = memory.remember_exchange("耳机保修多久", "04_售后保修.md")
    print(f"问答结果也记一条：{exchange}")
    print()
    print("== 换一个对象，模拟下次再打开程序 ==")
    reopened = UserMemory("demo_reader")
    print(f"磁盘上有 {len(reopened.store.records)} 条。新的空列表不会自己带上这些事实，磁盘会。")
    for query in QUERIES:
        print(f"问题：{query}")
        hits = reopened.search(query, top_k=3)
        if not hits:
            print("  （索引是空的）")
            continue
        for hit in hits:
            mark = "达到门槛" if hit.score >= memory_threshold() else "低于门槛"
            print(f"  {hit.score:.4f} {mark} {hit.text}")
        print()
    print("「放门口还是驿站」和记下来的那句有相同的字，所以过线。")
    print("「收货放哪里」换了说法，假向量往往过不了线。真模型更吃意思，假向量更吃用字。")
    print("若召回的句子里出现完整手机号或卡号，就是隐私没挡住。")
    print("长期记忆这一课看完了")


if __name__ == "__main__":
    main()
