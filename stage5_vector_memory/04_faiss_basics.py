# -*- coding: utf-8 -*-
"""阶段 5 · 示例 4：FAISS 的 add、search、编号，以及存到磁盘。

四句短文本用假向量，避免这一课卡在模型下载上。
索引写到 stage5_vector_memory/data/faiss_lesson/，该目录已忽略，不要提交。

    python stage5_vector_memory/04_faiss_basics.py

导读：stage5_vector_memory/docs/04_faiss.md
"""

from pathlib import Path

import faiss
import numpy as np

from embedder import hashed_bigram_matrix
from index_store import FaissStore, load_store, remove_saved_index
from vectors import l2_normalize

SENTENCES = (
    "未拆封七天可以退货",
    "运费满99元包邮",
    "纸质发票不提供",
    "人工客服到21点",
)


def main() -> None:
    print("== 归一化之前，长向量的点积更大 ==")
    raw_index = faiss.IndexFlatIP(2)
    raw = np.array([[3.0, 4.0], [0.6, 0.8]], dtype=np.float32)
    raw_index.add(raw)
    query = np.array([[0.6, 0.8]], dtype=np.float32)
    scores, ids = raw_index.search(query, 2)
    print("两条其实同一个方向。[3, 4] 更长，内积分数更高：")
    for score, row_id in zip(scores[0], ids[0]):
        values = []
        for value in raw[int(row_id)]:
            values.append(f"{float(value):.1f}")
        print(f"  id={int(row_id)}  分数={float(score):.4f}  向量=[{', '.join(values)}]")
    unit_index = faiss.IndexFlatIP(2)
    unit_index.add(l2_normalize(raw))
    scores, ids = unit_index.search(l2_normalize(query), 2)
    print("归一化之后，两条的内积都接近 1，长的那条不再自动赢：")
    for score, row_id in zip(scores[0], ids[0]):
        print(f"  id={int(row_id)}  分数={float(score):.4f}")
    print()

    print("== float32 ==")
    probe = faiss.IndexFlatIP(2)
    probe.add(np.array([[1.0, 2.0]], dtype=np.float64))
    print("这一版 FAISS 接受了 float64，读回来是：", probe.reconstruct(0))
    print("它帮你转了。老版本不一定这么做。索引里我们仍然先写成 float32。")
    try:
        probe.add(np.ones((1, 3), dtype=np.float32))
    except AssertionError as error:
        detail = str(error).strip() or "AssertionError"
        print("格数和索引维度不一致时，原始 FAISS 会拒绝：", detail)
    print()

    print("== add、search、编号 ==")
    vectors = hashed_bigram_matrix(list(SENTENCES))
    store = FaissStore(int(vectors.shape[1]), "fake", "hashed-bigram")
    records = []
    for index, sentence in enumerate(SENTENCES, start=1):
        records.append(
            {
                "text": sentence,
                "source": "demo",
                "title": "四句",
                "index": index,
                "kind": "demo",
            }
        )
    store.add(vectors, records)
    print(f"索引条数 {store.index.ntotal}，元数据 {len(store.records)} 条。这两个数必须相等。")
    hits = store.search(hashed_bigram_matrix(["可以退货吗"]), top_k=3)
    for rank, hit in enumerate(hits, start=1):
        print(f"  {rank}. id={hit.row_id}  {hit.score:.4f}  {hit.text}")
    print("id 是 add 时的行号，从 0 起。用它去 records[id] 才能拿回原文。")
    print()

    print("== 问得比库存多时，编号会是 -1 ==")
    over_scores, over_ids = store.index.search(hashed_bigram_matrix(["包邮"]), 6)
    print("  ids =", [int(item) for item in over_ids[0]])
    print("  库存只有 4 条，多出来的位置是 -1，分数是一个极小的数，不能拿去当原文。")
    print("  我们的 search 会把 -1 丢掉。上面打印的是原始 FAISS 的返回值。")
    print()

    print("== 保存再读回 ==")
    folder = Path(__file__).resolve().parent / "data" / "faiss_lesson"
    remove_saved_index(folder)
    store.save(folder)
    print(f"写到了 {folder / 'index.faiss'}")
    print(f"原文在 {folder / 'meta.json'}")
    loaded = load_store(folder, expect_dim=store.dim, expect_model="hashed-bigram")
    again = loaded.search(hashed_bigram_matrix(["可以退货吗"]), top_k=1)
    print(f"读回后的第一名仍是 id={again[0].row_id} {again[0].text}")
    try:
        load_store(folder, expect_dim=store.dim + 1, expect_model="hashed-bigram")
    except ValueError as error:
        print("故意用错误的维度去读：")
        print(" ", error)
    try:
        store.add(np.ones((1, 3), dtype=np.float32), [{"text": "维度不对"}])
    except ValueError as error:
        print("往 256 维索引里写入 3 维：")
        print(" ", error)
    print()
    print("FAISS 这一课看完了")


if __name__ == "__main__":
    main()
