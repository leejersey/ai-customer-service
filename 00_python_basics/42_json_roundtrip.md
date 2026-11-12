# JSON 来回：字典变成文本，文本再变回字典

[HTTP 课](23_http_json.md) 用 `json.dumps` 把一个小字典变成文本，用 `json.loads` 变回来。[第 27 课](27_json_parse.md) 处理模型交来的、可能不合法的那一段。阶段 3 要存的是一整份消息列表，以及一张 dataclass 小表。Redis 只保存文本，不保存 Python 对象。

阶段 3 用在 [会话记忆](../stage3_memory/docs/05_session_store.md)。`WorkingMemory` 本身怎么写，在 [第 41 课](41_dataclass.md)。

## 先用一句人话

`dumps` 把列表或字典抄成一串 JSON 文本。`loads` 把这串文本变回列表或字典。变回来的是新的字典，不是原来的那个对象。dataclass 要先 `asdict`，否则 `dumps` 会拒绝。

## 打个比方

Python 对象是你桌上的表格，出了这个进程别人不认。JSON 是双方都认的抄写格式。你把表格抄成一段话放进 Redis。下次读出来，得到的是一份按这段话重新画的表，不是桌上那张纸又飞回来了。

## 自己动手

先存一条消息。`ensure_ascii=False` 让中文还是中文：

```python
import json

message = {"role": "user", "content": "订单号 10086"}
text = json.dumps(message, ensure_ascii=False)
print(text)
back = json.loads(text)
print(back["content"])
print(back is message)
```

预期：

```text
{"role": "user", "content": "订单号 10086"}
订单号 10086
False
```

最后一行是 `False`：`loads` 造了一个新字典。你改 `back["content"]`，原来的 `message` 不变。

dataclass 不能直接交出去：

```python
import json
from dataclasses import asdict, dataclass, field

@dataclass
class Card:
    intent: str | None = None
    slots: dict[str, str] = field(default_factory=dict)

card = Card(intent="退款")
card.slots["order_id"] = "10086"
try:
    json.dumps(card)
except TypeError as error:
    print(type(error).__name__)

text = json.dumps(asdict(card), ensure_ascii=False)
print(text)
restored = json.loads(text)
print(type(restored).__name__)
print(restored["slots"]["order_id"])
```

预期：

```text
TypeError
{"intent": "退款", "slots": {"order_id": "10086"}}
dict
10086
```

`None` 写进 JSON 会变成 `null`，读回来又是 `None`。这和 [第 23 课](23_http_json.md) 里 `true` / `false` / `null` 的对应是同一件事。

一段坏文本要接住，否则一整份会话会因为一条坏消息读不出来：

```python
import json

try:
    json.loads("订单号 10086")
except json.JSONDecodeError:
    print("这一条不是 JSON")
```

预期：

```text
这一条不是 JSON
```

`JSONDecodeError` 在第 27 课。阶段 3 的会话库遇到它就跳过这一条，继续读后面的消息。

## 常见错误

`dumps` 时不加 `ensure_ascii=False`。中文会变成 `\u8ba2\u5355` 这种写法。程序仍能 `loads` 回来，但你用 redis-cli 查看时看不懂。阶段 3 因此固定加上这个参数。

以为 `loads` 会得到 `Card`。它只得到字典。要回到 dataclass，得再调用 `Card` 的构造，或者阶段 3 里的 `from_dict`。JSON 不记得原来的类名。

把 Redis 客户端、文件对象放进字典再 `dumps`。那些对象没有 JSON 写法，结果是 `TypeError`。要存的是订单号和句子，不是连接本身。连接对象在 [第 43 课](43_connection.md)。

## 练习

1. `json.dumps({"ok": True}, ensure_ascii=False)` 里，`True` 在文本中变成什么？
2. 为什么 `WorkingMemory` 要先变成字典，才能放进 `dumps`？
3. `loads` 之后改返回值的某个键，原来的字典会跟着变吗？

## 答案

1. 变成小写的 `true`。这是 JSON 的写法，不是 Python 的 `True`。
2. dataclass 对象不是 JSON 认识的列表或字典。`asdict` 先收成字典，`dumps` 才接受。
3. 不会。`loads` 交出新的字典，两边不是同一个对象。
