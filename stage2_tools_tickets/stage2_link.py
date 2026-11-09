# -*- coding: utf-8 -*-
"""让阶段 2 找得到阶段 0 的 config.py 和阶段 1 的意图模块。

只 import 本文件不会改查找清单。必须先调用 enable()，再 import config 或 rule_intent。
"""

import sys
from pathlib import Path

# 这两个文件夹都不在阶段 2 旁边的默认查找范围里。
ROOT = Path(__file__).resolve().parent.parent
STAGE0_DIR = ROOT / "stage0_basics"
STAGE1_DIR = ROOT / "stage1_intent"


def enable() -> None:
    """把阶段 1 和阶段 0 放进模块查找清单的最前面。"""
    # 后插入的会排到更前面。阶段 1 放最后插入，这样 rule_intent 优先从阶段 1 找到。
    for folder in (STAGE0_DIR, STAGE1_DIR):
        text = str(folder)
        if text in sys.path:
            continue
        sys.path.insert(0, text)
