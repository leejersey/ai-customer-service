# -*- coding: utf-8 -*-
"""把 knowledge 文件夹里的说明读成一份一份文档。

文件躺在磁盘上时还不是列表。这里只负责读进来，不负责切开，也不负责检索。
"""

from pathlib import Path

# 只认这两种。知识库里若放了图片或其他笔记，不要被当成政策正文。
TEXT_SUFFIXES = {".md", ".txt"}


class Document:
    """一份说明：从哪个文件来，标题是什么，正文全文。

    不用字典，是为了后面写 document.title 时知道有哪些栏。
    栏就这三个。路径不放进来，打印和检索只需要文件名。
    """

    def __init__(self, source: str, title: str, text: str) -> None:
        self.source = source
        self.title = title
        self.text = text

    def __repr__(self) -> str:
        return f"Document(source={self.source!r}, title={self.title!r}, chars={len(self.text)})"


def knowledge_dir() -> Path:
    """知识库和这份代码放在一起，不跟你执行命令时的当前目录走。"""
    return Path(__file__).resolve().parent / "knowledge"


def title_of(path: Path, text: str) -> str:
    """优先用文内第一行当标题。Markdown 的 # 只是标记，不是标题正文。"""
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "":
            continue
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip()
        return stripped
    # 空文件仍要有个名字，否则列表里会出现空白标题。
    return path.stem


def load_documents(folder: Path | None = None) -> list[Document]:
    """读文件夹里全部 .md 和 .txt，按文件名排序。

    排序是为了每次运行的打印顺序一样。iterdir 本身不保证顺序。
    """
    directory = knowledge_dir() if folder is None else Path(folder)
    if not directory.is_dir():
        raise FileNotFoundError(f"找不到知识库文件夹：{directory}")

    paths = []
    for path in directory.iterdir():
        if not path.is_file():
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        paths.append(path)

    documents = []
    for path in sorted(paths, key=lambda item: item.name):
        text = path.read_text(encoding="utf-8")
        documents.append(Document(source=path.name, title=title_of(path, text), text=text))

    if not documents:
        raise RuntimeError(f"知识库是空的：{directory}")
    return documents
