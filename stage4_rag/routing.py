# -*- coding: utf-8 -*-
"""政策问句走知识库，查订单和办工单仍走阶段 2 的工具。

「退货政策是几天」和「我要退货」都含有退货。前者要的是规定，后者要的是工单。
只靠阶段 1 的关键词，两句都会进退款。这里多看一句是在问规定，还是在要求办理。
"""

import re

import stage4_link

stage4_link.enable()

from rule_intent import classify_by_rules

# 阶段 2 用更完整的句式执行。这里只决定要不要把这句话交给它。
_TICKET_COMMAND = re.compile(r"工单\s*\d+")

# 这些词出现时，多半是在问本店怎么规定，而不是在要求立刻建单。
_POLICY_CUES = (
    "政策",
    "规定",
    "几天",
    "多久",
    "是否",
    "能不能",
    "可以吗",
    "怎么",
    "如何",
    "无理由",
    "运费",
    "包邮",
    "什么条件",
)

# 这些词出现时，人已经在办退款，不要改去念政策。
_FILE_CUES = ("我要退", "帮我退", "申请退", "给我退")


def _asking_policy(text: str) -> bool:
    for cue in _POLICY_CUES:
        if cue in text:
            return True
    return False


def _asking_to_file(text: str) -> bool:
    for cue in _FILE_CUES:
        if cue in text:
            return True
    return False


def choose_path(text: str) -> str:
    """返回 tools 或 rag。

    tools：阶段 2 的查订单、退款、投诉、转人工、工单命令。
    rag：政策、常见问题和其余不办工单的句子。答不答得上，由检索分数再决定。
    """
    if _TICKET_COMMAND.search(text):
        return "tools"
    intent = classify_by_rules(text)["intent"]
    if intent in {"查订单", "投诉", "转人工"}:
        return "tools"
    if intent == "退款":
        if _asking_policy(text) and not _asking_to_file(text):
            return "rag"
        return "tools"
    return "rag"
