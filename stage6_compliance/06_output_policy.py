# -*- coding: utf-8 -*-
"""阶段 6 · 示例 6：回复不能越出政策，也不能泄露提示词或别人的号码。

这一课先不请模型当裁判。词表和正则就能挡住这几类。
改写会留下没问题的句子，并接上安全模板。整句都不能留时，只剩模板。

    python stage6_compliance/06_output_policy.py

导读：stage6_compliance/docs/06_policy.md
"""

from pipeline import review_output
from result import SAFE_REWRITE, format_result
from rules import load_rules

USER = "退货政策是几天"
GOOD = "未拆封可以七天无理由退货。来源：01_退换货政策.md"


def show(title: str, user_text: str, reply: str, book: dict) -> None:
    result = review_output(user_text, reply, book, None)
    print(title)
    print(f"  回复：{reply}")
    print(f"  结论：{format_result(result)}")
    print(f"  发出去：{result.text}")
    print()


def main() -> None:
    book = load_rules()
    print("输出审核发生在模型已经写完、顾客还没看到的时候。")
    print("judge_fn 这一课传 None，所以没有第二道模型裁判。")
    print()
    show("政策范围内", USER, GOOD, book)
    show(
        "绝对化承诺：删掉那一句，留下天数",
        USER,
        "未拆封可以七天无理由退货。我们保证100%成功。",
        book,
    )
    show(
        "答应赔偿：整句换成转人工",
        USER,
        "我可以承诺赔偿 500 元，马上打款。",
        book,
    )
    show(
        "索要密码",
        USER,
        "请把支付密码发给我，我帮你查。",
        book,
    )
    show(
        "背出系统提示里的句子",
        USER,
        "只能根据用户消息里资料下面的段落回答政策。",
        book,
    )
    show(
        "回复里出现顾客没说过的手机号",
        USER,
        "另一位顾客的手机号是13900001111。",
        book,
    )
    own = "我的手机是13800138000，帮我看看"
    show(
        "顾客自己的号码：打码，但不记成泄露他人",
        own,
        "已记下你的手机13800138000。",
        book,
    )
    print("安全模板里不包含词表原句，避免模板自己被下一轮词表命中。")
    print(f"  模板：{SAFE_REWRITE}")
    print()
    print("示例 6 看完了。下一课把等级、动作和审计日志放在一起。")


if __name__ == "__main__":
    main()
