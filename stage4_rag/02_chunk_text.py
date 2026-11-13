# -*- coding: utf-8 -*-
"""阶段 4 · 示例 2：按段落切开，再按字数重叠切开。

用一组十个字看重叠，再用知识库看真正的长段。不需要密钥。

    python stage4_rag/02_chunk_text.py

导读：stage4_rag/docs/02_chunk.md
"""

from chunking import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    chunk_documents,
    split_by_length,
    split_paragraphs,
)
from documents import load_documents


def show_toy() -> None:
    """十个字足够看见窗口往前走，又短到能在屏幕上对齐。"""
    sample = "一二三四五六七八九十"
    print("== 同一句，两种切法 ==")
    print(f"原句：{sample}")
    print("块长 6，重叠 0：")
    for piece in split_by_length(sample, size=6, overlap=0):
        print(f"  {piece}")
    print("块长 6，重叠 2：")
    for piece in split_by_length(sample, size=6, overlap=2):
        print(f"  {piece}")
    print("第二段的「五六」在第一段末尾已经出现过。切断的那两个字没有丢。")
    try:
        split_by_length(sample, size=6, overlap=6)
    except ValueError as error:
        print(f"重叠等于块长时拒绝：{error}")
    print()


def show_knowledge() -> None:
    documents = load_documents()
    print("== 知识库 ==")
    print(f"切块长度 {CHUNK_SIZE} 字，相邻重叠 {CHUNK_OVERLAP} 字。")
    total = 0
    long_chunks = []
    for document in documents:
        paragraphs = split_paragraphs(document.text)
        chunks = chunk_documents([document], CHUNK_SIZE, CHUNK_OVERLAP)
        total += len(chunks)
        print(f"{document.source}：{len(paragraphs)} 段正文，切成 {len(chunks)} 块")
        for earlier, later in zip(chunks, chunks[1:]):
            # 只有按字数切开的块才会刚好写满块长，下一块又从重叠处接上。
            if len(earlier.text) != CHUNK_SIZE:
                continue
            overlap = earlier.text[-CHUNK_OVERLAP:]
            if later.text.startswith(overlap):
                long_chunks.append((earlier, later, overlap))
    print(f"合计 {total} 块。")
    print()
    if not long_chunks:
        print("没有段落超过块长。把 CHUNK_SIZE 改小再运行，就能看见重叠。")
        return
    earlier, later, overlap = long_chunks[0]
    print(f"== 超长段的重叠：{earlier.source} 第{earlier.index}块和第{later.index}块 ==")
    print("前一块末尾：")
    print(overlap)
    print("后一块开头：")
    print(later.text[:CHUNK_OVERLAP])
    print("两行应该相同。问句若刚好落在切痕上，两块都还能看见这几个字。")
    print()


def main() -> None:
    show_toy()
    show_knowledge()
    print("切块完成")


if __name__ == "__main__":
    main()
