# 阶段 2 导读目录

先做完阶段 1 的 [导读](../../stage1_intent/docs/README.md)。这一阶段不再重讲意图规则怎么写。新语法出现时，导读会停下来，去 `00_python_basics/` 第 33 课往后。

## 本阶段需要的基础课

新的，等导读叫停再读，不要先通读：

- [33 类和方法](../../00_python_basics/33_class_methods.md)
- [34 with](../../00_python_basics/34_with.md)
- [35 sqlite3 与 SQL](../../00_python_basics/35_sqlite.md)
- [36 日期时间](../../00_python_basics/36_datetime.md)
- [37 默认参数](../../00_python_basics/37_default_args.md)
- [38 星号解包](../../00_python_basics/38_star_args.md)

还会用到、这一阶段第一次依赖它们把工单跑起来的旧课：

- [23 JSON 和 dumps](../../00_python_basics/23_http_json.md)
- [25 正则](../../00_python_basics/25_regex.md)
- [26 从别的文件夹导入](../../00_python_basics/26_import_other_folder.md)
- [27 解析 JSON](../../00_python_basics/27_json_parse.md)
- [28 函数放进字典](../../00_python_basics/28_functions_in_dict.md)
- [30 assert](../../00_python_basics/30_assert.md)

## 阅读顺序

建库、状态、工具、追问和离线演示不需要 API 密钥。

1. 运行 `python stage2_tools_tickets/01_create_database.py`，读 [建库](01_database.md)。
2. 运行 `python stage2_tools_tickets/02_ticket_states.py`，读 [状态流转](02_states.md)。
3. 运行 `python stage2_tools_tickets/03_tool_functions.py`，读 [四个工具](03_tools.md)。这一步会重建数据库。
4. 运行 `python stage2_tools_tickets/04_function_calling.py`，读 [function calling](04_function_calling.md)。没有密钥时只打印说明书。
5. 运行 `python stage2_tools_tickets/05_fill_slots.py`，读 [追问补槽位](05_slots.md)。这一步也会重建数据库。
6. 运行 `python stage2_tools_tickets/06_cli_with_tools.py`，读 [命令行客服](06_cli.md)。按屏幕上的句子试一轮，再输入 `退出`。
7. 运行 `python stage2_tools_tickets/07_offline_demo.py`，读 [离线演示](07_offline.md)。最后一行应是「离线演示通过」。
8. 读 [阶段小结](stage_summary.md)。名词忘了查 [名词表](glossary.md)。

示例 4 有密钥时会调用模型，只演示一轮工具。示例 6 有密钥时，模型负责把已经查到的结果说出来，工具仍由程序执行。
