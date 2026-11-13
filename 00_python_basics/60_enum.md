# 枚举：一组允许使用的名字

敏感词的等级只有低、中、高，动作只有放行、改写、转人工、拦截。用普通字符串也能写，但手误打成「放行吧」时，程序会把它当成一个新动作。枚举把允许的值先列出来。

阶段 6 用在 [风险等级](../stage6_compliance/docs/07_risk.md) 的 `RiskLevel` 和 `ReviewAction`。

## 先用一句人话

`Enum` 是一个类，里面每一行是一个成员。成员有名字，也有你赋给它的值。比较时用成员，写进日志时用 `.value` 里的中文。

## 打个比方

餐厅的小票不接受随便写的菜名。菜单上印了四道，点单只能是这四道。写了菜单上没有的字，后厨不把它当成「默认来一份店长推荐」，而是退回。审核也一样：不认识的动作不能默认放行。

## 自己动手

`enum` 是标准库，不用 pip。

```python
from enum import Enum

class RiskLevel(Enum):
    LOW = "低"
    MEDIUM = "中"
    HIGH = "高"

print(RiskLevel.HIGH)
print(RiskLevel.HIGH.value)
print(RiskLevel.HIGH == RiskLevel.HIGH)
print(RiskLevel.HIGH == "高")
```

预期：

```text
RiskLevel.HIGH
高
True
False
```

最后一行是 `False`。成员和它的值不是同一个对象。日志和 JSON 里要中文时，写 `.value`。从词表读回中文时，用值去找成员：

```python
def as_level(text):
    for item in RiskLevel:
        if item.value == text:
            return item
    return RiskLevel.HIGH

print(as_level("中"))
print(as_level("超级"))
```

预期：

```text
RiskLevel.MEDIUM
RiskLevel.HIGH
```

找不到时返回高，是阶段 6 的选择：写错的等级不能变成低。

## 常见错误

用 `RiskLevel.HIGH == "高"` 做判断，永远进不了那一支。要么比成员，要么比 `.value`。

自己写 `if text == "高" or text == "中" or text == "低"`，漏掉一个拼写。枚举把这四个（或三个）词放在一处，循环 `for item in RiskLevel` 就能看全。

把 `.name` 写进给顾客看的句子。`.name` 是 `HIGH` 这种英文标识，`.value` 才是「高」。

## 练习

1. `RiskLevel.LOW.value` 是什么？`RiskLevel.LOW.name` 是什么？
2. 为什么 `as_level("超级")` 返回高，而不是低？
3. 枚举和 [第 13 课](13_lists_dicts.md) 里的普通字符串列表有什么不同？

## 答案

1. `.value` 是 `"低"`。`.name` 是 `"LOW"`。
2. 「超级」不在三个成员的值里。审核把不认识的等级当成高，避免手误把风险放掉。
3. 列表只是一排字，写错一个程序不会提醒你「这不在菜单上」。枚举的成员是固定的那几个，比较和遍历都对着这几个。

下一课把每一轮审核追加进文件：[JSON Lines](61_json_lines.md)。
