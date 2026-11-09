# -*- coding: utf-8 -*-
"""让阶段 1 找得到阶段 0 的 config.py。

只 import 本文件不会改查找清单。必须先调用 enable()，再 import config。
"""

import sys
from pathlib import Path

# config.py 不在本文件旁边，而在上一级的 stage0_basics。
STAGE0_DIR = Path(__file__).resolve().parent.parent / "stage0_basics"


def enable() -> None:
    """把 stage0_basics 放进模块查找清单的最前面。"""
    folder = str(STAGE0_DIR)
    if folder in sys.path:
        return
    # 插到最前面，避免电脑上别的名叫 config 的库先被找到。
    sys.path.insert(0, folder)
