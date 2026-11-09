# 把函数放进字典：选中了再调用

[函数课](11_functions.md) 说过：`greet` 没有括号，是把函数拿在手里；`greet()` 才执行。阶段 1 的路由器把好几块「拿在手里的函数」放进字典，用意图当键。

## 打个比方

总机台上有一排按钮，按钮上写着「咨询」「退款」。按钮下面接的是不同的分机，分机就是函数。来电先被分类，总机按下对应按钮。没有这张表的话，你就要写一长串 `if intent == "咨询"`。意图再多一个，就要再加一支。表加一行就行。

## 自己动手

```python
def say_hi():
    return "你好"

def say_bye():
    return "再见"

actions = {"hi": say_hi, "bye": say_bye}
print(actions["hi"])
print(actions["hi"]())
```

预期第一行是一串类似 `<function say_hi at 0x...>` 的文字，表示拿到了函数本身，没有执行。第二行：

```text
你好
```

键不存在：

```python
print(actions["nope"])
```

```text
KeyError: 'nope'
```

`.get` 可以在没有这个键时给一个备用函数，对话就不会被 `KeyError` 打死：

```python
def unknown():
    return "没接到"

print(actions.get("nope", unknown)())
```

预期：

```text
没接到
```

`HANDLERS.get(intent, handle_other)` 就是这个写法。备用的是 `handle_other` 这个函数，仍然没有括号。括号在下一行 `handler(...)` 才加上。

## 常见错误

写成 `"咨询": handle_consult()`。字典建好的那一瞬间，咨询函数就已经执行了，值变成了字符串。以后无论顾客说什么，你取出的都是当时那句固定回复，参数也传不进去。当时还没有顾客的句子，调用多半直接 `TypeError`，因为 `handle_consult` 需要 `text` 和 `result`。

取出函数后忘记加括号，把函数打印给顾客。屏幕上会是 `<function ...>`，不是中文回复。

## 练习

1. 字典的值应该是 `say_hi` 还是 `say_hi()`？什么时候加括号？
2. 为什么不认识的意图要用 `.get`，而不是 `HANDLERS[intent]`？
3. 路由器会不会把「音质好不好」从「其他」改判成「咨询」？

## 答案

1. 值是 `say_hi`。选中之后、有了参数再写 `handler(text, result)`。
2. 方括号在键不存在时抛 `KeyError`，整段对话中断。`.get` 可以改走「其他」。
3. 不会。路由器不重新分类。规则已经判成其他，它就调用 `handle_other`。
