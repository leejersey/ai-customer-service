# sorted：按某一格排序，以及 lambda

[列表](13_lists_dicts.md) 自己有顺序，那是你放进去的顺序。阶段 4 要按分数从高到低排，分数写在字典或对象的某一格里，不是列表本身的顺序。

阶段 4 用在 [检索](../stage4_rag/docs/03_retrieve.md) 的 `sorted(hits, key=lambda hit: hit.score, reverse=True)`。文件名排序也用了 `key`，只是那一格是文件名。

## 先用一句人话

`sorted` 交出一份新列表，原来的那份不动。`key` 告诉它：比较的时候看哪一格。`lambda` 是一个不写名字的小函数，专门用来指出那一格。`reverse=True` 是从大到小。

## 打个比方

三张收据摊在桌上。你按金额从高到低另排一列，原桌面上的左右位置还在。`key` 就是你用来比大小的那一栏金额，不是收据的整张纸。

## 自己动手

```python
rows = [
    {"source": "发票", "score": 0.2},
    {"source": "保修", "score": 0.8},
    {"source": "运费", "score": 0.5},
]
ranked = sorted(rows, key=lambda row: row["score"], reverse=True)
for row in ranked:
    print(row["source"], row["score"])
print(rows[0]["source"])
```

预期：

```text
保修 0.8
运费 0.5
发票 0.2
发票
```

最后一行仍是 `发票`。`sorted` 没有改原来的 `rows`。

`lambda row: row["score"]` 等于这样一个函数，只是没有名字：

```python
def score_of(row):
    return row["score"]
```

`key=score_of` 和 `key=lambda row: row["score"]` 是同一件事。一行能写完、也不需要在别的地方调用时，阶段 4 用 `lambda`。

不要写成 `key=row["score"]`。那样会立刻去取一个还不存在的 `row`，而不是「等一下对每一行再取」。

`reverse=True` 不能漏。漏了就是从小到大，最低分会排到检索结果的第一名。

## 常见错误

`lambda` 后面用了语句而不是一个值，例如在里面写 `print`。`lambda` 只能放一个表达式。要多行，就写 `def`。

写成 `rows = rows.sort(...)`。列表的 `sort` 会改原列表，并且交回 `None`。你把 `rows` 换成了 `None`。阶段 4 用 `sorted`，原列表还在，新顺序在另一份里。

`key` 忘了写，直接 `sorted` 一列字典。字典之间不能比较，你会得到 `TypeError`。必须告诉它看 `score`。

## 练习

1. `sorted` 会不会把原来的列表改掉？
2. `reverse=True` 时，分数 `0.2` 和 `0.8` 谁在前面？
3. `lambda hit: hit.score` 里，`hit` 是什么？

## 答案

1. 不会。它交出一份新列表。
2. `0.8` 在前面。`reverse=True` 是从大到小。
3. 每一次拿起来的那一项。函数体用它去取 `.score`。名字叫 `hit` 还是 `row` 都可以，只要前后一致。

下一课把两排对齐，配成二字词：[zip](51_zip.md)。
