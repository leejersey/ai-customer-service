# 星号：把一串值收进来，或把字典拆成参数

函数平常一个参数写一个名字。有时名字要到运行时才知道，比如模型交来一份 JSON 对象，键就是参数名。两个星号负责这件事。

阶段 2 用在 [执行工具](../stage2_tools_tickets/docs/04_function_calling.md) 的 `function(**arguments)`。函数放进字典是 [第 28 课](28_functions_in_dict.md)，这一课多出来的是星号。

## 先用一句人话

一个星号把多出来的位置参数收成一个元组。两个星号把多出来的、带名字的参数收成一个字典。反过来，调用时两个星号放在字典前面，是把字典拆开，每个键变成一个参数名。

## 打个比方

一个星号是「后面这些没写名字的，都放进一个袋子」。两个星号是「这些已经贴了标签的，按标签放进对应的格子」。标签必须和函数参数的名字一样，否则格子对不上。

## 自己动手

一个星号：

```python
def total(*numbers):
    result = 0
    for number in numbers:
        result = result + number
    return result

print(total(1, 2, 3))
print(total())
```

预期：

```text
6
0
```

`numbers` 是元组。一个都没传时，它是空元组，循环不执行。

两个星号，在定义里收集：

```python
def show(name, **extra):
    print(name)
    print(extra)

show("小星", city="杭州")
```

预期：

```text
小星
{'city': '杭州'}
```

`city` 不是 `show` 事先写好的参数。它被收进 `extra` 这个字典。

两个星号，在调用里拆开。这是阶段 2 真正用的方向：

```python
def greet(name, city):
    print(f"{name} 在 {city}")

info = {"name": "小星", "city": "杭州"}
greet(**info)
```

预期：

```text
小星 在 杭州
```

等价于 `greet(name="小星", city="杭州")`。键是参数名，值是传进去的东西。

键对不上：

```python
def greet(name, city):
    print(name, city)

greet(**{"name": "小星", "town": "杭州"})
```

```text
TypeError: greet() got an unexpected keyword argument 'town'
```

少了键也会 `TypeError`，提示缺少必须的参数。阶段 2 接住这种 `TypeError`，收成「参数和工具对不上」，不让整个客服退出。

工具登记表就是第 28 课的字典，加上这一课的拆包：

```python
def query_order(order_id):
    return "查" + order_id

tools = {"query_order": query_order}
arguments = {"order_id": "10086"}
print(tools["query_order"](**arguments))
```

预期：

```text
查10086
```

`tools["query_order"]` 先拿到函数本身，后面的 `(**arguments)` 才调用。星号在括号里面。

## 常见错误

调用时括号里只放 `arguments`，没有两个星号。整个字典会变成 `order_id` 这一个参数，函数收到的是字典不是字符串。接下来用字符串方法就会失败。

写成 `**arguments` 却放在函数名和括号之间，那是语法错误。星号出现在调用的括号里，或出现在另一条赋值里，例如 `pieces = {**arguments}`。

一个星号和两个星号拆的东西不同。`greet(*info)` 会把字典的键按位置传进去，传的是 `"name"`、`"city"` 这两个字符串，不是杭州。阶段 2 的参数来自 JSON 对象，用两个星号。

## 练习

1. `greet(**{"name": "小星", "city": "杭州"})` 和 `greet("小星", "杭州")` 的结果一样吗？
2. 模型多写了一个 JSON 字段，`function(**arguments)` 会怎样？
3. 只从登记表取出 `query_order`，和取出之后用 `**arguments` 调用，差在哪？

## 答案

1. 打印一样。一种用名字从字典拆开，一种按位置传。两个值都进了 `name` 和 `city`。
2. 抛出 `TypeError`，说有意料之外的关键字参数。阶段 2 把这个错误收成字典交回去。
3. 没有括号时只是拿到函数。加上 `(**arguments)` 才按字典里的键去调用。
