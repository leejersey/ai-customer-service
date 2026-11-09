# -*- coding: utf-8 -*-
"""不联网的检查。直接运行：

    python stage1_intent/test_rules.py

断言失败时程序会停，并显示 AssertionError。
"""

from llm_intent import parse_model_output
from rule_intent import classify_by_rules


def test_transfer_keyword() -> None:
    result = classify_by_rules("转人工")
    assert result["intent"] == "转人工"


def test_order_id_and_intent() -> None:
    result = classify_by_rules("订单号：10086 到哪了")
    assert result["intent"] == "查订单"
    assert result["slots"]["order_id"] == "10086"


def test_paraphrase_misses_keywords() -> None:
    # 这句话是咨询，但词表里没有「音质」。记录局限，不要在这里改成期望「咨询」。
    result = classify_by_rules("音质好不好")
    assert result["intent"] == "其他"


def test_bad_json_falls_back() -> None:
    result = parse_model_output("我觉得这是查订单。")
    assert result["source"] == "fallback"
    assert result["intent"] == "其他"


def test_json_with_extra_words() -> None:
    raw = '好的 {"intent":"退款","confidence":0.8,"slots":{"order_id":null}}'
    result = parse_model_output(raw)
    assert result["source"] == "llm"
    assert result["intent"] == "退款"
    assert result["slots"]["order_id"] is None


if __name__ == "__main__":
    test_transfer_keyword()
    test_order_id_and_intent()
    test_paraphrase_misses_keywords()
    test_bad_json_falls_back()
    test_json_with_extra_words()
    print("规则和解析测试通过")
