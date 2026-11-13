# pathlib：列出文件夹里的文件

[读文本文件](29_read_text.md) 会用 `Path.read_text` 打开一个已经知道名字的文件。阶段 4 的知识库是一个文件夹，里面有好几份说明，名字不是写死在一行里的。

阶段 4 用在 [加载文档](../stage4_rag/docs/01_load.md) 的 `directory.iterdir()`。读出正文仍然用第 29 课的 `read_text`。

## 先用一句人话

`Path` 是地址。`iterdir()` 是按这个地址打开抽屉，把里面的每一项逐个交给你。每一项仍是一个 `Path`，不是文件里的文字。

## 打个比方

抽屉上的标签是文件夹的地址。你拉开抽屉，看见一叠文件的封面。封面告诉你文件名和后缀。要把信纸上的字读出来，还得对其中一张再做一次 `read_text`。

## 自己动手

在项目根目录运行：

```python
from pathlib import Path

folder = Path("stage4_rag/knowledge")
names = []
for path in folder.iterdir():
    if not path.is_file():
        continue
    if path.suffix.lower() not in {".md", ".txt"}:
        continue
    names.append(path.name)
for name in sorted(names):
    print(name)
```

预期是这 8 行，顺序固定：

```text
01_退换货政策.md
02_运费与配送.md
03_会员积分.md
04_售后保修.md
05_支付方式.md
06_发票.md
07_常见问题.md
08_营业时间.txt
```

`iterdir()` 交出来的顺序不保证。所以先收进列表，再 `sorted`。`path.suffix` 是最后一个点后面的部分，包含点，例如 `.md`。`path.name` 是文件名，不含文件夹。

`is_file()` 用来跳过子文件夹。知识库现在没有子文件夹，写上是为了以后多放一层时不会把文件夹当成一篇政策。

文件内容仍要第 29 课的写法：

```python
text = path.read_text(encoding="utf-8")
```

## 常见错误

文件夹不存在：

```text
FileNotFoundError: [Errno 2] No such file or directory: 'stage4_rag/knowledge'
```

你不在项目根目录，相对路径就指错了。脚本里用 `Path(__file__).resolve().parent / "knowledge"`，跟文件走，不跟当前目录走。

把 `iterdir()` 当成已经读完的字符串。它给出的是一个一个地址。对地址 `for`，拿到的是 `Path`。要对 `path.read_text()` 的结果再 `for`，才是一行一行或一个字一个字。

忘记跳过不想要的后缀。文件夹里若有编辑器留下的杂项，也会被读进知识库。阶段 4 只收 `.md` 和 `.txt`。

## 练习

1. `path.name` 和 `path.read_text(encoding="utf-8")` 哪一个会打开文件？
2. 为什么打印文件名之前要 `sorted`？
3. `path.suffix` 对 `08_营业时间.txt` 得到什么？

## 答案

1. `read_text` 才打开文件。`name` 只是文件名这几个字。
2. `iterdir()` 不保证顺序。不排序的话，两次运行的打印可能不一样，对照文档会对不上。
3. `.txt`。点在结果里面。

下一课把读进来的长字符串按空行切开：[split 和 join](47_split_join.md)。
