# 阶段 0 怎么读

你是第一次写 Python 的话，不要先把 `config.py` 硬看完。语法在单独的 [基础课](../../00_python_basics/README.md) 里，不在本目录重讲。打开一份脚本导读，它会按文件从上到下带你走。遇到没学过的语法，导读会写「👉 不懂……？先看基础课」，你就去做那一课的例子，再回到原行。

## 本阶段需要的基础课

阶段 0 用到基础课第 01 到 23 课。第 24 课往后是阶段 1 才用的，这一阶段可以先不读。还不会打开终端时，先做清单最上面的三课，否则小例子没有地方敲。

- 👉 不懂终端？先看 [基础课 · 终端](../../00_python_basics/01_terminal.md)
- 👉 不会运行 `.py` 文件？先看 [基础课 · .py 文件](../../00_python_basics/02_py_file.md)
- 👉 不懂 `print`？先看 [基础课 · print](../../00_python_basics/03_print.md)
- [基础课 · 注释](../../00_python_basics/04_comments.md)
- [基础课 · 变量](../../00_python_basics/05_variables.md)
- [基础课 · 数字](../../00_python_basics/06_numbers.md)
- [基础课 · 字符串](../../00_python_basics/07_strings.md)
- [基础课 · import](../../00_python_basics/08_import.md)
- [基础课 · 虚拟环境](../../00_python_basics/09_venv_pip.md)
- [基础课 · 缩进](../../00_python_basics/10_indentation.md)
- [基础课 · 函数](../../00_python_basics/11_functions.md)
- [基础课 · if](../../00_python_basics/12_if.md)
- [基础课 · 列表和字典](../../00_python_basics/13_lists_dicts.md)
- [基础课 · for](../../00_python_basics/14_for.md)
- [基础课 · while](../../00_python_basics/15_while.md)
- [基础课 · try/except](../../00_python_basics/16_try_except.md)
- [基础课 · None](../../00_python_basics/17_none.md)
- [基础课 · if \_\_name\_\_](../../00_python_basics/18_name_main.md)
- [基础课 · input](../../00_python_basics/19_input.md)
- [基础课 · 环境变量](../../00_python_basics/20_env.md)
- [基础课 · 对象和方法](../../00_python_basics/21_objects.md)
- [基础课 · 生成器](../../00_python_basics/22_generators.md)
- [基础课 · HTTP、API、JSON](../../00_python_basics/23_http_json.md)

清单里的课不要一口气读完。先做最上面三课，然后只打开下面这份导读，跟着它走。导读叫停时再回到基础课。

1. [顺着 `01_hello_llm.py` 逐行读](01_hello_llm.md)。执行到 `import` 时，它会让你转去读 [config.py 的逐行导读](00_config.md)，读完再回来。

之后每一份都先运行，再逐行读。新语法才停下来，旧语法导读会指回已经读过的课。

2. 运行 `python stage0_basics/02_messages_roles.py`，读 [第 2 个脚本](02_messages_roles.md)。
3. 运行 `python stage0_basics/03_streaming.py`，读 [第 3 个脚本](03_streaming.md)。
4. 运行 `python stage0_basics/04_cli_chatbot.py`，读 [第 4 个脚本](04_cli_chatbot.md)。
5. [阶段小结](stage_summary.md)。
6. 大模型用词忘了再查 [名词表](glossary.md)。编程语法忘了回 [基础课](../../00_python_basics/README.md)，不要在名词表里找 `import`。

没有密钥也可以把导读读完。脚本缺密钥时会说明原因并退出。
