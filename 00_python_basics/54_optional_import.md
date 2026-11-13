# 可选依赖：没装上就走另一条路

[try / except](16_try_except.md) 接得住运行中的失败。[导入](08_import.md) 说过，第三方库没装时，`import` 会失败。[虚拟环境](09_venv_pip.md) 讲的是把库装进哪一个 Python。这一课是第三种情况：这个库可以没有，程序改走备用方案，而不是退出。

阶段 5 用在 [嵌入](../stage5_vector_memory/docs/02_embedder.md)。`sentence-transformers` 很大，可以不装。没装、模型下不来，或者设置了 `USE_FAKE_EMBEDDING=1`，就改用假向量。

## 先用一句人话

把 `import` 放进 `try`。失败如果是「没有这个库」，就走 `except ImportError`，用你自己写的备用代码继续。

## 打个比方

柜台上最好有一台精密秤。秤还没到货时，你仍可以用弹簧秤把今天的练习做完。你得事先写好「秤不在就换弹簧秤」，而不是一摸到空位子就把整个店关了。

## 自己动手

下面这个名字故意不存在，所以谁运行结果都一样：

```python
try:
    import not_a_real_package_stage5
    print("装了")
except ImportError:
    print("没装，走备用方案")
print("程序还活着")
```

预期：

```text
没装，走备用方案
程序还活着
```

Python 3 在「根本没有这个包」时抛出的是 `ModuleNotFoundError`。它是 `ImportError` 的一种，所以 `except ImportError` 接得住。

`from 某个包 import 没有的名字` 也是 `ImportError`，但不是 `ModuleNotFoundError`。写 `except ImportError` 两种都接。只写 `except ModuleNotFoundError` 时，第二种仍会摔出去。

阶段 5 的 `embedder.py` 就是这样包住 `sentence-transformers` 的。接住之后改用哈希二字词，并留下一行原因，脚本再打印出来。空的 `except:` 会把失败吞掉，你不知道为什么变成了假向量。至少要留下原因。

## 常见错误

`except ImportError` 写在 `import` 已经失败、程序已经停掉之后。`try` 必须包住那句 `import` 本身。

把所有失败都当成「没装库」。模型下载失败往往是别的异常，不是 `ImportError`。阶段 5 在导入成功之后，再用一个更宽的 `except Exception` 接住加载失败，然后才改用假向量。两种失败要分开写，原因才说得清。

备用方案假装和真模型一样聪明。假向量对得上相同的字，对不上「退钱」和「退款」。备用方案要在屏幕上说清楚自己少了什么。

## 练习

1. 没装某个库时，`except ImportError` 为什么也能接住 `ModuleNotFoundError`？
2. 为什么不能写空的 `except:`，然后悄悄继续？
3. 阶段 5 在库已经装上、但模型文件下不来时，还会不会进 `except ImportError`？

## 答案

1. `ModuleNotFoundError` 是 `ImportError` 的一种。接住上级，这种失败也在里面。
2. 你连「失败过」都不知道，后面的结果会像没发生过一样。要打印原因，或改走一条说得清的备用路。
3. 不会。那时候包已经导入了。加载模型的失败要另外接。阶段 5 接住之后同样改用假向量，原因字符串和「没装库」不是同一句。

下一课把「同一个词每次都变成同一个整数」交给 hashlib：[hashlib](55_hashlib.md)。
