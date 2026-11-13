# -*- coding: utf-8 -*-
"""阶段 4 · 示例 1：把知识库里的文件读成文档。

只读不切。不检索，不调用模型，不需要密钥。

    python stage4_rag/01_load_documents.py

导读：stage4_rag/docs/01_load.md
"""

from documents import load_documents


def main() -> None:
    documents = load_documents()
    print(f"读到 {len(documents)} 份说明。")
    print("此时每一份仍是一整段字符串。下一课才按标题和字数切开。")
    print()
    for document in documents:
        print(document.source)
        print(f"  标题：{document.title}")
        print(f"  字数：{len(document.text)}")
    print()
    print("加载完成")


if __name__ == "__main__":
    main()
