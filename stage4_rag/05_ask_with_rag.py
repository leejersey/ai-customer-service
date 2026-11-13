# -*- coding: utf-8 -*-
"""阶段 4 · 示例 5：检索之后，够分才调用 DeepSeek。

没有密钥时仍打印检索和提示，不联网。

    python stage4_rag/05_ask_with_rag.py

导读：stage4_rag/docs/05_ask.md
"""

import stage4_link

stage4_link.enable()

from answering import complete_with_client, prepare
from config import create_client, describe_settings, print_api_error, require_settings
from llm_intent import api_key_ready
from prompting import NOT_FOUND, SCORE_THRESHOLD
from retrieve import build_index

# 三条够看清：一条政策、一条知识库明确说「不写」、一条完全没写。
QUESTIONS = (
    "耳机保修多久",
    "星河耳机卖多少钱",
    "你们今年招实习生吗",
)


def main() -> None:
    index = build_index()
    use_model = api_key_ready()
    client = None
    model = None
    if use_model:
        settings = require_settings()
        describe_settings(settings)
        client = create_client(settings)
        model = settings.model
        print("密钥可用。最高分达到阈值时才会请求对话接口。")
    else:
        print("没有可用的 API 密钥。这一课只打印检索和提示，不调用模型。")
    print(f"阈值：{SCORE_THRESHOLD}")
    print()

    for question in QUESTIONS:
        hits = index.search(question, top_k=3)
        plan = prepare(question, hits, SCORE_THRESHOLD)
        print(f"问题：{question}")
        print(f"最高分：{plan['best_score']:.4f}  {hits[0].source} 第{hits[0].index}段")
        if not plan["call_model"]:
            print(f"回答：{plan['answer']}")
            print()
            continue
        if client is None or model is None:
            print("回答：（跳过生成。有密钥时，模型只能根据下面的资料说话。）")
            print(plan["messages"][1]["content"])
            print()
            continue
        try:
            answer = complete_with_client(client, model, plan["messages"])
        except Exception as error:
            print_api_error(error)
            answer = NOT_FOUND
            print("这一问没有拿到模型回复。")
        print(f"回答：{answer}")
        print()
    print("问答结束")


if __name__ == "__main__":
    main()
