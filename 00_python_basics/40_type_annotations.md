# 类型注解：参数旁边的注记

[函数课](11_functions.md) 见过 `def main() -> None`。箭头表示这个函数不打算交还有用的值。阶段 3 还在参数旁边写注记，例如 `message: dict`、`messages: list[dict]`、`order_id: str | None`。

阶段 3 的 [工作记忆](../stage3_memory/docs/01_working_memory.md) 和后面的会话库都这样写。读的人不用猜「这个参数是一整句，还是一整份历史」。

## 先用一句人话

冒号后面是给人看的类型说明。Python 运行时不靠它判断对错。写错了类型，程序仍可能跑起来；写对了，读代码的人少走弯路。

## 打个比方

货架标签写着「这里放字符串」。标签不会把放错的盒子弹回去。它让下一班的人不用打开盒子才知道该放什么。

## 自己动手

```python
def label(order_id: str | None) -> str:
    if order_id is None:
        return "还没有订单号"
    return "订单 " + order_id

print(label(None))
print(label("10086"))
```

预期：

```text
还没有订单号
订单 10086
```

`str | None` 表示：要么是字符串，要么是 `None`。竖线读作「或者」。`None` 的含义在 [第 17 课](17_none.md)。

列表的注记写在名字旁边，列表本身还是要你创建：

```python
messages: list[dict] = []
messages.append({"role": "user", "content": "你好"})
print(len(messages))
```

预期：

```text
1
```

`list[dict]` 没有制造出一个列表。等号右边的 `[]` 才是那份空列表。

注记挡不住类型用错：

```python
def label(order_id: str) -> str:
    return order_id + "号"

print(label(10086))
```

```text
TypeError: unsupported operand type(s) for +: 'int' and 'str'
```

调用时已经把整数传进去了。失败发生在加号，不是发生在冒号。注解没有替你做检查。

## 常见错误

只写 `messages: list[dict]`，忘记写 `= []`。那一行只是注解加名字，名字还没有值，下一行就会 `NameError`。

把 `str | None` 理解成「空字符串也行」。空字符串是 `str`，`None` 是另一样东西。阶段 3 用 `None` 表示「这项还没有」，用 `""` 表示「有这项，内容是空的」。两种都要能写出来，所以注记里才会出现 `|`。

以为改了注解就改变了函数行为。删掉所有冒号和箭头，能跑的函数还是能跑。留下它们，是为了读 `load_working` 时知道交回来的是 `WorkingMemory`，不是一句文本。

## 练习

1. `label(None)` 为什么不会进 `return "订单 " + order_id` 那一支？
2. `messages: list[dict] = []` 里，哪个部分真正创建了列表？
3. 注解写成 `order_id: str`，调用时传入 `10086` 这个整数，Python 会在调用的那一刻拒绝吗？

## 答案

1. `None` 使 `if order_id is None` 成立，函数在上一行已经 `return`。
2. 等号右边的 `[]`。左边的 `list[dict]` 只是注记。
3. 不会。注记不检查。整数会进函数，直到函数里拿它做字符串才失败。
