# 阶段 5：向量检索（FAISS）与长期记忆

阶段 4 用二字词的 TF-IDF 在店铺说明里找段落。用字一样才能对上，「退钱」和「退款」对不上。阶段 4 也说过：DeepSeek 这一课的接口没有 embeddings，向量和 FAISS 留到这一阶段。

这一阶段做两件事。一是把文字变成一串数，用 FAISS 按方向找最接近的几段，知识库仍是阶段 4 的 `knowledge/` 和切块。二是按顾客把可以长期留下的事实写成向量，存在磁盘上，下次再问时找回来。阶段 3 的 Redis 仍是短期对话，空闲大约 30 分钟就过期。

零基础的读法在 [docs/README.md](docs/README.md)。新语法在 [基础课](../00_python_basics/README.md) 第 53 到 57 课，导读第一次用到时会叫停。不在本目录里再讲一遍。

## 本阶段需要的基础课

- 👉 不懂 numpy 的形状和 float32？先看 [基础课 · numpy 数组](../00_python_basics/53_numpy_array.md)
- 👉 不懂没装库时改走备用？先看 [基础课 · 可选依赖](../00_python_basics/54_optional_import.md)
- 👉 不懂 hashlib？先看 [基础课 · hashlib](../00_python_basics/55_hashlib.md)
- 👉 不懂创建文件夹？先看 [基础课 · 创建文件夹](../00_python_basics/56_path_mkdir.md)
- 👉 不懂模块级缓存？先看 [基础课 · 模块级缓存](../00_python_basics/57_module_cache.md)

导读里每次用到时还会再写一次。完整清单在 [导读目录](docs/README.md)。

`sentence-transformers` 会带上很大的 torch，第一次还会下载中文模型 `BAAI/bge-small-zh-v1.5`。它可以不装。没装、模型下不来，或环境变量 `USE_FAKE_EMBEDDING=1` 时，脚本改用哈希二字词假向量。假向量能把 FAISS 的添加、搜索、存盘跑完，但不会把「退钱」和「退款」拉近。真模型才会。

没有密钥时可以运行：

```bash
USE_FAKE_EMBEDDING=1 python stage5_vector_memory/01_what_is_vector.py
USE_FAKE_EMBEDDING=1 python stage5_vector_memory/02_get_embeddings.py
python stage5_vector_memory/03_numpy_vectors.py
python stage5_vector_memory/04_faiss_basics.py
USE_FAKE_EMBEDDING=1 python stage5_vector_memory/05_compare_retrieval.py
USE_FAKE_EMBEDDING=1 python stage5_vector_memory/06_long_term_memory.py
USE_FAKE_EMBEDDING=1 python stage5_vector_memory/07_cli_with_vector.py
python stage5_vector_memory/08_offline_demo.py
```

示例 1、3 不读这个开关，本身就不会下载模型。示例 8 在文件开头自己打开假向量，不读密钥，不联网，最后一行是「离线演示通过」。示例 4 的四句短文本也只用假向量。示例 2、5、6、7 在没装模型时会自动改用假向量；想跳过任何下载尝试，就加上 `USE_FAKE_EMBEDDING=1`。

示例 7 没有密钥时，政策题复述资料，订单和工单仍走阶段 2，写入 `stage2_tools_tickets/data/shop.db`。长期记忆写在 `stage5_vector_memory/data/memory/`。这些生成文件已在 `.gitignore` 里，不要提交。

退款仍然只会写成工单，不会打款。不要把真实顾客的手机号、卡号或对话写进这些练习。规则会把练习用的号码换成「已省略」，但练习数据本身也不要提交。

## 文件一览

| 文件 | 你要它做什么 | 教程 |
| --- | --- | --- |
| `embedder.py` | 真模型或假向量，二选一，只加载一次 | [第 2 课](docs/02_embedder.md) |
| `vectors.py` | 收成 float32，并按行把长度变成 1 | [第 3 课](docs/03_numpy.md) |
| `01_what_is_vector.py` | 看见「一串数」，并和二字词对比「退钱 / 退款」 | [第 1 课](docs/01_vector.md) |
| `02_get_embeddings.py` | 打印这次用的是哪一种向量、形状和类型 | [第 2 课](docs/02_embedder.md) |
| `03_numpy_vectors.py` | 形状、float64 和 float32、归一化 | [第 3 课](docs/03_numpy.md) |
| `index_store.py` | IndexFlatIP、编号、`index.faiss` 和 `meta.json` | [第 4 课](docs/04_faiss.md) |
| `04_faiss_basics.py` | 四句短文本的 add、search、存盘 | [第 4 课](docs/04_faiss.md) |
| `knowledge_index.py` | 用阶段 4 的切块建成向量索引 | [第 5 课](docs/05_compare.md) |
| `05_compare_retrieval.py` | 同一问，二字词和向量各查一次 | [第 5 课](docs/05_compare.md) |
| `remember.py` | 哪些句子值得记，号码先抹掉 | [第 6 课](docs/06_memory.md) |
| `memory_store.py` | 一位顾客一个文件夹 | [第 6 课](docs/06_memory.md) |
| `06_long_term_memory.py` | 写入、换一个对象再召回 | [第 6 课](docs/06_memory.md) |
| `ask.py` | 政策、记忆、复述放在同一次回答里 | [第 7 课](docs/07_cli.md) |
| `07_cli_with_vector.py` | 可以对话的客服 | [第 7 课](docs/07_cli.md) |
| `08_offline_demo.py` | 假向量、假复述、断言工单和隐私 | [第 8 课](docs/08_offline.md) |

阶段关系在 [docs/stage_summary.md](docs/stage_summary.md)。客服用词在 [docs/glossary.md](docs/glossary.md)。
