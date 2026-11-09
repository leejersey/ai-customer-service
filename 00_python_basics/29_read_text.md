# 用 pathlib 读文本文件

阶段 0 只用 `Path` 拼出 `.env` 在哪。阶段 1 要把标准答案从 `labeled_examples.json` 读进内存。文件不会因为躺在文件夹里就变成 Python 列表。

## 打个比方

`Path` 是地址。`read_text` 才是按这个地址把信的内容取出来，变成一个长字符串。JSON 文件取出来仍是字符串。要变成列表，还得 `json.loads`，那是上一课的事。

## 自己动手

在项目根目录运行：

```python
from pathlib import Path

path = Path("stage1_intent/data/labeled_examples.json")
print(path.name)
print(path.parent.name)
text = path.read_text(encoding="utf-8")
print(text.splitlines()[0])
print(text.splitlines()[1])
```

预期：

```text
labeled_examples.json
data
[
  {"text": "这款耳机怎么连接蓝牙", "intent": "咨询"},
```

第一行是文件名。`parent.name` 是它所在的文件夹名 `data`。`splitlines()` 按行切开，第 0 行是 `[`，第 1 行是第一条数据。你的编辑器如果把 JSON 排成一行，第 1 行会不同。我们仓库里的文件是分行的。

`encoding="utf-8"` 必须写上。不写时，有的系统用别的编码读中文，会 `UnicodeDecodeError`。

文件不存在：

```text
FileNotFoundError: [Errno 2] No such file or directory: 'stage1_intent/data/labeled_examples.json'
```

你不在项目根目录时，这条相对路径会指错。脚本里用 `Path(__file__).resolve().parent / "data" / "labeled_examples.json"`，和找 `.env` 一样，跟文件走。

## 常见错误

`read_text` 之后直接 `for item in text`。字符串的 for 是一个字一个字，不是一条测试数据一个。要先 `json.loads`。

把路径写成字符串去做除法。`Path` 才能用 `/` 拼接。普通字符串相加要自己加斜杠。

## 练习

1. `path.name` 和 `path.read_text()` 分别得到什么？
2. 为什么读测试集要写 `encoding="utf-8"`？
3. 脚本放在 `stage1_intent/` 里时，为什么不用 `"data/labeled_examples.json"` 这种跟当前目录走的相对路径？

## 答案

1. `name` 只是文件名字符串，不打开文件。`read_text()` 才是文件里的全部文字。
2. 文件里有中文。写明 UTF-8，换一台电脑也不会猜错编码。
3. 当前目录取决于你在哪执行命令。`__file__` 是脚本自己的位置，从它的父目录去找 `data`，两条命令（在根目录运行或在 `stage1_intent` 里运行）都能找到。
