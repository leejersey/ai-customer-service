# for：把一叠纸逐张拿出来

`for` 不是「从 1 数到 10」这一种才能用。它的基本意思是：对这一叠里的每一张，做一次缩进的那一块。

`01_hello_llm.py` 里：

```python
for index, message in enumerate(messages):
    print(f"[{index}] {message['role']}: {message['content']}")
```

## 先用一句人话

`for 一张 in 一叠:` 下面的行会对每一张执行。这一张用完，自动拿下一张。叠拿完了，循环结束，继续执行和 `for` 对齐的下一行。

## 打个比方

你面前有一叠点菜单。你不会写「处理第 1 张、处理第 2 张」两段几乎一样的步骤。你写「对每一张：念出编号和内容」。加到 100 张也不用把代码复制 100 遍。

## 自己动手

```python
for role in ["system", "user"]:
    print(role)
print("循环结束")
```

预期：

```text
system
user
循环结束
```

`enumerate` 在给每一张纸的同时给一个从 0 开始的编号：

```python
papers = ["封面", "问题"]
for index, paper in enumerate(papers):
    print(index, paper)
```

预期：

```text
0 封面
1 问题
```

`index, paper` 是一次接住两样东西，和函数返回两个值的接法一样。`enumerate` 每次交还「编号」和「这张纸」。

循环变量只在每一轮代表「当前这张」。循环结束后，它留在最后一轮的值上，不要靠它去代表全部。

流式那一课的 `for chunk in stream:` 也是 `for`，但那一叠纸还没印完，你每要下一张，才等网络送来下一张。那是生成器课的内容。语法仍然是这个 `for`。

## 常见错误

忘记冒号或忘记缩进，错误和 `if` 相同：`SyntaxError: expected ':'` 或 `IndentationError`。

在循环里改一叠纸的成员个数，比如边 `for` 边 `pop`。你会对着一张已经被抽走的纸发呆，结果漏掉或重复。要删元素时，先另做一叠，或者倒着删。我们的脚本不在 `for` 里面 `pop`。

把 `for message in messages:` 写成 `for messages in messages:`。名字被自己盖掉，循环结束后原来的列表名指向最后一条，整叠纸从名字上丢了。循环变量要换一个名字，比如 `message`。

## 练习

1. 对列表 `["停", "自己说完"]` 逐个打印，并在全部打完后打印 `完`。写出输出的三行。
2. `enumerate` 交还的第一样是什么？它从几开始？
3. 为什么打印两条消息不用复制两段 `print`，而用 `for`？

## 答案

1. 输出是 `停`、`自己说完`、`完`。
2. 编号，从 0 开始。第一条的编号是 0。
3. 两条和两百条是同一种步骤。`for` 把「对每一条做一次」写出来，条数变了也不用改这段结构。
