# -*- coding: utf-8 -*-
"""把一句中文变成一串小数。

DeepSeek 这一课用的对话接口没有 embeddings，所以不向 api.deepseek.com 要向量。
优先用本机的中文嵌入模型 BAAI/bge-small-zh-v1.5（sentence-transformers）。
模型或库不可用，或者环境变量 USE_FAKE_EMBEDDING=1 时，改用哈希二字词。

假向量和阶段 4 一样看字面：同一对字落在同一格，所以「退货」能对上「退货」。
「退钱」和「退款」用字不同，假向量不会把它们拉近。真模型才会。
假向量换来的是：不下载模型、不联网，后面的 FAISS 练习仍然跑得完。
"""

import hashlib
import os
from pathlib import Path

import numpy as np

from vectors import cosine, l2_normalize

# 小模型的中文向量是 512 维。假向量故意用另一维，换模型之后旧索引对不上，错误才看得见。
FAKE_DIM = 256
MODEL_NAME = "BAAI/bge-small-zh-v1.5"
# bge 检索时建议给问题加这句前缀，文档不加。假向量不加，否则前缀的字会占满格子。
QUERY_PREFIX = "为这个句子生成表示以用于检索相关文章："

# 和阶段 4 的 _SKIP 同一份。标点不参加组词，否则符号会变成「词」。
# 这里再写一遍，是为了本文件不导入阶段 4 也能单独把字变成向量。
_SKIP = set(
    " \t\r\n，。！？、；："
    + "\"'“”‘’「」"
    + "（）()【】[]《》<>"
    + "·…—-.,!?;:/\\|@#$%^&*_+={}~～"
)

# 模块级缓存。模型只在第一次嵌入时加载。再问下一句时不要重新下载。
_BACKEND = None
_MODEL = None
_REASON = ""
_ENV_LOADED = False


def _load_env() -> None:
    """让写在 .env 里的 USE_FAKE_EMBEDDING 生效。命令行里已经设置的值优先。"""
    global _ENV_LOADED
    if _ENV_LOADED:
        return
    _ENV_LOADED = True
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    # override=False：终端里临时写的 1 不会被 .env 里的空值盖掉。
    load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=False)


def fake_requested() -> bool:
    """环境变量明确要求假向量时，连模型都不去碰。"""
    _load_env()
    value = os.environ.get("USE_FAKE_EMBEDDING", "").strip().lower()
    return value in {"1", "true", "yes", "on"}


def _ensure_backend() -> None:
    """决定这一次进程用真模型还是假向量。决定一次就记住。"""
    global _BACKEND, _MODEL, _REASON
    if _BACKEND is not None:
        return
    _load_env()
    if fake_requested():
        _BACKEND = "fake"
        _MODEL = None
        _REASON = "USE_FAKE_EMBEDDING 已打开，使用哈希二字词假向量。近义词不会被拉近。"
        return
    try:
        # 进度条和「未登录 Hugging Face」会盖住我们自己的那一行原因。
        os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
        os.environ.setdefault("HF_HUB_VERBOSITY", "error")
        os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
        os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
        from sentence_transformers import SentenceTransformer
    except ImportError:
        _BACKEND = "fake"
        _MODEL = None
        _REASON = (
            "没有安装 sentence-transformers，改用假向量。"
            "这个库会带上很大的 torch，可以不装。装上并关掉 USE_FAKE_EMBEDDING 之后才会用真模型。"
        )
        return
    try:
        _MODEL = SentenceTransformer(MODEL_NAME)
    except Exception as error:
        # 没网、模型下不来、缓存坏了，都落到假向量。练习不能停在下载上。
        _BACKEND = "fake"
        _MODEL = None
        _REASON = (
            "中文嵌入模型暂时加载不了（"
            + type(error).__name__
            + "），改用假向量。练习可以继续。近义词不会被拉近。"
        )
        return
    _BACKEND = "bge"
    dim = _model_dimension(_MODEL)
    _REASON = f"已加载本地嵌入模型 {MODEL_NAME}，维度 {dim}。查询句会加上检索用的前缀。"


