# -*- coding: utf-8 -*-
"""让阶段 6 找得到前面阶段的配置、工单和向量客服。

只 import 本文件不会改查找清单。必须先调用 enable()，再 import 那些模块。
示例 1 到 7 和示例 9 不调用它：审核本身只用标准库。
示例 8 的命令行客服才需要阶段 5。
"""

import sys
from pathlib import Path

# 这些文件夹都不在阶段 6 旁边的默认查找范围里。
ROOT = Path(__file__).resolve().parent.parent
STAGE0_DIR = ROOT / "stage0_basics"
STAGE1_DIR = ROOT / "stage1_intent"
STAGE2_DIR = ROOT / "stage2_tools_tickets"
STAGE4_DIR = ROOT / "stage4_rag"
STAGE5_DIR = ROOT / "stage5_vector_memory"


def enable() -> None:
    """把阶段 5、4、2、1、0 放进模块查找清单。

    后插入的会排到更前面。阶段 2 放最后插入，db 和 service 优先从阶段 2 找到。
    """
    for folder in (STAGE5_DIR, STAGE4_DIR, STAGE0_DIR, STAGE1_DIR, STAGE2_DIR):
        text = str(folder)
        if text in sys.path:
            continue
        sys.path.insert(0, text)
