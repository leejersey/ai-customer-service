# 阶段 0 教程目录

代码注释只解释「为什么要这样写」。每一行在做什么、数据长什么样、改掉以后会怎样，都写在下面这些文档里。建议先把对应脚本跑一遍，看见现象，再回来读。

环境还没装好的话，先按 [阶段 0 的安装说明](../README.md) 做完虚拟环境、依赖和 `.env`，再进入第 2 步。

## 推荐阅读顺序

1. [名词表](glossary.md)。先扫一遍。看不懂的词先跳过，做完实验再回来查。
2. [课前：配置怎么进程序](00_config.md)。搞清虚拟环境、环境变量，以及为什么创建客户端还不等于调用模型。
3. 运行 `python stage0_basics/01_hello_llm.py`，然后读 [第 1 课：一次请求，一次回复](01_hello_llm.md)。
4. 运行 `python stage0_basics/02_messages_roles.py`，然后读 [第 2 课：角色和必须重发的历史](02_messages_roles.md)。
5. 运行 `python stage0_basics/03_streaming.py`，然后读 [第 3 课：流式输出](03_streaming.md)。
6. 运行 `python stage0_basics/04_cli_chatbot.py`，然后读 [第 4 课：命令行客服](04_cli_chatbot.md)。
7. [阶段小结：这些概念以后用在哪里](stage_summary.md)。

没有密钥也可以把文档读完。脚本在缺密钥时会说明原因并退出，不会把项目弄坏。
