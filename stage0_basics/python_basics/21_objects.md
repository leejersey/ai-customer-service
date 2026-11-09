# 对象、方法、关键字参数：点号左边是谁

`01_hello_llm.py` 里最容易看成一团咒语的一行是：

```python
response = client.chat.completions.create(
    model=settings.model,
    messages=messages,
    temperature=TEMPERATURE,
    max_tokens=MAX_TOKENS,
    stream=False,
)
```

把它拆开之前，先认识三样东西：对象、方法、关键字参数。

## 对象是带着功能的值

字符串不只是字，它还带着操作。你已经用过：

```python
text = "  退出  "
print(text.strip())
```

`text` 是一个字符串对象。`.strip` 是这个对象会做的一件事，叫方法。方法就是属于这个对象的函数。调用时同样要加括号：`.strip()`。

数字、列表、字典也都是对象。`papers.append("新的")` 里，`append` 是列表的方法。

自己做一种新对象，用 `class`。`config.py` 里的 `Settings` 就是：

```python
class Settings:
    def __init__(self, api_key, base_url, model):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
```

`class` 是模具。`Settings(...)` 按模具做出一个具体的对象。做出的那一个叫实例。

`__init__` 是刚做出实例时自动执行的方法，用来把值放进这个实例。`self` 就是「正在被做出的那一个」。`self.model = model` 的意思是：这个实例自己的 `model`，等于传进来的那个参数。

之后可以写 `settings.model`，从这一个实例里把模型名拿出来。点号在这里不是小数点。两边有名字时，它是「里面的」。

你现在不要去写新的类。只要能读懂：`Settings` 把三样东西捆在一起，避免调用时把顺序写反；`settings.model` 是在取其中一样。

## 库和 SDK

库是一组可以 `import` 的模块。SDK（软件开发工具包）是专门帮你调用某项服务的库，通常还附带文档和对象。`openai` 这个包就是一个 SDK：它知道怎么把你的 Python 值变成 HTTP 请求。

`client = create_client(settings)` 得到的 `client` 就是这个 SDK 给你的一个对象。创建它只是把地址和密钥放进对象，不联网。对象课要记住这一点，因为点号看起来很忙，其实很多点号只是在取里面的下一层。

## 从左到右读点号

`client.chat.completions.create` 读成：

1. `client`：我们建好的客户端对象。
2. `.chat`：它里面负责「聊天」的那一层。
3. `.completions`：聊天下面的「补全」这一层。名字来自接口的历史叫法，你不必改它。
4. `.create`：真正发出一次请求的方法。有括号才真的调用。

中间两层没有括号，因为那里是在往下取对象，不是在执行动作。只有 `create(...)` 有括号，动作发生在这里。

如果写成 `client.chat.completions.create` 而不加括号，你只是拿着这个方法本身，请求不会发出去。交互模式里你会看到一串表示「这是一个方法」的文字，而不是回复。

## 关键字参数：用名字把值送进函数

括号里的 `model=settings.model` 不是在比较，也不是在给 `settings.model` 重新赋值。它是在说：这个参数的名字叫 `model`，请使用右边的值。

```python
def show(model, temperature):
    print(model)
    print(temperature)

show(model="deepseek-chat", temperature=0.7)
```

预期：

```text
deepseek-chat
0.7
```

因为带了名字，顺序可以调换：

```python
show(temperature=0.7, model="deepseek-chat")
```

结果一样。`create` 的参数很多，用名字写上，你才看得出 `0.7` 是温度不是别的数字。

右边的 `settings.model` 是我们盒子里的值。左边的 `model` 是 SDK 规定的参数名。两边碰巧都叫 model 一类的词，但是两个位置。

`stream=False` 的 `False` 是 Python 里的「假」，和 `True` 相对。没有引号。写成 `"False"` 就变成了四个字母的文字，意思不同。

## 常见错误

方法忘记括号：`text.strip` 不会去掉空格，`text.strip()` 才会。

点号左边是 `None`：

```text
AttributeError: 'NoneType' object has no attribute 'prompt_tokens'
```

先检查是不是 `None`，再点进去。

关键字参数把名字拼错：

```text
TypeError: show() got an unexpected keyword argument 'temp'
```

SDK 不认识 `temp`。要写它文档里的 `temperature`。我们把这个名字写在代码里，就是为了和接口对齐。

## 练习

1. 用一句话区分 `client.chat` 和 `create(...)`。
2. `show(temperature=0.7, model="deepseek-chat")` 为什么不会把 0.7 误认为模型名？
3. `settings = Settings("密钥", "https://api.deepseek.com", "deepseek-chat")` 之后，怎样取出模型名？假设类就是上面那个写法。

## 答案

1. `client.chat` 是往下取一层对象，没有发起请求。`create(...)` 才是调用方法，一次请求发生在这里。
2. 值是用参数名字送进去的。`temperature=` 明确把 0.7 交给温度，和写在第几个位置无关。
3. `settings.model`。点号从这一个实例里取出当时放进去的模型名。
