# 函数：起了名字的一组步骤

`def main():` 定义一个函数。定义的时候，里面的步骤先不做。等到某一行写 `main()`，那些步骤才按顺序发生。

## 先用一句人话

函数是贴了名字的菜谱段落。`def` 是在抄录这段菜谱。名字后面加括号，才是按这段做一次。

## 打个比方

你把「冲一杯茶」写成一张卡片。写卡片不会把水烧开。你对别人说「冲一杯茶」这张卡片上的步骤，水才会烧开。说两次，就做两次。

## 定义、参数、返回值、调用

```python
def bowl(food):
    return "一碗" + food

print("还没调用")
print(bowl("面"))
print(bowl("饭"))
```

预期：

```text
还没调用
一碗面
一碗饭
```

- `def bowl(food):` 里的 `food` 是参数，一张空白标签。调用时才把具体的东西贴上去。
- `return` 把结果交还给调用的那一行。`print(bowl("面"))` 是在打印交回来的那份结果。
- 没有 `return` 的函数，交回来的是 `None`。[None 课](17_none.md) 专门讲它。`main` 没有 `return`，它靠 `print` 把东西写到屏幕上，而不是把一句回复交还给别人。

调用时参数按位置对上：

```python
def full_name(family, given):
    return family + given

print(full_name("星", "河"))
```

预期：

```text
星河
```

写反了就会变成 `河星`。这就是 `config.py` 要把三项配置放进一个 `Settings` 对象、而不是靠调用者记住顺序的原因。对象课再讲这个盒子怎么做。

我们的 `request_reply(client, model, messages)` 有三个参数。调用时必须按这个顺序给，除非用名字对上（关键字参数，在对象课里和 `temperature=` 一起讲）。

## `-> None` 是什么

```python
def main() -> None:
```

箭头后面是给人读的注记：这个函数不打算交还一个有用的值。Python 运行时不靠这行来检查对错。删掉 `-> None`，行为不变。留下它，是提醒读代码的人不要写 `answer = main()` 还指望 `answer` 里有模型的回复。回复已经在函数里面被 `print` 掉了。

## 自己动手时注意定义和调用的差别

把函数放进文件：

```python
def greet():
    print("你好")

print("文件开始")
greet()
print("文件结束")
```

预期：

```text
文件开始
你好
文件结束
```

如果删掉 `greet()` 那一行，只剩下「文件开始」和「文件结束」。函数被记住了，但没人使用。

`01_hello_llm.py` 最后有 `main()`，所以你运行文件时才会走到请求。这一句被包在 `if __name__ == "__main__":` 里，那一课说明为什么不把 `main()` 直接写在文件顶层的最外面。

## 常见错误

定义时多写了括号里的具体句子，调用时又忘了括号：

```python
def greet():
    print("你好")

greet
```

交互模式可能显示一串 `<function greet ...>`，文件里则什么都不打印。没有括号就是「把函数本身拿在手里」，不是「执行它」。

调用时参数个数不对：

```text
TypeError: bowl() missing 1 required positional argument: 'food'
```

或者：

```text
TypeError: bowl() takes 1 positional argument but 2 were given
```

数一数 `def` 那一行有几个参数，调用的括号里就要有几个值（带默认值的可以少给，阶段 0 先不展开默认值）。

在 `return` 后面还写了同级的 `print`。`return` 会立刻离开函数，它后面的同级代码不会执行。

## 练习

1. 写函数 `twice(text)`，返回文字重复两遍。`print(twice("哈"))` 的预期是什么？
2. 只定义 `def main():` 而不调用，运行文件时，`main` 里面的 `print` 会发生吗？
3. `reply, response = request_reply(...)` 为什么左边有两个名字？这要求函数的 `return` 写成什么样？

## 答案

1. 函数体是 `return text + text`。预期输出 `哈哈`。
2. 不会。定义只是登记步骤。
3. 函数要 `return` 两样东西，例如 `return reply, response`。左边的逗号是在同时接住这两样。这叫按位置拆开。两样东西的类型可以不同：一句回复的文字，和整份响应。
