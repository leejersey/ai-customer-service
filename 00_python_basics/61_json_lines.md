# 追加写入和 JSON Lines：一行一条，不覆盖上一轮

[第 34 课](34_with.md) 用 `"w"` 写文件。`"w"` 会把原来的内容清掉，再写下这一次的字。审计要留下每一轮，所以用 `"a"` 接在文件末尾。每一行单独是一段 JSON，这种文件叫 JSON Lines。

阶段 6 用在 [审计日志](../stage6_compliance/docs/07_risk.md) 的 `append_record`。

## 先用一句人话

`open(路径, "a", encoding="utf-8")` 表示追加。文件不存在就创建，存在就把新的一行写到最后。一行一个 JSON 对象，读的时候按行 `json.loads`，不用把整个文件当成一个大数组。

## 打个比方

`"w"` 是把账本撕掉重写今天这一页。`"a"` 是在最后一页后面再订一页。JSON Lines 是规定每一页只有一笔账，笔和笔之间换行，以后要查某一笔，不用把整本账拆开重钉。

## 自己动手

在一个临时文件上试。试完可以删掉。不要把真实的手机号写进去。

```python
import json
from pathlib import Path

path = Path("lesson61_demo.jsonl")
if path.exists():
    path.unlink()

record = {"action": "放行", "text": "没有号码"}
with path.open("a", encoding="utf-8") as handle:
    handle.write(json.dumps(record, ensure_ascii=False) + "\n")

record["action"] = "拦截"
with path.open("a", encoding="utf-8") as handle:
    handle.write(json.dumps(record, ensure_ascii=False) + "\n")

for line in path.read_text(encoding="utf-8").splitlines():
    print(json.loads(line)["action"])
path.unlink()
```

预期：

```text
放行
拦截
```

两行都在。如果两次都用 `"w"`，第二次会只剩「拦截」。

`Path.open` 和 `open(path, "a")` 用的是同一个模式字母。`encoding="utf-8"` 让中文仍是中文。`ensure_ascii=False` 的原因在 [JSON 来回](42_json_roundtrip.md)。目录还不存在时，要先 `mkdir`，那是 [第 56 课](56_path_mkdir.md)。

整个文件如果写成一个 JSON 数组，每追加一笔都要先读出全部、改数组、再整份覆盖。日志变长之后，这一来一回既慢，也容易在写到一半时把文件写坏。一行一条可以只打开末尾。

## 常见错误

追加时忘了 `"\n"`。两段 JSON 粘在同一行，下一回 `json.loads` 会报 `JSONDecodeError`。

用 `"a"` 却希望每次运行都从空文件开始。追加会把昨天的练习留在文件里。演示脚本如果要干净的结果，先 `unlink` 再写。

把顾客的完整手机号写进行。文件在 `.gitignore` 里，不代表你的磁盘上没有明文。写入之前要打码。阶段 6 在 `append_record` 里再打一次，就是防调用方忘了。

`"w"` 和 `"a"` 看反。排查时文件里只有最后一轮，多半是模式用成了 `"w"`。

## 练习

1. 同一个路径用 `"w"` 写两次「第一行」「第二行」，文件里还剩什么？
2. 为什么每一行末尾要有换行？
3. 审计文件为什么不提交到 Git？

## 答案

1. 只剩「第二行」。`"w"` 先清空。
2. 没有换行，两段 JSON 连在一起，按行解析会失败。
3. 里面是运行时产生的练习记录。即使打过码，也不属于课程源码。`.gitignore` 忽略了 `stage6_compliance/data/` 和 `*.jsonl`。

下一课把一个函数交给另一个函数：[函数作为参数](62_pass_function.md)。
