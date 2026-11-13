# any 和 all：有一个就行，还是每一个都要

`for` 可以自己写「找到一个就停」。`any` 和 `all` 把这件事收成一个是或否。阶段 6 用它们看词表里有没有命中，以及裁判交回的 JSON 里两个字段是否都在。

阶段 6 用在 [词表](../stage6_compliance/docs/02_rules.md) 的 `has_word`，以及 [裁判](../stage6_compliance/docs/05_judge.md) 的字段检查。

## 先用一句人话

`any` 问：这里面有没有一个是真的。`all` 问：是不是每一个都是真的。它们接受一个列表，也接受「算到一个就停」的那一种写法。

## 打个比方

安检口的 `any` 是：包里只要有一件违禁品，整包停下。`all` 是：清单上的每一项都盖了章，才放行。有一项没盖，整张清单不算通过。

## 自己动手

```python
print(any([False, True, False]))
print(all([True, True]))
print(all([True, False]))
```

预期：

```text
True
True
False
```

词表是同一件事。不用先把「每一个词在不在」做成一张完整的表：

```python
words = ["垃圾客服", "谢谢"]
text = "你们这些垃圾客服"
print(any(word in text for word in words))
print(all(word in text for word in words))
```

预期：

```text
True
False
```

`word in text for word in words` 是逐个算。`any` 遇到第一个真就可以停。这和 [列表推导](31_list_comprehension.md) 长得像，但不必先存成列表。[生成器](22_generators.md) 讲过「一次给你一个」。

空的一列要分开记。没有任何一项时，`any` 是 `False`（没有一件违禁品）。`all` 是 `True`（没有一项不合格）。所以检查「字段都在」时，字段名单不能是空的，否则空名单也会被说成通过。

```python
print(any([]))
print(all([]))
```

预期：

```text
False
True
```

阶段 6 的 `has_word` 还多看了一眼 `word` 自己。空字符串 `"" in text` 永远是真，一个空词会让每一句都命中。所以写成 `word and word in text`。

## 常见错误

`any` 后面忘了写可迭代的东西，写成 `any(word in text, words)`。两个参数会 `TypeError`。要的是一个序列，或一段 `for`。

把 `all` 理解成「大部分都真」。差一个也是 `False`。裁判的 JSON 缺了 `reason`，`all` 就是 `False`，然后走拒绝，不能放行。

空名单上用 `all`，得到 `True`，于是把「没有要求」当成「全部满足」。名单要写死那两个字段名。

## 练习

1. `any(len(word) > 3 for word in ["退款", "保证100%"])` 的结果是什么？
2. 为什么空字符串不能放进敏感词列表？
3. `all(key in {"verdict": "通过"} for key in ("verdict", "reason"))` 为什么是 `False`？

## 答案

1. `True`。`"保证100%"` 的长度大于 3，有一个真就可以。
2. `"" in "任何句子"` 是 `True`。空词会命中所有输入。
3. 字典里没有 `reason`。`all` 要求每一个键都在。缺一个就失败。阶段 6 因此拒绝这份 JSON。

下一课给等级和动作各起一组固定的名字：[枚举](60_enum.md)。
