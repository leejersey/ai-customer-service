# datetime：把「现在」写成固定格式的文本

阶段 2 的订单和工单要记下创建、更新的时间。数据库那一列存的是字符串。`datetime` 负责拿出现在的时刻，并规定这串字长什么样。

阶段 2 用在 [建库](../stage2_tools_tickets/docs/01_database.md) 的 `now_text`。

## 先用一句人话

`datetime.now()` 是此刻。`strftime` 按你给的式样把它变成文本。式样里的 `%Y` 是四位年，`%m` 是两位月，`%d` 是两位日，`%H` 是 24 小时制的小时，`%M` 是分，`%S` 是秒。

## 打个比方

钟是一个对象，账本只收得下字。`strftime` 是一张橡皮章，把钟盖成 `2026-11-09 08:30:00` 这种固定宽度的字。月和日不足两位时补 0，后面按文本排序才不会把 2 月排到 11 月后面。

## 自己动手

```python
from datetime import datetime

now = datetime.now()
text = now.strftime("%Y-%m-%d %H:%M:%S")
print(text)
print(len("2026-11-09 08:30:00"))
```

第一行是你运行时的当地时间，所以和别人的屏幕不同。长度那一行应是：

```text
19
```

式样本身不出现在结果里。`%Y` 被换成数字，中间的 `-`、空格、`:` 原样留下。

把这种文本读回 `datetime`，用同一个式样：

```python
from datetime import datetime

text = "2026-11-09 08:30:00"
moment = datetime.strptime(text, "%Y-%m-%d %H:%M:%S")
print(moment.year, moment.month, moment.day)
```

预期：

```text
2026 11 9
```

阶段 2 的代码只写出、不读回。存进去的字以后要能被这个式样认出来，所以写入和阅读必须用同一套 `%Y-%m-%d %H:%M:%S`。

`datetime.now()` 用的是这台电脑的当地时间。练习时你看屏幕右下角的钟，应对得上这串字里的小时。

## 常见错误

式样写错，或者文本少了一截：

```text
ValueError: time data '2026-11-09' does not match format '%Y-%m-%d %H:%M:%S'
```

`strptime` 要求整串都符合式样。只有日期、没有时间，就不能用带 `%H:%M:%S` 的式样去读。

`%m` 和 `%M` 不是同一个。`%m` 是月，`%M` 是分。写反以后，分的位置会出现月份，或者直接解析失败。

忘记从 `datetime` 模块里拿出类：

```python
import datetime
text = datetime.now().strftime("%Y-%m-%d")
```

```text
AttributeError: module 'datetime' has no attribute 'now'
```

`import datetime` 拿到的是模块。类也叫 `datetime`，所以要写 `datetime.datetime.now()`。我们的代码用 `from datetime import datetime`，名字直接就是类。两种写法不要混在同一行里。

## 练习

1. `"%Y-%m-%d"` 盖出来的文本里有没有小时？
2. 为什么月份要补 0，账本按文本排序才可靠？
3. 阶段 2 为什么用 `now()` 的当地时间，而不是先换算成另一套时区再存？

## 答案

1. 没有。式样里没有 `%H`，结果就停在日期。
2. 不补 0 时，`"2"` 的文本会排在 `"11"` 后面，因为比较到第一个字符 `"2" > "1"`。补成 `"02"` 之后，`"02"` 在 `"11"` 前面。
3. 这是单机练习。存当地时间，你对照自己的钟就行。代码注释里写了这个原因。
