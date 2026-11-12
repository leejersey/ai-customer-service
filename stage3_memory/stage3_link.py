# -*- coding: utf-8 -*-
"""让阶段 3 找得到阶段 0 的配置、阶段 1 的意图和阶段 2 的工单。

只 import 本文件不会改查找清单。必须先调用 enable()，再 import 那些模块。
"""

import sys
from pathlib import Path

# 这三个文件夹都不在阶段 3 旁边的默认查找范围里。
ROOT = Path(__file__).resolve().parent.parent
STAGE0_DIR = ROOT / "stage0_basics"
STAGE1_DIR = ROOT / "stage1_intent"
STAGE2_DIR = ROOT / "stage2_tools_tickets"


def enable() -> None:
    """把阶段 2、阶段 1、阶段 0 放进模块查找清单的最前面。"""
    # 后插入的会排到更前面。阶段 2 放最后插入，db、service 优先从阶段 2 找到。
    for folder in (STAGE0_DIR, STAGE1_DIR, STAGE2_DIR):
        text = str(folder)
        if text in sys.path:
            continue
        sys.path.insert(0, text)
