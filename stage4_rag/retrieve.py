# -*- coding: utf-8 -*-
"""用二字词的 TF-IDF 和余弦相似度找出最相关的几段。

本课调用的 DeepSeek 接口只有对话补全，没有 embeddings（把句子变成向量的接口）。
所以这里不请求任何向量服务，用标准库自己数字、自己算分数。
阶段 5 才会用真正的向量和 FAISS。这一阶段故意把乘法留在眼前。

二字词就是一次取相邻的两个字，当作一个小关键词。中文没有空格，又不必为此安装分词库。
"""

import math
from collections import Counter

from chunking import CHUNK_OVERLAP, CHUNK_SIZE, chunk_documents
from documents import load_documents

# 这些符号不参加组词。去掉之后，前后的字会接上，标点才不会变成「词」。
# 引号分两段写，是为了字符串本身的引号不会把这一行提前截断。
_SKIP = set(
    " \t\r\n，。！？、；："
    + "\"'“”‘’「」"
    + "（）()【】[]《》<>"
    + "·…—-.,!?;:/\\|@#$%^&*_+={}~～"
)


class Hit:
    """一段资料和它与问题的分数。shared 是两边都出现了的二字词，方便看见为什么命中。"""

    def __init__(
        self,
        source: str,
        title: str,
        index: int,
        text: str,
        score: float,
        shared: tuple[str, ...],
    ) -> None:
        self.source = source
        self.title = title
        self.index = index
        self.text = text
        self.score = score
        self.shared = shared

    def __repr__(self) -> str:
        return f"Hit(source={self.source!r}, index={self.index}, score={self.score:.4f})"


def character_bigrams(text: str) -> list[str]:
    """去掉空白和标点后，把相邻两个字配成一对。"""
    chars = []
    for ch in text:
        if ch in _SKIP or ch.isspace():
            continue
        chars.append(ch)
    pairs = []
    # zip 在较短的那一排结束。第二排少了第一个字，于是配成 (第1,第2)、(第2,第3)…
    for left, right in zip(chars, chars[1:]):
        pairs.append(left + right)
    return pairs


def term_counts(text: str) -> Counter:
    """每个二字词出现了几次。"""
    return Counter(character_bigrams(text))


def shared_terms(query: str, text: str) -> set[str]:
    """问题和这一段都有的二字词。只看有没有，不看次数。"""
    return set(term_counts(query)) & set(term_counts(text))


def build_idf(chunk_counts: list[Counter]) -> dict[str, float]:
    """越少见的二字词，权重越高。

    几乎每段都有的字对，不能用来区分「在问发票」还是「在问运费」。
    log 把「出现在很多段里」压矮。加 1 是为了分母不为 0，也避免每段都有的词权重变成 0。
    """
    total = len(chunk_counts)
    document_frequency = Counter()
    for counts in chunk_counts:
        # 一篇里出现多次也只算这段有这个词。IDF 关心的是「有多少段出现过」。
        for term in counts:
            document_frequency[term] += 1
    idf = {}
    for term, frequency in document_frequency.items():
        idf[term] = math.log((total + 1) / (frequency + 1)) + 1.0
    return idf


def tfidf_vector(counts: Counter, idf: dict[str, float]) -> dict[str, float]:
    """词频乘上 IDF。问题里的词若知识库从没出现，就没有权重，不能靠它得分。"""
    total = sum(counts.values())
    if total == 0:
        return {}
    vector = {}
    for term, count in counts.items():
        weight = idf.get(term)
        if weight is None:
            continue
        tf = count / total
        vector[term] = tf * weight
    return vector


def cosine(left: dict[str, float], right: dict[str, float]) -> float:
    """两个向量有多同向。没有公共词时是 0。完全同向时接近 1。

    先把对得上的维度相乘再相加，再除以各自的长度。
    除以长度，是为了不让「这段特别长所以词很多」自动赢过短段。
    """
    if not left or not right:
        return 0.0
    dot = 0.0
    for term in set(left) & set(right):
        dot += left[term] * right[term]
    left_norm = math.sqrt(sum(value * value for value in left.values()))
    right_norm = math.sqrt(sum(value * value for value in right.values()))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return dot / (left_norm * right_norm)


class TfidfIndex:
    """建一次索引，后面每个问题都拿它来查。IDF 要用到全部段，所以不能每问一次就只看一段。"""

    def __init__(self, chunks: list) -> None:
        self.chunks = list(chunks)
        self.counts = []
        for chunk in self.chunks:
            self.counts.append(term_counts(chunk.text))
        self.idf = build_idf(self.counts)
        self.vectors = []
        for counts in self.counts:
            self.vectors.append(tfidf_vector(counts, self.idf))

    def search(self, query: str, top_k: int = 3) -> list[Hit]:
        """返回分数最高的 top_k 段。分数从高到低。"""
        if top_k < 1:
            raise ValueError("top_k 至少为 1")
        query_counts = term_counts(query)
        query_vector = tfidf_vector(query_counts, self.idf)
        query_terms = set(query_counts)
        hits = []
        for chunk, vector, counts in zip(self.chunks, self.vectors, self.counts):
            score = cosine(query_vector, vector)
            shared = tuple(sorted(query_terms & set(counts)))
            hits.append(
                Hit(
                    source=chunk.source,
                    title=chunk.title,
                    index=chunk.index,
                    text=chunk.text,
                    score=score,
                    shared=shared,
                )
            )
        ranked = sorted(hits, key=lambda hit: hit.score, reverse=True)
        return ranked[:top_k]

    def missing_terms(self, query: str) -> list[str]:
        """问题里有、但任何一段都没出现过的二字词。它们对分数没有贡献。"""
        missing = set(term_counts(query)) - set(self.idf)
        return sorted(missing)


def build_index(folder=None, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> TfidfIndex:
    """读知识库、切块、建索引。示例脚本都从这里进入，避免每份脚本各写一遍。"""
    documents = load_documents(folder)
    chunks = chunk_documents(documents, size, overlap)
    return TfidfIndex(chunks)
