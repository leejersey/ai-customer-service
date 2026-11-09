# 函数交回一个字典

阶段 0 的函数要么 `return` 一个字符串，要么一次交还两样东西。阶段 1 的分类结果有意图、置信度、订单号、来源。用位置记住「第 2 个是置信度」很容易写反。所以 `classify_by_rules` 交回一个字典。

第一次出现在 `stage1_intent/rule_intent.py` 的 `return { ... }`。

字典本身在 [列表和字典](13_lists_dicts.md)。函数在 [函数](11_functions.md)。这一课只讲「把好几样有名字的结果装进一个字典再交回去」。

## 打个比方

以前交回的是两张没写名字的纸条，收的人必须记得第一张是意图、第二张是置信度。现在交回一张填好的表格，栏名印在上面。换栏的顺序也不会拿错。

## 自己动手

```python
def classify(text):
    return {"intent": "其他", "confidence": 0.2, "text": text}

result = classify("你好")
print(result["intent"])
print(result["confidence"])
```

预期：

```text
其他
0.2
```

键写错：

```python
print(result["score"])
```

```text
KeyError: 'score'
```

调用方只认你们约定好的键。阶段 1 约定的键是 `intent`、`confidence`、`slots`、`source`。`slots` 里面再有一个字典，键是 `order_id`。

## 常见错误

写成 `return intent, confidence`，调用处却写 `result["intent"]`。逗号交回的不是字典，会得到：

```text
TypeError: tuple indices must be integers or slices, not str
```

`tuple` 就是以前说的「捆在一起的两样东西」。它只能用数字下标，不能用栏名。

忘记 `return`，函数交回 `None`，接着 `result["intent"]` 会变成：

```text
AttributeError: 'NoneType' object has no attribute ...
```

实际上对 `None` 使用 `["intent"]` 的信息是：

```text
TypeError: 'NoneType' object is not subscriptable
```

## 练习

1. 写函数 `pack(name)`，交回 `{"name": name, "ok": True}`。`pack("小星")["ok"]` 是什么？
2. 为什么分类结果不用 `return intent, confidence, slots, source` 四个位置？
3. `result["slots"]["order_id"]` 这串方括号在做什么？

## 答案

1. `True`。没有引号，是布尔值，不是文字。
2. 四个位置没有名字。中间插入一个新值，后面的调用全部错位。字典靠键取，多一个键不会弄乱旧键。
3. 先取出 `slots` 那个字典，再从里面取出 `order_id`。两层表格。
