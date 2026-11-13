# -*- coding: utf-8 -*-
"""用阶段 4 的切块，建成 FAISS 知识库索引。

切块规则不重写。阶段 4 的二字词索引仍可拿来对照，文件在 stage4_rag/retrieve.py。
"""

import stage5_link

stage5_link.enable()

from chunking import CHUNK_OVERLAP, CHUNK_SIZE, chunk_documents
from documents import load_documents

from embedder import backend_name, embed_texts, embedder_id
from index_store import FaissStore


def build_knowledge_store() -> FaissStore:
    """读 knowledge/、切块、嵌入、add。每次运行在内存里建一份，不依赖事先保存的索引。"""
    documents = load_documents()
    chunks = chunk_documents(documents, CHUNK_SIZE, CHUNK_OVERLAP)
    texts = []
    records = []
    for chunk in chunks:
        texts.append(chunk.text)
        records.append(
            {
                "text": chunk.text,
                "source": chunk.source,
                "title": chunk.title,
                "index": chunk.index,
                "kind": "knowledge",
            }
        )
    vectors = embed_texts(texts, as_query=False)
    store = FaissStore(int(vectors.shape[1]), backend_name(), embedder_id())
    store.add(vectors, records)
    return store


def search_knowledge(store: FaissStore, question: str, top_k: int = 3) -> list:
    """问题按查询向量嵌入。真模型会加检索前缀，假向量不加。"""
    if len(store.records) == 0:
        return []
    vector = embed_texts([question], as_query=True)
    return store.search(vector, top_k)
