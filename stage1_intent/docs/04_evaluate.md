# 顺着评估脚本逐行读

先运行：

```bash
python stage1_intent/test_rules.py
python stage1_intent/04_evaluate.py
```

两条都不需要密钥。第一条成功时最后是「规则和解析测试通过」。第二条会打印规则准确率 `13/20 = 0.65`，并列出 7 句不一致。数字若变了，说明词表或测试集被改过，以你屏幕为准，再回来对原因。

## 标准答案文件

打开 `stage1_intent/data/labeled_examples.json`。它是一个列表，每项是 `text` 和 `intent`。这些 `intent` 必须是 `INTENTS` 里的六个字，否则评估脚本的 `assert` 会停。

文件里故意放了规则会错的句子，例如「音质好不好」「我不想退款」「今天天气怎么样」。全放容易题，准确率会是 1，你学不到局限。

## `metrics.py`

先停下来读 [准确率](../../stage0_basics/python_basics/32_accuracy.md)。

`accuracy` 用 `enumerate` 对齐两份列表。长度不同或为空，抛 `ValueError`，不去做除法。`confusion` 做出字典套字典。`.get(guess, 0) + 1` 是在计数。

没有用新的除法符号。Python 3 的 `/` 得到小数。

## `04_evaluate.py` 前半：读文件和断言

先停下来读 [读文本文件](../../stage0_basics/python_basics/29_read_text.md) 和 [assert](../../stage0_basics/python_basics/30_assert.md)。

```python
DATA_PATH = Path(__file__).resolve().parent / "data" / "labeled_examples.json"
raw = path.read_text(encoding="utf-8")
data = json.loads(raw)
```

路径跟脚本走。`json.loads` 复习解析课。这里的文件是我们自己写的，解析失败应该暴露，不要兜底成「其他」。兜底是对付模型的。测试集坏了就该停下。

三个 `assert` 检查每一条是字典、有两个键、意图合法。失败信息里带了未知意图的名字。

## 列表推导

先停下来读 [列表推导](../../stage0_basics/python_basics/31_list_comprehension.md)。

```python
texts = [item["text"] for item in rows]
gold = [item["intent"] for item in rows]
rule_predictions = [classify_by_rules(text)["intent"] for text in texts]
```

第三行对每句调用规则函数，只留下意图字符串。订单号不参与准确率。阶段 1 的分数只回答「意图标签对不对」，不回答「订单号抽没抽对」。订单号由 `test_rules.py` 用一条断言单独盯着。

## 报告

`show_report` 再数一遍猜对的条数，是为了打印 `13/20` 这种分数，而不只打印 `0.65`。`:.2f` 在准确率课里。不一致的句子用 `continue` 跳过猜对的，只印错的。

混淆那一行：

```python
parts = [f"{guess} {count} 次" for guess, count in row.items()]
```

`.items()` 在列表推导课的例子里。`"，".join(parts)` 把几段用中文逗号接成一行。`join` 在阶段 0 流式课里用空字符串接过片段，这里换了分隔符。

`assert 0.5 < rule_score < 1.0` 在报告打印之后。全对或太差都会在这里停下。它保护的是「这份教材还展示着局限」，不是在测顾客。

## 有密钥才跑模型

`api_key_ready()` 为假就打印一句并 `return`。规则分数已经打出来了。

有密钥时，普通 `for` 加 `try`。一句网络失败就记下「其他」并继续，否则一个 401 会让整份对比消失。失败被记成「其他」会拉低准确率。那是诚实的：没分出来就不算对。打印仍会走 `print_api_error`，你看得到原因。

最后两句打印提醒：模型准确率更高，只说明更接近这 20 条标签，不说明它查到了物流。

## `test_rules.py`

五个函数各测一件事：转人工、订单号 10086、音质被判成其他、坏 JSON 兜底、废话中间的合法 JSON。最后的 `if __name__` 把它们依次调用。

「音质」那条断言期望是「其他」，不是「咨询」。改成期望咨询，测试会失败，直到你改词表。测试在这里锁住的是当前局限，防止有人无意中把演示用的反例修掉还以为全部正确。

pytest 可以以后再装。现在用 `python stage1_intent/test_rules.py`。

下一课把分类和路由接回能打字的客服：[命令行](05_cli.md)。
