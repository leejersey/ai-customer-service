# dataclass：把字段写在类的身上

[类和方法](33_class_methods.md) 里，`__init__` 要自己把每个参数放进 `self`。字段一多，漏写一个，对象上就缺这一格。`dataclass` 让你把字段写在类的身体里，Python 替你写初始化，并给出一个能直接看懂的打印。

阶段 3 用在 [工作记忆](../stage3_memory/docs/01_working_memory.md) 的 `WorkingMemory`。注记的写法在 [第 40 课](40_type_annotations.md)。

## 先用一句人话

`@dataclass` 写在 `class` 的上一行。类里面直接写 `名字: 类型 = 默认值`。做出对象时，没传的字段用默认值。`print` 这个对象，会看到每个字段现在是什么。

## 打个比方

普通的类是你自己钉的表格，每一格都要亲手写上初始值。`dataclass` 是印好栏目的表格。你只填和默认值不一样的那几格。两张表是两份纸，不会因为你在左边写了订单号，右边也出现同一个号。

## 自己动手

```python
from dataclasses import asdict, dataclass, field

@dataclass
class Card:
    intent: str | None = None
    slots: dict[str, str] = field(default_factory=dict)

left = Card()
right = Card()
left.slots["order_id"] = "10086"
print(left)
print(right.slots)
print(asdict(left))
```

预期：

```text
Card(intent=None, slots={'order_id': '10086'})
{}
{'intent': None, 'slots': {'order_id': '10086'}}
```

`left` 和 `right` 各有一份 `slots`。`asdict` 把对象收成普通字典。后面要 `json.dumps` 时用它，因为 dataclass 对象本身不是 JSON 能直接写的东西。那一步在 [第 42 课](42_json_roundtrip.md)。

不要给字典字段写一个现成的 `{}`：

```python
from dataclasses import dataclass

@dataclass
class Shared:
    slots: dict = {}
```

在 Python 3.11 及以后，定义这个类就会失败：

```text
ValueError: mutable default <class 'dict'> for field slots is not allowed: use default_factory
```

`field(default_factory=dict)` 的意思是：每做出一个对象，再调用一次 `dict()`，得到一个新的空字典。3.10 上如果侥幸写成 `= {}`，所有对象会共用同一个字典，给其中一个写入订单号，另一个也看得到。两种结果都不是「每个会话一份槽位」。

## 常见错误

忘记 `@dataclass` 那一行。类还在，但 `Card(intent="退款")` 会说 `__init__` 不接受这个参数，因为你没有自己写 `__init__`。装饰器负责把字段收成初始化参数。

在类的身体里写 `slots = {}`，又想让每个对象分开。那是类上的一个共享值，不是字段的默认工厂。阶段 3 的槽位必须用 `field(default_factory=dict)`。

把 `print(card)` 的结果当成 JSON 去存。它是给人看的文字，键没有引号，`None` 也不是 `null`。要存进 Redis，先 `asdict`，再按第 42 课变成 JSON，或者按阶段 3 的做法收成全是字符串的 HASH。

## 练习

1. 上面的 `right.slots["ticket_id"] = "2"` 之后，`left.slots` 里有 `ticket_id` 吗？
2. `Card(intent="退款")` 时，`slots` 是什么？
3. 为什么阶段 3 不用第 33 课那种手写 `__init__` 来做这张小表？

## 答案

1. 没有。两份字典是 `default_factory` 分别造出来的。
2. 一个新的空字典 `{}`。`intent` 用了你传入的 `"退款"`，没传的字段走默认值。
3. 字段有六项。手写初始化容易漏一项，打印时也看不出哪一格是空的。`dataclass` 把栏目、默认值和可读的 `print` 放在一起。
