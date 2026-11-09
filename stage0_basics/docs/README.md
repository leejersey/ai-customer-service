# 阶段 0 怎么读

你是第一次写 Python 的话，不要从头到尾通读概念，也不要先把 `config.py` 硬看完。打开一份脚本导读，它会按文件从上到下带你走。遇到没学过的语法，导读会写「先停下来读」，你就去 `python_basics` 做那一课的例子，再回到原行。

还不会打开终端时，先做这三课，否则小例子没有地方敲：

1. [终端](../python_basics/01_terminal.md)
2. [`.py` 文件和 `python 文件.py`](../python_basics/02_py_file.md)
3. [`print`](../python_basics/03_print.md)

然后只打开这一份导读，跟着它走完全部语法课：

4. [顺着 `01_hello_llm.py` 逐行读](01_hello_llm.md)。执行到 `import` 时，它会让你转去读 [config.py 的逐行导读](00_config.md)，读完再回来。

之后每一份都先运行，再逐行读。新语法才停下来，旧语法导读会指回已经读过的课。

5. 运行 `python stage0_basics/02_messages_roles.py`，读 [第 2 个脚本](02_messages_roles.md)。
6. 运行 `python stage0_basics/03_streaming.py`，读 [第 3 个脚本](03_streaming.md)。
7. 运行 `python stage0_basics/04_cli_chatbot.py`，读 [第 4 个脚本](04_cli_chatbot.md)。
8. [阶段小结](stage_summary.md)。
9. 大模型用词忘了再查 [名词表](glossary.md)。编程语法忘了回 [python_basics 目录](../python_basics/README.md)，不要在名词表里找 `import`。

没有密钥也可以把导读读完。脚本缺密钥时会说明原因并退出。
