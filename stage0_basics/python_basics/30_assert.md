# assert：认为必须成立，否则立刻停下

测试是在说：这几条我不打算靠眼睛看。条件不成立，程序自己喊停，并告诉你哪一句失败了。

`assert 条件` 条件为真就什么都不发生。为假就抛出 `AssertionError`，后面的代码不跑。

## 打个比方

出厂前的检查员。订单号必须是 `10086` 这一关过不了，就不要继续装进客服里给顾客用。它不是给顾客看的回复。

## 自己动手

```python
assert 1 + 1 == 2
print("通过了")
```

预期：

```text
通过了
```

```python
assert 1 == 2, "一不该等于二"
```

```text
AssertionError: 一不该等于二
```

逗号后面的字符串会写进错误里。阶段 1 的测试集检查用了这种写法，例如未知意图时带上那个意图的名字。

`python stage1_intent/test_rules.py` 成功时最后一行是 `规则和解析测试通过`。任何一条 `assert` 失败，都看不到这句，终端停在 `AssertionError`。

## pytest 是什么

pytest 是第三方工具，用 pip 安装，名字是 `pytest`。它会寻找名叫 `test_` 开头的函数并执行。我们的 `test_rules.py` 里的函数已经按这个名字写了，所以装了 pytest 之后可以运行：

```bash
pytest stage1_intent/test_rules.py
```

没安装会是：

```text
pytest: command not found
```

或者 `ModuleNotFoundError`。阶段 1 不把 pytest 写进 `requirements.txt`。直接 `python stage1_intent/test_rules.py` 就够，因为文件末尾的 `if __name__` 会把这些函数调用一遍。两种跑法测的是同一批断言。

## 常见错误

写成 `assert(条件, "说明")`。这是在 assert 一个括号里的元组。非空元组永远为真，于是检查永远通过，说明也变成了元组的第二项，不会在失败时出现。要写成 `assert 条件, "说明"`，逗号在括号外面。

用 `assert` 检查用户输入或密钥。有人运行 Python 时加上 `-O`，断言会被拿掉。密钥这种必须存在的事，用 `if` 加 `raise SystemExit`，阶段 0 就是这么做的。`assert` 留给「开发时这批例子必须怎样」。

## 练习

1. `assert classify` 的结果意图是 `"转人工"`，失败时希望看到句子 `应该转人工`。写出这一行。假设 `result` 已经是字典。
2. 为什么没装 pytest 仍然可以测规则？
3. 顾客输入为空时，该用 `assert` 还是 `if`？

## 答案

1. `assert result["intent"] == "转人工", "应该转人工"`。
2. `test_rules.py` 在 `if __name__ == "__main__"` 里自己调用了每个测试函数。`python 文件.py` 就会跑到那些 `assert`。
3. 用 `if`。空输入是运行时的正常情况，要提示再输入，不是开发错误。断言被优化关掉时，空输入检查会消失。
