# 默认参数：这个名字没出现时用哪一个值

函数课里的参数，调用时都要传。有的参数大多数时候是同一个值，就可以在定义时写上默认值。调用的人少传一个，这个名字仍然有值。

阶段 2 用在 [工具函数](../stage2_tools_tickets/docs/03_tools.md) 的 `create_ticket`：不说顾客是谁，就是「演示用户」；不说订单号，就是空字符串。

## 先用一句人话

默认值写在定义那一行的等号右边。调用时这个参数被省略，就用默认值。调用时写了，哪怕写的是空字符串，用的也是你写的那个，不是默认值。

## 打个比方

茶默认不加糖。你说「一杯茶」，店员按 0 份糖做。你说「一杯茶，糖不要」，你已经对糖这件事作了回答，店员不会再偷偷改成默认。空字符串就是「我传了，内容是空的」。

## 自己动手

```python
def cup(drink, sugar=0):
    return f"{drink}，糖{sugar}份"

print(cup("茶"))
print(cup("茶", 2))
print(cup("茶", sugar=1))
```

预期：

```text
茶，糖0份
茶，糖2份
茶，糖1份
```

没有默认值的参数必须放在有默认值的前面。反过来写，定义的时候就会失败：

```text
SyntaxError: non-default argument follows default argument
```

`cup(drink, sugar=0)` 合法。`cup(sugar=0, drink)` 不合法。

空字符串不会触发默认值：

```python
def name_of(user="演示用户"):
    text = user.strip()
    if text == "":
        text = "演示用户"
    return text

print(name_of())
print(name_of("  "))
print(name_of("甲"))
```

预期：

```text
演示用户
演示用户
甲
```

第一行没传 `user`，用的是默认值。第二行传了几个空格，默认值不生效，要靠函数里面再判断。阶段 2 的 `create_ticket` 就是这么做的：模型可能把 `user_name` 传成空字符串。

## 不要用可变对象当默认值

默认值在函数定义时就算好，以后每次调用共用那一个对象。列表是可变的：

```python
def add_item(item, box=[]):
    box.append(item)
    return box

print(add_item("茶"))
print(add_item("糖"))
```

预期不是两份各自只有一个东西的列表，而是：

```text
['茶']
['茶', '糖']
```

第二次调用看见的是第一次放进去的茶。默认的那个列表只有一个，两次调用是同一个盒子。

要每次一个新列表，默认值用 `None`，进函数再创建：

```python
def add_item(item, box=None):
    if box is None:
        box = []
    box.append(item)
    return box

print(add_item("茶"))
print(add_item("糖"))
```

预期：

```text
['茶']
['糖']
```

`None` 表示「没给盒子」。字符串、数字当默认值不会出现这个问题，因为你不会去改那个字符串的内部。阶段 2 的默认值是字符串。

## 常见错误

调用时位置写错。`create_ticket("退款", "不想要了", "10086")` 会把 `"10086"` 当成 `user_name`，因为第三个参数是顾客名，订单号是第四个。阶段 2 调用时都写 `ticket_type=`、`order_id=` 这种名字。名字对上了，顺序可以换。这和 [关键字参数](21_objects.md) 是同一件事。

## 练习

1. `cup("茶")` 里 `sugar` 是多少？是谁决定的？
2. 为什么 `name_of("  ")` 不能单靠默认参数变成「演示用户」？
3. 默认参数写成 `box=[]` 时，两次调用为什么会互相看见？

## 答案

1. 是 0。定义 `sugar=0` 时写的。这次调用没有再传糖。
2. 调用已经传了 `user`，默认值被盖住。空格去掉后是空字符串，要在函数里面再写成「演示用户」。
3. 默认的列表在定义时只创建一次。两次调用的 `box` 是同一个列表，`append` 都加在它身上。
