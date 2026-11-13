# -*- coding: utf-8 -*-
"""阶段 6 · 示例 2：用 JSON 词表做敏感词检查，并看见误报和漏报。

词表在 rules.json。改完保存，再运行本脚本，不用改 Python。
绝对化承诺只检查输出。顾客问「你们保证100%吗」不应被当成客服在承诺。

    python stage6_compliance/02_sensitive_words.py

导读：stage6_compliance/docs/02_rules.md
"""

from result import decide, format_result
from rules import has_word, load_rules, sensitive_hits


def show(title: str, text: str, where: str, book: dict) -> None:
    result = decide(sensitive_hits(text, book, where), text)
    print(f"{title}")
    print(f"  句子：{text}")
    print(f"  检查位置：{where}")
    print(f"  结论：{format_result(result)}")
    print()


def main() -> None:
    book = load_rules()
    print(f"规则文件：stage6_compliance/rules.json")
    print("词写的是短语。单个「垃圾」或单个「永不」不在表里。")
    print()

    show("辱骂，输入就要转人工", "你们这些垃圾客服", "input", book)
    show("竞品诋毁，不让这句话进入回复", "别家都是骗子，买我们的", "output", book)
    show("绝对化承诺只查输出", "我们保证100%不会出问题", "output", book)
    show("同一句放在输入里不查「保证100%」", "你们保证100%吗", "input", book)
    show("正常的退货问题", "未拆封可以七天无理由退货吗", "output", book)

    print("—— 漏报 ——")
    print("「废物」中间多一个空格，短语对不上，规则放行。人换种骂法也会漏。")
    missed = "你们这些废 物"
    missed_result = decide(sensitive_hits(missed, book, "input"), missed)
    print(f"  句子：{missed}")
    print(f"  结论：{format_result(missed_result)}")
    print("「永不关机」不含「永不出现」，所以也不命中。词如果改成单个「永不」，这句就会误伤。")
    battery = "这款耳机永不关机吗"
    print(f"  句子：{battery}")
    print(f"  结论：{format_result(decide(sensitive_hits(battery, book, 'output'), battery))}")
    print()

    print("—— 误报：假如有人把词改成单个「垃圾」——")
    print("下面这组词不在 rules.json 里，只在这次运行的内存里。")
    too_wide = ["垃圾"]
    question = "垃圾分类怎么预约"
    print(f"  句子：{question}")
    print(f"  过宽的词是否命中：{has_word(question, too_wide)}")
    print(f"  正式词表是否命中：{has_word(question, ['垃圾客服', '废物'])}")
    print("正式词表不命中。所以表里写「垃圾客服」，不写「垃圾」。")
    print()
    print("示例 2 看完了。下一课用正则把号码打码。")


if __name__ == "__main__":
    main()
