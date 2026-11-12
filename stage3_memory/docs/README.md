# 阶段 3 导读目录

先做完阶段 2 的 [导读](../../stage2_tools_tickets/docs/README.md)。这一阶段不再重讲工单怎么插入。新语法出现时，导读会停下来，去 `00_python_basics/` 第 39 课往后。

## 本阶段需要的基础课

新的，等导读叫停再读，不要先通读：

- 👉 不懂切片？先看 [基础课 · 切片](../../00_python_basics/39_slice.md)
- 👉 不懂类型注解？先看 [基础课 · 类型注解](../../00_python_basics/40_type_annotations.md)
- 👉 不懂 dataclass？先看 [基础课 · dataclass](../../00_python_basics/41_dataclass.md)
- 👉 不懂把结构变成 JSON 再变回来？先看 [基础课 · JSON 来回](../../00_python_basics/42_json_roundtrip.md)
- 👉 不懂连接对象？先看 [基础课 · 连接对象](../../00_python_basics/43_connection.md)
- 👉 不懂 time？先看 [基础课 · time](../../00_python_basics/44_time.md)
- 👉 不懂环境变量的默认值？先看 [基础课 · 环境变量的默认值](../../00_python_basics/45_env_defaults.md)

还会用到、这一阶段第一次靠它们把会话跑起来的旧课：

- [13 列表和字典](../../00_python_basics/13_lists_dicts.md)（`sys.argv` 是列表，元组在这一课）
- [16 try / except](../../00_python_basics/16_try_except.md)
- [20 环境变量](../../00_python_basics/20_env.md)
- [23 JSON](../../00_python_basics/23_http_json.md)
- [26 从别的文件夹导入](../../00_python_basics/26_import_other_folder.md)
- [27 解析 JSON](../../00_python_basics/27_json_parse.md)
- [30 assert](../../00_python_basics/30_assert.md)
- [33 类和方法](../../00_python_basics/33_class_methods.md)
- [34 with](../../00_python_basics/34_with.md)

## 阅读顺序

示例 1、2 和离线演示不需要 API 密钥，也不需要 Redis。示例 3 没有密钥时走假摘要。示例 4、5、6 在 Redis 没启动时会说明并改用 fakeredis。

1. 运行 `python stage3_memory/01_working_memory.py`，读 [工作记忆](01_working_memory.md)。
2. 运行 `python stage3_memory/02_truncate.py`，读 [截断](02_truncate.md)。
3. 运行 `python stage3_memory/03_summarize.py`，读 [摘要](03_summarize.md)。
4. 运行 `python stage3_memory/04_redis_basics.py`，读 [Redis](04_redis.md)。想看到跨进程的键，先按 [阶段说明](../README.md) 启动 Redis，再运行一次。
5. 运行 `python stage3_memory/05_session_store.py`，读 [会话记忆](05_session_store.md)。
6. 运行 `python stage3_memory/06_cli_with_memory.py demo-1`，读 [命令行客服](06_cli.md)。按屏幕上的句子试一轮，输入 `退出`。用同一个 `demo-1` 再启动一次。
7. 运行 `python stage3_memory/07_offline_demo.py`，读 [离线演示](07_offline.md)。最后一行应是「离线演示通过」。
8. 读 [阶段小结](stage_summary.md)。名词忘了查 [名词表](glossary.md)。

示例 6 只有连上真正的 Redis 时，退出再启动才接得上同一段会话。fakeredis 的数据随进程结束。离线演示用两个客户端共用一台假服务器，在一个进程里把「重新连上」这件事断言住。
