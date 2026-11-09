# -*- coding: utf-8 -*-
"""阶段 1 · 示例 2：让模型输出 JSON，并在格式坏掉时退回兜底。

没有密钥时会说明原因并结束，不会假装已经分类成功。
解析函数本身不联网，坏 JSON 的演示不需要密钥。

    python stage1_intent/02_llm_classifier.py

导读：stage1_intent/docs/02_llm_json.md
"""

import stage0_link

stage0_link.enable()

from config import create_client, describe_settings, print_api_error, require_settings
from llm_intent import api_key_ready, classify_by_llm, parse_model_output

# 这两段是模型可能吐出的坏文本。放在这里是为了没有密钥也能看见兜底。
BROKEN_SAMPLES = [
    "我觉得这是查订单。",
    '说明如下：{"intent":"查订单","confidence":0.9,"slots":{"order_id":"10086"}}',
    '{"intent":"不存在的意图","confidence":0.9,"slots":{"order_id":null}}',
]

LIVE_SAMPLES = [
    "订单号 10086 到哪了",
    "音质好不好",
    "我不想退款，只问保修多久",
]


def show_parse_samples() -> None:
    print("下面三段不调用模型，只检查解析。")
    for raw in BROKEN_SAMPLES:
        result = parse_model_output(raw)
        print(f"原文：{raw}")
        print(f"  结果：intent={result['intent']} source={result['source']} error={result.get('error')}")
        print()


def main() -> None:
    show_parse_samples()
    if not api_key_ready():
        print("没有可用的 DEEPSEEK_API_KEY，跳过真正的模型分类。")
        print("规则分类不需要密钥：python stage1_intent/01_rule_classifier.py")
        return
    settings = require_settings()
    describe_settings(settings)
    client = create_client(settings)
    print("下面三句会调用模型。回复被要求是 JSON，不是客服回答。")
    for text in LIVE_SAMPLES:
        try:
            result = classify_by_llm(client, settings.model, text)
        except Exception as error:
            print_api_error(error)
            print("这一句失败了，后面的句子还继续。")
            continue
        print(f"顾客：{text}")
        print(
            f"  意图={result['intent']}  置信度={result['confidence']}  "
            f"订单号={result['slots']['order_id']}  来源={result['source']}"
        )


if __name__ == "__main__":
    main()
