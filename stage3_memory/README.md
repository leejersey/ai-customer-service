# 阶段 3：工作记忆和短期记忆

阶段 2 把工单写进了 SQLite。关掉终端再打开，工单还在，上一句闲聊和「正在等订单号」不在。这一阶段把这两件事分开：手头办到哪了，叫工作记忆；最近这一段会话要在进程外面多留一会儿，叫短期记忆，放在 Redis 里。

零基础的读法在 [docs/README.md](docs/README.md)。新语法在 [基础课](../00_python_basics/README.md) 第 39 到 45 课，导读第一次用到时会叫停。不在本目录里再讲一遍。

没有密钥、也没有 Redis 时可以运行：

```bash
python stage3_memory/01_working_memory.py
python stage3_memory/02_truncate.py
python stage3_memory/03_summarize.py
python stage3_memory/04_redis_basics.py
python stage3_memory/05_session_store.py
python stage3_memory/06_cli_with_memory.py
python stage3_memory/07_offline_demo.py
```

示例 1 和 2 不联网。示例 3 没有密钥时只用假摘要。示例 4 和 5 会先试本机 Redis，连不上就改用 fakeredis，并在屏幕上写明原因。示例 6 是可以对话的客服。没有 Redis 时它也能聊，但退出程序后会话会消失。示例 7 不读密钥、不连接本机 6379，最后一行是「离线演示通过」。

配好阶段 0 的 `.env` 之后，示例 3 会再请模型写一段摘要，示例 6 会让模型把工具结果说成客服的话。工具仍然在你的电脑上执行。

## 启动 Redis

短期记忆要在「退出后再启动」时还在，需要一台真正的 Redis。Docker 一行：

```bash
docker run --name stage3-redis -p 6379:6379 -d redis:7
```

名字已经存在时，改成 `docker start stage3-redis`。不用时 `docker stop stage3-redis`。

macOS 也可以：`brew install redis`，然后 `brew services start redis`。

Windows 建议用 Docker Desktop，执行上面同一条命令。或者在 WSL 里执行 `sudo apt update && sudo apt install -y redis-server`，再 `sudo service redis-server start`。

默认地址是 `redis://localhost:6379/0`。要改地址或过期秒数，写在项目根目录的 `.env`，名字见 `.env.example` 里的 `REDIS_URL` 和 `STAGE3_SESSION_TTL_SECONDS`。地址里若带密码，程序不会把密码打印出来。

这一阶段新的 pip 包是 `redis` 和 `fakeredis`，已经写在根目录的 `requirements.txt`。在已经激活的虚拟环境里执行 `pip install -r requirements.txt`。

退款仍然只会写成工单，不会打款。不要把真实顾客的对话写进这些练习。

阶段 4 在回答政策之前先查店铺自己的说明，从 [stage4_rag/README.md](../stage4_rag/README.md) 继续。

## 文件一览

| 文件 | 你要它做什么 | 教程 |
| --- | --- | --- |
| `working.py` | 工作记忆这张小表 | [第 1 课](docs/01_working_memory.md) |
| `01_working_memory.py` | 对比对话历史和小表 | [第 1 课](docs/01_working_memory.md) |
| `window.py` | 按轮数、按字符数留下最近一段 | [第 2 课](docs/02_truncate.md) |
| `02_truncate.py` | 打印切短前后的 messages | [第 2 课](docs/02_truncate.md) |
| `summary.py` | 旧消息换成摘要；没有密钥时用假摘要 | [第 3 课](docs/03_summarize.md) |
| `03_summarize.py` | 跑一次压缩 | [第 3 课](docs/03_summarize.md) |
| `backend.py` | 连接 Redis，失败则改用替身 | [第 4 课](docs/04_redis.md) |
| `04_redis_basics.py` | SET、EXPIRE、LIST、HASH | [第 4 课](docs/04_redis.md) |
| `store.py` | 按 session_id 保存消息、摘要、槽位 | [第 5 课](docs/05_session_store.md) |
| `05_session_store.py` | 写入后再用另一个对象读回 | [第 5 课](docs/05_session_store.md) |
| `bridge.py` | 把阶段 2 的一轮写进工作记忆 | [第 6 课](docs/06_cli.md) |
| `speak.py` | 有密钥时，把工具结果说成客服的话 | [第 6 课](docs/06_cli.md) |
| `session_flow.py` | 一轮结束时保存，并在过长时摘要 | [第 6 课](docs/06_cli.md) |
| `06_cli_with_memory.py` | 带会话编号的命令行客服 | [第 6 课](docs/06_cli.md) |
| `07_offline_demo.py` | 断言窗口、摘要、续期和沿用订单号 | [第 7 课](docs/07_offline.md) |

阶段关系在 [docs/stage_summary.md](docs/stage_summary.md)。客服用词在 [docs/glossary.md](docs/glossary.md)。
