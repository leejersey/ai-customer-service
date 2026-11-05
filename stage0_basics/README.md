# 阶段 0：环境、大模型 API 基础和命令行客服

这一阶段不做智能体框架，也不接数据库。目标只有一个：弄清你的 Python 程序是怎样把一段对话发给大模型，再把回复拿回来的。

跑完四个脚本之后，你应该能回答这些问题：

- 一次「调用大模型」在程序里到底是哪几行？
- `system`、`user`、`assistant` 分别是谁在说话？
- 为什么第二句话要连同第一句话一起再发一遍？
- 流式输出时，完整回复是谁负责拼起来的？
- 密钥为什么不能写在 `.py` 文件里？

没有 DeepSeek 密钥也可以把文档和注释读完。密钥缺失时，脚本会打印中文说明并退出，不会把仓库弄坏。`python -m py_compile` 这种只检查语法的命令也不需要密钥。

## 文件一览

| 文件 | 你要它做什么 |
| --- | --- |
| `config.py` | 读取项目根目录的 `.env`，创建客户端，并把常见 API 错误翻译成中文 |
| `01_hello_llm.py` | 只发一轮：一条系统消息加一条用户消息，打印完整回复和 token 用量 |
| `02_messages_roles.py` | 连续发两轮，让你看见第二次请求里带着第一次的回复 |
| `03_streaming.py` | 边生成边打印，并把片段拼回一整段 |
| `04_cli_chatbot.py` | 一个可以连续聊天的命令行客服，输入 `退出` 结束 |

四个脚本都要在**项目根目录**运行（根目录是有 `README.md` 和 `.env.example` 的那一层）。配置是按文件位置寻找 `.env` 的，所以在 `stage0_basics` 目录里执行 `python 01_hello_llm.py` 也可以找到密钥。教程下面的命令统一从根目录写。

## 开始之前

请安装 **Python 3.10 或更高版本**。检查方法：

```bash
python3 --version
```

Windows 上如果 `python3` 不存在，试试：

```bash
py --version
```

下面凡是写成 `python` 的地方，都换成你这台电脑上能用的那个命令。版本号至少是 3.10。

你还需要能上网。真正调用模型时会访问 `https://api.deepseek.com`。只做语法检查则不必联网。

## 1. 创建并激活虚拟环境

虚拟环境是这个项目专用的一套 Python 包，装在项目里的 `.venv` 目录中。这样不会把库装进系统 Python，换一台电脑时也不会和别的项目打架。`.venv` 已经写在 `.gitignore` 里，不要提交它。

在项目根目录执行。

macOS 或 Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell：

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

如果 PowerShell 提示不允许运行脚本，先看微软关于执行策略的说明，或暂时改用「命令提示符」：

```bat
py -m venv .venv
.venv\Scripts\activate.bat
```

激活成功后，命令行前面通常会多出 `(.venv)`。以后每次新开一个终端想继续练习，都要重新执行上面的激活命令。`python -m venv` 只需要做一次。

退出虚拟环境的命令是：

```bash
deactivate
```

## 2. 安装依赖

仍然在项目根目录，并且确认已经激活虚拟环境：

```bash
pip install -r requirements.txt
```

这一阶段只有两个库：

- `openai`：OpenAI 官方的 Python SDK。DeepSeek 提供了与它兼容的聊天接口，所以我们不另找一个 DeepSeek 专用库，只是把地址和密钥换成 DeepSeek 的。
- `python-dotenv`：从 `.env` 文件把配置读进环境变量。

本仓库使用的调用方式是 `chat.completions`（聊天补全）。OpenAI 后来还有一套 Responses API，阶段 0 **不要**照着那套新文档改，因为我们要对齐的是 DeepSeek 的兼容接口。

装完可以确认库已经在当前环境里：

```bash
python -c "import openai, dotenv; print('依赖已安装')"
```

如果这行报 `ModuleNotFoundError`，多半是虚拟环境没有激活，pip 把包装到了别的 Python 上。

## 3. 获取 DeepSeek API 密钥

