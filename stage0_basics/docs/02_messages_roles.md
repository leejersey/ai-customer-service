# 顺着 `02_messages_roles.py` 逐行读

先运行：

```bash
python stage0_basics/02_messages_roles.py
```

把两次「即将发送的 messages」留在屏幕上。这份导读按行号往下走。和第一课相同的语法不再把整课重讲一遍，但每一行仍然说明它在这个文件里干什么。没读过 [第一课导读](01_hello_llm.md) 的话，先回去，否则这里的「和第一课一样」没有着落。

## 第 1 到 9 行

第 1 行是注释。第 2 到 7 行是文档字符串，告诉你这个文件会自己发两轮，第二句用了「上面这个订单」。运行时不会打印这段。

第 9 行：

```python
from config import create_client, describe_settings, print_api_error, require_settings
```

和 `01` 第 10 行是同一句。加载 `config.py` 的过程不会再来一遍新语法。四个名字再次被带进来。

## 第 11 到 20 行：这一课的三个常量

```python
TEMPERATURE = 0.3
MAX_TOKENS = 200
SYSTEM_PROMPT = (
    "你是「星河数码」的客服。用简体中文回答，不超过 80 个字。"
    "不要编造具体的退款金额或物流单号。不确定的规则，就说需要人工确认。"
)
```

注释说温度放低，是为了让你看列表，而不是看文采飘不飘。`0.3` 仍是数字。`200` 把回复限制短一点，打印历史时才不会被一大段话淹没。

`SYSTEM_PROMPT` 的括号不是调用函数。紧挨着的两个字符串，Python 会把它们拼成一句。写成两行只是为了这一行别太长。拼完的结果里，两句中文是连着的，中间没有自动换行。岗位说明要求不超过 80 个字，并且不要编金额和运单号。删掉它，请求仍可能成功，但模型更可能编出一个退款数字。

## 第 23 到 27 行：show_messages 只负责打印

```python
def show_messages(messages: list[dict[str, str]]) -> None:
    print("即将发送的 messages：")
    for index, message in enumerate(messages):
        print(f"  [{index}] {message['role']}: {message['content']}")
```

`def` 先记住，不打印。参数名 `messages` 是「调用时交进来的那一整叠」。函数看不见外面还有没有另一叠。

`list[dict[str, str]]` 和 `-> None` 都是给人读的注记：这是列表，元素是字典，字典的键和值是字符串；函数不交还有用的值。删掉这些注记，运行不变。

`for` 和第一课的打印循环一样。多了两个空格，只是为了屏幕上缩进好看，好和标题对齐。

## 第 30 到 57 行：request_reply 把「发一次」写成一个函数

文档字符串说：两次调用共用它，这样除了列表以外的参数不会一次一个样。这是设计原因。

```python
response = client.chat.completions.create(
    model=model,
    messages=messages,
    ...
)
```

和第一课的 `create` 是同一种调用。差别只在 `messages` 这个参数每次交进来的列表不一样。`stream=False` 仍然要整段 JSON。流式是下一个文件的事，这个函数不掺进去。

失败时 `print_api_error` 然后 `SystemExit`。这个文件没有循环可以继续，所以失败就结束，和第一课一样。

```python
return reply, response
```

逗号交还两样东西：回复文字，和整份响应。文字要放进下一轮列表。响应里还有 `usage`，用来比较 token。如果只 `return reply`，后面就没法打印 `prompt_tokens`。

## 第 60 到 68 行：print_usage

```python
if usage is None:
    print(...)
    return
print(f"{turn_name} token：prompt={usage.prompt_tokens}, ...")
```

`return` 在这里没有值，只是离开函数。用量缺失时不要再去点 `usage.prompt_tokens`，否则 `AttributeError`。

f-string 被拆成两段圆括号里的字符串，和上面 `SYSTEM_PROMPT` 一样，是为了换行书写，不是两句输出。

## 第 71 到 79 行：main 开头，列表里只有封面

```python
def main() -> None:
    settings = require_settings()
    describe_settings(settings)
    client = create_client(settings)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]
```

前三行和第一课相同：读配置、打印地址、做客户端。客户端在两轮之间不重建。重建也不会让服务器记得你，只是让人误以为「新客户端 = 新会话」。

列表一开始只有第 0 格，岗位说明。注释说这份列表是唯一的对话状态，进程结束就没了。服务器不留底。这句话是这一课要证明的事。

## 第 81 到 93 行：第 1 轮

```python
messages.append({
    "role": "user",
    "content": "我买的耳机想退货，订单尾号是 86。",
})
show_messages(messages)
reply, response = request_reply(client, settings.model, messages)
```

`append` 在列表末尾加一格。现在是两格：system 和 user。`show_messages` 在发送之前，所以你看见的是即将送出的文件夹。

`reply, response = ...` 左边两个名字，接住 `return reply, response`。顺序不能反。反了的话 `reply` 会变成整份响应，`print(reply)` 会印出一堆对象文字，而不是那句中文。

然后打印回复，再 `print_usage("第 1 轮", response.usage)`。记下这一轮的 `prompt` 数字。

## 第 95 到 96 行：把专家刚说的话钉回文件夹

```python
messages.append({"role": "assistant", "content": reply})
```

`assistant` 不是新的命令，是上一轮 `content` 的原文。不钉回去，下一轮的列表里就没有专家自己的话。订单尾号仍在顾客那一格里。这两个事实不一样。实验时不要混。

## 第 98 到 113 行：第 2 轮故意说「上面这个订单」

```python
messages.append({
    "role": "user",
    "content": "那上面这个订单，如果已经拆封了，还能退吗？",
})
show_messages(messages)
reply, response = request_reply(client, settings.model, messages)
```

第二句里没有「86」，也没有「耳机」。它听得懂，只因为 `request_reply` 收到的是整份 `messages`，里面第 1 格还有尾号。注释写的就是这个。

发送前的打印应该是 4 格，下标 0 到 3：system、第一句 user、assistant、第二句 user。然后脚本再把第二段回复 `append` 上去，结束时 `len(messages)` 是 5。这第 5 格没有被再发送，因为没有第 3 轮。

第 2 轮的 `prompt` 数字应该大于第 1 轮。变大是因为纸变多了，不是因为模型「想得更久」。`completion` 才跟它新写了多少有关。

## 第 115 到 119 行：脚本自己把结论印出来

这四行 `print` 是在提醒你对照。它们不是发给模型的。如果你看到的第 2 轮打印并不是 4 格，先不要怪模型，先看有没有哪一行 `append` 被你改掉了。

## 第 122 到 127 行

和第一课一样的 `if __name__ == "__main__"`。没有它，别人 `import` 这个文件就会连打两次付费请求。注释说的是这件事。

## 改一行会看见什么

1. 注释掉第 96 行再运行。第 2 轮打印里没有 `assistant`。尾号还在第一句 user 里，模型仍可能提到 86。这个实验丢掉的是「专家自己的上一句」，不是整个历史。看完改回。
2. 让第 108 行不要把长列表传进去，改成只含最新那句 user 的新列表，并且 `show_messages` 也打印那份短列表。回复会开始不知道「上面」是哪一单。看完改回传 `messages`。
3. 把第二句改成带「订单尾号 86」。即使做了实验 2，模型也能答。说明这个实验靠「第二句本身不含关键事实」。改回去。

下一份文件仍是一次请求，但回信改成一段一段来：[第 3 个脚本](03_streaming.md)。
