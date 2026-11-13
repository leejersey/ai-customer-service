# -*- coding: utf-8 -*-
"""阶段 5 · 示例 8：不调用模型，不下载嵌入，也不联网。

假向量加上假的复述。工单写进本目录 data/offline_demo.db，不动 shop.db。
长期记忆只用 offline_demo 这个编号，不会清掉你在示例 7 里用 local 记下的事实。

    python stage5_vector_memory/08_offline_demo.py

导读：stage5_vector_memory/docs/08_offline.md
"""

import json
import os

# 必须写在导入 embedder 之前。否则第一次嵌入可能已经去加载真模型。
os.environ["USE_FAKE_EMBEDDING"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

from pathlib import Path

import stage5_link

stage5_link.enable()

import numpy as np

import db
import service
from prompting import NOT_FOUND, SCORE_THRESHOLD
from retrieve import build_index
from retrieve import cosine as keyword_cosine
from retrieve import term_counts
from routing import choose_path

from ask import answer_question, vector_threshold
from embedder import FAKE_DIM, backend_name, embedder_id, hashed_bigram_matrix
from index_store import FaissStore, load_store, remove_saved_index
from knowledge_index import build_knowledge_store, search_knowledge
from memory_store import UserMemory
from remember import facts_from_rules, redact_secrets
from vectors import as_float32_matrix, cosine

COVERED = (
    ("退货政策是几天", "01_退换货政策.md", "七天"),
    ("不满99元运费是多少", "02_运费与配送.md", "运费 8 元"),
    ("耳机保修多久", "04_售后保修.md", "365"),
    ("可以开纸质发票吗", "06_发票.md", "不提供纸质发票"),
    ("人工客服营业到几点", "08_营业时间.txt", "21:00"),
)

MISSING = "今天月球冷不冷"
SYNONYM = "我想退钱"


def keyword_score(left: str, right: str) -> float:
    left_counts = {term: float(count) for term, count in term_counts(left).items()}
    right_counts = {term: float(count) for term, count in term_counts(right).items()}
    return keyword_cosine(left_counts, right_counts)


def check_vectors() -> None:
    print("== 假向量 ==")
    assert backend_name() == "fake"
    assert embedder_id() == "hashed-bigram"
    matrix = hashed_bigram_matrix(["退款", "退钱", "未拆封可以七天无理由退货"])
    assert matrix.shape == (3, FAKE_DIM)
    assert matrix.dtype == np.float32
    length = float(np.linalg.norm(matrix[0]))
    assert abs(length - 1.0) < 1e-5
    assert cosine(matrix[0], matrix[0]) > 0.99
    assert abs(cosine(matrix[0], matrix[1])) < 0.01
    assert keyword_score("退款", "退钱") == 0.0
    assert keyword_score("退款", "退款") > 0.99
    narrow = as_float32_matrix([1.0, 2.0])
    assert narrow.dtype == np.float32
    assert narrow.shape == (1, 2)
    print("「退款」和自己的余弦接近 1。「退款」和「退钱」在假向量和二字词里都接近 0。")
    print(f"维度 {FAKE_DIM}，类型 float32，第一行长度 {length:.4f}。")
    print()


def check_faiss_roundtrip() -> None:
    print("== FAISS 编号和存盘 ==")
    sentences = ["未拆封七天可以退货", "运费满99元包邮", "纸质发票不提供"]
    vectors = hashed_bigram_matrix(sentences)
    store = FaissStore(FAKE_DIM, "fake", "hashed-bigram")
    records = []
    for index, sentence in enumerate(sentences, start=1):
        records.append(
            {
                "text": sentence,
                "source": "demo",
                "title": "demo",
                "index": index,
                "kind": "demo",
            }
        )
    store.add(vectors, records)
    hits = store.search(hashed_bigram_matrix(["可以退货吗"]), top_k=3)
    assert hits[0].text == "未拆封七天可以退货"
    assert hits[0].row_id == 0
    assert hits[0].score >= hits[1].score
    folder = Path(__file__).resolve().parent / "data" / "offline_faiss"
    remove_saved_index(folder)
    store.save(folder)
    loaded = load_store(folder, expect_dim=FAKE_DIM, expect_model="hashed-bigram")
    again = loaded.search(hashed_bigram_matrix(["可以退货吗"]), top_k=1)
    assert again[0].text == hits[0].text
    try:
        load_store(folder, expect_dim=FAKE_DIM + 1, expect_model="hashed-bigram")
    except ValueError as error:
        assert "维度" in str(error)
    else:
        raise AssertionError("维度变了必须拒绝")
    meta_path = folder / "meta.json"
    payload_text = meta_path.read_text(encoding="utf-8")
    payload = json.loads(payload_text)
    payload["records"].append({"text": "多出来的一条"})
    meta_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    try:
        load_store(folder)
    except ValueError as error:
        assert "对不上" in str(error)
    else:
        raise AssertionError("元数据和索引条数不一致必须拒绝")
    # 演示完把文件改回成对的那一版，避免下次误以为磁盘上的索引是坏的。
    meta_path.write_text(payload_text, encoding="utf-8")
    print("第一名的 id 是 0，对应「未拆封七天可以退货」。读回后仍是这一句。")
    print("维度不对、元数据多了一条，都会被拒绝。")
    print()


def check_knowledge(store) -> None:
    print("== 知识库：原词能对上，近义词在假向量里对不上 ==")
    assert vector_threshold() == 0.22
    tfidf = build_index()
    assert len(tfidf.chunks) == len(store.records)
    for question, source, phrase in COVERED:
        result = answer_question(question, store, memory=None, remember=False)
        assert result["best_score"] >= vector_threshold()
        assert result["hits"][0].source == source
        assert result["source"] == "echo"
        assert "没有调用模型" in result["answer"]
        assert phrase in result["answer"]
        assert source in result["answer"]
        word_top = tfidf.search(question, top_k=1)[0]
        assert word_top.source == source
        assert word_top.score >= SCORE_THRESHOLD
        print(f"{question} → {source}  向量 {result['best_score']:.4f}")

    synonym = answer_question(SYNONYM, store, memory=None, remember=False)
    word_synonym = tfidf.search(SYNONYM, top_k=1)[0]
    assert synonym["best_score"] < vector_threshold()
    assert word_synonym.score < SCORE_THRESHOLD
    assert synonym["answer"] == NOT_FOUND
    print(f"{SYNONYM} → 假向量 {synonym['best_score']:.4f}，二字词 {word_synonym.score:.4f}，都低于各自的门。")
    print("知识库写的是退款、退货。假向量不会因为「退钱」意思接近就过线。")

    missing = answer_question(MISSING, store, memory=None, remember=False)
    assert missing["answer"] == NOT_FOUND
    assert missing["best_score"] < vector_threshold()
    print(f"{MISSING} → {NOT_FOUND}  （{missing['best_score']:.4f}）")
    print()


def check_memory() -> None:
    print("== 长期记忆 ==")
    memory = UserMemory("offline_demo")
    memory.reset()
    saved = memory.add_text("我住在杭州，收货喜欢放门口，不要放驿站")
    assert saved
    assert "杭州" in saved[0]
    phone = "请记住我的手机号13800138000和卡号6222021234567890"
    redacted = redact_secrets(phone)
    assert "13800138000" not in redacted
    assert "6222021234567890" not in redacted
    phone_saved = memory.add_text(phone)
    assert phone_saved
    assert "13800138000" not in phone_saved[0]
    assert "6222021234567890" not in phone_saved[0]
    assert facts_from_rules("今天天气不错") == []
    weather = memory.add_text("今天天气不错")
    assert weather == []
    exchange = memory.remember_exchange("耳机保修多久", "04_售后保修.md")
    assert exchange is not None
    assert "04_售后保修.md" in exchange
    assert "365" not in exchange
    assert facts_from_rules("我住在哪") == []

    fresh_recent = []
    reopened = UserMemory("offline_demo")
    assert fresh_recent == []
    assert len(reopened.store.records) >= 3
    recalled = reopened.recall("我住在哪")
    assert recalled
    assert "杭州" in recalled[0].text
    place = reopened.recall("放门口还是驿站")
    assert place
    assert "门口" in place[0].text or "驿站" in place[0].text
    missed = reopened.recall("收货放哪里")
    assert missed == []
    number_hits = reopened.search("我的手机号是多少", top_k=3)
    for hit in number_hits:
        assert "13800138000" not in hit.text
        assert "6222021234567890" not in hit.text
    print("新的列表是空的。重新打开同一位顾客，仍能召回杭州。")
    print("手机号和卡号只以省略号的形式存在。")
    print(f"记忆文件夹：{memory.folder}")
    print()


def check_routing_and_tools(store) -> None:
    print("== 分流和阶段 2 工具 ==")
    assert choose_path("退货政策是几天") == "rag"
    assert choose_path("我想退钱") == "tools"
    assert choose_path("我要退款") == "tools"
    assert choose_path("我住在杭州") == "rag"
    assert choose_path("订单号 10086") == "tools"
    print("问政策走检索。说「我要退款」或「我想退钱」走工具，避免只念政策不建单。")

    demo_path = Path(__file__).resolve().parent / "data" / "offline_demo.db"
    db.use_database(demo_path)
    db.reset_database()
    session = {"pending": None}
    first = service.handle_turn("我要退款", session)
    assert first["asked"] == "order_id"
    assert db.count_tickets() == 0
    second = service.handle_turn("订单号 10086", session)
    assert second["tool"] == "create_ticket"
    assert second["result"]["ticket"]["order_id"] == "10086"
    assert db.count_tickets() == 1
    looked = service.handle_turn("查订单 10086", {"pending": None})
    assert "星河蓝牙耳机" in looked["reply"]
    result = answer_question("退货政策是几天", store, memory=None, remember=False)
    assert "七天" in result["answer"]
    noted = answer_question(
        "请记住我的手机号13800138000",
        store,
        memory=UserMemory("offline_demo"),
        remember=True,
    )
    assert "13800138000" not in noted["answer"]
    assert "已省略" in noted["answer"]
    print("退款先追问，补上 10086 后写成工单。政策题仍从知识库复述出「七天」。")
    print(f"离线库：{demo_path}")
    print("没有改动 shop.db。")
    print()


def main() -> None:
    print("离线演示不读取 API 密钥，不下载嵌入模型，也不连接网络。")
    print("USE_FAKE_EMBEDDING=1 已在本文件开头写上。")
    print()
    check_vectors()
    check_faiss_roundtrip()
    store = build_knowledge_store()
    check_knowledge(store)
    check_memory()
    check_routing_and_tools(store)
    print("离线演示通过")


if __name__ == "__main__":
    main()
