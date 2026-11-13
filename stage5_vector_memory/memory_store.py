# -*- coding: utf-8 -*-
"""一个顾客一份长期记忆：FAISS 索引加 meta.json，放在 data/memory/顾客编号/。

阶段 3 的 Redis 记的是最近这一段对话，空闲大约 30 分钟就过期。
这里记的是可以留很久的事实。进程结束、下次再问，只要还在磁盘上就能按意思找回来。
data/ 已在 gitignore 里。不要把练习里的顾客事实提交进仓库。
"""

from datetime import datetime
from pathlib import Path

from embedder import backend_name, embed_texts, embedder_id, embedding_dim
from index_store import FaissStore, load_store, remove_saved_index
from remember import redact_secrets, select_facts

# 假向量和真模型的分数不能共用一道门。数字是对着本课的短事实试出来的。
FAKE_MEMORY_THRESHOLD = 0.2
BGE_MEMORY_THRESHOLD = 0.45
# 几乎同一句再出现时不写第二遍。单位向量的余弦接近 1 才算同一句。
DUPLICATE_THRESHOLD = 0.92


def memory_threshold() -> float:
    if backend_name() == "bge":
        return BGE_MEMORY_THRESHOLD
    return FAKE_MEMORY_THRESHOLD


def memory_root() -> Path:
    return Path(__file__).resolve().parent / "data" / "memory"


def safe_user_id(user_id: str) -> str:
    """顾客编号会变成文件夹名。拒绝空串和会跳出目录的符号。"""
    cleaned = user_id.strip()
    if cleaned == "" or cleaned in {".", ".."}:
        raise ValueError("顾客编号不能是空的")
    for ch in cleaned:
        if ch.isalnum() or ch in {"-", "_"}:
            continue
        raise ValueError("顾客编号只使用字母、数字、下划线和减号")
    return cleaned


class UserMemory:
    """打开某个顾客的文件夹。没有文件就从空索引开始。"""

    def __init__(self, user_id: str, root: Path | None = None) -> None:
        self.user_id = safe_user_id(user_id)
        base = memory_root() if root is None else root
        self.folder = base / self.user_id
        index_path = self.folder / "index.faiss"
        if index_path.is_file():
            self.store = load_store(
                self.folder,
                expect_dim=embedding_dim(),
                expect_model=embedder_id(),
            )
            return
        self.store = FaissStore(embedding_dim(), backend_name(), embedder_id())

    def reset(self) -> None:
        """删掉这一位顾客的索引文件，内存里也换成空的。不影响其他顾客。"""
        remove_saved_index(self.folder)
        self.store = FaissStore(embedding_dim(), backend_name(), embedder_id())

    def add_facts(self, facts: list[str]) -> list[str]:
        """写入还没有的事实，并立刻保存。返回这次新写下的那些。"""
        saved = []
        for fact in facts:
            if fact.strip() == "":
                continue
            if self._already_have(fact):
                continue
            vector = embed_texts([fact], as_query=False)
            self.store.add(
                vector,
                [
                    {
                        "text": fact,
                        "source": "memory",
                        "title": self.user_id,
                        "index": len(self.store.records) + 1,
                        "kind": "fact",
                        "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    }
                ],
            )
            saved.append(fact)
        if saved:
            self.store.save(self.folder)
        return saved

    def add_text(self, text: str, client=None, model: str | None = None) -> list[str]:
        """先判断值不值得记，再写入。"""
        return self.add_facts(select_facts(text, client=client, model=model))

    def remember_exchange(self, question: str, source: str) -> str | None:
        """政策问答结束后留下「问过什么、答复来自哪份文件」。

        不把资料正文抄进记忆。抄到一半会把「365」切成「3」，看起来像另一条规定。
        天数仍以知识库为准。号码仍然先抹掉。
        """
        question = redact_secrets(question.strip())
        if len(question) > 40:
            question = question[:40]
        fact = f"以前问过「{question}」，答复来自 {source}"
        saved = self.add_facts([fact])
        if not saved:
            return None
        return saved[0]

    def search(self, query: str, top_k: int = 3) -> list:
        """不设门。调用方想看低分时用这个。"""
        if len(self.store.records) == 0:
            return []
        vector = embed_texts([query], as_query=True)
        return self.store.search(vector, top_k)

    def recall(self, query: str, top_k: int = 3) -> list:
        """只留下达到门槛的事实。不够像就不送进提示。"""
        threshold = memory_threshold()
        chosen = []
        for hit in self.search(query, top_k=top_k):
            if hit.score >= threshold:
                chosen.append(hit)
        return chosen

    def _already_have(self, fact: str) -> bool:
        if len(self.store.records) == 0:
            return False
        vector = embed_texts([fact], as_query=False)
        hits = self.store.search(vector, 1)
        if not hits:
            return False
        return hits[0].score >= DUPLICATE_THRESHOLD
