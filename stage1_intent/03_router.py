# -*- coding: utf-8 -*-
"""阶段 1 · 示例 3：意图决定走哪一个函数。不需要 API 密钥。

    python stage1_intent/03_router.py

导读：stage1_intent/docs/03_router.md
"""

from router import route_by_rules

SAMPLES = [
    "转人工",
    "订单号：10086 到哪了",
    "我要退货",
    "音质好不好",
]


def main() -> None:
    print("这一步仍然不联网。分类用规则，回复用写死的函数。")
    print()
    for text in SAMPLES:
        result, reply = route_by_rules(text)
        print(f"顾客：{text}")
        print(f"  意图={result['intent']}")
        print(f"  回复：{reply}")
        print()
    print("「音质好不好」会被规则判成其他，所以回复也是其他那一句。")
    print("路由器没有纠正分类。它只负责：已经判成什么，就调用哪一个函数。")


if __name__ == "__main__":
    main()
