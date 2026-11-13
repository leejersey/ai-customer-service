# -*- coding: utf-8 -*-
"""阶段 6 · 示例 5：让模型把回复分成通过、需修改、拒绝。

没有密钥时只演示解析。解析失败的默认是拒绝，不是通过。
有密钥时再请 DeepSeek 看两句已经写好的回复。裁判失败同样拒绝。

    python stage6_compliance/05_llm_judge.py

导读：stage6_compliance/docs/05_judge.md
"""

import stage6_link

stage6_link.enable()

from config import create_client, describe_settings, require_settings
from llm_intent import api_key_ready

from judge import CLOSED_REASON, hits_from_verdict, llm_judge, parse_verdict
from result import decide, format_result


CASES = (
    ('{"verdict":"通过","reason":"符合退货政策"}', "通过"),
    ('好的。{"verdict":"需修改","reason":"把天数说死了"}', "需修改"),
    ("```json\n{\"verdict\":\"拒绝\",\"reason\":\"在索要密码\"}\n```", "拒绝"),
    ("今天天气不错", "拒绝"),
    ('{"verdict":"也许","reason":"看情况"}', "拒绝"),
    ('{"verdict":"通过"}', "拒绝"),
    ("", "拒绝"),
)


def show_parse() -> None:
    print("== 解析 ==")
    print("合法的三个词会留下。废话、非法取值、缺字段、空文本都变成拒绝。")
    for raw, expected in CASES:
        judged = parse_verdict(raw)
        result = decide(hits_from_verdict(judged), "（回复略）")
        preview = raw.replace("\n", " ")
        if len(preview) > 42:
            preview = preview[:42] + "…"
        print(f"  原文：{preview}")
        print(f"  期望：{expected}    实际：{judged['verdict']}    ok={judged['ok']}")
        print(f"  收成：{format_result(result)}")
        assert judged["verdict"] == expected
        if judged["ok"]:
            assert result.action != "拦截" or expected == "拒绝"
        else:
            assert expected == "拒绝"
            assert result.action == "拦截"
            assert CLOSED_REASON in result.reason
        print()
    closed = parse_verdict("不是 JSON")
    print(f"关闭时的原因固定为：{CLOSED_REASON}")
    print(f"  实际原因：{closed['reason']}")
    print("  这里的动作是拦截，不是放行。审核失败不能默认放行。")
    print()


def show_live() -> None:
    print("== 调用 DeepSeek ==")
    if not api_key_ready():
        print("没有可用的 API 密钥。这一段跳过，不联网。")
        print("上面的解析已经可以说明失败时怎么关闭。")
        return
    settings = require_settings()
    describe_settings(settings)
    client = create_client(settings)
    samples = (
        "未拆封可以七天无理由退货。来源：01_退换货政策.md",
        "我们保证100%退款，并且马上打款到你的卡上。",
    )
    for reply in samples:
        judged = llm_judge(client, settings.model, reply)
        result = decide(hits_from_verdict(judged), reply)
        print(f"  回复：{reply}")
        print(f"  裁判：{judged['verdict']}  ok={judged['ok']}  {judged['reason']}")
        print(f"  收成：{format_result(result)}")
        print()


def main() -> None:
    print("裁判只输出 JSON。客服回复另算。解析由我们做，不交给模型自己解释。")
    print()
    show_parse()
    show_live()
    print("示例 5 看完了。下一课用规则检查回复有没有越出政策。")


if __name__ == "__main__":
    main()
