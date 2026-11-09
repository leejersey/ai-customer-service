# 顺着 `04_cli_chatbot.py` 逐行读

先运行：

```bash
python stage0_basics/04_cli_chatbot.py
```

不要只说「你好」。先输入「我想退昨天买的耳机」，再输入「那运费谁出」，最后整行输入 `退出`。读的时候对照屏幕上的条数。

## 第 1 到 11 行

文档字符串比前几个文件多说明了退出词：必须是整行。第 11 行的导入和前面相同。

## 第 13 到 18 行：温度，以及退出词的集合

```python
TEMPERATURE = 0.3
MAX_TOKENS = 512
EXIT_COMMANDS = {"quit", "exit", "q", "退出"}
```

`0.3` 是希望客服说法稳一点。它不让回复变得更真实。

`EXIT_COMMANDS` 用花括号但里面没有冒号，所以是集合，不是字典。先回到 [列表课](../python_basics/13_lists_dicts.md) 的「集合」一节，把那两行 `in` 的例子敲一遍，如果当时跳过了。

`"quit" in EXIT_COMMANDS` 为真。`"我想 quit" in EXIT_COMMANDS` 为假。注释说的就是：句子中间出现这个词，不要把人踢出去。

## 第 20 到 27 行：很长的岗位说明

三引号字符串。加载时只是放进 `SYSTEM_PROMPT`，还不发送。内容你要逐句当真地读，但要知道它们的身份：

- 规定名字、语言、句子长短。
- 承认没有订单数据库。
- 禁止编运单号、到货时间、金额。
- 禁止索要密码和完整卡号。

这些是交给模型的文字，不是 Python 的 `if`。程序里没有任何一行在读数据库，也没有任何一行在检查银行卡。问它「订单 10086 的运单号」时，它如果编了一个号码，那个号码是假的。阶段 2 才会有真正的查询。阶段 6 才会在发送前后做检查。

## 第 30 到 46 行：request_reply 失败时不自己结束程序

```python
def request_reply(client, model, messages):
    response = client.chat.completions.create(...)
    if not response.choices:
        raise RuntimeError("响应里没有 choices。")
    ...
    return reply
```

`create` 和第一课相同，`messages` 仍然是整份历史。注释提醒：只传最新一句，对话就接不上。

这里没有 `try`。失败会抛出去。没有 choices 时主动 `raise RuntimeError`，也就是自己制造一个失败，让外层的 `except` 接住。如果在这里 `raise SystemExit`，一次空响应就会把整个客服关掉。外层还想继续等下一句。

这个函数只 `return reply`，不交还 `usage`。这一课的重点不是比较 token，而是循环。

## 第 49 到 58 行：客户端和列表都在循环外面

```python
client = create_client(settings)
messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
]
```

放进 `while` 里面的话，每一句都会得到一叠只剩封面的新纸，第二句永远接不上。记忆是这个 `messages` 变量还活着，不是 `client` 这个对象记得你。程序一退出，变量就没了。注释说的是这件事。

四行 `print` 是给操作的人看的说明书，不进入 `messages`，所以不计进发给模型的 token。

## 第 66 到 75 行：循环开始，先读一行

```python
while True:
    try:
        user_text = input("你：").strip()
    except EOFError:
        print("\n输入结束，再见。")
        return
    except KeyboardInterrupt:
        print("\n已退出。")
        return
```

先停下来读 [while](../python_basics/15_while.md) 和 [input](../python_basics/19_input.md)。`while True` 不会自己停。离开的办法在后面的 `return`。

`input` 交回字符串。`.strip()` 去掉首尾空格，避免 `退出 ` 对不上集合。

`EOFError` 是没有下一行了（Ctrl+D 或管道结束）。这不是 401。当成告别。`KeyboardInterrupt` 是 Ctrl+C。两个 `except` 都 `return`，函数结束，循环一起结束。

`\n` 在 [字符串课](../python_basics/07_strings.md)。Ctrl+C 时光标常常停在一行中间，先换行，字才不会粘在 `你：` 后面。

## 第 77 到 84 行：先认口令，再决定发不发

```python
if user_text.lower() in EXIT_COMMANDS:
    print("小星：感谢咨询，再见。")
    return
if user_text == "":
    print("请输入内容。想结束时，整行输入：退出")
    continue
```

`.lower()` 把 `QUIT` 变成 `quit`，中文不受影响。成立就 `return`。这一支在 `append` 之前，所以「退出」不会变成一次付费请求，也不会进历史。

空字符串走 `continue`：回到 `while` 的开头再 `input`。改成 `return` 的话，多按一次回车就下班。这是 while 课的练习所对应的真实代码。

`我想 quit 退货` 两个 `if` 都不进，会落到下面被发送。你可以现在就试。

## 第 86 到 95 行：先放进列表，失败再拿出来

```python
messages.append({"role": "user", "content": user_text})
try:
    reply = request_reply(client, settings.model, messages)
except Exception as error:
    print_api_error(error)
    if messages and messages[-1]["role"] == "user":
        messages.pop()
    print("这一轮没有写入历史。...")
    continue
```

先 `append` 再请求，是因为请求需要这句已经在列表里。失败时这句就成了没有配对回复的最后一格。`messages[-1]` 是最后一格。确认它是 `user` 再 `pop`，避免误删封面。

`continue` 回到输入，不执行下面的 `append` assistant。所以失败的一轮，条数不加。

想看见这件事：把 `.env` 里的模型名临时改成 `definitely-not-a-model`，问一句，应该看到中文错误和「没有写入历史」，然后还能输入 `退出`。看完把模型名改回去。

如果注释掉 `pop` 再制造一次失败，下一句会把那句没得到回复的 user 一起送出去。历史就脏了。

## 第 97 到 101 行：成功才成对增加

```python
messages.append({"role": "assistant", "content": reply})
print(f"小星：{reply}")
print(f"（当前 messages 共 {len(messages)} 条，下一次会全部重新发送。）")
```

一条 user 加一条 assistant。开头还有一条 system。所以第一轮成功后条数是 3，第二轮成功后是 5。如果你数到 4 或 6，先停，不要加新功能，回到这一节对一下每次成功是不是加了两格。

这一行打印的条数是本机列表的 `len`。服务器没有保存一份对应的档案。下一次 `create` 会把这些全部再放进 JSON。条数涨，`prompt_tokens` 就涨。

## 第 104 到 109 行

`if __name__` 包住 `main()`。没有这道门，别人导入这个文件就会立刻进入 `input` 循环。Ctrl+C 若发生在 `main` 里的 `input` 上，内层那个 `except` 会先接住。最外层这个是在防循环外面的打断。

## 这一份文件仍然不会的事

它会接上「那运费谁出」，是因为列表还在，并且每轮整包重发。关掉再开，不靠别的存储，耳机和运费都没了。系统提示写了不能查订单，只是降低编造的倾向。

这些限制以后分别交给意图识别、SQLite 工具、Redis、文档检索、长期记忆和合规检查。对照表在 [阶段小结](stage_summary.md)。
