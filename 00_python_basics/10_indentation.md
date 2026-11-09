# 缩进：冒号下面的行属于谁

Python 用行首的空格表示「这几行是上面那一句的内部」。不是用大括号。`def main():` 后面缩进的行，都在 `main` 里面。`if` 后面缩进的行，只有条件成立才执行。

## 先用一句人话

冒号表示「下面开始一块」。一块里面的每一行，行首空格数要一样。这块结束的标志，是下一行退回原来的位置。

## 打个比方

大纲：

```text
今天的步骤：
    第一步
    第二步
明天再做的事
```

「明天」和「今天的步骤」对齐，所以它不属于「今天」。Python 就是在看这种对齐。

我们的文件用 4 个空格缩进一层。不要用 Tab 和空格混着来。

## 自己动手

先看对的：

```python
print("外层")
if True:
    print("内层")
print("又回到外层")
```

`True` 表示条件成立，`if` 课会讲。预期：

```text
外层
内层
又回到外层
```

把内层的缩进删掉：

```python
if True:
print("内层")
```

```text
IndentationError: expected an indented block after 'if' statement on line 1
```

冒号已经答应「下面有一块」，下一块却是空的，Python 拒绝运行。

同一块里空格数不一致：

```python
if True:
    print("四格")
   print("三格")
```

```text
IndentationError: unindent does not match any outer indentation level
```

## 和我们脚本的关系

`01_hello_llm.py` 里，`def main():` 下面直到 `print(f"服务端报告的模型：...")` 都多缩进一层，所以它们都在 `main` 里面。文件最后的 `if __name__ == "__main__":` 退回到行首，表示它不在 `main` 里面。它负责调用 `main`。

`try:` 下面再缩进一层。`except` 和 `try` 对齐，表示「试」结束了，开始「如果失败」。`except` 下面又缩进，那些行只有失败时才执行。

读代码时先看垂直对齐，再读文字。对齐告诉你谁包着谁。

## 常见错误

从网页复制代码，混进了 Tab。看起来对齐，Python 却说 `TabError: inconsistent use of tabs and spaces in indentation`。把那一块删掉，用编辑器重新打 4 个空格。

以为空格只是好看，运行前用格式化工具把缩进「整理」到错误的层级。整理之后如果 `except` 跑进了 `try` 里面，意思就变了。改完看一眼对齐。

## 练习

1. 下面「结束」会打印吗？

   ```python
   if False:
       print("里面")
   print("结束")
   ```

2. `IndentationError` 是逻辑算错了，还是文字结构不合法、程序根本没开始做后面的事？
3. 怎样靠眼睛判断 `if __name__` 那一段不在 `main` 函数里面？

## 答案

1. 会。`结束` 和 `if` 对齐，不在条件里面。`里面` 不会打印，因为条件是 `False`。
2. 结构不合法。`IndentationError` 属于语法错误这一类，Python 还没有开始执行后面的打印或网络请求。
3. 看行首。`def main` 和 `if __name__` 都顶在最左边，所以它们是同一层的两块，后者不在前者内部。
