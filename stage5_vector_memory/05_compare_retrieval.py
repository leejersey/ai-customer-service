# -*- coding: utf-8 -*-
"""阶段 5 · 示例 5：同一批知识库，二字词和 FAISS 各查一次。

切块仍用阶段 4。没有密钥。嵌入用当前后端：假向量或本机模型。

    USE_FAKE_EMBEDDING=1 python stage5_vector_memory/05_compare_retrieval.py

导读：stage5_vector_memory/docs/05_compare.md
"""

import stage5_link

stage5_link.enable()

from prompting import SCORE_THRESHOLD
from retrieve import build_index

from ask import vector_threshold
from embedder import backend_name, describe_backend
from knowledge_index import build_knowledge_store, search_knowledge

# 前三句用了资料里的原词。后两句换了说法。最后一句知识库没写。
QUESTIONS = (
    "退货政策是几天",
    "不满99元运费是多少",
    "耳机保修多久",
    "我想退钱",
    "退钱一般是几天",
    "进水了还保修吗",
    "耳机进水了还能不能修",
    "今天月球冷不冷",
)


def main() -> None:
    print(describe_backend())
    tfidf = build_index()
    store = build_knowledge_store()
    print(f"阶段 4 索引 {len(tfidf.chunks)} 块。向量索引 {len(store.records)} 条。两边块数应相同。")
    print(f"二字词阈值 {SCORE_THRESHOLD}。向量阈值 {vector_threshold()}（后端 {backend_name()}）。")
    print("两道门不能互相借用。0.15 不是向量的及格线。")
    print()
    for question in QUESTIONS:
        word_hits = tfidf.search(question, top_k=3)
        vector_hits = search_knowledge(store, question, top_k=3)
        print(f"问题：{question}")
        print("  二字词 TF-IDF")
        for rank, hit in enumerate(word_hits, start=1):
            mark = "达到阈值" if hit.score >= SCORE_THRESHOLD else "低于阈值"
            print(f"    {rank}. {hit.score:.4f} {mark} {hit.source} 第{hit.index}段")
        print("  向量检索")
        for rank, hit in enumerate(vector_hits, start=1):
            mark = "达到阈值" if hit.score >= vector_threshold() else "低于阈值"
            print(f"    {rank}. {hit.score:.4f} {mark} {hit.source} 第{hit.index}段")
        print()
    if backend_name() == "fake":
        print("假向量和二字词都看「退钱」这两个字有没有出现。知识库写的是「退款」「退货」，所以这句会偏。")
        print("装上 bge 并且不要设置 USE_FAKE_EMBEDDING，再跑一次，看「我想退钱」会不会靠近退换货。")
    else:
        print("真模型按意思靠近。「我想退钱」即使没有「退款」两个字，也应更靠近退换货，而不是发票。")
    print("对比完成")


if __name__ == "__main__":
    main()
