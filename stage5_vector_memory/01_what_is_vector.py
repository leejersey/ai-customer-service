# -*- coding: utf-8 -*-
"""阶段 5 · 示例 1：向量是一串数，意思接近时这串数的方向接近。

本脚本只用假向量，不下载模型，也不调用 DeepSeek。
对照的是阶段 4 的二字词：用字不同的「退钱」和「退款」，两边都对不上。

    python stage5_vector_memory/01_what_is_vector.py

导读：stage5_vector_memory/docs/01_vector.md
"""

import stage5_link

stage5_link.enable()

import numpy as np

from embedder import FAKE_DIM, character_bigrams, hashed_bigram_matrix
from retrieve import cosine as keyword_cosine
from retrieve import term_counts
from vectors import cosine


def keyword_score(left: str, right: str) -> float:
    """阶段 4 的余弦，直接用词的次数当权重。没有公共二字词就是 0。"""
    left_counts = {term: float(count) for term, count in term_counts(left).items()}
    right_counts = {term: float(count) for term, count in term_counts(right).items()}
    return keyword_cosine(left_counts, right_counts)


def preview(vector) -> str:
    row = np.asarray(vector, dtype=np.float32).reshape(-1)
    parts = []
    for value in row[:8]:
        parts.append(f"{float(value):.3f}")
    return "[" + ", ".join(parts) + ", …]"


def nonzero_count(vector) -> int:
    count = 0
    for value in np.asarray(vector, dtype=np.float32).reshape(-1):
        if float(value) != 0.0:
            count += 1
    return count


def main() -> None:
    print("向量就是把一句话写成一串数。这一课先用假向量，所以不下载模型。")
    print(f"假向量固定 {FAKE_DIM} 格。真模型 bge-small-zh 是 512 格，几乎每一格都有小数。")
    print("假向量大部分格子是 0，只有这句话里的二字词落进去的那几格不是 0。")
    print()

    sample = hashed_bigram_matrix(["退款"])
    print("「退款」切成二字词：", " ".join(character_bigrams("退款")))
    print("前 8 个数：", preview(sample))
    print(f"不是 0 的格子有 {nonzero_count(sample)} 个。形状 {tuple(sample.shape)}，类型 {sample.dtype}。")
    print()

    pairs = (
        ("退款", "退款"),
        ("退款", "退钱"),
        ("七天无理由退货", "未拆封可以七天无理由退货"),
        ("七天无理由退货", "可以开纸质发票吗"),
    )
    print("同一对字，方向就接近。换一种说法，假向量和阶段 4 的关键词都会变远。")
    for left, right in pairs:
        matrix = hashed_bigram_matrix([left, right])
        word = keyword_score(left, right)
        vector_score = cosine(matrix[0], matrix[1])
        print(f"  {left}    vs    {right}")
        print(f"    二字词余弦 {word:.4f}    假向量余弦 {vector_score:.4f}")
    print()
    print("「退款」和「退钱」的二字词余弦是 0：一边只有「退款」，另一边只有「退钱」。")
    print("假向量同样对不上。真嵌入模型会把这两种说法拉近，那是下一课在加载的模型。")
    print("向量这一课看完了。相近不是魔法，是两串数的方向。")


if __name__ == "__main__":
    main()
