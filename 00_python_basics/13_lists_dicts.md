# 列表和字典：有顺序的一排，和按名字取的格子

模型不接收「一整段没有结构的聊天记录」。它要一个列表，列表里每个元素是一个字典。`01_hello_llm.py` 里第一次出现就是：

```python
messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": USER_PROMPT},
]
```

方括号 `[]` 做列表。花括号 `{}` 在这里做字典。字典的花括号里是一对一对的 `键: 值`。

## 打个比方

列表是一叠编了号的纸，编号从 0 开始，不是从 1。第一张纸的编号是 0。你说「第 0 张」不是说没有，是说最上面那张。

字典是一张表格的一行，每一格有栏名。`role` 这一栏填 `system`，`content` 这一栏填提示词。栏名叫键，格子里的东西叫值。

## 列表：创建、下标、追加、长度

```python
papers = ["封面", "顾客的话"]
print(papers[0])
print(papers[1])
print(len(papers))
papers.append("专家的回复")
print(papers)
print(len(papers))
```

预期：

```text
封面
顾客的话
2
['封面', '顾客的话', '专家的回复']
3
```

`append` 改的是原来那一叠，加在末尾。`len` 是张数。

最后一张也可以写成 `papers[-1]`，不用先数一共几张。失败时我们 `pop()`，默认拿掉最后一张：

```python
papers.pop()
print(papers)
```

预期变回两张：`['封面', '顾客的话']`。

下标超出范围：

```python
print(papers[9])
```

```text
IndexError: list index out of range
```

所以取 `response.choices[0]` 之前，要先确认这叠纸不是空的。空的时候连 `[0]` 都不存在。

## 字典：按名字取，不按顺序记

```python
message = {"role": "user", "content": "我想退货"}
print(message["role"])
print(message["content"])
```

预期：

```text
user
我想退货
```

键写错：

```python
print(message["text"])
```

```text
KeyError: 'text'
```

没有这个栏。我们的代码约定只用 `role` 和 `content` 这两个键。

列表里装字典，就先用下标取出哪一张纸，再用键取出哪一栏：

```python
messages = [{"role": "system", "content": "你是客服"}]
print(messages[0]["role"])
```

预期：

```text
system
```

这和 `response.choices[0].message.content` 是同一种「先取第 0 个，再往里拿」的动作。那里用的是点号不是方括号，因为那一层已经是对象。对象课会对照这件事。

## 顺手认识元组

`return reply, response` 交还的是两样东西捆在一起，圆括号可以写出来：`(reply, response)`。这种用圆括号、通常不再改内容的排列叫元组。阶段 0 你只要会在左边用逗号接住它。不要把它和「调用函数的圆括号」搞混：`main()` 的括号是调用，`(reply, response)` 的括号是打包。

## 顺手认识集合

命令行客服有：

```python
EXIT_COMMANDS = {"quit", "exit", "q", "退出"}
```

花括号里如果只有值、没有冒号，它不是字典，是集合。集合用来问「这个东西在不在里面」，不关心第几个。

```python
words = {"quit", "退出"}
print("quit" in words)
print("我想 quit" in words)
```

预期：

```text
True
False
```

`in` 问的是整段文字是不是集合成员，不是「里面是否包含这几个字母」。所以「我想 quit」不会被当成退出命令。

## 常见错误

列表编号从 1 开始数，于是把第一条叫 `[1]`。你拿到的是第二条。我们打印时用 `enumerate` 把 0 显示出来，就是为了让眼睛习惯。

字典用中文冒号 `：` 代替英文冒号 `:`：

```text
SyntaxError: invalid character '：' (U+FF1A)
```

`append` 写成赋值：`papers = papers.append("新的")`。`append` 交还的是 `None`，这行会把整叠纸换成 `None`，下一行就坏。只要写 `papers.append("新的")`，不要再赋回去。

## 练习

1. 建立一个含两个字典的列表：第一句角色 `system`、内容 `你是客服`，第二句角色 `user`、内容 `订单 86`。打印第二句的内容。
2. 空列表 `[]` 上写 `[0]`，错误类型叫什么？
3. `"quit" in "我想 quit"` 和 `"quit" in {"quit", "exit"}` 结果各是什么？哪一个才是我们用来判断整行命令的那种？

## 答案

1. `messages[1]["content"]` 得到 `订单 86`。下标 1 是第二句，因为第一句是 0。
2. `IndexError`。
3. 前者是 `True`，因为那是在一段文字里查找子串。后者也是 `True`，但是在问集合成员。判断退出命令用的是后者这种整段匹配。`"我想 quit" in {"quit", "exit"}` 才是 `False`。
