# -*- coding: utf-8 -*-
"""阶段 4 · 示例 3：用二字词 TF-IDF 检索，打印 top-k 和分数。

不调用模型。DeepSeek 的对话接口没有 embeddings，这里的分数是本地算的。

    python stage4_rag/03_search_chunks.py

导读：stage4_rag/docs/03_retrieve.md
"""

from prompting import SCORE_THRESHOLD
from retrieve import build_index

# 前几句用了资料里的原词。最后两句是知识库没写的话题，用来看低分。
QUESTIONS = (
    "退货政策是几天",
    "不满99元运费是多少",
    "100积分抵多少元",
    "耳机保修多久",
    "进液还保修吗",
    "支持货到付款吗",
    "可以开纸质发票吗",
    "没有订单号能不能凭姓名查询",
    "人工客服营业到几点",
    "星河耳机卖多少钱",
    "你们今年招实习生吗",
    "今天月球冷不冷",
)


def main() -> None:
    index = build_index()
    print(f"索引里有 {len(index.chunks)} 块，词表 {len(index.idf)} 个二字词。")
    print("没有请求向量接口。阶段 5 才会用 FAISS。")
    print(f"下面的阈值是 {SCORE_THRESHOLD}。它不是概率。")
    print()
    for question in QUESTIONS:
        hits = index.search(question, top_k=3)
        missing = index.missing_terms(question)
        print(f"问题：{question}")
        if missing:
            shown = " ".join(missing[:8])
            print(f"  知识库里从没出现的二字词：{shown}")
        else:
            print("  问题里的二字词都在某段里出现过。")
        for rank, hit in enumerate(hits, start=1):
            shared = " ".join(hit.shared[:8]) if hit.shared else "（没有）"
            mark = "达到阈值" if hit.score >= SCORE_THRESHOLD else "低于阈值"
            print(
                f"  {rank}. {hit.score:.4f} {mark} {hit.source} 第{hit.index}段"
            )
            print(f"     对上的词：{shared}")
        print()
    print("检索完成")


if __name__ == "__main__":
    main()
