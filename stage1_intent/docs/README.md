# 阶段 1 导读目录

先做完阶段 0 的 [逐行导读](../../stage0_basics/docs/README.md)。这一阶段不再重讲 `import` 和 `while`。新语法出现时，导读会写「👉 不懂……？先看基础课」，链到 [基础课](../../00_python_basics/README.md) 里的具体一课，不在本目录重讲。

## 本阶段需要的基础课

阶段 0 那 23 课默认你已经会，清单在 [阶段 0 导读](../../stage0_basics/docs/README.md#本阶段需要的基础课)。下面是这一阶段会停下来读、或会再点到的课。

- 👉 不懂函数怎样一次交回好几样？先看 [基础课 · 函数交回字典](../../00_python_basics/24_return_dict.md)
- 👉 不懂正则？先看 [基础课 · 正则](../../00_python_basics/25_regex.md)
- 👉 不懂跨文件夹导入？先看 [基础课 · 从另一个文件夹导入](../../00_python_basics/26_import_other_folder.md)
- 👉 不懂解析不一定合法的 JSON？先看 [基础课 · 解析 JSON](../../00_python_basics/27_json_parse.md)
- 👉 不懂把函数放进字典？先看 [基础课 · 函数放进字典](../../00_python_basics/28_functions_in_dict.md)
- 👉 不懂读文本文件？先看 [基础课 · 读文本文件](../../00_python_basics/29_read_text.md)
- 👉 不懂 assert？先看 [基础课 · assert](../../00_python_basics/30_assert.md)
- 👉 不懂列表推导？先看 [基础课 · 列表推导](../../00_python_basics/31_list_comprehension.md)
- 👉 不懂准确率？先看 [基础课 · 准确率](../../00_python_basics/32_accuracy.md)

正文里还会再点到这些已经学过的课：[列表和字典](../../00_python_basics/13_lists_dicts.md)（元组在这一课）、[for](../../00_python_basics/14_for.md)、[`if __name__`](../../00_python_basics/18_name_main.md)、[环境变量](../../00_python_basics/20_env.md)。

规则和评估不需要 API 密钥。

1. 运行 `python stage1_intent/01_rule_classifier.py`，读 [规则分类](01_rules.md)。
2. 运行 `python stage1_intent/02_llm_classifier.py`，读 [模型与 JSON](02_llm_json.md)。
3. 运行 `python stage1_intent/03_router.py`，读 [路由器](03_router.md)。
4. 运行 `python stage1_intent/test_rules.py`，再运行 `python stage1_intent/04_evaluate.py`，读 [评估](04_evaluate.md)。
5. 运行 `python stage1_intent/05_cli_with_intent.py`，读 [接回命令行客服](05_cli.md)。
6. 读 [阶段小结](stage_summary.md)。
7. 下一阶段是工具和工单：[阶段 2 导读](../../stage2_tools_tickets/docs/README.md)。
