# -*- coding: utf-8 -*-
"""风险等级、动作，以及把多条命中收成一份 ComplianceResult。

等级和动作用枚举，是为了词表里写错一个字时不会悄悄变成「放行」。
交出去的 dataclass 仍用中文文本，审计日志里读得懂。
"""

from dataclasses import dataclass
from enum import Enum


class RiskLevel(Enum):
    LOW = "低"
    MEDIUM = "中"
    HIGH = "高"


class ReviewAction(Enum):
    ALLOW = "放行"
    REWRITE = "改写"
    HANDOFF = "转人工"
    BLOCK = "拦截"


# 数字越大越严重。同时命中时留下更严重的那一个。
# 拦截比转人工更靠前：已经不该把这句话继续往下送。
LEVEL_RANK = {RiskLevel.LOW: 1, RiskLevel.MEDIUM: 2, RiskLevel.HIGH: 3}
ACTION_RANK = {
    ReviewAction.ALLOW: 0,
    ReviewAction.REWRITE: 1,
    ReviewAction.HANDOFF: 2,
    ReviewAction.BLOCK: 3,
}

# 模板故意避开词表里的原句。模板里如果出现「承诺赔偿」，再审一遍会把自己拦住。
SAFE_REWRITE = "以店铺公示的退换货政策为准。对话里只能登记工单，不能答应赔钱，也不能说出退款的具体数字或到账时间。"
SAFE_HANDOFF = "已为你转接人工客服。在人工接入前，我不能答应赔钱，也不能说出退款的具体数字。"
SAFE_BLOCK = "这个问题我不能继续回答。如需人工协助，请说「转人工」。"


@dataclass
class ComplianceResult:
    """一轮审核的结论。text 是审核之后可以拿去显示的那一句，不一定是原文。"""

    level: str
    hits: list[str]
    action: str
    text: str
    reason: str


def _as_level(text: str) -> RiskLevel:
    """词表里的等级写错时当成高，避免一个拼写错误把风险放掉。"""
    for item in RiskLevel:
        if item.value == text:
            return item
    return RiskLevel.HIGH


def _as_action(text: str) -> ReviewAction:
    """动作写错时当成拦截。不认识的动作不能默认放行。"""
    for item in ReviewAction:
        if item.value == text:
            return item
    return ReviewAction.BLOCK


def _rewrite(text: str, found: list[dict]) -> str:
    """只删掉含有词表原词的句子。模型给出的理由通常不在原文里，那种情况整句换模板。"""
    for item in found:
        if item["category"] == "模型审核":
            return SAFE_REWRITE
    words = []
    for item in found:
        word = item.get("word") or ""
        if word:
            words.append(word)
    kept = []
    for piece in text.split("。"):
        if piece.strip() == "":
            continue
        if any(word in piece for word in words):
            continue
        kept.append(piece)
    if not kept:
        return SAFE_REWRITE
    return "。".join(kept) + "。" + SAFE_REWRITE


def _apply(action: ReviewAction, text: str, found: list[dict]) -> str:
    if action == ReviewAction.ALLOW:
        return text
    if action == ReviewAction.REWRITE:
        return _rewrite(text, found)
    if action == ReviewAction.HANDOFF:
        return SAFE_HANDOFF
    return SAFE_BLOCK


def decide(found: list[dict], text: str) -> ComplianceResult:
    """没有命中就是低和放行。有命中时，等级和动作各取最严重的一条。"""
    if not found:
        return ComplianceResult("低", [], "放行", text, "没有命中规则")
    known_levels = {item.value for item in RiskLevel}
    known_actions = {item.value for item in ReviewAction}
    levels = []
    actions = []
    for item in found:
        level = _as_level(item["level"])
        action = _as_action(item["action"])
        # 动作或等级不在四个词 / 三个词里时，整条抬到高并且拦截。
        if item["level"] not in known_levels or item["action"] not in known_actions:
            level = RiskLevel.HIGH
            action = ReviewAction.BLOCK
        levels.append(level)
        actions.append(action)
    level = max(levels, key=lambda item: LEVEL_RANK[item])
    action = max(actions, key=lambda item: ACTION_RANK[item])
    labels = []
    for item in found:
        labels.append(f"{item['category']}:{item['word']}")
    reason = "；".join(labels)
    shown = _apply(action, text, found)
    return ComplianceResult(level.value, labels, action.value, shown, reason)


def format_result(result: ComplianceResult) -> str:
    if result.hits:
        hit_text = "、".join(result.hits)
    else:
        hit_text = "无"
    return f"{result.level} / {result.action}  命中：{hit_text}"
