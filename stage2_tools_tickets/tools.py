# -*- coding: utf-8 -*-
"""四个工具：查订单、建工单、改状态、查工单。

这里不调用大模型。模型只会提出「请执行某个名字」，真正动手的是这些函数。
退款工单不会打款，只是在表里插一行。
"""

import db
from states import StatusMachine

# 和 schema.py 里的枚举是同一组字。示例 7 会检查两边没有各写各的。
TICKET_TYPES = ("退款", "投诉", "转人工")

# 默认顾客。真实系统会知道是谁登录的。练习项目没有登录。
DEFAULT_USER_NAME = "演示用户"

# 规则不变，不必每个请求都新建一台状态机。
_MACHINE = StatusMachine()


def _clean_text(value) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _as_ticket_id(ticket_id):
    """工单编号在 JSON 里有时是数字，有时是字符串。库里的主键是整数。"""
    # JSON 的 true 在 Python 里是 bool，而 bool 也算 int。int(True) 会变成 1，会改错工单。
    if isinstance(ticket_id, bool) or ticket_id is None:
        return None
    if isinstance(ticket_id, int):
        return ticket_id
    text = str(ticket_id).strip()
    if text.isdigit():
        return int(text)
    return None


def _load_ticket(connection, ticket_id: int) -> dict | None:
    row = connection.execute(
        """
        SELECT id, user_name, order_id, ticket_type, description, status, created_at, updated_at
        FROM tickets
        WHERE id = ?
        """,
        (ticket_id,),
    ).fetchone()
    if row is None:
        return None
    return dict(row)


def query_order(order_id: str) -> dict:
    """按订单号查一行。没查到是正常业务结果，返回 ok 为假，不抛异常。"""
    text = _clean_text(order_id)
    if text == "":
        return {"ok": False, "error": "缺少订单号"}
    try:
        db.require_database()
    except FileNotFoundError as error:
        return {"ok": False, "error": str(error)}
    with db.ShopConnection(db.location.path) as connection:
        row = connection.execute(
            """
            SELECT order_id, user_name, product, amount_yuan, status, created_at
            FROM orders
            WHERE order_id = ?
            """,
            (text,),
        ).fetchone()
        if row is None:
            return {"ok": False, "error": f"没有找到订单 {text}"}
        return {"ok": True, "order": dict(row)}


def create_ticket(
    ticket_type: str,
    description: str,
    user_name: str = DEFAULT_USER_NAME,
    order_id: str = "",
) -> dict:
    """插入一张工单，初始状态固定为待处理。

    user_name 和 order_id 有默认值：调用时可以不传。
    默认值只在「这个名字根本没出现」时生效。传了空字符串仍要再判断一次。
    状态不交给调用方填，避免新建时直接写成已关闭。
    """
    kind = _clean_text(ticket_type)
    body = _clean_text(description)
    name = _clean_text(user_name) or DEFAULT_USER_NAME
    order_text = _clean_text(order_id)
    if kind not in TICKET_TYPES:
        return {"ok": False, "error": f"不认识的工单类型：{kind}"}
    if body == "":
        return {"ok": False, "error": "工单需要一段描述"}
    if kind == "退款":
        if order_text == "":
            return {"ok": False, "error": "退款工单需要订单号"}
        # 先查订单。没有这张订单就不要留下一张无法对账的退款单。
        found = query_order(order_text)
        if not found["ok"]:
            return {"ok": False, "error": f"没有订单 {order_text}，还不能建退款工单"}
    try:
        db.require_database()
    except FileNotFoundError as error:
        return {"ok": False, "error": str(error)}
    created_at = db.now_text()
    with db.ShopConnection(db.location.path) as connection:
        cursor = connection.execute(
            """
            INSERT INTO tickets (
                user_name, order_id, ticket_type, description, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (name, order_text, kind, body, "待处理", created_at, created_at),
        )
        # 编号由数据库分配。再查一次，返回的字典和表里的行是同一份。
        ticket = _load_ticket(connection, int(cursor.lastrowid))
    return {"ok": True, "ticket": ticket}


def update_ticket_status(ticket_id: int, status: str) -> dict:
    """只按状态机允许的那一步更新。非法流转不写库。"""
    number = _as_ticket_id(ticket_id)
    if number is None or number <= 0:
        return {"ok": False, "error": "工单编号必须是正整数"}
    target = _clean_text(status)
    try:
        db.require_database()
    except FileNotFoundError as error:
        return {"ok": False, "error": str(error)}
    try:
        with db.ShopConnection(db.location.path) as connection:
            current_row = _load_ticket(connection, number)
            if current_row is None:
                return {"ok": False, "error": f"没有找到工单 {number}"}
            previous = current_row["status"]
            try:
                moved = _MACHINE.move(previous, target)
            except ValueError as error:
                # 模型读不懂异常对象。把原因收成字典，调用方可以回传给模型。
                return {"ok": False, "error": str(error)}
            updated_at = db.now_text()
            connection.execute(
                """
                UPDATE tickets
                SET status = ?, updated_at = ?
                WHERE id = ?
                """,
                (moved, updated_at, number),
            )
            ticket = _load_ticket(connection, number)
    except FileNotFoundError as error:
        return {"ok": False, "error": str(error)}
    return {"ok": True, "previous_status": previous, "ticket": ticket}


def get_ticket(ticket_id: int) -> dict:
    """按编号读一张工单。"""
    number = _as_ticket_id(ticket_id)
    if number is None or number <= 0:
        return {"ok": False, "error": "工单编号必须是正整数"}
    try:
        db.require_database()
    except FileNotFoundError as error:
        return {"ok": False, "error": str(error)}
    with db.ShopConnection(db.location.path) as connection:
        ticket = _load_ticket(connection, number)
    if ticket is None:
        return {"ok": False, "error": f"没有找到工单 {number}"}
    return {"ok": True, "ticket": ticket}


# 值是函数本身，没有括号。键必须和 schema.py 里的 name 一模一样。
# 模型说出别的名字时，下面的 .get 会得到 None，不会去执行任意函数。
TOOL_FUNCTIONS = {
    "query_order": query_order,
    "create_ticket": create_ticket,
    "update_ticket_status": update_ticket_status,
    "get_ticket": get_ticket,
}
