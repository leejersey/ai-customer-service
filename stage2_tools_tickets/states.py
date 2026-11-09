# -*- coding: utf-8 -*-
"""工单状态只允许按一条链往前走。

状态机不记住「这张工单现在是什么」。那是数据库某一行的事。
这里只回答：从当前这一格，能不能走到目标那一格。
"""

# 四个名字要和数据库里写进去的文字完全一致。多一个空格也会被当成不认识。
STATUS_NAMES = ("待处理", "处理中", "已解决", "已关闭")


class StatusMachine:
    """用一张字典记下「当前状态 → 唯一的下一步」。

    规则放在字典里，而不是写成一长串 if。
    改流程时改这张表，move 不用跟着加分支。
    """

    def __init__(self) -> None:
        # 已关闭没有下一格，所以不写这个键。没有这个键，就表示走不下去。
        self.allowed = {
            "待处理": "处理中",
            "处理中": "已解决",
            "已解决": "已关闭",
        }

    def chain_text(self) -> str:
        """顺着字典排出「待处理 → …」，给示例脚本打印。

        最多走名单那么多步。表如果被改成一个圈，这里会停，避免演示自己死循环。
        """
        steps = ["待处理"]
        current = "待处理"
        for _ in range(len(STATUS_NAMES)):
            if current not in self.allowed:
                break
            current = self.allowed[current]
            steps.append(current)
        return " → ".join(steps)

    def move(self, current: str, target: str) -> str:
        """允许就把目标状态交回去。不允许就抛出 ValueError，调用方必须看见失败。"""
        if current not in STATUS_NAMES:
            raise ValueError(f"不认识的状态：{current}")
        if target not in STATUS_NAMES:
            raise ValueError(f"不认识的状态：{target}")
        expected = self.allowed.get(current)
        if expected is None:
            raise ValueError(f"「{current}」已经是最后一步，不能再改成「{target}」")
        if target != expected:
            raise ValueError(
                f"不能从「{current}」直接改成「{target}」。下一步只能是「{expected}」"
            )
        return target
