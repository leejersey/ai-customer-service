# numpy 数组：一整排类型相同的数

[数字](06_numbers.md) 里的 `3.0` 是一个小数。[列表](13_lists_dicts.md) 可以把很多小数排在一起。阶段 5 要把一句话变成几百个小数，再交给 FAISS。列表能装，但格子的类型不统一，内存也不连在一起。numpy 的数组就是为这种「一整排数」准备的。

阶段 5 用在 [numpy 向量](../stage5_vector_memory/docs/03_numpy.md) 的 `shape`、`dtype` 和按行归一化。余弦为什么要除以长度，仍看 [余弦相似度](52_cosine.md)。

## 先用一句人话

`np.array` 做出一张表。`shape` 告诉你有几行几格。`dtype` 告诉你每一格是 64 位小数还是 32 位小数。归一化是把每一行的长度变成 1，方向留着。

## 打个比方

列表像一串用绳子拴住的珠子，珠子可以是数，也可以是字。数组像一块切好的格子冰，每一格必须是同一种数。FAISS 只接受这种冰块，而且要 32 位那一号，不要默认的 64 位。

## 自己动手

在已经安装 numpy 的环境里运行。安装见 [虚拟环境和 pip](09_venv_pip.md)，包名是 `numpy`。

```python
import numpy as np

row = np.array([3.0, 4.0])
print(row.shape)
print(row.dtype)
narrow = row.astype(np.float32)
print(narrow.dtype)
length = np.linalg.norm(narrow)
unit = narrow / length
print(unit)
print(float(np.linalg.norm(unit)))
```

预期：

```text
(2,)
float64
float32
[0.6 0.8]
1.0
```

`shape` 是 `(2,)`：一行，里面 2 格。逗号留着，是为了让人看出这是元组，不是一个带括号的数。

`dtype` 是 `float64`。你写的 `3.0` 是 Python 小数，numpy 默认用 64 位来装。`astype(np.float32)` 才换成 32 位。FAISS 的索引按 32 位存。

`3` 和 `4` 的长度是 `5`（3²+4² 再开平方）。除完是 `0.6` 和 `0.8`，长度变成 `1`。方向没变。两行都变成 1 之后，点积才是 [余弦](52_cosine.md)。

多行时形状是 `(行数, 每一行的格数)`：

```python
table = np.array([[1.0, 0.0], [0.0, 1.0]], dtype=np.float32)
print(table.shape)
```

预期是 `(2, 2)`。

## 常见错误

`np.array([1.0, 2.0])` 看起来对了，`dtype` 却是 `float64`。有的 FAISS 版本会帮你转成 `float32`，有的会报错，更老的会把同一块内存按更窄的格子来读。那样读，`[1.0, 2.0]` 会变成乱七八糟的数：

```python
wide = np.array([1.0, 2.0])
print(wide.view(np.float32))
```

会看到类似 `[0. 1.875 0. 2.]`。`view` 没有换算，只是换了一副眼镜。要换算用 `astype`。

忘了除以长度。点积会被「这一行数字特别大」带着走。阶段 5 的 `l2_normalize` 就是在做除法。全零的行没有方向，不能除以 0，要留着全零。

`import numpy` 失败，报 `ModuleNotFoundError`。说明当前这个 Python 里还没有 numpy。回到 [虚拟环境](09_venv_pip.md)，在激活后的环境里 `pip install numpy`。

## 练习

1. `np.array([1.0, 2.0, 3.0])` 的 `shape` 是什么？`dtype` 默认是什么？
2. 为什么写入 FAISS 之前要 `astype(np.float32)`？
3. `[3.0, 4.0]` 归一化之后，两个数大约是多少？长度变成多少？

## 答案

1. `shape` 是 `(3,)`。默认 `dtype` 是 `float64`。
2. 索引按 32 位小数存放。64 位要么被拒绝，要么占双倍内存，要么在不转换的实现里被读成别的数。
3. 大约 `0.6` 和 `0.8`。长度变成 `1`。

下一课看「库没装上时不要整段崩溃」：[可选依赖](54_optional_import.md)。
