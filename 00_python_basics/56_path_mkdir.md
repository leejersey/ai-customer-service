# 创建文件夹：父母不在时一并建好

[列出文件夹](46_path_iterdir.md) 是去一个已经在的目录里看文件。[读文本](29_read_text.md) 打开一个已经知道名字的文件。阶段 5 第一次保存索引时，`data/memory/某位顾客/` 往往还不存在。要先把文件夹建出来。

阶段 5 用在 [FAISS](../stage5_vector_memory/docs/04_faiss.md) 的 `folder.mkdir`，以及保存前删掉过期的 `index.faiss`。

## 先用一句人话

`path.mkdir(parents=True, exist_ok=True)` 的意思是：中间缺的文件夹一起建；文件夹已经在，也不要报错。

## 打个比方

你要在「仓库 / 顾客 / 张三」里放一个箱子。仓库那一层可能还没有。`parents=True` 是把路上缺的房间一起盖好。`exist_ok=True` 是：房间已经盖过了，就直接进去，不要对着已有的门再喊一次「盖不了」。

## 自己动手

在项目根目录运行。生成的目录在 `stage5_vector_memory/data/` 里，这个目录已被 git 忽略。

```python
from pathlib import Path

folder = Path("stage5_vector_memory/data/lesson56_demo")
folder.mkdir(parents=True, exist_ok=True)
print(folder.is_dir())
folder.mkdir(parents=True, exist_ok=True)
print("第二次也不会报错")
```

预期：

```text
True
第二次也不会报错
```

`parents=True` 类似老的 `os.makedirs`。课程里已经在用 `Path`，所以这里用 `Path.mkdir`，不再另学一套 `os.makedirs`。两句做的是同一件事：中间目录一起建。

删掉一个文件用 `unlink`，文件夹还在：

```python
note = folder / "note.txt"
note.write_text("临时", encoding="utf-8")
note.unlink()
print(note.is_file())
print(folder.is_dir())
```

预期：

```text
False
True
```

阶段 5 的离线演示在重跑前会 `unlink` 自己的 `index.faiss` 和 `meta.json`，避免上次的维度还占着位子。不要对知识库里的 `.md` 调用 `unlink`。

## 常见错误

文件夹已经在，又 `mkdir()`，既没有 `exist_ok=True`：

```text
FileExistsError: [Errno 17] File exists: 'stage5_vector_memory/data/lesson56_demo'
```

第二次保存索引时就会撞上。保存用的是 `exist_ok=True`。

只写 `mkdir()`，上一层 `data` 还不存在：

```text
FileNotFoundError: [Errno 2] No such file or directory: '.../data/lesson56_demo'
```

加上 `parents=True`，缺的上层会一起出现。

`unlink` 用在了文件夹上。删文件夹不是这一课的事。阶段 5 只删那两个生成出来的文件。

## 练习

1. `parents=True` 和 `exist_ok=True` 各在防哪一种报错？
2. `Path.mkdir` 和 `os.makedirs` 在这一课里是什么关系？
3. 为什么离线演示要删掉旧的 `index.faiss`，而不是接着往里面加？

## 答案

1. `parents=True` 防的是上层目录不存在时的 `FileNotFoundError`。`exist_ok=True` 防的是目录已经在时的 `FileExistsError`。
2. 都是「把中间缺的目录一起建出来」。这一课用 `Path.mkdir`，因为前面已经在用 `Path`。
3. 索引的维度和模型名写在文件里。换了嵌入之后，旧文件的格子对不上新向量。删掉再重建，比把两套数混在一个索引里安全。

下一课让模型只加载一次：[模块级缓存](57_module_cache.md)。
