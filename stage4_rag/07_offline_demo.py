# -*- coding: utf-8 -*-
"""阶段 4 · 示例 7：不调用模型，也不联网。

假模型只复述检索到的资料。工单写进本目录的 offline_demo.db，不动 shop.db。

    python stage4_rag/07_offline_demo.py

导读：stage4_rag/docs/07_offline.md
"""

from pathlib import Path

import stage4_link

stage4_link.enable()

import db
import service
from answering import answer_question, echo_retrieved
from chunking import CHUNK_OVERLAP, CHUNK_SIZE, split_by_length
from documents import TEXT_SUFFIXES, load_documents
from prompting import NOT_FOUND, SCORE_THRESHOLD, build_messages
from retrieve import build_index, cosine
from routing import choose_path

# 这些问句的原词写在对应文件里。换一种说法（比如把「七天」说成别的词）分数会掉，那是二字词的局限。
COVERED = (
    ("退货政策是几天", "01_退换货政策.md", "七天"),
    ("不满99元运费是多少", "02_运费与配送.md", "运费 8 元"),
    ("100积分抵多少元", "03_会员积分.md", "100 积分抵 1 元"),
    ("耳机保修多久", "04_售后保修.md", "365"),
    ("支持货到付款吗", "05_支付方式.md", "不支持货到付款"),
    ("可以开纸质发票吗", "06_发票.md", "不提供纸质发票"),
    ("没有订单号能不能凭姓名查询", "07_常见问题.md", "不能凭姓名查询"),
    ("人工客服营业到几点", "08_营业时间.txt", "21:00"),
    ("星河耳机卖多少钱", "07_常见问题.md", "不写售价"),
)

MISSING = (
    "你们今年招实习生吗",
    "今天月球冷不冷",
)


def check_load_and_chunk() -> None:
    print("== 加载和切块 ==")
    documents = load_documents()
    assert len(documents) == 8
    for document in documents:
        suffix = Path(document.source).suffix.lower()
        assert suffix in TEXT_SUFFIXES
        assert document.title != ""
        assert len(document.text) > 0
    parts = split_by_length("一二三四五六七八九十", size=6, overlap=2)
    assert parts == ["一二三四五六", "五六七八九十"]
    try:
        split_by_length("一二三四五", size=4, overlap=4)
    except ValueError:
        print("重叠不小于块长时，切块会拒绝。")
    else:
        raise AssertionError("重叠等于块长必须拒绝")
    print(f"8 份说明都读到了。示例句的重叠是「五六」。块长 {CHUNK_SIZE}，重叠 {CHUNK_OVERLAP}。")
    print()


def check_overlap_in_knowledge(index) -> None:
    print("== 知识库里的长段重叠 ==")
    found = False
    chunks = index.chunks
    for earlier, later in zip(chunks, chunks[1:]):
        if earlier.source != later.source:
            continue
        if len(earlier.text) != CHUNK_SIZE:
            continue
        overlap = earlier.text[-CHUNK_OVERLAP:]
        if later.text.startswith(overlap):
            found = True
            print(f"{earlier.source} 第{earlier.index}块末尾和第{later.index}块开头都是：")
            print(overlap)
            break
    assert found
    print()


def check_retrieval(index) -> None:
    print("== 检索和假模型 ==")
    identical = cosine({"天": 1.0, "数": 1.0}, {"天": 1.0, "数": 1.0})
    assert identical > 0.99
    unrelated = cosine({"退货": 1.0}, {"发票": 1.0})
    assert unrelated == 0.0
    print("方向相同的向量余弦接近 1，没有公共词时是 0。")

    for question, source, phrase in COVERED:
        result = answer_question(question, index)
        assert result["best_score"] >= SCORE_THRESHOLD
        assert result["hits"][0].source == source
        assert result["messages"] is not None
        echoed = echo_retrieved(result["messages"])
        assert echoed == result["answer"]
        assert "没有调用模型" in result["answer"]
        assert phrase in result["answer"]
        assert source in result["answer"]
        scores = [hit.score for hit in result["hits"]]
        assert scores == sorted(scores, reverse=True)
        print(f"{question} → {source}  {result['best_score']:.4f}  含「{phrase}」")

    watery = index.search("进液还保修吗", top_k=3)
    joined = "\n".join(hit.text for hit in watery)
    assert any(hit.source == "04_售后保修.md" for hit in watery)
    assert "进液" in joined
    assert watery[0].score >= watery[1].score
    print("「进液还保修吗」的前几段里能看见进液。保修两个字也会让期限段排得很靠前。")

    for question in MISSING:
        result = answer_question(question, index)
        assert result["answer"] == NOT_FOUND
        assert result["messages"] is None
        assert result["best_score"] < SCORE_THRESHOLD
        print(f"{question} → {NOT_FOUND}  （{result['best_score']:.4f}）")
    print()


def check_prompt_labels(index) -> None:
    print("== 来源标签 ==")
    hits = index.search("可以开纸质发票吗", top_k=2)
    messages = build_messages("可以开纸质发票吗", hits)
    assert messages[0]["role"] == "system"
    assert NOT_FOUND in messages[0]["content"]
    user = messages[1]["content"]
    assert "[来源：06_发票.md" in user
    assert "顾客的问题：可以开纸质发票吗" in user
    print("system 要求没写到就说那八个字。user 里带有文件名。")
    print()


def check_routing_and_tools() -> None:
    print("== 分流和阶段 2 工具 ==")
    assert choose_path("退货政策是几天") == "rag"
    assert choose_path("发票怎么开") == "rag"
    assert choose_path("我要退款") == "tools"
    assert choose_path("我要退货") == "tools"
    assert choose_path("订单号 10086") == "tools"
    assert choose_path("投诉包装破了") == "tools"
    assert choose_path("转人工") == "tools"
    assert choose_path("查询工单 1") == "tools"
    print("问政策走 rag，要办理和查订单走 tools。")

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
    print("退款先追问，补上 10086 后写成工单。查订单读到的是种子数据里的耳机。")
    print(f"离线库：{demo_path}")
    print("没有改动 shop.db。")
    print()


def main() -> None:
    print("离线演示不读取 API 密钥，也不连接网络。")
    print("假模型把检索到的原文复述出来。分数低于阈值时，回答是固定的那一句。")
    print()
    check_load_and_chunk()
    index = build_index()
    check_overlap_in_knowledge(index)
    check_retrieval(index)
    check_prompt_labels(index)
    check_routing_and_tools()
    print("离线演示通过")


if __name__ == "__main__":
    main()