1. 打开 [DeepSeek 开放平台](https://platform.deepseek.com) 并登录。
2. 找到 API keys 页面，创建一个新密钥。
3. 密钥通常只完整显示一次。立刻复制到你自己的 `.env`，不要发到聊天里，也不要截图发出去。
4. 到余额页面确认账户可以调用。没有余额时，接口常返回 HTTP 402，脚本会提示你去看余额。

这是 DeepSeek 的密钥，不是 OpenAI 的密钥。两边不通用。

调用会花少量费用。本阶段的示例都很短，但不要自己写死循环反复请求。

## 4. 填写 .env

在项目根目录把模板复制成真正的配置文件。

macOS 或 Linux：

```bash
cp .env.example .env
```

Windows 命令提示符：

```bat
copy .env.example .env
```

用文本编辑器打开 `.env`，改成你自己的密钥。三个名字要保持不变：

```bash
DEEPSEEK_API_KEY=在这里粘贴你的DeepSeek密钥
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

填写时注意：

- 只替换第一行等号右边的文字。不要加引号，等号两边不要加空格。
- 第二行保持 `https://api.deepseek.com`。不要写成 `https://api.deepseek.com/chat/completions`。SDK 会自己在地址后面接上 `/chat/completions`。你把路径写进 `base_url`，最终地址就会错。
- 第三行是模型名。本阶段约定使用 `deepseek-chat`，四个脚本都从这里读，所以换模型时不用改 Python 文件。
- 文件请保存为 **UTF-8**。`.env` 被 `.gitignore` 忽略了，`git status` 里不应该出现它。

关于模型名：截至 2026 年 11 月，DeepSeek 官方快速开始文档里的示例模型是 `deepseek-flash`（另有 `deepseek-v4-pro`）。如果运行后原始信息里说模型不存在、已下线或 model 不合法，把 `.env` 里这一行改成：

```bash
DEEPSEEK_MODEL=deepseek-flash
```

然后重新运行即可。

错误示范，不要把密钥写进代码：

```python
client = OpenAI(api_key="sk-不要把真实密钥写在这里")
```

代码会进入 Git 历史，删掉这一行也清不掉已经推送过的提交。密钥只放 `.env`。

## 5. 按顺序运行四个脚本

下面的命令都在项目根目录、已激活的虚拟环境里执行。模型的具体用词每次可能不同。只要脚本没有报错，并且打印出了中文回复，就算这一步成功。

想先确认语法、暂时又不想联网时，可以执行：

```bash
python -m py_compile stage0_basics/config.py stage0_basics/01_hello_llm.py stage0_basics/02_messages_roles.py stage0_basics/03_streaming.py stage0_basics/04_cli_chatbot.py
```

没有任何输出就表示语法通过。这条命令不会读取密钥，也不会调用 API。

### 5.1 一次请求，一次回复

```bash
python stage0_basics/01_hello_llm.py
```

你应该看到：

1. 接口地址、模型名，以及「密钥已读取、屏幕上不显示」。
2. 即将发送的两条消息：`system` 和 `user`。
3. 一段客服风格的回复。
4. `finish_reason`。`stop` 表示模型自己说完了，`length` 表示被 `MAX_TOKENS` 截断。
5. 三组 token 数字：提示、回复、合计。

这一课的代码几乎没有封装。请打开 `01_hello_llm.py`，对着 `client.chat.completions.create(...)` 看：一次 API 调用就是这个函数。

### 5.2 角色和多轮历史

```bash
python stage0_basics/02_messages_roles.py
```

脚本会自己发两轮，不用你打字。请重点比较两次「即将发送的 messages」：

- 第 1 轮只有 `system` 和第一句 `user`。
- 第 1 轮的回复被追加成 `assistant`。
- 第 2 轮又多了一句 `user`：「那上面这个订单，如果已经拆封了，还能退吗？」

第二句里的「上面这个订单」指的是尾号 86。模型能接上，是因为我们把第一轮也放进了同一次请求，不是因为网站记住了你。

再看两轮的 `prompt` token。第二轮通常更大，因为历史变长了。

### 5.3 流式输出

```bash
python stage0_basics/03_streaming.py
```

「模型：」后面的文字会陆续出现。网速很快时，可能快到像一下子打印出来，这是正常的。脚本最后还会：

- 把片段重新拼成完整回复，再打印一遍
- 告诉你收到了多少个非空片段
- 提醒你：如果要做多轮对话，必须把拼好的全文放进 `assistant` 消息

### 5.4 命令行客服

```bash
python stage0_basics/04_cli_chatbot.py
```

试着连续输入两句，第二句引用第一句，例如：

```text
你：我想退昨天买的耳机
你：那运费谁出？
```

第二句没有再说「耳机」，但历史里有上一句，所以小星有机会接上。它**不能**查询真实物流。如果你报一个订单号，它应该按系统提示承认目前查不到，而不是编一个运单号。模型有时仍会说得太满，这正是后面合规阶段要处理的事。

结束对话时，整行输入下面任意一个词：

```text
退出
quit
exit
q
```

直接按 Ctrl+C 也可以离开。单独按回车不会发给模型，脚本会提醒你再输入。

每一轮成功后，屏幕上会显示当前 `messages` 有多少条。这个数字包含最前面的系统提示，而且会一直增加。

## 6. 建议怎么读这些代码

不要从 `config.py` 硬读。推荐顺序是：

1. 先跑 `01_hello_llm.py`，再从上到下读它。每一段中文注释都对应紧挨着的那一行代码。
2. 再跑、再读 `02`，专门看列表是怎样 `append` 的。
3. 读 `03`，只关注 `for chunk in stream` 这个循环。
4. 读 `04`，看 `while True` 怎样把前面三课套在一起。
5. 最后读 `config.py`。它负责找 `.env`、拒绝占位密钥，以及把英文异常翻译成中文。四个脚本都 `import` 它，所以这些事不用各写一遍。

注释故意写得很密。阶段 0 结束以后，日常代码不需要给每一行都写注释；这里是为了让你第一次能独立看懂。

## 7. 关键概念

### 7.1 什么是一次 LLM API 调用

LLM 是大语言模型。在这个项目里，你并不在自己的电脑上运行那个模型。你的脚本把一段 JSON 通过 HTTPS 发给 DeepSeek 的服务器，服务器跑模型，再把 JSON 结果返回来。

可以把它想成一次函数调用，只不过函数的本体在别人的机房里：

```text
你的脚本
  |
  |  model、messages、temperature、max_tokens
  v
OpenAI SDK  ---- HTTPS ---->  https://api.deepseek.com/chat/completions
  ^                                    |
  |                                    v
打印到终端  <---- 回复文本和 token 用量 ----  大模型
```

SDK 是帮你组请求、带上密钥、解析结果的库。密钥放在请求头里，不会出现在我们打印的消息正文中。`create_client()` 只是把地址和密钥准备好，**真正联网发生在** `chat.completions.create(...)`。

和这次调用关系最大的参数是：

| 参数 | 作用 |
| --- | --- |
| `model` | 用哪一个模型。我们从 `DEEPSEEK_MODEL` 读取 |
| `messages` | 到目前为止的对话，每一条都有 `role` 和 `content` |
| `temperature` | 回答的随机程度 |
| `max_tokens` | 这次回复最多生成多少 token |
| `stream` | `False` 等全文；`True` 一段段返回 |

### 7.2 消息和角色

`messages` 是一个列表，不是一段糊在一起的长字符串。每一项都是字典：

```python
{"role": "system", "content": "你是客服……"}
{"role": "user", "content": "我想退货"}
{"role": "assistant", "content": "可以的，请提供订单尾号。"}
```

| 角色 | 谁写的 | 做什么 |
| --- | --- | --- |
| `system` | 开发者 | 规定身份、语气和禁止事项。通常一直放在第 0 条 |
| `user` | 用户 | 顾客这次说的话 |
| `assistant` | 模型 | 模型之前的回复。下一轮要原样放回去，模型才知道自己说过什么 |

没有第四种「记忆角色」。记忆如果存在，也只是我们把旧消息继续留在这个列表里。

`04_cli_chatbot.py` 的系统提示还写了两件阶段 0 做不到的事：查不到真实订单，也不准跟顾客要密码和完整银行卡号。模型会尽量遵守，但不能当成已经做好的安全系统。

### 7.3 Token

模型不按「一次调用固定价格」来理解长度，而是按 token 计。token 是模型内部的一小段文本。一个英文单词常常是一到数个 token；一个汉字也常常要占一个甚至更多 token。你不需要自己切分，接口会在 `usage` 里告诉你结果。

- `prompt_tokens`：这次**发出去**的内容，包含系统提示、之前所有轮次和当前问题。
- `completion_tokens`：模型**新写回来**的内容。
- `total_tokens`：两者相加。

所以历史越长，下一次的 `prompt_tokens` 越大，费用和等待都会上升。`max_tokens` 限制的是回复，不是历史。回复因为这个上限停住时，`finish_reason` 会是 `length`。

### 7.4 temperature

`temperature` 影响模型在多个合理用词之间怎么选。

- 接近 `0`：更稳定，同一句问两遍，回答更像。客服适合这个区间。
- `0.7` 左右：仍然通顺，但用词会有变化。示例 1 和示例 3 用的是这个值。
- 再升高：更发散，也更容易跑题或说得不严谨。

示例 4 使用 `0.3`，因为客服更需要稳，而不是每句都换一种说法。温度不是「更聪明」的旋钮。

### 7.5 流式输出

非流式时，程序在 `create()` 里一直等到全文结束，然后你才看到第一个字。流式时，服务器每写出一小段就发一个 chunk。总生成时间差不多，但屏幕上更早有字，等待感会轻一些。

每个 chunk 里真正要看的是：

```text
chunk.choices[0].delta.content
```

`delta` 的意思是「新增的这一小段」，不是累计到目前的全文。它经常是空的：有的包只是在说「开始了」或「结束了」。

因此脚本要做三件打印函数不会替你做的事：

1. 跳过空片段。
2. 用 `end=""` 把片段接在同一段话里，并用 `flush=True` 立刻显示。`print` 默认可能攒一批才出现在屏幕上。
3. 用一个列表收集片段，最后 `"".join(pieces)` 得到可以放进历史的完整回复。

只打印、不保存，下一轮就断了。示例 3 的结尾把这件事写成了一行你将来要写的代码。

### 7.6 为什么历史必须重新发送

一次 HTTP 请求结束，服务器就处理完了。下一次请求是新的，默认不会记得上一次的 `messages`。这也叫无状态。

错误的直觉是：我已经跟它说过订单尾号，后面只发新的一句就行。那样的话，第二句「上面这个订单」没有所指。

正确的做法是客户端自己保存列表：

```text
第 1 次发送：[system, user]
把回复追加为 assistant

第 2 次发送：[system, user, assistant, user]
```

`02_messages_roles.py` 会把这两次列表都打印出来。`04_cli_chatbot.py` 则在你每次回车时做同样的事。

代价你已经在 token 那一节看到了：列表无限变长不现实。后面的短期记忆、RAG 和长期记忆，都是在解决「不能每次把所有话原样塞回去」的问题。阶段 0 先把这个限制看清楚。

请求失败时，示例 4 会把刚刚放进去的那句 `user` 再 `pop` 掉。否则下一轮会带着一句从来没有得到过回复的话，历史就脏了。

## 8. 常见错误和解决办法

| 你看到的现象 | 原因 | 处理 |
| --- | --- | --- |
| `ModuleNotFoundError: openai` 或 `dotenv` | 依赖没装进当前这个 Python | 确认命令行有 `(.venv)`，再执行 `pip install -r requirements.txt` |
| 终端里的中文说明：没有可用的 `DEEPSEEK_API_KEY` | 还没有 `.env`，或仍是占位文字 | 按第 4 节复制并填写。也可以先不调用，继续读代码 |
| `AuthenticationError`，或 HTTP 401 | 密钥被拒绝 | 重新复制密钥，去掉空格和引号；确认它来自 DeepSeek |
| 原始信息里出现 402 或余额不足 | 账户没有可用额度 | 到控制台查看余额 |
| `RateLimitError` 或 HTTP 429 | 请求太密，或额度临时用尽 | 等一会儿再试，不要写循环重刷 |
| `APIConnectionError` 或超时 | 没连上服务器 | 检查网络和代理。`base_url` 保持 `https://api.deepseek.com` |
| `NotFoundError`，或提示 model 不存在 | 模型名已不能用，或地址写错了 | 把 `DEEPSEEK_MODEL` 改成 `deepseek-flash`。不要把 `/chat/completions` 写进 `base_url` |
| 读取 `.env` 失败，并提示编码 | 文件不是 UTF-8 | 用编辑器另存为 UTF-8 |
| 终端里的中文变成乱码 | 终端编码不是 UTF-8 | 换用支持 UTF-8 的终端；Windows 可设置 `PYTHONIOENCODING=utf-8` |
| 第二句和第一句对不上 | 没有把上一轮放回 `messages` | 对照示例 2，确认既追加了 `assistant`，也追加了新的 `user` |
| 流式输出挤成一行，或等很久才出现 | 没设置 `end=""` 或 `flush=True` | 对照示例 3 的 `print(piece, end="", flush=True)` |
| 程序好像卡住 | 正在等网络，失败时 SDK 还会再试一次 | 最多等大约一分钟。仍无结果就看是不是连接错误 |
| `git status` 里出现 `.env` | 忽略规则没生效，或文件名不对 | 文件名必须正好是 `.env`，并且位于项目根目录。不要执行 `git add .env` |

脚本捕获接口错误后会打印「错误类型」和「原始信息」。处理问题时请把这两行一起看：中文说明告诉你方向，原始信息告诉你服务器的原话。

## 9. 小练习

做的时候只改你能解释的那几行。每做完一题，用对应的脚本跑一次。

1. **换一个问题。** 修改 `01_hello_llm.py` 里的 `USER_PROMPT`，改成一个你真正想问客服的句子。观察回复和 token 数字怎么变。
2. **改系统提示。** 把示例 1 的 `SYSTEM_PROMPT` 改成「只用三条短列表回答」。看模型是否听开发者的话，而不是只听用户的话。
3. **比较温度。** 把示例 1 的 `TEMPERATURE` 先改成 `0`，同一问题运行两次；再改成 `1.2`，再运行两次。感受稳定和发散的差别，然后改回 `0.7`。
4. **增加第三轮。** 在 `02_messages_roles.py` 末尾再追加一句用户消息：「那运费呢？」发送前把上一轮的 `assistant` 放进列表。确认新打印出来的 `messages` 里还能看到订单尾号 86。
5. **故意弄丢历史。** 把示例 2 里「追加 assistant」的那一行先注释掉，运行并看第二轮还知不知道订单。看完一定改回来。
6. **增加清空命令。** 在 `04_cli_chatbot.py` 里，如果用户整行输入 `清空`，就把 `messages` 恢复成只含那一条 `system`。不要把系统提示也删掉，否则客服人设会丢。
7. **思考题，不用交代码。** 如果顾客连续聊了 100 轮，而我们每次都重发全部历史，费用、速度和回答质量会怎样？这和后面的 Redis、RAG、FAISS 分别可能解决哪一种「记不住」？
8. **选做：挡一下银行卡号。** 现在顾客如果输入一长串数字，程序会原样放进 `messages` 发给模型。可以在 `append` 之前做一个很粗的检查：发现连续 12 位以上数字时，不发送，并提示「请不要提供完整银行卡号」。阶段 6 才会做真正的合规审查，这里只是体会「发送前还能插一步」。

## 10. 安全提醒

- `.env` 不要提交，不要打包发给同学，也不要贴进提问。
- 示例密钥和 `sk-` 开头的教学假字符串都不能用来调用，也不要换成你的真密钥后提交。
- 阶段 0 的客服没有订单数据库。它说自己查到了物流时，那是模型在编，不是程序查到的。
- 系统提示里的「不要索要密码」只是一句交给模型的话。程序本身还不会拦截敏感信息，除非你做了练习 8 那样的检查。

## 11. 下一步

阶段 0 完成的标志，是你能独立讲清楚：客户端、一次 `create()`、三种角色，以及历史为什么在本地列表里。

阶段 1 会在这个命令行客服前面加一层意图识别：先判断顾客想干什么，再组织回答。那个代码还没有放进仓库。做完上面的练习再往下走即可。
