# None：这里有一个名字，但里面没有值

`None` 是 Python 自带的一个值，表示「没有」。它不是数字 0，不是空字符串 `""`，也不是空列表 `[]`。

`01_hello_llm.py` 里：

```python
if usage is None:
    print("这次响应没有附带 token 用量。")
```

## 先用一句人话

盒子可以贴着标签，但里面是一张写着「空」的专用卡片。这张卡片和「装了一个 0」不是一回事。0 是一个数量。`None` 是「这次根本没给你这个数量」。

## 打个比方

快递单上「重量」那一栏画了斜线，表示没称。这和写着 0 公斤不同。0 公斤是称过了。斜线是没有这项数据。`usage is None` 就是在看这一栏是不是斜线。有斜线就不要去读 `prompt_tokens`，否则会再摔一跤。

## 自己动手

```python
usage = None
if usage is None:
    print("没有用量")
else:
    print(usage)
```

预期：

```text
没有用量
```

判断 `None` 时写 `is None`，不要写 `== None`。效果大多数时候一样，但 `is` 问的是「是不是这张唯一的空卡片」。读别人的 Python 代码时你会一直看见 `is None`。

没有 `return` 的函数交出来的也是 `None`：

```python
def say():
    print("说话了")

result = say()
print(result)
```

预期：

```text
说话了
None
```

第一行是函数里面的 `print`。第二行是它交回来的值。`main()` 就是这种：屏幕上有字，是因为里面调用了 `print`，不是因为 `main()` 把回复交了回来。

`append` 也交回 `None`。所以不要写 `papers = papers.append("x")`。列表课说过这件事。

## 和空字符串的差别

```python
text = ""
print(text is None)
print(text == "")
```

预期：

```text
False
True
```

空字符串是「有一段文字，长度是 0」。模型返回 `""` 时，`usage` 仍可能不是 `None`。我们的代码两个都查：先看有没有 choices，再看 `content` 是不是一段非空的文字。

## 常见错误

还没赋值就去问它是不是 `None`：

```text
NameError: name 'usage' is not defined
```

`None` 不能救一个根本不存在的名字。名字要先出现过，哪怕你让它等于 `None`。

把 `None` 当成 0 去相加：

```python
print(None + 1)
```

```text
TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'
```

`NoneType` 就是「None 这种类型」。看见它，回想有个值缺失，你却拿去运算了。

## 练习

1. `reply = ""` 时，`reply is None` 是真还是假？
2. 为什么 `usage` 是 `None` 时不能写 `usage.prompt_tokens`？
3. 一个只含 `print("嗨")`、没有 `return` 的函数，调用完接到变量里，那个变量是什么？

## 答案

1. 假。它是空字符串，不是 `None`。
2. `None` 里面没有 `prompt_tokens` 这个栏。去点它会得到 `AttributeError: 'NoneType' object has no attribute 'prompt_tokens'`。
3. `None`。`print` 只影响屏幕，不作为函数的返回值。
