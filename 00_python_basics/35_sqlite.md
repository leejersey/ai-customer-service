# sqlite3：把表存在一个文件里

列表和字典在程序退出后就没了。阶段 2 的订单和工单要留在磁盘上，下次运行还在。SQLite 是 Python 标准库 `sqlite3` 就能打开的一种数据库：整个库通常就是一个文件。

阶段 2 用在 [建库](../stage2_tools_tickets/docs/01_database.md)。SQL 是你对这个文件说的几句固定格式的话。这一课只学四句：`CREATE`、`INSERT`、`SELECT`、`UPDATE`。

## 先用一句人话

建表是画空表格的栏目。插入是加一行。查询是按条件把行拿出来。更新是改某一格。栏目的名字和类型在建表时定好，后面每行都按这个填。

## 打个比方

`shop.db` 是一个抽屉里的账本。Python 字典是你手里的便签，合上程序便签就扔了。账本合上以后还在抽屉里。SQL 是账本封面规定的填写办法：先画栏目，再按行写，按条件翻，按格子改。

## 自己动手

在一个空目录里运行。跑完可以把 `demo.db` 删掉。

```python
import sqlite3

connection = sqlite3.connect("demo.db")
connection.execute(
    """
    CREATE TABLE goods (
        name TEXT PRIMARY KEY,
        price INTEGER NOT NULL
    )
    """
)
connection.execute(
    "INSERT INTO goods (name, price) VALUES (?, ?)",
    ("耳机", 299),
)
connection.commit()
row = connection.execute(
    "SELECT name, price FROM goods WHERE name = ?",
    ("耳机",),
).fetchone()
print(row[0], row[1])
connection.execute(
    "UPDATE goods SET price = ? WHERE name = ?",
    (259, "耳机"),
)
connection.commit()
row = connection.execute(
    "SELECT price FROM goods WHERE name = ?",
    ("耳机",),
).fetchone()
print(row[0])
connection.close()
```

预期：

```text
耳机 299
259
```

对照四句：

- `CREATE TABLE` 画出 `goods`。`TEXT` 是文本，`INTEGER` 是整数。`PRIMARY KEY` 是主键，同一张表里不能有两行同名的耳机。`NOT NULL` 表示这一格不能不填。
- `INSERT INTO ... VALUES` 加一行。`?` 是占位符，真正的值放在后面的元组里，按位置对上。
- `SELECT ... WHERE` 取出符合条件的行。`fetchone()` 拿一行。没有匹配时它交回 `None`。
- `UPDATE ... SET ... WHERE` 改格子。没有 `WHERE` 会把表里每一行都改掉。
- `commit()` 把这一批改动真正写进文件。不提交就 `close()`，这一轮的插入和更新会丢掉。

`("耳机",)` 末尾的逗号不能省。没有逗号时，圆括号只是把字符串包起来，不是元组。`execute` 会报参数不够或类型不对。两个以上的值不用纠结这个逗号，`("耳机", 299)` 已经是元组。

阶段 2 还把 `row_factory` 设成 `sqlite3.Row`，于是可以写 `row["name"]`，再 `dict(row)` 收成普通字典。默认情况下一行是元组，只能写 `row[0]`。

`execute` 一次一句。两句建表语句连在一个字符串里时，用 `executescript`。

## 不要把值拼进 SQL 句子

占位符是为了让值保持「值」，而不是变成句子的一部分。下面这种写法不要用：

```python
name = "耳机"
connection.execute(f"SELECT price FROM goods WHERE name = '{name}'")
```

这一次碰巧能查到。若 `name` 来自别人输入的 `耳机' OR '1'='1`，条件的形状就被改掉了。更严重的输入还可能带上 `DELETE`。`?` 不会把输入当成 SQL，只当成要比较的文本。

## 常见错误

表已经存在时再 `CREATE`：

```text
sqlite3.OperationalError: table goods already exists
```

练习时先删掉 `demo.db`，或在建表前 `DROP TABLE IF EXISTS goods`。阶段 2 的示例是删掉整个库文件再创建，这样旧工单也不会残留。

查询一个没有的表：

```text
sqlite3.OperationalError: no such table: goods
```

`sqlite3.connect` 在文件不存在时会新建一个空文件，里面还没有表。要先 `CREATE`，再 `SELECT`。

`WHERE` 忘了写，`UPDATE` 把所有商品价格都改了。改完用 `SELECT` 把整张表打出来核对，不要只看「语句没报错」。

## 练习

1. `("耳机",)` 和 `("耳机")` 有什么差别？
2. 为什么价格用 `INTEGER`，阶段 2 的订单号却用 `TEXT`？
3. `fetchone()` 在没有这一行时交回什么？

## 答案

1. 有逗号才是只有一个元素的元组。没有逗号就是字符串本身。`execute` 的第二个参数要的是一串参数。
2. 价格要拿来当整数。订单号要和正则抽出来的字符串一致，前导零也不能丢，所以用文本。
3. `None`。没查到是一种正常结果，不是自动抛出的异常。阶段 2 把它收成 `{"ok": False, ...}`。
