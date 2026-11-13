# -*- coding: utf-8 -*-
"""把审核结论追加进 JSON Lines 文件。写入前再打一次码，调用方漏了也不会留下明文号码。

用追加而不是覆盖：每一轮是一行，下一次运行还在文件末尾。这个目录已在 .gitignore 里。
"""

import json
from datetime import datetime
from pathlib import Path

from pii import mask_value
from result import ComplianceResult

DATA_DIR = Path(__file__).resolve().parent / "data"
DEMO_LOG = DATA_DIR / "audit_demo.jsonl"
OFFLINE_LOG = DATA_DIR / "offline_audit.jsonl"


def now_text() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def append_record(path: Path, record: dict) -> None:
    """mode 是 a：文件已有内容时接在最后，没有文件时就创建。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    safe = mask_value(record)
    line = json.dumps(safe, ensure_ascii=False)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(line + "\n")


def append_audit(path: Path, result: ComplianceResult, checkpoint: str) -> None:
    append_record(
        path,
        {
            "time": now_text(),
            "checkpoint": checkpoint,
            "level": result.level,
            "action": result.action,
            "hits": list(result.hits),
            "reason": result.reason,
            "text": result.text,
        },
    )


def read_audit(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip() == "":
            continue
        rows.append(json.loads(line))
    return rows
