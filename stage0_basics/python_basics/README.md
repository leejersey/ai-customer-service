# Python 零基础小课

这些课不讲客服机器人本身。每一课只讲一个编程概念，并且都可以单独动手。

不要从第 1 课一口气读到最后。正确用法是：打开某一份[代码导读](../docs/README.md)，读到「先停下来读」时再进来，做完例子，再回到导读的下一行。

唯一的例外：如果你从来没用过终端，先把下面三课按顺序做完，否则后面的例子没有地方敲。

1. [终端：cd、ls、路径](01_terminal.md)
2. [`.py` 文件，以及 `python 文件.py` 在做什么](02_py_file.md)
3. [`print`：让程序把字显示出来](03_print.md)

其余课在导读里第一次用到时再读：

| 课 | 内容 | 我们的代码里第一次需要它 |
| --- | --- | --- |
| [04 注释](04_comments.md) | `#` 开头的字为什么不执行 | 每个脚本第 1 行 |
| [05 变量](05_variables.md) | 名字、等号、改值 | `TEMPERATURE = 0.7` |
| [06 数字](06_numbers.md) | 整数、小数、和字符串的差别 | `0.7`、`256` |
| [07 字符串](07_strings.md) | 引号、`\n`、三引号、f-string | `SYSTEM_PROMPT = "..."` |
| [08 import](08_import.md) | 模块、三种导入写法、Python 去哪找文件 | `from config import ...` |
| [09 虚拟环境和 pip](09_venv_pip.md) | 为什么要 `.venv`，第三方库从哪来 | 导入 `openai` 失败时 |
| [10 缩进](10_indentation.md) | 冒号下面必须退进一格 | 第一次写 `def` / `if` / `for` |
| [11 函数](11_functions.md) | `def`、参数、`return`、调用 | `def main()` |
| [12 if](12_if.md) | 条件、`else`、比较 | `if not response.choices` |
| [13 列表和字典](13_lists_dicts.md) | 创建、下标、`append`、键 | `messages = [...]` |
| [14 for](14_for.md) | 一个一个取出 | `for index, message in enumerate(...)` |
| [15 while](15_while.md) | 重复、`break`、`continue` | `04_cli_chatbot.py` 的 `while True` |
| [16 try/except](16_try_except.md) | 接住失败，而不是整段崩溃 | `try:` 包住那次请求 |
| [17 None](17_none.md) | 「这里没有值」 | `if usage is None` |
| [18 `if __name__`](18_name_main.md) | 为什么文件末尾有这句 | 每个脚本最后 |
| [19 input](19_input.md) | 停下来等你打一行字 | 命令行客服 |
| [20 环境变量和 .env](20_env.md) | 密钥为什么不写在 `.py` 里 | `config.py` 读 `DEEPSEEK_API_KEY` |
| [21 对象、方法和关键字参数](21_objects.md) | 点号调用、`name=value` | `client.chat.completions.create(...)` |
| [22 生成器](22_generators.md) | `yield`，以及流式的 `for` | `03_streaming.py` |
| [23 HTTP、API、JSON](23_http_json.md) | 一次网络请求长什么样 | 第一次 `create()` |
| [24 函数交回字典](24_return_dict.md) | 用键而不是位置带走多个结果 | `classify_by_rules` 的 `return` |
| [25 正则](25_regex.md) | `re`，按形状找订单号 | `rule_intent.py` 的 `import re` |
| [26 从别的文件夹导入](26_import_other_folder.md) | `sys.path.insert` | `stage0_link.enable()` |
| [27 解析不可靠的 JSON](27_json_parse.md) | `json.loads`、`JSONDecodeError`、`find` | `parse_model_output` |
| [28 函数放进字典](28_functions_in_dict.md) | 选中后再加括号调用 | `HANDLERS` |
| [29 读文本文件](29_read_text.md) | `Path.read_text` | 标准答案 JSON |
| [30 assert](30_assert.md) | 断言，以及 pytest 可以以后再装 | `test_rules.py` |
| [31 列表推导](31_list_comprehension.md) | 一行做出新列表 | 评估脚本取出标签 |
| [32 准确率](32_accuracy.md) | 猜对条数 / 总条数，混淆计数 | `metrics.py` |

每课都有：人话解释、比方、要你亲手敲的例子和预期输出、常见报错原文、两三道练习和答案。阶段 1 的新语法是第 24 到 32 课，仍然不要一口气读完，等导读叫停再读。
