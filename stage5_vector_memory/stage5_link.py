# -*- coding: utf-8 -*-
"""让阶段 5 找得到前面阶段的配置、工单、检索和知识库。

只 import 本文件不会改查找清单。必须先调用 enable()，再 import 那些模块。
"""

import sys
from pathlib import Path

# 这些文件夹都不在阶段 5 旁边的默认查找范围里。
ROOT = Path(__file__).resolve().parent.parent
STAGE0_DIR = ROOT / "stage0_basics"
STAGE1_DIR = ROOT / "stage1_intent"
STAGE2_DIR = ROOT / "stage2_tools_tickets"
STAGE4_DIR = ROOT / "stage4_rag"


def enable() -> None:
    """把阶段 4、阶段 2、阶段 1、阶段 0 放进模块查找清单的最前面。"""
    # 后插入的会排到更前面。阶段 2 放最后插入，db、service 优先从阶段 2 找到。
    # 阶段 4 要排在阶段 2 后面插入之前，这样 retrieve、chunking 仍从阶段 4 找到。
    for folder in (STAGE4_DIR, STAGE0_DIR, STAGE1_DIR, STAGE2_DIR):
        text = str(folder)
        if text in sys.path:
            continue
        sys.path.insert(0, text)
