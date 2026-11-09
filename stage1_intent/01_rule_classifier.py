# -*- coding: utf-8 -*-
"""阶段 1 · 示例 1：用关键词猜意图。

先运行（不需要 API 密钥）：

    python stage1_intent/01_rule_classifier.py

再读：stage1_intent/docs/01_rules.md
"""

from rule_intent import classify_by_rules

# 这几句是故意挑选的。有的词能对上，有的句子意思对、词却对不上，有的词在否定里。
SAMPLES = [
    "转人工",
    "订单号：10086 的物流到哪了",
    "我要退货",
    "这款耳机怎么连接蓝牙",
    "音质好不好",
    "我不想退款，只问保修多久",
    "今天天气怎么样",
    "你好呀",
]


def main() -> None:
    print("规则分类不联网。命中靠的是词出现过，不是听懂了这句话。")
    print()
    for text in SAMPLES:
        result = classify_by_rules(text)
        order_id = result["slots"]["order_id"]
        print(f"顾客：{text}")
        print(
            f"  意图={result['intent']}  置信度={result['confidence']}  "
            f"订单号={order_id}  来源={result['source']}"
        )
    print()
    print("请特别看最后四句：")
    print("- 「音质好不好」是在咨询，但词表里没有这些字，会落到「其他」。")
    print("- 「不想退款」里仍然有「退款」，规则分不清否定。")
    print("- 「怎么样」里面含有「怎么」，闲聊会被误判成咨询。")
    print("- 「你好呀」没有任何关键词，才落到「其他」，置信度也更低。")


if __name__ == "__main__":
    main()
