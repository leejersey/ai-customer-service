# json.loads：把文本变成字典，以及解析失败

[HTTP 课](23_http_json.md) 用 `json.dumps` 把字典变成文本，用 `json.loads` 把一段合法 JSON 变回来。阶段 1 的模型经常不那么听话：前面加一句「好的」，或者干脆用中文回答。这一课专门处理「这段字可能不是 JSON」。

`json` 是标准库。

## 打个比方

`loads` 是验收员。表格合格，就交回字典。表格缺括号，他不会猜你的意图，而是把单子退回，并说坏在第几个字符。我们的程序接住这张退单，改走兜底，而不是让整个客服崩溃。

## 自己动手

```python
import json

text = '{"intent": "咨询", "confidence": 0.8}'
data = json.loads(text)
print(data["intent"])
print(data["confidence"])
```

预期：

```text
咨询
0.8
```

注意 JSON 里的键必须是双引号。Python 字典可以用单引号，JSON 不行。

坏文本：

```python
import json
json.loads("我觉得这是查订单。")
```

```text
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```

`JSONDecodeError` 是 `json.loads` 失败时的那种错误。用 `except json.JSONDecodeError` 接住。接成 `except ValueError` 有时也能接住，因为这个错误是 `ValueError` 的一种，但写具体的名字，读代码的人知道你在等解析失败。

## 从废话里把花括号剪出来

模型可能写成：`说明如下：{"intent":"退款",...}`。

`find` 从左边找第一个 `{` 的位置，找不到就交回 `-1`。`rfind` 从右边找最后一个 `}`。

```python
text = '说明如下：{"intent":"退款"} 完'
start = text.find("{")
end = text.rfind("}")
print(start, end)
print(text[start : end + 1])
```

预期：

```text
5 19
{"intent":"退款"}
```

位置数字可能因空格略有不同，关键是切片里只剩对象。`end + 1` 是因为切片的右端不包含。不加上 1 会把 `}` 切掉，`loads` 仍然失败。

剪完再 `loads`。剪不出来就让 `loads` 失败，走兜底。不要在失败时假装意图是「查订单」。

JSON 的 `null` 进 Python 变成 `None`。所以 `order_id` 没有时，字典里是 `None`，不是文字 `"null"`。

## 常见错误

用 `json.load` 去读一个字符串。`load` 要的是文件对象，`loads` 的 `s` 表示 string。对字符串用 `load` 会 `AttributeError`。

解析成功却不检查 `intent` 是不是六个允许值之一。模型可以输出合法 JSON，但意图写成「生气」。格式对，不等于内容可用。阶段 1 在 `loads` 之后还检查意图、置信度范围和 `slots` 是不是字典。

`except Exception` 把 `JSONDecodeError` 和其他笔误混在一起。解析函数里只接 `JSONDecodeError`，别的错误仍然暴露出来，方便你发现自己写错了键。

## 练习

1. `json.loads("[]")` 得到什么类型？我们的分类器为什么还要拒绝它？
2. `find` 返回 `-1` 时，切片 `text[-1 : 0]` 有用吗？代码为什么要先判断？
3. 兜底结果为什么仍要有 `intent` 和 `slots` 这两个键？

## 答案

1. 得到一个列表。分类器要的是带 `intent` 的对象。列表没有这个键，后面 `data.get` 也不是我们要的形状，所以拒绝。
2. 没有用。`-1` 不是「没找到就别切」的自动开关。不判断就会切出错误的一段，或者从末尾开始切。
3. 路由器和评估脚本都按这些键取。失败如果交回另一种形状，调用方要写第二套读取逻辑，更容易漏。
