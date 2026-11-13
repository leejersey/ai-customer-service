# -*- coding: utf-8 -*-
"""把一篇长文切成检索用的小段。

先按空行和标题切开，再把仍然太长的段按字数切开，相邻两段重叠一段字。
整篇当一块时，问发票也会把退货规定一起送进提示。切得太碎时，天数和条件会落在两块里。
"""


class Chunk:
    """检索时的一小段。index 从 1 起，是给人看的「第几段」，不是列表下标。"""

    def __init__(self, source: str, title: str, index: int, text: str) -> None:
        self.source = source
        self.title = title
        self.index = index
        self.text = text

    def __repr__(self) -> str:
        preview = self.text.replace("\n", " ")
        if len(preview) > 24:
            preview = preview[:24] + "…"
        return (
            f"Chunk(source={self.source!r}, index={self.index}, "
            f"chars={len(self.text)}, text={preview!r})"
        )


def split_paragraphs(text: str) -> list[str]:
    """按空行分段。单独成段的 Markdown 标题并进它下面的正文。"""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    parts = []
    for part in normalized.split("\n\n"):
        cleaned = part.strip()
        if cleaned != "":
            parts.append(cleaned)

    merged = []
    pending_titles = []
    for part in parts:
        if _is_heading(part):
            # 标题先攒着。单独成段的话，短标题会在检索里胜过真正的规定。
            pending_titles.append(part)
            continue
        if pending_titles:
            merged.append("\n".join(pending_titles + [part]))
            pending_titles = []
        else:
            merged.append(part)
    # 文件末尾若只剩标题，不再单独成段。文档标题已经放在 Document.title 里。
    return merged


def _is_heading(part: str) -> bool:
    """这一小段的每一行都是 # 标题时，它自己还不是完整的一条规定。"""
    saw_line = False
    for line in part.split("\n"):
        stripped = line.strip()
        if stripped == "":
            continue
        saw_line = True
        if not stripped.startswith("#"):
            return False
    return saw_line


def split_by_length(text: str, size: int, overlap: int) -> list[str]:
    """按字数切。overlap 是下一段开头要重复的字数。

    重叠必须小于块长。否则窗口不往前走，循环会停在原地。
    重叠用来保住被切断的那一句：它在前一段的末尾，也在后一段的开头。
    """
    if size < 1:
        raise ValueError("切块长度至少为 1")
    if overlap < 0:
        raise ValueError("重叠不能是负数")
    if overlap >= size:
        raise ValueError("重叠必须小于切块长度，否则窗口不会往前走")
    if len(text) <= size:
        return [text]

    pieces = []
    start = 0
    while start < len(text):
        end = start + size
        if end > len(text):
            end = len(text)
        pieces.append(text[start:end])
        if end == len(text):
            break
        # 下一段从这一段结束的位置往回退 overlap 个字。
        start = end - overlap
    return pieces


def chunk_document(document, size: int, overlap: int) -> list[Chunk]:
    """一篇文档先按段，超长的段再按字数。段号在这一篇内部从 1 编号。"""
    chunks = []
    number = 1
    for paragraph in split_paragraphs(document.text):
        for piece in split_by_length(paragraph, size, overlap):
            chunks.append(
                Chunk(
                    source=document.source,
                    title=document.title,
                    index=number,
                    text=piece,
                )
            )
            number += 1
    return chunks


def chunk_documents(documents: list, size: int, overlap: int) -> list[Chunk]:
    chunks = []
    for document in documents:
        chunks.extend(chunk_document(document, size, overlap))
    return chunks


# 100 个字大约能放下「一个小标题加一条规定」。再长，一块里就会混进下一条。
# 重叠 25 是块长的四分之一：被切断的那半句会在下一块开头再出现一次。
# 数字选得偏小，是为了在屏幕上看见切痕。真正上线时块往往更长，道理相同。
CHUNK_SIZE = 100
CHUNK_OVERLAP = 25
