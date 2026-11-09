# try / except：预计会失败的步骤，不要把整个程序摔碎

网络、密钥、用户按 Ctrl+C，都不是你把加号写成减号那种错误。它们会在运行中途发生。`try` 把「可能会失败的步骤」圈起来。失败如果属于你写明的那一种，就走 `except` 那一块，而不是直接甩出一大段英文追溯然后死掉。

`01_hello_llm.py` 里：

```python
try:
    response = client.chat.completions.create(...)
except Exception as error:
    print_api_error(error)
    raise SystemExit(1)
```

## 先用一句人话

`try` 是在说：先试这些行。如果摔了你认得的那种跤，就不要把整个柜台砸了，改做 `except` 下面的补救。

## 打个比方

你把一只易碎的杯子递给顾客。`try` 是递的动作。杯子没碎，就当这段没发生过特殊的事，继续往下。杯子碎了，`except` 是你事先准备好的「道歉并换一条路」，而不是呆站着看一地碎片（那一地碎片就是没被接住的追溯）。

## 自己动手

```python
try:
    number = int("abc")
except ValueError:
    print("这不是整数")
print("程序还活着")
```

预期：

```text
这不是整数
程序还活着
```

`int("abc")` 本来会这样死掉：

```text
ValueError: invalid literal for int() with base 10: 'abc'
```

`except ValueError` 只接这一种。别的失败仍然会摔出去。

`except ValueError as error` 把失败本身放进名字 `error`，你可以 `print(error)` 看到原因，而不只是知道「失败了」。

我们写 `except Exception`，是接住一大类普通失败，包括网络库抛出来的那些。`Exception` 是很多错误的共同上级。写得这么宽，好处是客服不会因为一种没料到的接口错误而整段崩溃；坏处是你自己的笔误（比如变量名打错）也可能被接住，看起来像「接口坏了」。所以 `print_api_error` 对不是接口错误的情况会多打印一段追溯，让你还能看见是哪一行。

`KeyboardInterrupt`（Ctrl+C）不属于 `Exception` 这一支，普通的 `except Exception` 接不住它。脚本最外层才单独写了 `except KeyboardInterrupt`。

## raise 是主动摔一跤，或把跤再抛出去

`raise SystemExit(1)` 不是接口失败。它是我们决定：「说明已经打印完了，现在以失败代码结束程序。」退出码 1 表示没成功。终端里可以用 `echo $?`（Windows 是 `echo %ERRORLEVEL%` 或看 PowerShell 的 `$LASTEXITCODE`）看到它，阶段 0 不要求你每次检查。

如果 `except` 里既不打印也不 `raise`，失败就变成沉默。调用方还以为拿到了回复。所以要么补救出一条可用的回复，要么明确结束或回到循环问下一句。第 1 课选择结束。第 4 课选择回到 `input`。

## 常见错误

`except` 和 `try` 中间夹了一行不缩进的代码，或者 `except` 缩进到了 `try` 里面。对齐看[缩进课](10_indentation.md)。`except` 要和 `try` 对齐。

写成 `except ValueError` 却去接网络错误。网络错误不是 `ValueError`，还是会整段崩溃。接接口失败时，我们用更宽的 `Exception`，再在处理函数里分辨是哪一种。

空的 `except:` 什么都不写。失败被吞掉，你连「失败过」都不知道。不要这样写。

## 练习

1. 让 `int("12")` 成功时打印那个数字，让 `int("十二")` 失败时打印 `没听懂`，并且两种情况之后都打印 `结束`。
2. 为什么第 1 课在 `except` 里要 `raise SystemExit(1)`，而不是打印完就去读 `response`？
3. Ctrl+C 为什么常常不会被 `except Exception` 接住？

## 答案

1. `try:` 里面 `print(int("12"))` 或先对 `"十二"` 做一次给你看的失败路径。结构是：`try` 里做 `int`，`except ValueError` 里打印 `没听懂`，和 `try` 对齐的下一行打印 `结束`。成功路径的输出是 `12` 然后 `结束`。失败路径是 `没听懂` 然后 `结束`。
2. 失败时赋值 `response = ...` 没有完成，根本没有 `response` 这个值。继续读它会再出 `NameError`。这一课又没有别的回复可显示，所以结束。
3. `KeyboardInterrupt` 是用来打断程序的特殊信号，设计上不被普通的 `Exception` 处理块接住，否则你可能连 Ctrl+C 都停不下来。我们在最外层单独接它。
