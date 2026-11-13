# -*- coding: utf-8 -*-
"""FAISS 的平面内积索引，外加一份「第几号是哪段原文」的 JSON。

IndexFlatIP 在单位向量上的分数就是余弦。它把第 0 号、第 1 号按 add 的顺序编号。
编号只能和 meta.json 里的列表对齐着看。只改其中一边，查回来的就是别人的段落。
"""

import json
from pathlib import Path

import faiss
import numpy as np

from vectors import l2_normalize


class VectorHit:
    """一条检索结果。字段和阶段 4 的 Hit 对齐，后面的提示才能沿用同样的来源标签。"""

    def __init__(
        self,
        row_id: int,
        score: float,
        text: str,
        source: str,
        title: str,
        index: int,
        kind: str,
    ) -> None:
        self.row_id = row_id
        self.score = score
        self.text = text
        self.source = source
        self.title = title
        self.index = index
        self.kind = kind

    def __repr__(self) -> str:
        return (
            f"VectorHit(row_id={self.row_id}, score={self.score:.4f}, "
            f"source={self.source!r}, index={self.index})"
        )


class FaissStore:
    """内存里的索引和元数据。save 时才落到磁盘。"""

    def __init__(self, dim: int, backend: str, model: str) -> None:
        if dim < 1:
            raise ValueError("维度至少为 1")
        self.dim = dim
        self.backend = backend
        self.model = model
        self.records: list[dict] = []
        self.index = faiss.IndexFlatIP(dim)

    def add(self, vectors, records: list[dict]) -> None:
        """按顺序追加。这一次的第 0 行会变成索引里的下一个编号。"""
        if len(records) == 0:
            return
        matrix = l2_normalize(vectors)
        if matrix.shape[0] != len(records):
            raise ValueError(
                f"向量有 {matrix.shape[0]} 行，元数据有 {len(records)} 条，两边必须一样多"
            )
        if matrix.shape[1] != self.dim:
            raise ValueError(
                f"向量是 {matrix.shape[1]} 维，索引是 {self.dim} 维。"
                "换了嵌入模型之后要新建索引，不能往旧索引里续写。"
            )
        # 再拷一份字典。调用方后来改自己的字典，不应把已经入库的字改掉。
        copied = []
        for record in records:
            copied.append(dict(record))
        self.index.add(matrix)
        self.records.extend(copied)
        self._aligned()

    def search(self, vector, top_k: int) -> list[VectorHit]:
        """分数从高到低。问得比库存多时，FAISS 会用 -1 补位，这里直接丢掉。"""
        if top_k < 1:
            raise ValueError("top_k 至少为 1")
        if len(self.records) == 0:
            return []
        matrix = l2_normalize(vector)
        if matrix.shape[1] != self.dim:
            raise ValueError(
                f"查询向量是 {matrix.shape[1]} 维，索引是 {self.dim} 维。"
                "换了嵌入模型之后，旧索引不能继续用。"
            )
        k = top_k if top_k < len(self.records) else len(self.records)
        scores, ids = self.index.search(matrix, k)
        hits = []
        for score, row_id in zip(scores[0], ids[0]):
            if int(row_id) < 0:
                continue
            record = self.records[int(row_id)]
            hits.append(
                VectorHit(
                    row_id=int(row_id),
                    score=float(score),
                    text=str(record.get("text", "")),
                    source=str(record.get("source", "")),
                    title=str(record.get("title", "")),
                    index=int(record.get("index", 0)),
                    kind=str(record.get("kind", "")),
                )
            )
        return hits

    def save(self, folder: Path) -> None:
        """索引是二进制，原文在 meta.json。两个文件要一起在，一起换。"""
        folder.mkdir(parents=True, exist_ok=True)
        self._aligned()
        faiss.write_index(self.index, str(folder / "index.faiss"))
        payload = {
            "dim": self.dim,
            "backend": self.backend,
            "model": self.model,
            "records": self.records,
        }
        text = json.dumps(payload, ensure_ascii=False, indent=2)
        (folder / "meta.json").write_text(text, encoding="utf-8")

    def _aligned(self) -> None:
        if int(self.index.ntotal) != len(self.records):
            raise RuntimeError(
                f"索引里有 {int(self.index.ntotal)} 条，元数据有 {len(self.records)} 条，对不上。"
                "编号按写入顺序对应，不能只改其中一边。"
            )
        if int(self.index.d) != self.dim:
            raise RuntimeError(
                f"索引维度是 {int(self.index.d)}，记录的维度是 {self.dim}。"
            )


def load_store(
    folder: Path,
    *,
    expect_dim: int | None = None,
    expect_model: str | None = None,
) -> FaissStore:
    """读回索引和元数据。条数、维度、模型名有一个对不上就拒绝。"""
    index_path = folder / "index.faiss"
    meta_path = folder / "meta.json"
    if not index_path.is_file() or not meta_path.is_file():
        raise FileNotFoundError(f"这个文件夹里没有成对的索引和元数据：{folder}")
    index = faiss.read_index(str(index_path))
    payload = json.loads(meta_path.read_text(encoding="utf-8"))
    records = payload.get("records")
    if not isinstance(records, list):
        raise ValueError("meta.json 里的 records 应该是列表")
    store = FaissStore(
        dim=int(payload["dim"]),
        backend=str(payload["backend"]),
        model=str(payload["model"]),
    )
    store.index = index
    store.records = records
    if int(index.ntotal) != len(records):
        raise ValueError(
            f"索引里有 {int(index.ntotal)} 条，元数据有 {len(records)} 条，对不上。"
            "请删掉 index.faiss 和 meta.json，用同一份数据重建。"
        )
    if int(index.d) != store.dim:
        raise ValueError(
            f"索引维度是 {int(index.d)}，meta.json 写的是 {store.dim}。两个文件不是同一次保存的。"
        )
    if expect_dim is not None and store.dim != expect_dim:
        raise ValueError(
            f"这份索引是 {store.model} 的 {store.dim} 维；现在的向量是 {expect_dim} 维。"
            "换模型后维度变了，请删掉旧索引再重建。"
        )
    if expect_model is not None and store.model != expect_model:
        raise ValueError(
            f"这份索引是用 {store.model} 建的，现在的嵌入是 {expect_model}。"
            "模型换了，即使维度碰巧相同，格子的含义也不同。请删掉旧索引再重建。"
        )
    return store


def remove_saved_index(folder: Path) -> None:
    """只删这一对生成文件。换模型或离线演示重跑时，避免旧维度还占着位子。"""
    if not folder.is_dir():
        return
    for name in ("index.faiss", "meta.json"):
        path = folder / name
        if path.is_file():
            path.unlink()
