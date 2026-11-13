# collections.Counter：替你数次数

[字典](13_lists_dicts.md) 可以自己写「有这个键就加 1，没有就设成 1」。阶段 4 要对很多二字词做这件事，标准库里有一个专门的计数器。

阶段 4 用在 [检索](../stage4_rag/docs/03_retrieve.md) 的 `term_counts`。那里每个二字词出现几次，就是词频。

这不是 [类和方法](33_class_methods.md) 里那个自己写的 `class Counter`。那个例子只为了讲 `self`。这一课的 `Counter` 来自 `collections`，要先导入。

## 先用一句人话

`Counter` 是一本数次数的字典。你把一串词交给它，它告诉你每个词有几次。问一个从没出现的词，得到 `0`，不会 `KeyError`。

## 打个比方

柜台上的划正字。每见到一张写着「退货」的小票，就在「退货」下面加一笔。没人交过「发票」，你问发票有几笔，答案是 0，不是把账本合上。

## 自己动手

```python
from collections import Counter

counts = Counter(["退货", "运费", "退货"])
print(counts["退货"])
print(counts["发票"])
print(counts.most_common(2))
```

预期：

```text
2
0
[('退货', 2), ('运费', 1)]
```

`most_common(2)` 是次数最多的两项，每一项是 `(词, 次数)`。只要前 1 项，就写 `most_common(1)`。

它也能直接数一条字符串里的字。阶段 4 不这么用，二字词是先配好再交给 `Counter` 的：

```python
print(Counter(["退货", "退货"])["退货"])
```

预期是 `2`。

`for term in counts` 走的是词，不是次数。次数用 `counts[term]` 取。

## 常见错误

没导入就写 `Counter`：

```text
NameError: name 'Counter' is not defined
```

要写 `from collections import Counter`。

把它和普通字典一样，问一个没有的键时期待 `KeyError`。`Counter` 会给你 `0`。阶段 4 用这个差别：一段里没有的二字词，次数就是 0，循环不用先判断键在不在。

和自己写的类用了同一个英文名。导入之后，这个名字指向标准库的计数器。不要在同一个文件里再写一个 `class Counter`。

## 练习

1. `Counter(["a", "a", "b"])["a"]` 是多少？`["c"]` 是多少？
2. `most_common(1)` 的第一项里，第 0 个是词还是次数？
3. 它和第 33 课里的 `class Counter` 是同一个东西吗？

## 答案

1. `2` 和 `0`。`"c"` 没出现过，计数器给 0。
2. 第 0 个是词，第 1 个是次数。
3. 不是。第 33 课那个类是为了讲 `self` 随手起的名字。这一课必须从 `collections` 导入。

下一课看两个集合交在哪里：[集合运算](49_set_ops.md)。
