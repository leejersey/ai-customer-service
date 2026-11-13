# -*- coding: utf-8 -*-
"""阶段 5 · 示例 2：向谁要这串数。

DeepSeek 没有嵌入接口。本课用本机的中文模型；没有库、没有模型，或
USE_FAKE_EMBEDDING=1 时，用示例 1 的假向量。

    USE_FAKE_EMBEDDING=1 python stage5_vector_memory/02_get_embeddings.py

导读：stage5_vector_memory/docs/02_embedder.md
"""

import os

from embedder import (
    FAKE_DIM,
    MODEL_NAME,
    QUERY_PREFIX,
    backend_name,
    describe_backend,
    embed_texts,
    embedding_dim,
    hashed_bigram_matrix,
)
from vectors import cosine

SENTENCES = (
    "未拆封可以七天无理由退货",
    "我想把钱退回来",
    "可以开纸质发票吗",
)


def preview(vector) -> str:
    parts = []
    for value in vector.reshape(-1)[:8]:
        parts.append(f"{float(value):.3f}")
    return "[" + ", ".join(parts) + ", …]"


def main() -> None:
    print("DeepSeek 的对话地址仍是 https://api.deepseek.com ，这里不向它要向量。")
    if os.environ.get("USE_FAKE_EMBEDDING", "").strip() == "":
        print("没有设置 USE_FAKE_EMBEDDING。会试着加载 " + MODEL_NAME + "。")
        print("这个模型要另外下载。不想下载时，在命令前面加上 USE_FAKE_EMBEDDING=1。")
    print(describe_backend())
    print(f"这一次用的是 {backend_name()}，维度 {embedding_dim()}。")
    print()

    matrix = embed_texts(list(SENTENCES), as_query=False)
    print(f"三条句子堆成一张表：形状 {tuple(matrix.shape)}，类型 {matrix.dtype}。")
    print("形状的第一个数是句子条数，第二个数是每一条有几格。")
    for sentence, row in zip(SENTENCES, matrix):
        print(f"  {sentence}")
        print(f"    {preview(row)}")
    same = cosine(matrix[0], matrix[0])
    far = cosine(matrix[0], matrix[2])
    print()
    print(f"第一句和自己的余弦是 {same:.4f}。和发票那句是 {far:.4f}。")
    print("再嵌入一次。模型若已经在内存里，不会重新加载，也不会重新下载。")
    again = embed_texts([SENTENCES[0]], as_query=False)
    print(f"第二次形状 {tuple(again.shape)}，和第一次第一行的余弦 {cosine(matrix[0], again[0]):.4f}。")
    print()

    if backend_name() == "bge":
        print("真模型给问题加了前缀：" + QUERY_PREFIX)
        print("文档不加这句。前缀只在 as_query=True 时出现。")
    else:
        print("现在走的是假向量，问题前面不会加那句前缀。")
        print(f"假向量是 {FAKE_DIM} 维。真模型是 512 维。两边的索引不能混用。")
        fake = hashed_bigram_matrix(["退款", "退钱"])
        print(f"假向量里「退款」和「退钱」的余弦是 {cosine(fake[0], fake[1]):.4f}。")
        print("真模型才会让这两种说法靠近。假向量换来的是离线也能跑。")
    print()
    print("嵌入完成")


if __name__ == "__main__":
    main()
