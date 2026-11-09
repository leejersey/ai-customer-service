# -*- coding: utf-8 -*-
"""阶段 1 · 示例 4：用标准答案给规则打分。有密钥时再给模型打分。

没有密钥也会打印规则的准确率和混淆情况。

    python stage1_intent/04_evaluate.py

导读：stage1_intent/docs/04_evaluate.md
"""

import json
from pathlib import Path

import stage0_link

stage0_link.enable()

from config import create_client, print_api_error, require_settings
from llm_intent import api_key_ready, classify_by_llm
from metrics import accuracy, confusion
from rule_intent import INTENTS, classify_by_rules

# 标准答案放在旁边的文件里，而不是写死在这段循环里。换句子时不用改计算代码。
DATA_PATH = Path(__file__).resolve().parent / "data" / "labeled_examples.json"


def load_rows(path: Path) -> list[dict]:
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, list) or len(data) == 0:
        raise ValueError("测试集必须是非空的列表")
    for item in data:
        assert isinstance(item, dict), "每一条都必须是对象"
        assert "text" in item and "intent" in item, "每一条都要有 text 和 intent"
        assert item["intent"] in INTENTS, f"未知意图：{item['intent']}"
    return data


def show_report(title: str, gold: list[str], predicted: list[str], texts: list[str]) -> None:
    score = accuracy(gold, predicted)
    correct = 0
    for index, expected in enumerate(gold):
        if predicted[index] == expected:
            correct = correct + 1
    print(f"{title}准确率：{correct}/{len(gold)} = {score:.2f}")
    print("和标准答案不一致的句子：")
    mismatches = 0
    for index, text in enumerate(texts):
        if gold[index] == predicted[index]:
            continue
        mismatches = mismatches + 1
        print(f"  {text} | 标准答案 {gold[index]} | 预测 {predicted[index]}")
    if mismatches == 0:
        print("  （没有）")
    print("混淆计数（标准答案 → 预测 → 次数）：")
    table = confusion(gold, predicted)
    for expected, row in table.items():
        parts = [f"{guess} {count} 次" for guess, count in row.items()]
        print(f"  {expected}：{', '.join(parts)}")
    print()


def main() -> None:
    rows = load_rows(DATA_PATH)
    texts = [item["text"] for item in rows]
    gold = [item["intent"] for item in rows]
    rule_predictions = [classify_by_rules(text)["intent"] for text in texts]
    show_report("规则", gold, rule_predictions, texts)
    # 规则若全对，这份测试集就没有暴露局限。全错则词表完全没用。
    rule_score = accuracy(gold, rule_predictions)
    assert 0.5 < rule_score < 1.0

    if not api_key_ready():
        print("没有可用的 DEEPSEEK_API_KEY，跳过模型准确率。规则结果仍然有效。")
        return

    settings = require_settings()
    client = create_client(settings)
    llm_predictions = []
    for text in texts:
        try:
            result = classify_by_llm(client, settings.model, text)
        except Exception as error:
            print_api_error(error)
            llm_predictions.append("其他")
            continue
        llm_predictions.append(result["intent"])
    show_report("模型", gold, llm_predictions, texts)
    print("对比时看两份准确率，也看同一句规则错、模型是否也错。")
    print("模型更高不表示它查过订单，只表示分类更接近这份标准答案。")


if __name__ == "__main__":
    main()
