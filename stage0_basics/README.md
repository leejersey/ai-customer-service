# 阶段 0：环境、大模型 API 基础和命令行客服

这一阶段不做智能体框架，也不接数据库。目标只有一个：弄清你的 Python 程序是怎样把一段对话发给大模型，再把回复拿回来的。

跑完并读完各课之后，你应该能回答这些问题：

- 一次「调用大模型」发出去的 JSON 里有哪些字段，拿回来的正文在哪一格？
- `system`、`user`、`assistant` 分别是谁写的，删掉其中一格会怎样？
- 为什么第二句话要连同第一句话一起再发一遍，证据是什么？
- 流式输出时，完整回复是谁负责拼起来的？只打印、不保存会怎样？
- 密钥为什么不能写在 `.py` 文件里，创建客户端和真正拨号又差在哪？

这些答案不在代码注释里。注释只写「为什么这样写」。语法第一次出现时，导读会让你停下来去读 `python_basics/`。不要把那些小课当成可以跳过的附录。

没有 DeepSeek 密钥也可以把文档读完。密钥缺失时，脚本会打印中文说明并退出，不会把仓库弄坏。`python -m py_compile` 这种只检查语法的命令也不需要密钥。

## 文件一览

| 文件 | 你要它做什么 | 教程 |
| --- | --- | --- |
| `config.py` | 读取项目根目录的 `.env`，创建客户端，并把常见 API 错误翻译成中文 | [课前](docs/00_config.md) |
| `01_hello_llm.py` | 只发一轮，打印完整回复、结束原因和 token 用量 | [第 1 课](docs/01_hello_llm.md) |
| `02_messages_roles.py` | 连续发两轮，让你看见第二次请求里带着第一次的回复 | [第 2 课](docs/02_messages_roles.md) |
| `03_streaming.py` | 边生成边打印，并把片段拼回一整段 | [第 3 课](docs/03_streaming.md) |
| `04_cli_chatbot.py` | 一个可以连续聊天的命令行客服，输入 `退出` 结束 | [第 4 课](docs/04_cli_chatbot.md) |

零基础的读法在 [docs/README.md](docs/README.md)：顺着脚本走，遇到新语法就进入 [python_basics](python_basics/README.md)。名词表在 [docs/glossary.md](docs/glossary.md)，只解释大模型用词，不解释 `import`。阶段关系在 [docs/stage_summary.md](docs/stage_summary.md)。

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

## 5. 推荐阅读顺序

从来没写过程序的人，按 [docs/README.md](docs/README.md) 走。顺序是：

1. [终端](python_basics/01_terminal.md)、[怎样运行 `.py`](python_basics/02_py_file.md)、[`print`](python_basics/03_print.md)。这三课不依赖本仓库的脚本。
2. 打开 [01 的逐行导读](docs/01_hello_llm.md)。它会在 `import`、变量、字符串、函数、列表、`if`、`for`、异常、对象和 JSON 第一次出现时叫你停下来。执行到导入那一行，转去 [config.py 的逐行导读](docs/00_config.md)，读完再回来。
3. 运行并逐行读 [02](docs/02_messages_roles.md)、[03](docs/03_streaming.md)、[04](docs/04_cli_chatbot.md)。新出现的 `while`、`input`、生成器，导读里有单独的停课点。
4. 读 [阶段小结](docs/stage_summary.md)。

想只检查语法、不联网：

```bash
python -m py_compile stage0_basics/config.py stage0_basics/01_hello_llm.py stage0_basics/02_messages_roles.py stage0_basics/03_streaming.py stage0_basics/04_cli_chatbot.py
```

没有任何输出就表示通过。这条命令不读密钥。

上面第 1 到第 4 节是安装命令本身。命令为什么要激活 `.venv`、为什么 `.env` 不会被 Python 自动读到，以阅读顺序第 2 步里那两课为准，不要只抄命令。

## 6. 常见错误和解决办法

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

## 7. 实验、误解和测验在各课里面

不要只改一个提示词就算练完。每一课都有「跑起来然后观察」和「如果改掉它会怎样」，以及常见误解和小测验。改完要能说出你预期屏幕上哪一行会变。

- 温度、`max_tokens` 和删掉系统提示：[第 1 课](docs/01_hello_llm.md)
- 不重发历史、以及第二句为什么必须本身不含订单号：[第 2 课](docs/02_messages_roles.md)
- 只打印不保存、以及 `flush`：[第 3 课](docs/03_streaming.md)
- 失败后历史变脏、整行退出命令、编造的运单号：[第 4 课](docs/04_cli_chatbot.md)

阶段结束时用 [阶段小结](docs/stage_summary.md) 检查：你是在说「列表被重新发送」，还是在说「AI 记住了」。

## 8. 安全提醒

- `.env` 不要提交，不要打包发给同学，也不要贴进提问。
- 示例密钥和 `sk-` 开头的教学假字符串都不能用来调用，也不要换成你的真密钥后提交。
- 阶段 0 的客服没有订单数据库。它说自己查到了物流时，那是模型在编，不是程序查到的。
- 系统提示里的「不要索要密码」只是一句交给模型的话。程序本身还不会拦截敏感信息。

## 9. 下一步

阶段 0 完成的标志，不是脚本能跑，而是你能指出：正文在哪个字段、历史为什么在本地列表里、流式全文是谁拼的、系统提示为什么挡不住编造。

阶段 1 会在这个命令行客服前面加一层意图识别。那个代码还没有放进仓库。先做完各课实验，再读阶段小结。
