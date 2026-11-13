# -*- coding: utf-8 -*-
"""阶段 4 · 示例 4：把检索结果拼成消息。分数不够就不拼。

不调用模型，所以没有密钥也能看见提示长什么样。

    python stage4_rag/04_build_prompt.py

导读：stage4_rag/docs/04_prompt.md
"""

from answering import prepare
from prompting import NOT_FOUND, SCORE_THRESHOLD
from retrieve import build_index


def show(index, question: str) -> None:
    hits = index.search(question, top_k=3)
    plan = prepare(question, hits, SCORE_THRESHOLD)
    print(f"问题：{question}")
    print(f"最高分：{plan['best_score']:.4f}    阈值：{SCORE_THRESHOLD}")
    if not plan["call_model"]:
        print(f"不把资料交给模型。直接回答：{plan['answer']}")
        print()
        return
    print("最高分够了。下面是将要发送的 messages。")
    print()
    for message in plan["messages"]:
        print(f"----- role={message['role']} -----")
        print(message["content"])
        print()


def main() -> None:
    index = build_index()
    print(f"资料没写到时，固定回答这八个字：{NOT_FOUND}")
    print("够分才拼提示。不够分就不要请模型发挥。")
    print()
    show(index, "耳机保修多久")
    show(index, "你们今年招实习生吗")
    print("提示拼装完成")


if __name__ == "__main__":
    main()
