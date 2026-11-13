# -*- coding: utf-8 -*-
"""阶段 6 · 示例 7：ComplianceResult、风险等级，以及一行一条的审计日志。

日志写在 stage6_compliance/data/audit_demo.jsonl。该目录已忽略，不要提交。
故意把明文号码放进记录，读回来时应只剩打码。这是在锁「写入时还会再打一次」。

    python stage6_compliance/07_risk_and_audit.py

导读：stage6_compliance/docs/07_risk.md
"""

from dataclasses import asdict

from audit import DEMO_LOG, append_record, read_audit
from result import ComplianceResult, decide, format_result

RAW_PHONE = "13800138000"


def main() -> None:
    if DEMO_LOG.exists():
        DEMO_LOG.unlink()

    print("没有命中：低，放行，原文保持不变。")
    clear = decide([], "未拆封可以七天无理由退货。")
    print(f"  {format_result(clear)}")
    print(f"  {clear}")
    print()

    print("只有绝对化承诺：中，改写。")
    medium = decide(
        [{"category": "绝对化承诺", "word": "保证100%", "level": "中", "action": "改写"}],
        "我们保证100%成功。",
    )
    print(f"  {format_result(medium)}")
    print()

    print("中和高同时出现：等级取高，动作取更严重的拦截。")
    mixed = decide(
        [
            {"category": "绝对化承诺", "word": "保证100%", "level": "中", "action": "改写"},
            {"category": "泄露系统提示", "word": "系统提示片段", "level": "高", "action": "拦截"},
        ],
        "我们保证100%成功。",
    )
    print(f"  {format_result(mixed)}")
    print("  发出去的是拦截模板，不是改写后的半句。")
    print()

    print("词表里写了一个不认识的动作：不能当成放行。")
    unknown = decide(
        [{"category": "试探", "word": "样例", "level": "低", "action": "放行吧"}],
        "随便一句",
    )
    print(f"  {format_result(unknown)}")
    print()

    print("dataclass 可以收成普通字典，再写进日志。")
    sample = ComplianceResult("低", [], "放行", "没有号码的一句", "没有命中规则")
    print(f"  {asdict(sample)}")
    print()

    print("—— 审计日志 ——")
    append_record(
        DEMO_LOG,
        {
            "checkpoint": "input",
            "text": f"请记住手机{RAW_PHONE}",
            "note": "调用方这一次忘了打码",
        },
    )
    append_record(DEMO_LOG, asdict(clear) | {"checkpoint": "output"})
    rows = read_audit(DEMO_LOG)
    print(f"  文件：{DEMO_LOG}")
    print(f"  行数：{len(rows)}")
    for row in rows:
        print(f"  {row}")
    blob = DEMO_LOG.read_text(encoding="utf-8")
    print(f"  文件中还有明文手机号吗：{RAW_PHONE in blob}")
    print("  应是 False。追加写入不会把上一行冲掉，所以两行都在。")
    print()
    print("示例 7 看完了。下一课把审核套到阶段 5 的客服外面。")


if __name__ == "__main__":
    main()
