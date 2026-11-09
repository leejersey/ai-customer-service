# 阶段 2：工具调用和工单

阶段 1 能把「我要退款」分出来，回复仍是一句「我先记下了」。这一阶段把查订单、退款、投诉、转人工接上 SQLite：该查的去查表，该留的插入工单。模型可以提出调用哪个函数；真正执行的是本地代码。

零基础的读法在 [docs/README.md](docs/README.md)。新语法在 [基础课](../00_python_basics/README.md) 第 33 到 38 课，导读第一次用到时会叫停。不在本目录里再讲一遍。

没有密钥时可以运行：

```bash
python stage2_tools_tickets/01_create_database.py
python stage2_tools_tickets/02_ticket_states.py
python stage2_tools_tickets/03_tool_functions.py
python stage2_tools_tickets/04_function_calling.py
python stage2_tools_tickets/05_fill_slots.py
python stage2_tools_tickets/06_cli_with_tools.py
python stage2_tools_tickets/07_offline_demo.py
```

示例 1、3、5 会重建 `stage2_tools_tickets/data/shop.db`，已有工单会被清空。示例 2 不碰数据库。示例 4 没有密钥时只打印工具说明书并跳过模型。示例 6 没有密钥时用规则和程序写的回复，工单仍会写入 `shop.db`。示例 7 使用另一个文件 `offline_demo.db`，最后一行是「离线演示通过」。

配好阶段 0 的 `.env` 之后，示例 4 会请模型决定调用哪个工具，示例 6 会让模型把工具结果说成客服的话。工具仍然在你的电脑上执行。

这一阶段没有新的 pip 包。数据库用的是 Python 自带的 `sqlite3`。生成的 `*.db` 已写在 `.gitignore` 里，不要提交。

退款只会写成工单，不会打款。不要把真实顾客的订单写进这些练习脚本。

## 文件一览

| 文件 | 你要它做什么 | 教程 |
| --- | --- | --- |
| `db.py` | 建表、放入示例订单、打开并关闭连接 | [第 1 课](docs/01_database.md) |
| `01_create_database.py` | 重建 `shop.db` 并打印四张订单 | [第 1 课](docs/01_database.md) |
| `states.py` | 工单状态只能按链往前走一步 | [第 2 课](docs/02_states.md) |
| `02_ticket_states.py` | 打印允许和拒绝的流转 | [第 2 课](docs/02_states.md) |
| `tools.py` | `query_order`、`create_ticket`、`update_ticket_status`、`get_ticket` | [第 3 课](docs/03_tools.md) |
| `03_tool_functions.py` | 不经过模型，把四个工具跑一遍 | [第 3 课](docs/03_tools.md) |
| `schema.py` | 交给模型的 `tools` 说明书 | [第 4 课](docs/04_function_calling.md) |
| `calling.py` | 解析 `tool_calls`，执行，追加 `role=tool` | [第 4 课](docs/04_function_calling.md) |
| `04_function_calling.py` | 单步演示模型决定、程序执行、再要最终回复 | [第 4 课](docs/04_function_calling.md) |
| `slots.py` | 缺了哪个槽位、追问哪一句 | [第 5 课](docs/05_slots.md) |
| `service.py` | 阶段 1 的意图选工具，并记住还没补上的订单号 | [第 5 课](docs/05_slots.md) |
| `05_fill_slots.py` | 「我要退款」两轮：先问，再写入 | [第 5 课](docs/05_slots.md) |
| `06_cli_with_tools.py` | 可以对话的客服，能创建和查询工单 | [第 6 课](docs/06_cli.md) |
| `07_offline_demo.py` | 假的模型响应，断言数据库和状态机 | [第 7 课](docs/07_offline.md) |

阶段关系在 [docs/stage_summary.md](docs/stage_summary.md)。客服用词在 [docs/glossary.md](docs/glossary.md)。
