# 终端：你在哪个文件夹，怎么走进另一个

我们的脚本要用终端运行。终端不是 Python，它是你跟电脑说话的文字窗口：你写一行命令，回车，电脑做一件事，再把结果写回来。

在代码导读里，这是动手之前的第一课。脚本本身没有 `cd` 这几个字母，但你不进对文件夹，后面的 `python ...` 都会找错文件。

## 先用一句人话

终端始终站在某一个文件夹里。这个文件夹叫「当前目录」。`pwd` 问它在哪，`ls` 问这里有什么，`cd` 走进另一个文件夹。

## 打个比方

终端像一个只认口令的文件柜管理员。他永远站在某一层抽屉前面。你说「这里有什么」，他只报这一层，不会把整栋楼都报出来。你说「走进 stage0_basics」，他才挪到那一层。

## 先确认你开的是终端

- macOS：打开「终端」。
- Windows：打开 PowerShell。下面如果某条命令在 PowerShell 里不同，会单独写出。
- 你在 Cursor 里也可以打开终端面板，效果一样。

敲完一行要按回车。没按回车，命令还没发出去。

## 自己动手

先用资源管理器或访达找到这个项目的文件夹（里面能看见 `README.md`）。下面的命令假设你已经知道它在磁盘的什么位置。如果不知道，就在那个文件夹里对终端说「在这里打开」。很多编辑器的终端会直接从项目文件夹开始。

### 1. 我现在站在哪

```bash
pwd
```

你应该看到一行路径，内容因人而异，例如：

```text
/Users/你的名字/ai-customer-service
```

Windows PowerShell 里用：

```powershell
pwd
```

可能显示成：

```text
Path
----
C:\Users\你的名字\ai-customer-service
```

认的不是这串字和文档一模一样，而是：它告诉你一个文件夹位置。如果最后一段不是项目文件夹的名字，你还没站在项目里。

### 2. 这一层有什么

macOS 或 Linux：

```bash
ls
```

Windows PowerShell：

```powershell
dir
```

你应该能在输出里找到这几个名字（前后可能还有别的）：

```text
README.md
requirements.txt
stage0_basics
```

看不到 `README.md`，就说明 `pwd` 显示的地方不对，先不要运行 Python。

### 3. 走进子文件夹，再走出来

```bash
cd stage0_basics
pwd
cd ..
pwd
```

第一次 `pwd` 的末尾应该多出 `stage0_basics`。`cd ..` 的 `..` 意思是「上一层」。第二次 `pwd` 应该回到项目根目录，末尾不再是 `stage0_basics`。

路径分两种：

- 相对路径：从你现在站的地方出发，比如 `stage0_basics/01_hello_llm.py`。
- 绝对路径：从磁盘根开始写全，比如 `/Users/你的名字/ai-customer-service/README.md`。不随你站在哪而改变意思。

本仓库的教程命令都假设你站在项目根目录，用相对路径。

## 常见错误

把 `cd stage0_basics` 打错文件夹名：

```text
cd: no such file or directory: stage0_basic
```

Windows 可能是：

```text
cd : 找不到路径
```

意思是：你当前这一层没有叫这个名字的文件夹。用 `ls` 或 `dir` 看真实名字，不要猜。

在已经走进 `stage0_basics` 之后又执行一次 `cd stage0_basics`：同样是「没有这个文件夹」，因为那一层里面没有另一个 `stage0_basics`。先 `cd ..` 回到根目录。

## 练习

1. 站在项目根目录，用一条命令走进 `stage0_basics`，再用一条命令回到根目录。写出你用的两条命令。
2. `ls` 看不到 `README.md` 时，下一步应该做什么？
3. `stage0_basics/01_hello_llm.py` 这种写法，是相对路径还是绝对路径？

## 答案

1. `cd stage0_basics`，然后 `cd ..`。
2. 先运行 `pwd`，看自己站错了哪一层，再用 `cd` 走到含有 `README.md` 的那一层。不要立刻运行 Python。
3. 相对路径。它表示「从当前目录出发，进入 stage0_basics，里面的那个文件」。你必须已经站在项目根目录，这条路径才指向对的文件。
