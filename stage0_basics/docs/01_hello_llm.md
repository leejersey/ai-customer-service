# 顺着 `01_hello_llm.py` 逐行读

## 本课需要的基础课

这一页不重讲语法。下面这些课在正文第一次用到时会再停一次。完整清单见 [导读目录](README.md#本阶段需要的基础课)。

- 👉 不懂终端？先看 [基础课 · 终端](../../00_python_basics/01_terminal.md)
- 👉 不会运行 `.py` 文件？先看 [基础课 · .py 文件](../../00_python_basics/02_py_file.md)
- 👉 不懂 `print`？先看 [基础课 · print](../../00_python_basics/03_print.md)
- [基础课 · 注释](../../00_python_basics/04_comments.md)
- [基础课 · 字符串](../../00_python_basics/07_strings.md)
- [基础课 · import](../../00_python_basics/08_import.md)
- [基础课 · 虚拟环境](../../00_python_basics/09_venv_pip.md)
- [基础课 · 变量](../../00_python_basics/05_variables.md)
- [基础课 · 数字](../../00_python_basics/06_numbers.md)
- [基础课 · 缩进](../../00_python_basics/10_indentation.md)
- [基础课 · 函数](../../00_python_basics/11_functions.md)
- [基础课 · None](../../00_python_basics/17_none.md)
- [基础课 · 对象和方法](../../00_python_basics/21_objects.md)
- [基础课 · 列表和字典](../../00_python_basics/13_lists_dicts.md)
- [基础课 · for](../../00_python_basics/14_for.md)
- [基础课 · try/except](../../00_python_basics/16_try_except.md)
- [基础课 · HTTP、API、JSON](../../00_python_basics/23_http_json.md)
- [基础课 · if](../../00_python_basics/12_if.md)
- [基础课 · if \_\_name\_\_](../../00_python_basics/18_name_main.md)

打开 `stage0_basics/01_hello_llm.py`，和这份导读对照。不要跳行。每一节标题里的行号就是文件里的行号。

看到「👉 不懂……？先看基础课」，就去把那一课的例子敲一遍，再回来看下一节。已经读过的课不会让你重读全文，只会提醒你这行用到了它。

如果你从来没用过终端，在看第 1 行之前先做清单最上面的三课。

运行这个文件的命令是（人要站在项目根目录）：

```bash
python stage0_basics/01_hello_llm.py
```

这就是[基础课 · .py 文件](../../00_python_basics/02_py_file.md)里的「厨师读菜谱」。还没有密钥时，程序会用中文停下来。那也算跑过了。

## 第 1 行：注释

```python
# -*- coding: utf-8 -*-
```

👉 不懂注释？先看 [基础课 · 注释](../../00_python_basics/04_comments.md)。

这行以 `#` 开头，Python 不执行。`coding: utf-8` 是告诉编辑器：文件里的中文按 UTF-8 保存。Python 3 默认就是这样读的。删掉这行，脚本通常仍能运行。留下它，是免得旧编辑器把中文注释存乱。

## 第 2 到 7 行：文件顶上的说明

```python
"""阶段 0 · 示例 1：一次请求，一次回复。
...
"""
```

👉 不懂字符串？先看 [基础课 · 字符串](../../00_python_basics/07_strings.md) 里「三引号」那一节。后半的 f-string 可以先看完，变量课马上就要用。

这三对引号包住的是文档字符串，给读文件的人看。没有 `print`，所以运行时不会出现在屏幕上。它也不是发给模型的系统提示。系统提示是后面的 `SYSTEM_PROMPT`。

删掉这一段，程序行为不变，只是打开文件的人少了一段目录。

## 第 9 行：这行注释在说设计，不是在执行

```python
# 读密钥、建客户端、翻译错误都放在 config.py。这一课只保留「发一次、看懂结果」。
```

又是注释。它解释为什么下一行不自己写读密钥的代码。Python 跳过它。

## 第 10 行：导入

```python
from config import create_client, describe_settings, print_api_error, require_settings
```

👉 不懂 import？先看 [基础课 · import](../../00_python_basics/08_import.md)。如果这里报 `ModuleNotFoundError`，再看 👉 不懂虚拟环境？先看 [基础课 · 虚拟环境](../../00_python_basics/09_venv_pip.md)。

这句话的意思是：找到和本文件同目录的 `config.py`，把那个文件从头到尾加载一遍，然后把四个函数名带到这里。加载 `config.py` 时，它的顶层会执行，函数体先不执行。

所以读完导入课之后，先停下来，把 [config.py 逐行导读](00_config.md) 读完，再回到本文件第 12 行。否则 `require_settings` 对你来说是一个没见过的名字。

四个名字如果有一个在 `config.py` 里不存在，你会看到 `ImportError: cannot import name '...'`。那不是密钥问题。

## 第 12 到 13 行：温度这个名字

```python
TEMPERATURE = 0.7
```

上面的注释说：第一课不用 0，免得你以为模型在背课文。注释不执行。下一行才执行。

👉 不懂变量？先看 [基础课 · 变量](../../00_python_basics/05_variables.md)。👉 不懂数字？先看 [基础课 · 数字](../../00_python_basics/06_numbers.md)。

`TEMPERATURE` 是盒子的名字，`0.7` 是放进去的小数。全大写表示我们不打算在这个文件里再改它。Python 并不禁止修改。后面把它交给 `temperature=` 这个参数。删掉这一行，第 54 行就会 `NameError: name 'TEMPERATURE' is not defined`，请求发不出去。

## 第 15 到 16 行：回复长度上限

```python
MAX_TOKENS = 256
```

又是一个整数变量。256 限制的是模型这次新写的长度，不是你的问题最多 256 个字。把这里改成 `5` 再运行，回复会很短，而且后面的 `finish_reason` 多半变成 `length`。那是实验，看完改回 256。

## 第 18 到 19 行：系统提示这句文字

```python
SYSTEM_PROMPT = "你是「星河数码」的客服助手。请用简体中文回答，语气礼貌，控制在两句话以内。"
```

字符串课已经读过。这里是把一句中文放进名字 `SYSTEM_PROMPT`。英文双引号是包装纸，不会送给模型。里面的「」是中文引号，是文字的一部分。

这句是岗位说明：你是谁、用什么语言、说多短。它还不是请求。要等放进 `messages` 才会被发送。删掉引号会 `SyntaxError`。把内容改成「只用三个词回答」，模型的说法会跟着变，这就是岗位说明在起作用，不是 Python 语法在起作用。

## 第 21 到 22 行：用户的问题

```python
USER_PROMPT = "你好，请用两句话介绍你能帮顾客做什么。"
```

和上一行同一类。单独做成变量，是为了你改问题时不用钻进函数里面。改成一句更长的话再运行，后面的 `prompt_tokens` 会变大，因为发出去的字变多了。

## 第 25 行：定义 main，先不执行里面

```python
def main() -> None:
```

👉 不懂缩进？先看 [基础课 · 缩进](../../00_python_basics/10_indentation.md)。👉 不懂函数？先看 [基础课 · 函数](../../00_python_basics/11_functions.md)。`-> None` 在函数课里。还不放心就再看一眼 [基础课 · None](../../00_python_basics/17_none.md)。

从下一行开始，凡是缩进进去的，都先被记住，不立刻做。一直到第 99 行都在 `main` 里面。文件要是没有最后的 `main()`，这些行一次都不会发生，自然也不会花钱。

## 第 26 到 27 行：调用读配置的函数

```python
settings = require_settings()
```

这是函数调用：名字后面有括号。`require_settings` 来自第 10 行的导入。括号里没有参数，因为密钥它自己去 `.env` 里找。

返回值放进 `settings`。失败时那个函数会直接结束程序，不会交回一个空密钥。所以没有密钥时，你看不到后面的「即将发送的消息」。

## 第 28 到 29 行：打印地址和模型，不打印密钥

```python
describe_settings(settings)
```

又是调用。把刚才的 `settings` 交过去。函数里面有三条 `print`，所以屏幕上出现接口地址、模型名，以及「密钥已读取」。没有 `sk-`。如果这里改成打印 `settings.api_key`，密钥就会出现在屏幕上。我们故意不这么做。

## 第 30 到 31 行：准备客户端

```python
client = create_client(settings)
```

👉 不懂对象和方法？先看 [基础课 · 对象和方法](../../00_python_basics/21_objects.md) 的前半，知道「一个值可以带着功能」。

`client` 是 SDK 给你的对象。这一行不联网。删掉它，后面的 `client.chat...` 会 `NameError`。留下它但不调用 `create`，则一分钱都不花。

## 第 33 到 37 行：要发送的两句话

```python
messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": USER_PROMPT},
]
```

👉 不懂列表和字典？先看 [基础课 · 列表和字典](../../00_python_basics/13_lists_dicts.md)。

这是一个列表，两格，每格是一个字典。第 0 格是岗位说明，第 1 格是问题。`SYSTEM_PROMPT` 没有引号，所以放进去的是盒子里的那句中文，不是这八个英文字母。

还没有第三格。没有历史。删掉 `system` 那一格，请求往往仍能成功，但回复不再稳定地自称星河数码客服。

## 第 39 到 44 行：发送前先把列表念出来

```python
print()
print("即将发送的消息：")
for index, message in enumerate(messages):
    print(f"[{index}] {message['role']}: {message['content']}")
```

`print` 课已经学过。`print()` 空一行。

👉 不懂 for？先看 [基础课 · for](../../00_python_basics/14_for.md)。f-string 如果当时跳过了，回到 [基础课 · 字符串](../../00_python_basics/07_strings.md) 的那一节。

`enumerate` 给编号和这一格。编号从 0 开始，所以你应该看到 `[0] system` 和 `[1] user`。这段打印不改变即将发送的内容。删掉它，模型收到的还是那两句，只是你看不见。

花括号里的引号换成了单引号 `message['role']`，因为外面的 f-string 已经用了双引号。包装纸不能嵌套同一种还没结束的引号。

## 第 46 到 57 行：真正发出请求

```python
print()
print("正在请求模型，请稍等……")
try:
    response = client.chat.completions.create(
        model=settings.model,
        messages=messages,
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        stream=False,
    )
```

👉 不懂 try/except？先看 [基础课 · try/except](../../00_python_basics/16_try_except.md)。对象课里「关键字参数」和「从左到右读点号」两节在 [基础课 · 对象和方法](../../00_python_basics/21_objects.md)。👉 不懂 HTTP、API、JSON？先看 [基础课 · HTTP、API、JSON](../../00_python_basics/23_http_json.md)。

`client.chat.completions` 只是往下取对象，没有括号。`create(...)` 才联网。五个等号都是关键字参数，不是给变量重新赋值。

这一次送出去的 JSON 正文相当于（示例结构，密钥不在里面）：

```json
{
  "model": "deepseek-chat",
  "messages": [
    {"role": "system", "content": "你是「星河数码」的客服助手。请用简体中文回答，语气礼貌，控制在两句话以内。"},
    {"role": "user", "content": "你好，请用两句话介绍你能帮顾客做什么。"}
  ],
  "temperature": 0.7,
  "max_tokens": 256,
  "stream": false
}
```

你屏幕上「即将发送的消息」应该对得上 `messages` 里的两句中文。`false` 是 JSON 里的写法，代码里写的是 `False`。

`stream=False` 表示等全文写完再回来。不写这个参数，SDK 默认也是整段返回。写出来是为了和第三个脚本对照。

## 第 58 到 61 行：失败就说明并结束

```python
except Exception as error:
    print_api_error(error)
    raise SystemExit(1)
```

`except` 和 `try` 对齐，所以只有 `create` 失败才进来。`error` 是失败本身。`print_api_error` 把它翻译成中文，自己不退出。接着 `raise SystemExit(1)` 由我们结束程序。

如果打印完还去读 `response`，会 `NameError`，因为赋值没成功。密钥错误时你应该看到「密钥被拒绝了」，而不是一长串没人管的英文。

## 第 63 到 66 行：没有回复列表就别去取第 0 个

```python
if not response.choices:
    print("接口返回成功，但里面没有任何回复。可以重试一次。")
    raise SystemExit(1)
```

👉 不懂 if？先看 [基础课 · if](../../00_python_basics/12_if.md)。

`response` 是 SDK 把回执 JSON 做成的对象。`.choices` 对上 JSON 里的 `"choices"` 数组。空的时候 `[0]` 会 `IndexError`。先问空不空。

正常成功时这一支不会走进去，你看不到这两句打印。

## 第 68 到 72 行：取出正文，并确认它是一段有字的文字

```python
reply = response.choices[0].message.content
if not isinstance(reply, str) or reply.strip() == "":
    print("模型没有返回文本。...")
    raise SystemExit(1)
```

从左读到右：第 0 个 choice，里面的 `message`，里面的 `content`。这才是要给人看的句子。JSON 里它在 `choices[0].message.content`。

`isinstance(reply, str)` 问它是不是字符串。`reply.strip() == ""` 问去掉空白后是不是空的。两个用 `or` 连起来：是其中任何一种，都算没有文本。

下面这份是**示例回执**，不是你某次运行的原文。用来对栏名：

```json
{
  "choices": [
    {
      "index": 0,
      "message": {"role": "assistant", "content": "你好，我是星河数码的客服助手。我可以说明退换货要准备什么，但现在查不到真实订单。"},
      "finish_reason": "stop"
    }
  ],
  "usage": {"prompt_tokens": 52, "completion_tokens": 36, "total_tokens": 88}
}
```

你的数字和句子都会不同。栏的位置不该不同。

## 第 74 到 76 行：把正文打印出来

```python
print()
print("模型回复：")
print(reply)
```

`reply` 没有引号，所以打印的是那句回复，不是四个字母 r、e、p、l、y。如果这里写成 `print("reply")`，屏幕上永远是单词 reply，你会以为模型坏了。

## 第 78 到 85 行：为什么停

```python
finish_reason = response.choices[0].finish_reason
...
if finish_reason == "length":
    ...
elif finish_reason == "stop":
    ...
```

`==` 是在问相等，不是赋值。`stop` 表示模型自己说完。`length` 表示撞上了 `MAX_TOKENS`。两种情况下你都可能看到一句通顺的中文，所以要单独看这个字段。

把 `MAX_TOKENS` 改成 5 再运行，应该走进 `length` 那一支。看完改回来。

## 第 87 到 96 行：token 用量

```python
usage = response.usage
if usage is None:
    print("这次响应没有附带 token 用量。")
else:
    print(f"提示 token（prompt_tokens）：{usage.prompt_tokens}")
    ...
```

先确认 [基础课 · None](../../00_python_basics/17_none.md) 已经读过。

`usage is None` 表示回执里没有用量这一栏。有的话，`prompt_tokens` 含系统提示和用户问题，`completion_tokens` 只算新写的，`total_tokens` 一般是两者相加。这些名字和示例 JSON 里的键一致，只是点号和方括号的差别。

改长 `USER_PROMPT` 后再看 `prompt_tokens`，它应该变大。这是「发出去的字变多了」的证据。

## 第 98 到 99 行：对方实际用的模型名

```python
print(f"服务端报告的模型：{response.model}")
```

有时和你请求的字符串不完全一样，会更具体。排错时以这一行为准，不要只看 `.env`。

## 第 102 到 109 行：只有直接运行才调用 main

```python
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n已手动中断。")
```

👉 不懂 `if __name__`？先看 [基础课 · if \_\_name\_\_](../../00_python_basics/18_name_main.md)。

直接用 `python .../01_hello_llm.py` 时条件成立，`main()` 才执行，前面的请求才会发生。`except KeyboardInterrupt` 接住 Ctrl+C。这不是密钥错误，所以只说「已手动中断」，不调用 `print_api_error`。

`main()` 如果缩进错到 `if` 外面，导入这个文件的人也会触发一次请求。看它是不是缩在 `if` 里面。

## 读完后你应该能指出来

- 哪一行才联网：第 51 行的 `create`。
- 正文从哪个字段来：`choices[0].message.content`。
- 密钥为什么不在你打印的消息里：它在请求头，不在 `messages`。

下一份脚本会把这个「一次来回」做两遍，并让第二句离开第一句就听不懂：[第 2 个脚本](02_messages_roles.md)。
