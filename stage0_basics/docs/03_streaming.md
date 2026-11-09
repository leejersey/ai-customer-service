# 顺着 `03_streaming.py` 逐行读

先运行：

```bash
python stage0_basics/03_streaming.py
```

盯住「模型：」后面是一下子出现还是陆续出现。网很快时可能像一下子出现。脚本最后会告诉你非空片段有几个。大于 1，就可以确定不是等全文到齐才第一次给你。

没读过前两份导读就先回去。这一份只在新概念处停课。

## 第 1 到 16 行：和前面同一个骨架

注释、文档字符串、`from config import ...`、`TEMPERATURE = 0.7` 都是你见过的。`MAX_TOKENS = 400` 比第一课大。注释说回复太短的话，片段会在你眨眼之间到齐，看不出「陆续」。

两句提示是普通字符串。用户那句故意要「详细一点」，好让服务器有足够的字可以拆开送。

## 第 19 到 27 行：main 的前半仍不流式

```python
settings = require_settings()
describe_settings(settings)
client = create_client(settings)
messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": USER_PROMPT},
]
```

和第一课相同：读配置、做客户端、做一个两格的列表。还没有历史要重发。这个文件故意只发一轮，免得「流式」和「多轮」缠在一起。

## 第 29 到 33 行：先把说话人印在同一行的开头

```python
print()
print("开始流式输出。...")
print()
print("模型：", end="", flush=True)
```

前三个 `print` 只是说明。最后一个 `end=""` 取消换行，`flush=True` 立刻显示。先停下来复习 [print](../python_basics/03_print.md) 里「不换行」那一节，如果当时没敲过。

删掉 `end=""`，每个稍后到来的小片段都会独占一行，很难读成一段话。删掉 `flush=True`，有的终端仍逐段出现，有的会攒到最后。所以代码写明，不靠终端碰巧。

## 第 35 到 37 行：笔记本和结束原因分开准备

```python
pieces: list[str] = []
finish_reason = None
```

`pieces` 是空列表，用来留下文字。屏幕上的字不会自动进这个列表。`finish_reason = None` 是先放一张「还没有」的卡片。[None 课](../python_basics/17_none.md) 里说过：还没赋值就去读它会 `NameError`，所以先写成 `None`。结束原因要等最后一块数据才知道。

## 第 39 到 47 行：create 的返回值变了

```python
stream = client.chat.completions.create(
    ...
    stream=True,
)
```

先停下来读 [生成器](../python_basics/22_generators.md)。HTTP 课里 SSE 那一段如果跳过了，回到 [HTTP 课](../python_basics/23_http_json.md) 最后一节。

`stream=True` 时，`create` 很快交回一个流，不是带 `message.content` 的完整对象。真正的等待在下面的 `for` 里。JSON 这边每个小包长得像（示例，切分位置每次不同）：

```text
data: {"choices":[{"index":0,"delta":{"content":"请准备"},"finish_reason":null}]}
data: {"choices":[{"index":0,"delta":{"content":"订单号"},"finish_reason":null}]}
data: {"choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}
data: [DONE]
```

你在 Python 里拿到的 `chunk` 已经是解析后的对象，看不到 `data: ` 这四个字符。

## 第 48 到 61 行：循环里每一块只取新增的字

```python
for chunk in stream:
    if not chunk.choices:
        continue
    choice = chunk.choices[0]
    delta = choice.delta
    piece = delta.content if delta is not None else None
    if isinstance(piece, str) and piece != "":
        pieces.append(piece)
        print(piece, end="", flush=True)
    if choice.finish_reason:
        finish_reason = choice.finish_reason
```

`for` 的语法没变，右边不是列表。`continue` 在 [while 课](../python_basics/15_while.md) 里学过：这一轮剩下的别做了，去要下一块。有的包没有 `choices`（例如只带用量）。不去 `continue` 就去取 `[0]`，会在中途 `IndexError`。

`delta` 是这一包新增加的一点，不是从开头到现在的全文。用它覆盖上一屏，会只剩下最后几个字。

`piece = delta.content if delta is not None else None` 是写在一行里的 `if`：delta 存在就取 content，否则用 `None`。有的包连 delta 都没有。

只有确认为非空字符串才 `append` 并且打印。两件事变在相邻的两行，就是要你看见它们不是一件事。空字符串和 `None` 都跳过。第一块常常只有 `role`，没有字。

`finish_reason` 有值才记下。中间那些包的结束原因是空的，不能只看第一块。

## 第 62 到 67 行：失败可能发生在半句话之后

`except` 包住了整个 `for`，不只是 `create` 那一行。先 `print()` 换行，免得错误说明粘在半句话后面。然后翻译错误，并告诉你上面的字不是完整答案。这个文件没有把半句话写进 `messages`。

## 第 70 到 85 行：粘起来，但还不放进历史

```python
print()
full_reply = "".join(pieces)
```

`"".join(pieces)` 在生成器课里敲过。空字符串当胶水，不会额外插入竖线或空格。改成 `" | ".join(pieces)`，你会在「完整回复」里看见很多竖线，那些不是模型写的。

如果 `full_reply` 去掉空白后是空的，就结束。否则再打印一遍全文。这一遍不是第二次请求，是笔记本里的字。

最后几行 `print` 告诉你片段个数和结束原因，并打出你将来要写的那一行：

```python
messages.append({"role": "assistant", "content": full_reply})
```

本文件故意不执行这行。执行了，你还没分清「看见」和「记住」，列表里却已经有了。一轮回复在历史里应该是一条 `assistant`，不是每个片段各一条。

## 第 87 到 92 行

`if __name__` 和前面一样。Ctrl+C 时注释说明：已经打印的片段不会被保存。这是为了让「你打断了」和「没写入历史」是同一种结果。

## 改一行会看见什么

1. 把 `stream=True` 改成 `False`。`for chunk in stream` 会坏，因为整段响应对不上这种循环。看完改回 `True`。
2. 在 `pieces.append` 那一行前面加上 `continue`，让它只打印不保存。结尾的 `pieces` 是空的，屏幕上却有文章。
3. 去掉 `flush=True`，把问题再写长一点，看字是仍然逐段出现，还是顿一下一起出来。

下一份文件把这些放进一个你能打字的循环：[第 4 个脚本](04_cli_chatbot.md)。
