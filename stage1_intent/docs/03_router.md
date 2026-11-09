# 顺着路由器逐行读

## 本课需要的基础课

新的是把函数放进字典，选中后再调用。文件末尾的 `if __name__` 是复习。

- 👉 不懂把函数放进字典？先看 [基础课 · 函数放进字典](../../00_python_basics/28_functions_in_dict.md)
- [基础课 · if \_\_name\_\_](../../00_python_basics/18_name_main.md)

先运行：

```bash
python stage1_intent/03_router.py
```

不需要密钥。看「音质好不好」被判成其他之后，回复也是其他那一句。

## 六个处理函数

`router.py` 第 7 到 35 行，每个函数都接收 `text` 和 `result`，交回一句中文。它们不调用模型，也不查数据库。订单函数如果 `slots` 里有订单号，就把数字嵌进回复，用来证明槽位接住了。没有订单号，就请顾客补充。

`result["slots"].get("order_id")` 在槽位字典意外缺少这个键时得到 `None`，而不是 `KeyError`。分类器正常情况总会放这个键。`.get` 是多一层防护。

这些句子里反复出现「阶段 2」。那不是已经实现的功能。阶段 2 才会把「记下了」变成 SQLite 里的工单，并用工具去查订单。现在说「记下了」只是话术。

## 字典里的函数

👉 不懂把函数放进字典？先看 [基础课 · 函数放进字典](../../00_python_basics/28_functions_in_dict.md)。

```python
HANDLERS = {
    "咨询": handle_consult,
    ...
}
```

值没有括号。字典创建时不会发回复。

`route` 里：

```python
handler = HANDLERS.get(result.get("intent"), handle_other)
return handler(text, result)
```

先取意图字符串。结果字典连 `intent` 都没有时，`result.get` 得到 `None`，`HANDLERS.get(None, handle_other)` 用备用函数。然后才调用。两层 `.get` 都是为了别让坏结果把进程打死。

删掉 `.get` 的备用，改成 `HANDLERS[result["intent"]]`，遇到拼错的意图会 `KeyError`。演示脚本的「其他」不会触发这个，所以你看不出差别。要看见差别，得临时传一个 `{"intent": "生气", "slots": {}}`。

## `route_by_rules`

```python
result = classify_by_rules(text)
return result, route(text, result)
```

这是阶段 0 学过的「一次交还两样」。左边接住时要写成 `result, reply = route_by_rules(text)`。演示脚本就是这样打印的。

路由器不做第二遍分类。规则错了，回复就跟着错。这是这一课要看见的边界：分流和识别是两段代码。

## 演示脚本

`03_router.py` 只有一个循环和几行打印。句子包括转人工、带订单号、退货、音质。前三句的回复应分别提到转人工、订单 10086、还不能退钱。第四句是其他。

没有 `if __name__` 以外的新语法。末尾的守卫复习 [基础课 · if \_\_name\_\_](../../00_python_basics/18_name_main.md)。这个文件不联网，被别人导入时也不该把四句演示打出来，所以仍然要守卫。

下一课用一份写好的标准答案给规则打分：[评估](04_evaluate.md)。
