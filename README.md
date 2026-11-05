# AI 客服机器人：从零开始的分阶段学习项目

这是一个给 Python 初学者的练习仓库。我们会一步步做「星河数码」的客服机器人：先学会调用大模型，再做意图识别、工单、记忆、检索和合规，最后收成一个带网页接口的智能体。

你不需要一开始就懂人工智能。阶段 0 只假设你愿意使用命令行，并且准备边做边学 Python。

**现在仓库里只完成了阶段 0。** 下面的路线图用来看全貌，打勾的阶段才有代码。

## 学习路线

- [x] **阶段 0：环境搭建 + LLM API 基础 + 命令行聊天机器人**
  - 虚拟环境、密钥、一次请求一次回复、消息角色、流式输出，以及一个带历史的命令行客服
  - 教程：[stage0_basics/README.md](stage0_basics/README.md)
- [ ] **阶段 1：意图识别**
  - 先判断顾客是在咨询、查订单、要退换货，还是在投诉，再决定怎么答
- [ ] **阶段 2：工具调用 + 工单处理（SQLite）**
  - 让模型在需要时调用函数，把查不到的事情写成工单，存进 SQLite
- [ ] **阶段 3：工作记忆 + 短期记忆（Redis）**
  - 区分「这一轮手头正在处理的事」和「这条对话最近几分钟的上下文」，并用 Redis 保存短期记忆
- [ ] **阶段 4：RAG**
  - 回答前先检索店铺自己的说明文档，减少模型凭空编造政策
- [ ] **阶段 5：长期记忆（FAISS）**
  - 把可以长期保留的顾客偏好写成向量，用 FAISS 再找回来
- [ ] **阶段 6：合规审查**
  - 在回复发出去之前检查：有没有索要密码、有没有乱承诺退款、有没有泄露不该说的信息
- [ ] **阶段 7：整合（智能体循环 + FastAPI）**
  - 把上面的能力收成一个会循环思考和调用工具的智能体，并用 FastAPI 提供接口

## 从这里开始

先按 [阶段 0 的安装说明](stage0_basics/README.md) 准备虚拟环境、依赖和密钥。装好之后不要只顺着代码往下读。按这个顺序，每课都是先运行，再读文档里的「为什么」和实验：

1. [名词表](stage0_basics/docs/glossary.md)，先扫一遍，记不住就先跳过。
2. [课前：配置怎么进程序](stage0_basics/docs/00_config.md)。
3. 运行 `01_hello_llm.py`，读 [第 1 课](stage0_basics/docs/01_hello_llm.md)。
4. 运行 `02_messages_roles.py`，读 [第 2 课](stage0_basics/docs/02_messages_roles.md)。
5. 运行 `03_streaming.py`，读 [第 3 课](stage0_basics/docs/03_streaming.md)。
6. 运行 `04_cli_chatbot.py`，读 [第 4 课](stage0_basics/docs/04_cli_chatbot.md)。
7. [阶段小结](stage0_basics/docs/stage_summary.md)，把这一阶段的限制对上后面的记忆、检索和工具。

目录也可以从 [stage0_basics/docs/README.md](stage0_basics/docs/README.md) 进入。没有 API 密钥也可以把文档读完。密钥缺失时脚本会用中文说明原因并退出，语法检查不需要联网，也不需要密钥。

## 现在仓库里有什么

```text
.
├── README.md                 本文件：路线图
├── requirements.txt          阶段 0 的依赖
├── .env.example              配置模板（可以提交）
├── .gitignore                忽略 .env、.venv、__pycache__
└── stage0_basics/
    ├── README.md             安装步骤，以及指向各课文档
    ├── config.py             读取配置、翻译 API 错误
    ├── 01_hello_llm.py       一次请求，一次回复
    ├── 02_messages_roles.py  角色和多轮历史
    ├── 03_streaming.py       流式输出
    ├── 04_cli_chatbot.py     命令行客服
    └── docs/                 按课分开的教程、名词表和阶段小结
```

## 这个仓库的约定

- 说明文字、文档和代码注释用中文。
- 变量名、函数名和文件名用英文。
- 真实密钥只放在你自己电脑上的 `.env` 里。仓库里只有 `.env.example` 这种假占位符。
- 代码注释只解释为什么这样写，不把每一行再翻译一遍。每一课在做什么、JSON 长什么样、改掉以后会怎样，写在 `stage0_basics/docs/`。
