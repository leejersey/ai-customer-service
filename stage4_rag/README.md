# 阶段 4：RAG（检索增强生成）

阶段 3 把这一段会话留在 Redis 里。模型回答政策时，用的仍是它自己的记忆，天数可能和星河数码写的不一样。这一阶段先从 `knowledge/` 里找出相关的几段，再让模型只根据这几段说话。找不到就说「知识库里没有找到」。

零基础的读法在 [docs/README.md](docs/README.md)。新语法在 [基础课](../00_python_basics/README.md) 第 46 到 52 课，导读第一次用到时会叫停。不在本目录里再讲一遍。

## 本阶段需要的基础课

- 👉 不懂列出文件夹？先看 [基础课 · pathlib 列出文件](../00_python_basics/46_path_iterdir.md)
- 👉 不懂 split / join？先看 [基础课 · split 和 join](../00_python_basics/47_split_join.md)
- 👉 不懂 Counter？先看 [基础课 · Counter](../00_python_basics/48_counter.md)
- 👉 不懂集合的交和差？先看 [基础课 · 集合运算](../00_python_basics/49_set_ops.md)
- 👉 不懂 sorted 和 lambda？先看 [基础课 · sorted 和 lambda](../00_python_basics/50_sorted_key.md)
- 👉 不懂 zip？先看 [基础课 · zip](../00_python_basics/51_zip.md)
- 👉 不懂余弦相似度？先看 [基础课 · 余弦相似度](../00_python_basics/52_cosine.md)

导读里每次用到时还会再写一次，并带上这一课真正要看的那几条旧课。完整清单在 [导读目录](docs/README.md)。

没有密钥时可以运行：

```bash
python stage4_rag/01_load_documents.py
python stage4_rag/02_chunk_text.py
python stage4_rag/03_search_chunks.py
python stage4_rag/04_build_prompt.py
python stage4_rag/05_ask_with_rag.py
python stage4_rag/06_cli_with_rag.py
python stage4_rag/07_offline_demo.py
```

示例 1 到 4 不联网。示例 5 没有密钥时只打印检索和提示，不调用模型。示例 6 没有密钥时，政策题复述资料原文，订单和工单仍走阶段 2 的工具，并写入 `stage2_tools_tickets/data/shop.db`。示例 7 使用 `stage4_rag/data/offline_demo.db`，不读密钥，最后一行是「离线演示通过」。

配好阶段 0 的 `.env` 之后，示例 5 和示例 6 会在分数达到 0.15 时调用 DeepSeek。工具仍然在你的电脑上执行。检索也不请求向量接口：本课使用的 DeepSeek 接口只有对话补全，没有 embeddings。阶段 5 才用 FAISS。

这一阶段没有新的 pip 包。二字词、TF-IDF 和余弦都用 Python 标准库。生成的 `*.db` 已写在 `.gitignore` 里，不要提交。

退款仍然只会写成工单，不会打款。不要把真实顾客的对话写进这些练习。

## 文件一览

| 文件 | 你要它做什么 | 教程 |
| --- | --- | --- |
| `knowledge/` | 八份店铺说明：退换货、运费、积分、保修、支付、发票、常见问题、营业时间 | [第 1 课](docs/01_load.md) |
| `documents.py` | 读出文件名、标题和正文 | [第 1 课](docs/01_load.md) |
| `01_load_documents.py` | 打印八份说明的字数 | [第 1 课](docs/01_load.md) |
| `chunking.py` | 按标题分段，超长再按字数重叠切开 | [第 2 课](docs/02_chunk.md) |
| `02_chunk_text.py` | 用十个字看重叠，再看知识库里的长段 | [第 2 课](docs/02_chunk.md) |
| `retrieve.py` | 二字词 TF-IDF 和余弦，返回 top-k | [第 3 课](docs/03_retrieve.md) |
| `03_search_chunks.py` | 打印分数、对上的词和没出现过的词 | [第 3 课](docs/03_retrieve.md) |
| `prompting.py` | 带上来源标签；低于阈值不拼提示 | [第 4 课](docs/04_prompt.md) |
| `04_build_prompt.py` | 对比一问够分、一问不够分 | [第 4 课](docs/04_prompt.md) |
| `answering.py` | 够分才调用模型；否则复述或拒答 | [第 5 课](docs/05_ask.md) |
| `05_ask_with_rag.py` | 三问。没有密钥就跳过生成 | [第 5 课](docs/05_ask.md) |
| `routing.py` | 政策走检索，办理和查订单走阶段 2 | [第 6 课](docs/06_cli.md) |
| `06_cli_with_rag.py` | 可以对话的客服 | [第 6 课](docs/06_cli.md) |
| `07_offline_demo.py` | 假模型复述资料，并断言工单仍能写下 | [第 7 课](docs/07_offline.md) |

阶段关系在 [docs/stage_summary.md](docs/stage_summary.md)。客服用词在 [docs/glossary.md](docs/glossary.md)。
