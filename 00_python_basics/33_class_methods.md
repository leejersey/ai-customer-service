# 自己写类：把数据和方法放在一起

[对象课](21_objects.md) 讲过怎么读 `Settings`，并且说先不要自己写新的类。阶段 2 要写了。类是模具，方法是这个模具做出来的对象会做的事。

阶段 2 用在 [状态机](../stage2_tools_tickets/docs/02_states.md) 的 `StatusMachine`，以及 [建库](../stage2_tools_tickets/docs/01_database.md) 里放路径的 `DatabaseLocation`。

## 先用一句人话

`class` 画出一种新对象。`__init__` 在做出一个具体对象时，把属于它的数据放进 `self`。后面的方法用 `self` 拿到这份数据。

## 打个比方

模具是「柜台」。`Counter()` 是摆出一台柜台。`self.value` 是这台柜台上的数，不是所有柜台共用的一个数。`add` 是贴在这台柜台上的操作说明：加上多少，改的是自己这一台。

## 自己动手

```python
class Counter:
    def __init__(self):
        self.value = 0

    def add(self, amount):
        self.value = self.value + amount
        return self.value

left = Counter()
right = Counter()
print(left.add(2))
print(left.add(3))
print(right.add(10))
print(left.value)
```

预期：

```text
2
5
10
5
```

`left` 和 `right` 是两台柜台。给左边加，右边的 0 不会变成 5。`right.add(10)` 之后，左边的 `value` 仍是 5。

方法定义时第一个参数写成 `self`。调用时不要自己传 `self`：`left.add(2)` 里，Python 把 `left` 放进 `self`，把 `2` 放进 `amount`。

再看一个只保存规则、不保存「现在到了哪一步」的类：

```python
class Gate:
    def __init__(self):
        self.allowed = {"待处理": "处理中"}

    def move(self, current, target):
        expected = self.allowed.get(current)
        if target != expected:
            raise ValueError("不允许")
        return target

gate = Gate()
print(gate.move("待处理", "处理中"))
```

预期：

```text
处理中
```

`self.allowed` 是规则。`current` 是调用时临时交进来的，类里面没有记住它。阶段 2 的状态机就是这样：规则在对象里，某一张工单现在的状态在数据库那一行里。

## 常见错误

调用时多写了 `self`：

```text
TypeError: Gate.move() takes 3 positional arguments but 4 were given
```

`gate.move(gate, "待处理", "处理中")` 会把 `gate` 又传一次。写成 `gate.move("待处理", "处理中")`。

忘记 `self.`：

```python
class Gate:
    def __init__(self):
        self.allowed = {"待处理": "处理中"}

    def move(self, current, target):
        print(allowed)
```

```text
NameError: name 'allowed' is not defined
```

方法里面的名字不会自动变成对象的属性。要写 `self.allowed`。

把方法写在类的外面，却又想用 `self`，或者缩进退回到了行首，这个函数就不是方法。复习 [缩进](10_indentation.md)。

## 练习

1. 上面的 `left` 再调用一次 `add(1)`，`left.value` 是多少？`right.value` 是多少？
2. `Gate` 里为什么不把 `current` 存进 `self.current`，也仍然能 `move`？
3. `gate.move("待处理", "已关闭")` 会发生什么？

## 答案

1. 左边是 6，右边仍是 10。两次 `add` 改的是不同对象里的 `value`。
2. `current` 和 `target` 是这一次调用的参数。规则在 `self.allowed` 里，足够判断这一次允不允许。
3. `target` 和字典里的 `"处理中"` 不相等，抛出 `ValueError: 不允许`。
