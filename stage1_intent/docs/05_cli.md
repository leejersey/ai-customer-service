# 顺着带意图的客服逐行读

先在没有密钥时运行：

```bash
python stage1_intent/05_cli_with_intent.py
```

输入 `转人工`，回车，再输入 `退出`。你应看到意图是转人工、来源是 `rules`，回复是处理函数那句写死的话。然后程序结束。这条路径不调用模型。

有密钥时，同一条命令会多做两步：用模型做一次 JSON 分类，再让客服模型按这个意图说话。

## 和第 0 阶段客服的差别

退出命令、空行、`input`、历史列表，都和 `04_cli_chatbot.py` 相同。复习那份导读即可。新的是每一句顾客的话在进模型之前先分类。

文件开头先 `stage0_link.enable()`，才能 `from config import ...`。复习 [另一个文件夹](../../stage0_basics/python_basics/26_import_other_folder.md)。

## 没有密钥的那一支

```python
use_model = api_key_ready()
...
if use_model:
    settings = require_settings()
    ...
else:
    print("没有可用的 API 密钥。...")
```

`require_settings` 只在已经确认有密钥之后调用。如果无密钥也调用它，程序会在你打字之前就退出，规则对话没了。`client = None` 是先占一个名字。没有密钥的分支不会用到它。如果误用，会得到 `None` 没有 `chat` 的 `AttributeError`，而不是悄悄联网。

循环里 `else` 一支：

```python
result, reply = route_by_rules(user_text)
```

规则分类加处理函数。不往 `messages` 里追加。没有模型就没有要重发的历史。这和阶段 0 「列表是唯一记忆」不矛盾：这条分支根本没有第二次模型调用。

## 有密钥的那一支

先 `classify_by_llm`。网络失败就 `print_api_error`，再改用 `route_by_rules` 的结果，并把 `source` 改成 `rules-after-error`。`dict(result)` 复制一份再改，避免改到函数内部那份。你在屏幕上能看出这一句不是模型分的。

然后 `route` 得到处理函数的建议句 `reply_plan`。它先不直接说给顾客。拼进一条新的 `system` 消息：

```python
messages.append({"role": "user", "content": user_text})
messages.append({"role": "system", "content": note})
```

顾客原话单独一条，意图说明单独一条。以后回看列表，不会把「意图识别结果」误认为顾客说过的话。阶段 0 说过系统消息通常在第 0 条。这里在中间再插一条，是开发者在这一轮临时补充的说明。它会占 token，也会在下一轮被整包重发。

`request_reply` 和第 0 阶段一样，把整份 `messages` 送出去。失败时先弹出刚加的 system，再弹出 user。顺序不能反，否则会把更早的助手回复弹掉。两个 `if` 都看最后一条的 `role`，就是在确认弹的是这一轮的。

成功则把助手回复追加，并打印意图来源和回复。有密钥时，你看见的「小星」是模型写的，不是处理函数的原句。处理函数的原句在那条 system 笔记里，模型可以参考，也可以换一种说法。它仍然不能查数据库。系统提示和笔记都写了不要编造。

## 这一课没有新的 Python 语法

`while`、`input`、字典、函数返回两样东西，都链接回阶段 0。若某行看不懂，回到对应小课，不要在这一份里重新学一遍 `while`。

意图这一层做完了。它还不会下单、不会写工单。下一份说明阶段 2 接在哪里：[阶段小结](stage_summary.md)。
