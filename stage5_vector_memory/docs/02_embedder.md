# 顺着嵌入逐行读

## 本阶段需要的基础课

- 👉 不懂没装库时改走备用？先看 [基础课 · 可选依赖](../../00_python_basics/54_optional_import.md)
- 👉 不懂 hashlib 选格子？先看 [基础课 · hashlib](../../00_python_basics/55_hashlib.md)
- 👉 不懂为什么模型只加载一次？先看 [基础课 · 模块级缓存](../../00_python_basics/57_module_cache.md)
- 👉 不懂形状和 float32？先看 [基础课 · numpy 数组](../../00_python_basics/53_numpy_array.md)

先运行：

```bash
USE_FAKE_EMBEDDING=1 python stage5_vector_memory/02_get_embeddings.py
```

第一行原因应包含「USE_FAKE_EMBEDDING 已打开」。维度 `256`。三条句子的形状是 `(3, 256)`，类型 `float32`。第一句和自己的余弦是 `1.0000`。和「可以开纸质发票吗」大约是 `0.1140`，不是 0：两句都有一些二字词，哈希之后有的格子碰巧撞在一起。再嵌入一次，余弦仍是 `1.0000`，不会重新下载。

不设置这个环境变量、并且装了 `sentence-transformers`、模型也能加载时，原因会变成「已加载本地嵌入模型 BAAI/bge-small-zh-v1.5，维度 512」。

## 为什么不向 DeepSeek 要向量

`.env` 里的 `DEEPSEEK_BASE_URL` 仍是 `https://api.deepseek.com`。这一课用的接口只有对话补全，没有 embeddings。不要自己猜一个 `/embeddings` 路径。向量在你自己的电脑上算。

真模型是 `BAAI/bge-small-zh-v1.5`。它通过 `sentence-transformers` 加载。这个包装着 torch，下载体积大，所以写在依赖里，但允许不装。👉 没装时怎么接住 `ImportError`？先看 [基础课 · 可选依赖](../../00_python_basics/54_optional_import.md)。

三条路会落到假向量：

1. 环境变量 `USE_FAKE_EMBEDDING` 是 `1`、`true`、`yes` 或 `on`。
2. 导入 `sentence-transformers` 失败。
3. 包在，但模型加载失败（没网、缓存坏了）。

第 3 条不是 `ImportError`，`embedder.py` 的 `_ensure_backend` 用更宽的 `except Exception` 接住，并留下另一种原因。空的 `except` 不会用。

假向量的代价要说清楚：它和阶段 4 一样看二字词。「退款」和「退钱」的余弦是 `0.0000`。你得到的是「没有模型也能把后面的 FAISS 跑完」，不是「同义词突然会了」。

## 只加载一次

`_BACKEND` 和 `_MODEL` 放在模块顶上。第一次嵌入时赋值，并写了 `global`。👉 不懂为什么要 `global`？先看 [基础课 · 模块级缓存](../../00_python_basics/57_module_cache.md)。第二次再嵌入，`_BACKEND` 已经有值，直接返回。

示例 1 不调用 `embed_texts`，所以不会触发这次决定。它只调用 `hashed_bigram_matrix`，假向量函数本身不下载。

## 查询前缀

真模型检索时，问题前面加上「为这个句子生成表示以用于检索相关文章：」，文档不加。这是这个模型的用法，不是 DeepSeek 的参数。假向量不加。加了的话，前缀里的字会占满格子，正文的词被冲淡。`as_query=True` 只在后端是 `bge` 时生效。

## 常见坑

- 向 `https://api.deepseek.com` 请求向量。这一课没有那个接口。
- 装了库却忘了模型还要单独下载，把长时间的下载当成程序死了。不想下载就设 `USE_FAKE_EMBEDDING=1`。
- 假向量跑通了，就以为「退钱」已经能对上「退款」。看这一课最后打印的余弦，它是 0。
- 换了模型还用旧索引。假向量 256 维，bge 是 512 维。下一课的读取会拒绝这种混用。

## 练习

1. 三种情况里，哪几种会使用假向量？
2. 为什么第二次嵌入不再加载模型？
3. 查询前缀为什么不能加在假向量上？

## 答案

1. 要求假向量、库没装上、模型加载失败。三种都会，原因句子不同。
2. `_BACKEND` 已经记下了。模块级的名字还在，函数看到不是空的就返回。
3. 假向量按字占格子。前缀的字会占掉本来该留给正文的格子。

下一课把「形状、类型、长度变成 1」单独看一遍：[numpy](03_numpy.md)。
