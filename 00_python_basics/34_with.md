# with：进入时打开，离开时一定关上

阶段 2 每次查数据库都要打开一个连接，用完必须关掉。人会忘记写在最后一行的 `close()`，尤其是中间出错、后面的行根本没执行的时候。`with` 保证离开这块区域时，收尾仍然发生。

阶段 2 用在 [建库](../stage2_tools_tickets/docs/01_database.md) 的 `ShopConnection`。

## 先用一句人话

`with` 管的是一件「用完要还」的东西。进入语句时自动做开头的动作，无论里面是正常走完还是中途出错，离开时都做收尾。

## 打个比方

你推开一扇门走进房间。`with` 的约定是：人出来了要关门，人在里面摔倒了，门也要关上。不能把「记得关门」寄托在你还走得动。

这种对象叫上下文管理器。它有两个特殊方法：`__enter__` 在进入时调用，`__exit__` 在离开时调用。名字前后的双下划线表示 Python 会在固定时机自己来叫，不是给你在业务代码里随便点的普通方法。

## 自己动手

先看一扇自己写的门：

```python
class Door:
    def __enter__(self):
        print("开门")
        return "房间里"

    def __exit__(self, exc_type, exc, tb):
        print("关门")
        return False

with Door() as room:
    print(room)
```

预期：

```text
开门
房间里
关门
```

`as room` 接到的是 `__enter__` 交回来的值，这里是字符串 `"房间里"`。`return False` 的意思是：如果里面出了错，我关上了门，但错误还要继续往外抛，我没有把错误吞掉。

出错时门仍然会关：

```python
class Door:
    def __enter__(self):
        print("开门")
        return "房间里"

    def __exit__(self, exc_type, exc, tb):
        print("关门，当时的错误类型是", exc_type)
        return False

try:
    with Door() as room:
        raise ValueError("杯子碎了")
except ValueError:
    print("杯子的事已经另外处理")
```

预期：

```text
开门
关门，当时的错误类型是 <class 'ValueError'>
杯子的事已经另外处理
```

先关门，异常才落到外面的 `except`。若 `__exit__` 写成 `return True`，异常会被吞掉，外面的 `except` 不会执行。阶段 2 的连接选择 `return False`：文件要关上，写错的 SQL 仍要让人看见。

`__exit__` 里如果收尾动作自己也可能失败，可以用 `finally`，让「关上」排在提交或回滚之后，并且两边出错都执行：

```python
def finish(ok):
    try:
        if ok:
            print("提交")
        else:
            print("回滚")
    finally:
        print("关闭")

finish(True)
finish(False)
```

预期：

```text
提交
关闭
回滚
关闭
```

`finally` 是「无论 try 里面怎样，离开前都做」。`with` 把这件事收成进入和离开，调用的人不用每次手写 `finally`。

文件是最常见的现成上下文管理器：

```python
with open("note.txt", "w", encoding="utf-8") as handle:
    handle.write("你好\n")

with open("note.txt", encoding="utf-8") as handle:
    print(handle.read())
```

预期：

```text
你好
```

离开 `with` 后文件已经关上。再用完请自己删掉练习产生的 `note.txt`。阶段 1 读文本用过 `Path.read_text`，那是读完即关的短写法。需要在关上之前写多次，或要规定编码，就用 `with open`。

## sqlite3 自带的 with 不关闭连接

`with sqlite3.connect(路径) as 连接` 会在成功时提交、失败时回滚，官方说明里写了它不 `close`。阶段 2 因此自己写了 `ShopConnection`：`__enter__` 里连接并设置按列名读取，`__exit__` 里提交或回滚，再在 `finally` 里 `close`。

## 常见错误

`__exit__` 少写参数。它固定要接收异常类型、异常对象、追踪信息，加上 `self` 一共四个。少了会在离开 `with` 时出现：

```text
TypeError: Door.__exit__() takes 1 positional argument but 4 were given
```

在 `with` 里面 `return`，收尾仍然会做。函数可以返回，门还是会关。这是我们在工具函数里直接 `return` 错误字典时，连接仍会被关掉的原因。

## 练习

1. `__enter__` 的返回值会交给谁？
2. `__exit__` 返回 `False` 和返回 `True`，对外面的 `except` 有什么差别？
3. 为什么阶段 2 不直接写 `with sqlite3.connect(...)`？

## 答案

1. 交给 `as` 后面的名字。`with Door() as room` 里，`room` 就是 `__enter__` 返回的那个值。
2. `False` 让异常继续抛出，外面的 `except` 还能接住。`True` 表示「我已经处理过了」，异常消失。
3. 那个 `with` 负责提交或回滚，不负责 `close`。练习脚本会反复打开，所以 `ShopConnection` 在离开时关掉连接。
