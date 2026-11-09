# -*- coding: utf-8 -*-
"""SQLite 文件：两张表，以及打开、关闭、重建。

工具函数的参数要和 JSON Schema 一致，不能多一个「数据库路径」。
路径放在 location 这个对象上。测试换文件时改对象里面的 path，
已经 import 过这个模块的函数读到的仍是同一个对象。
"""

import sqlite3
from datetime import datetime
from pathlib import Path


# 跟这个文件走，不跟你执行命令时的当前目录走。
DATA_DIR = Path(__file__).resolve().parent / "data"


class DatabaseLocation:
    """数据库文件放在哪。

    若只放一个字符串，函数里写 `from db import DB_PATH` 会拿走当时的值，
    之后再给全局变量重新赋值，那些函数看不见。放进对象里，改的是对象的属性。
    """

    def __init__(self, path: Path) -> None:
        self.path = Path(path)


location = DatabaseLocation(DATA_DIR / "shop.db")


def use_database(path: Path) -> None:
    """离线演示换一个文件，避免把命令行客服已经记下的工单清掉。"""
    location.path = Path(path)


def now_text() -> str:
    """当前当地时间，存成文本。

    SQLite 这一课不依赖单独的日期类型。格式固定以后，按字符串排序就是按时间排序。
    用本机时间，是为了和你看屏幕的钟对得上。
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class ShopConnection:
    """进入 with 时打开，离开时提交并关闭。

    sqlite3 自带的 with 只会提交或回滚，不会 close。
    练习脚本反复开关，不关掉的话文件会一直被占用。
    """

    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self.connection = None

    def __enter__(self):
        self.connection = sqlite3.connect(self.path)
        # 按列名取值。换了 SELECT 的列顺序，后面的代码也不用跟着数下标。
        self.connection.row_factory = sqlite3.Row
        return self.connection

    def __exit__(self, exc_type, exc, tb) -> bool:
        if self.connection is None:
            return False
        try:
            if exc_type is None:
                self.connection.commit()
            else:
                # 中间失败时不要把半截 INSERT 留在文件里。
                self.connection.rollback()
        finally:
            self.connection.close()
            self.connection = None
        # False：异常继续抛出去。关掉连接不等于问题已经处理完。
        return False


# 订单号用 TEXT。阶段 1 的正则交回来的是字符串。存成整数的话，前导零会丢。
# 工单的 order_id 允许空字符串：投诉可以先没有订单。空字符串不是一张订单，所以不加外键。
SCHEMA_SQL = """
CREATE TABLE orders (
    order_id TEXT PRIMARY KEY,
    user_name TEXT NOT NULL,
    product TEXT NOT NULL,
    amount_yuan INTEGER NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name TEXT NOT NULL,
    order_id TEXT NOT NULL DEFAULT '',
    ticket_type TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""

# 这些订单号都能被阶段 1 的正则抽出来：没有标签时至少 5 位数字。
# 用字典而不是只靠位置，是为了读代码的人能看见 10086 是订单号。
SEED_ORDERS = [
    {
        "order_id": "10086",
        "user_name": "演示用户甲",
        "product": "星河蓝牙耳机",
        "amount_yuan": 299,
        "status": "已发货",
    },
    {
        "order_id": "20001888",
        "user_name": "演示用户乙",
        "product": "星河机械键盘",
        "amount_yuan": 459,
        "status": "已签收",
    },
    {
        "order_id": "30021",
        "user_name": "演示用户甲",
        "product": "星河鼠标",
        "amount_yuan": 129,
        "status": "待发货",
    },
    {
        "order_id": "88421",
        "user_name": "演示用户丙",
        "product": "星河扩展坞",
        "amount_yuan": 189,
        "status": "已签收",
    },
]


def _insert_order(connection, order: dict, created_at: str) -> None:
    # 问号的顺序必须和下面元组的顺序一致。字典负责让人读得懂，元组负责喂给 SQL。
    connection.execute(
        """
        INSERT INTO orders (
            order_id, user_name, product, amount_yuan, status, created_at
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            order["order_id"],
            order["user_name"],
            order["product"],
            order["amount_yuan"],
            order["status"],
            created_at,
        ),
    )


def reset_database() -> Path:
    """删掉旧文件再建。示例要反复运行，工单编号才每次都从 1 开始。"""
    location.path.parent.mkdir(parents=True, exist_ok=True)
    if location.path.exists():
        location.path.unlink()
    created_at = now_text()
    with ShopConnection(location.path) as connection:
        # execute 一次只能跑一句。建表有两句，所以用 executescript。
        connection.executescript(SCHEMA_SQL)
        for order in SEED_ORDERS:
            _insert_order(connection, order, created_at)
    return location.path


def ensure_database() -> Path:
    """文件已经在就保持原样。命令行客服不能每次启动都把工单清空。"""
    if location.path.exists():
        return location.path
    return reset_database()


def require_database() -> Path:
    """先确认文件在，再连接。

    sqlite3.connect 在文件不存在时会新建一个空文件。
    空文件里没有表，接下来的 SELECT 会报 no such table，而且留下一个坏文件。
    """
    if not location.path.exists():
        raise FileNotFoundError(
            f"还没有数据库文件：{location.path}。"
            "请先运行 python stage2_tools_tickets/01_create_database.py"
        )
    return location.path


def list_tables() -> list[str]:
    require_database()
    with ShopConnection(location.path) as connection:
        rows = connection.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
        ).fetchall()
        names = []
        for row in rows:
            names.append(row["name"])
    return names


def fetch_orders() -> list[dict]:
    require_database()
    with ShopConnection(location.path) as connection:
        # 按文本排序，示例的打印顺序才固定。这不是业务上的「订单先后」。
        rows = connection.execute(
            """
            SELECT order_id, user_name, product, amount_yuan, status, created_at
            FROM orders
            ORDER BY order_id
            """
        ).fetchall()
        orders = []
        for row in rows:
            orders.append(dict(row))
    return orders


def count_tickets() -> int:
    require_database()
    with ShopConnection(location.path) as connection:
        row = connection.execute("SELECT COUNT(*) AS total FROM tickets").fetchone()
        total = int(row["total"])
    return total