def backend_name() -> str:
    """fake 或 bge。阈值按这个名字分开，两套分数不是同一把尺子。"""
    _ensure_backend()
    return str(_BACKEND)


def embedder_id() -> str:
    """写进索引旁边的名字。换了这个名字，旧索引就不能再搜。"""
    _ensure_backend()
    if _BACKEND == "bge":
        return MODEL_NAME
    return "hashed-bigram"


def describe_backend() -> str:
    """给人看的一行原因。脚本自己打印，本模块不在导入时说话。"""
    _ensure_backend()
    return _REASON


def _model_dimension(model) -> int:
    """新版 sentence-transformers 把方法改名了。旧名字还会用，但会打印警告。"""
    method = getattr(model, "get_embedding_dimension", None)
    if method is None:
        method = model.get_sentence_embedding_dimension
    return int(method())


def embedding_dim() -> int:
    _ensure_backend()
    if _BACKEND == "fake":
        return FAKE_DIM
    return _model_dimension(_MODEL)


def character_bigrams(text: str) -> list[str]:
    """去掉空白和标点后，把相邻两个字配成一对。切法和阶段 4 相同。"""
    chars = []
    for ch in text:
        if ch in _SKIP or ch.isspace():
            continue
        chars.append(ch)
    pairs = []
    for left, right in zip(chars, chars[1:]):
        pairs.append(left + right)
    return pairs


def _bucket(gram: str, dim: int) -> tuple[int, float]:
    """同一对字每次都落在同一格，并带一个正负号。

    md5 在这里不是加密。它只负责把「退货」稳定地变成一个整数。
    正负号是为了不同的词撞进同一格时，不总是往同一个方向加。
    """
    digest = hashlib.md5(gram.encode("utf-8")).hexdigest()
    number = int(digest, 16)
    bucket = number % dim
    sign = 1.0 if ((number // dim) % 2) == 0 else -1.0
    return bucket, sign


def hashed_bigram_matrix(texts: list[str]) -> np.ndarray:
    """假向量。不下载模型。每一行是 float32，并且已经归一化。

    字面相同的二字词会把同一格加高，所以和阶段 4 一样吃「用字一样」。
    它没有 IDF，常见的「的一」也会占一格。真模型几乎每一格都有数，并且按意思靠近。
    """
    rows = np.zeros((len(texts), FAKE_DIM), dtype=np.float32)
    for row_index, text in enumerate(texts):
        if not isinstance(text, str):
            raise TypeError("列表里要放字符串")
        grams = character_bigrams(text)
        if not grams and text.strip() != "":
            # 只有一个字时没有「对」。把这一个字自己放进一格，避免整行是 0。
            grams = [text.strip()]
        for gram in grams:
            bucket, sign = _bucket(gram, FAKE_DIM)
            rows[row_index, bucket] += np.float32(sign)
    return l2_normalize(rows)


def embed_texts(texts: list[str], *, as_query: bool = False) -> np.ndarray:
    """返回形状 (条数, 维度) 的 float32。每一行长度是 1，全零行除外。

    as_query 只对真模型有意义：问题前面加检索前缀，文档不加。
    """
    if not isinstance(texts, list):
        raise TypeError("embed_texts 要的是字符串列表")
    for text in texts:
        if not isinstance(text, str):
            raise TypeError("列表里要放字符串")
    _ensure_backend()
    if len(texts) == 0:
        return np.zeros((0, embedding_dim()), dtype=np.float32)
    if _BACKEND == "fake":
        return hashed_bigram_matrix(texts)
    prepared = []
    for text in texts:
        if as_query:
            prepared.append(QUERY_PREFIX + text)
        else:
            prepared.append(text)
    matrix = _MODEL.encode(
        prepared,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )
    return l2_normalize(matrix)
