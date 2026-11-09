# -*- coding: utf-8 -*-
"""阶段 2 · 示例 2：工单状态只能按一条链往前走。不需要数据库，也不需要密钥。

    python stage2_tools_tickets/02_ticket_states.py

导读：stage2_tools_tickets/docs/02_states.md
"""

from states import StatusMachine

# 前三行是合法的一步。后面是跳步、往回走、已经关闭、以及订单上的词。
CASES = [
    ("待处理", "处理中"),
    ("处理中", "已解决"),
    ("已解决", "已关闭"),
    ("待处理", "已解决"),
    ("待处理", "已关闭"),
    ("已解决", "处理中"),
    ("已关闭", "处理中"),
    ("已发货", "处理中"),
]


def main() -> None:
    machine = StatusMachine()
    print(f"合法方向：{machine.chain_text()}")
    print("订单上的「已发货」「已签收」不在这条链里。")
    print()
    for current, target in CASES:
        try:
            moved = machine.move(current, target)
        except ValueError as error:
            # 一个非法例子若把程序打死，后面的例子就看不到了。状态机本身仍然抛错。
            print(f"{current} → {target}：拒绝。{error}")
            continue
        print(f"{current} → {target}：允许，结果是 {moved}")


if __name__ == "__main__":
    main()
