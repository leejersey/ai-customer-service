# 从另一个文件夹导入

[导入课](08_import.md) 说过：直接运行脚本时，查找清单的第一项是这个脚本自己所在的文件夹。`01_hello_llm.py` 和 `config.py` 坐在一起，所以 `from config import ...` 找得到。

`stage1_intent/llm_intent.py` 和 `config.py` 不在同一个文件夹。不处理的话就是：

```text
ModuleNotFoundError: No module named 'config'
```

这不是没安装 `config`。标准库和 pip 里都没有它。它在 `stage0_basics/`。

## 打个比方

图书管理员只在你现在站的这层找书。阶段 0 的书在另一层。`sys.path` 是他愿意去找的楼层清单。`insert(0, 文件夹)` 是把那一层插到清单最前面，让他先去那里。

## 自己动手

在项目根目录运行：

```bash
python -c "import sys; print(sys.path[0])"
```

`python -c` 没有脚本文件，第一项常常是空字符串，表示当前目录。再运行：

```bash
python -c "import stage1_intent.stage0_link as link; link.enable(); import sys; print(sys.path[0])"
```

如果当前目录不在包路径里，第二条可能先 `ModuleNotFoundError`。用文件方式更稳。把下面存成临时实验即可，项目里已经有同样的三行：

```python
import sys
from pathlib import Path

folder = Path("stage0_basics").resolve()
sys.path.insert(0, str(folder))
print(sys.path[0])
```

在项目根目录运行这段，预期是 `stage0_basics` 的绝对路径，每个人的前半段不同，最后一段是 `stage0_basics`。

`insert` 的 `0` 表示插到清单开头。用 `append` 会加到末尾。末尾太晚：如果别处已经有一个名叫 `config` 的库，会先命中那个，不是我们的文件。

## 为什么写成 enable 函数

导入课强调过：`import` 不应该顺便做惊人的事。所以 `stage0_link.py` 只定义 `enable`。真正改清单的是调用。而且这行必须出现在 `from config import ...` 之前。Python 执行到 `import config` 时立刻查找。查找失败不会在你后来 `enable()` 之后自动重试。

## 常见错误

先写 `from config import ...`，再 `enable()`。错误在第一行就已经抛出，后面的 `enable` 不会执行。

路径写成 `stage0_basics` 但你站在别的目录，相对路径会指错。项目里用 `Path(__file__).resolve().parent.parent`，跟文件走，不跟当前目录走。这和阶段 0 找 `.env` 是同一个原因。

## 练习

1. `ModuleNotFoundError: No module named 'config'` 在阶段 1 里首先怀疑什么？
2. 为什么 `sys.path.insert(0, folder)` 比 `append` 更合适？
3. `enable()` 调用两次，清单里会有两份相同路径吗？看 `stage0_link.py` 里哪一行在防止。

## 答案

1. 还没把 `stage0_basics` 放进查找清单，或者放得太晚。不是密钥问题。
2. 开头先被搜索。我们自己的 `config.py` 应该压过任何同名第三方库。
3. 不会。`if folder in sys.path: return` 已经在清单里就直接离开。
