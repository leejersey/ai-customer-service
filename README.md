# AI 客服机器人：从零开始的分阶段学习项目

这是一个给 Python 初学者的练习仓库。我们会一步步做「星河数码」的客服机器人：先学会调用大模型，再做意图识别、工单、记忆、检索和合规，最后收成一个带网页接口的智能体。

你不需要一开始就懂人工智能。开始之前只假设你愿意使用命令行，并且准备边做边学 Python。

**现在仓库里完成了基础课、阶段 0、阶段 1、阶段 2 和阶段 3。** 下面的路线图用来看全貌，打勾的阶段才有代码。

## 学习路线

先学，或按需查阅 [Python 基础课](00_python_basics/README.md)，再按阶段 0 → 7 往下走。基础课是单独的一门课，放在所有阶段前面。阶段文档讲这一阶段的客服在做什么；某个语法第一次出现时只给链接，不在阶段目录里重讲。

- [x] **Python 基础课**
  - 终端、语法、函数、导入、文件与 JSON、错误处理、网络请求、测试，阶段 2 用到的类、数据库和函数调用，以及阶段 3 用到的切片、注解、dataclass 和计时。零基础按课号 01 → 45 学；也可以先做前三课，等阶段导读叫停再查
  - 教程：[00_python_basics/README.md](00_python_basics/README.md)
- [x] **阶段 0：环境搭建 + LLM API 基础 + 命令行聊天机器人**
  - 虚拟环境、密钥、一次请求一次回复、消息角色、流式输出，以及一个带历史的命令行客服
  - 教程：[stage0_basics/README.md](stage0_basics/README.md)
- [x] **阶段 1：意图识别**
  - 用规则和模型判断咨询、查订单、退款、投诉、转人工还是其他，再分流到不同的回复
  - 教程：[stage1_intent/README.md](stage1_intent/README.md)
- [x] **阶段 2：工具调用 + 工单处理（SQLite）**
  - 让模型在需要时调用函数，把查订单、退款和投诉写成真正的查询和工单，存进 SQLite
  - 教程：[stage2_tools_tickets/README.md](stage2_tools_tickets/README.md)
- [x] **阶段 3：工作记忆 + 短期记忆（Redis）**
  - 区分「这一轮手头正在处理的事」和「这条对话最近几分钟的上下文」，并用 Redis 保存短期记忆
  - 教程：[stage3_memory/README.md](stage3_memory/README.md)
- [ ] **阶段 4：RAG**
  - 回答前先检索店铺自己的说明文档，减少模型凭空编造政策
- [ ] **阶段 5：长期记忆（FAISS）**
  - 把可以长期保留的顾客偏好写成向量，用 FAISS 再找回来
- [ ] **阶段 6：合规审查**
  - 在回复发出去之前检查：有没有索要密码、有没有乱承诺退款、有没有泄露不该说的信息
- [ ] **阶段 7：整合（智能体循环 + FastAPI）**
  - 把上面的能力收成一个会循环思考和调用工具的智能体，并用 FastAPI 提供接口

## 从这里开始

从来没写过 Python：先打开 [基础课](00_python_basics/README.md)。可以按推荐顺序把课学完，也可以只做前三课（[终端](00_python_basics/01_terminal.md)、[运行 `.py`](00_python_basics/02_py_file.md)、[`print`](00_python_basics/03_print.md)），然后进入阶段。阶段导读里看到「👉 不懂……？先看基础课」，就跳回那一课，做完再回到原来那一行。

安装虚拟环境、依赖和密钥的命令在 [阶段 0 安装说明](stage0_basics/README.md)。那些命令在干什么，读基础课的 [虚拟环境](00_python_basics/09_venv_pip.md) 和 [环境变量](00_python_basics/20_env.md)。逐行在干什么，打开 [阶段 0 导读](stage0_basics/docs/README.md)。导读开头有「本阶段需要的基础课」。

阶段 0 读完后，打开 [阶段 1 导读](stage1_intent/docs/README.md)。规则分类、断言和准确率不需要密钥。模型分类在没有密钥时会说明并跳过。阶段 1 新用到的语法是基础课第 24 到 32 课，仍然在基础课目录里，不在 `stage1_intent/` 里。

阶段 1 读完后，打开 [阶段 2 导读](stage2_tools_tickets/docs/README.md)。建库、状态流转、工具函数、追问和离线演示不需要密钥。示例 4 在没有密钥时只打印工具说明书。示例 6 没有密钥时仍会把工单写进数据库。阶段 2 新用到的语法是基础课第 33 到 38 课，仍然在 `00_python_basics/`，不在 `stage2_tools_tickets/` 里。

阶段 2 读完后，打开 [阶段 3 导读](stage3_memory/docs/README.md)。工作记忆、截断、假摘要和离线演示不需要密钥，也不需要 Redis。示例 4 和示例 5 在 Redis 没启动时会说明并改用 fakeredis。示例 6 要在退出后再启动仍记得订单号，需要先按该目录 README 启动 Redis。阶段 3 新用到的语法是基础课第 39 到 45 课，仍然在 `00_python_basics/`，不在 `stage3_memory/` 里。

没有 API 密钥也可以把导读读完。阶段 0 的脚本在缺密钥时会退出。阶段 1 的规则脚本不会。阶段 2 的示例 4 会说明并跳过模型，其余示例可以跑完。阶段 3 的示例 3 没有密钥时只用假摘要，示例 7 不连接本机 Redis。

## 现在仓库里有什么

```text
.
├── README.md                 本文件：路线图
├── requirements.txt          阶段 0 到阶段 3 的依赖
├── .env.example              配置模板（可以提交）
├── .gitignore                忽略 .env、.venv、__pycache__、数据库文件
├── scripts/check_md_links.py 检查 Markdown 相对链接是否都能打开
├── 00_python_basics/         Python 基础课。01–45 课都在这里，按主题写在该目录的 README
├── stage0_basics/
│   ├── README.md             安装步骤，以及指向各课文档
│   ├── config.py             读取配置、翻译 API 错误
│   ├── 01_hello_llm.py       一次请求，一次回复
│   ├── 02_messages_roles.py  角色和多轮历史
│   ├── 03_streaming.py       流式输出
│   ├── 04_cli_chatbot.py     命令行客服
│   └── docs/                 顺着每个脚本逐行读的导读，语法只链接到基础课
├── stage1_intent/            意图识别：规则、JSON 分类、路由、评估、客服
├── stage2_tools_tickets/     工具调用和工单：SQLite、状态机、function calling
└── stage3_memory/            工作记忆和短期记忆：截断、摘要、Redis 会话
```

## 这个仓库的约定

- 说明文字、文档和代码注释用中文。
- 变量名、函数名和文件名用英文。
- 真实密钥只放在你自己电脑上的 `.env` 里。仓库里只有 `.env.example` 这种假占位符。
- 代码注释只解释为什么这样写。逐行在干什么，写在各阶段的 `docs/`。
- 基础概念只写在 `00_python_basics/`。新的一课按主题归进基础课 README 的某一章，写清学什么、哪些阶段会用到，并按现有课号往后编号。阶段文档不要复制课文：概念第一次出现时写成「👉 不懂……？先看基础课 · ……」，链接到 `00_python_basics/` 里的具体文件，并在该阶段导读开头维护「本阶段需要的基础课」。
- 阶段 2 到 7 以后如果需要还没讲过的语法，也加进这门基础课，不要在新的阶段目录里再开一份语法讲义。
- 改完文档后运行 `python scripts/check_md_links.py`，确认相对链接都指向存在的文件。
