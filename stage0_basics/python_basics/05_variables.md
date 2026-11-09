# 变量：给一个值起名字

`01_hello_llm.py` 里第一次出现赋值是：

```python
TEMPERATURE = 0.7
```

等号在这里不是「数学上相等吗」，而是「把右边的值放进左边这个名字」。

## 先用一句人话

变量是贴了标签的盒子。标签是名字，盒子里是现在的值。你可以打开盒子换一件东西，标签可以不换。

## 打个比方

柜台抽屉上贴着「温度」。抽屉里现在放着纸条 `0.7`。后面的代码说「用温度」时，就是打开这个抽屉，而不是把「温度」两个字送给模型。

全大写的名字是我们的习惯：这个值设好后，这份脚本里不打算再改它。Python 并不禁止你改。大写只是给人看的约定，叫常量风格。真正防改要另写代码，阶段 0 不这么做。

## 自己动手

```python
shop = "星河数码"
print(shop)
shop = "另一家店"
print(shop)
```

预期：

```text
星河数码
另一家店
```

第二次赋值把盒子里的东西换了。第一张纸条不会留下来，除非你把它复制到了别的名字里。

名字可以指向另一个名字当前的值：

```python
temperature = 0.7
today = temperature
print(today)
```

预期：

```text
0.7
```

## 名字的规矩

可以用英文字母、数字、下划线。不能用空格。不要用中文当变量名，本仓库约定名字用英文。不要用数字开头。

大小写是不同的名字：`shop` 和 `Shop` 是两个盒子。

我们的脚本里，`TEMPERATURE` 和后面调用时写的 `temperature=TEMPERATURE` 不是同一个词的笔误。左边小写的 `temperature` 是函数规定的参数名；右边大写的 `TEMPERATURE` 是我们自己的盒子。关键字参数课会再讲这个等号。

## 常见错误

用之前没有赋值：

```python
print(shop)
```

```text
NameError: name 'shop' is not defined
```

盒子还没贴标签，Python 找不到这个名字。

名字里加了空格：

```python
my shop = "星河"
```

```text
SyntaxError: invalid syntax
```

应写成 `my_shop`。

把比较写成一个等号。比较「是不是相等」要用两个等号，`if` 课再练。一个等号永远是放进盒子。

## 练习

1. 让名字 `model` 先是 `deepseek-chat`，打印它，再改成 `deepseek-flash`，再打印。写出代码和两次输出。
2. 为什么 `print("TEMPERATURE")` 不会显示 `0.7`？
3. 下面哪一行是在改盒子里的值？`MAX_TOKENS = 256` 还是 `print(MAX_TOKENS)`？

## 答案

1. 代码是 `model = "deepseek-chat"`、`print(model)`、`model = "deepseek-flash"`、`print(model)`。输出两行：`deepseek-chat` 然后 `deepseek-flash`。
2. 引号里的是文字本身，四个字母 T、E、M…… Python 不会去打开名叫 `TEMPERATURE` 的盒子。
3. `MAX_TOKENS = 256` 是赋值。`print` 只查看，不改。
