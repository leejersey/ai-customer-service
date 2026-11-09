# import：把另一个文件里的名字拿过来用

`01_hello_llm.py` 在注释之后的第一句真正要执行的代码是：

```python
from config import create_client, describe_settings, print_api_error, require_settings
```

这是导入。不先懂这句话，后面的 `require_settings()` 就是凭空冒出来的名字。

## 先用一句人话

一个 `.py` 文件可以请 Python 去读另一个 `.py` 文件，并把那里面的一些名字带到当前文件里。这样同一段读密钥的代码不用在四个脚本里复制四遍。

被导入的那个文件叫模块。模块就是一个 `.py` 文件（也有少数模块是用别的语言写好、装进 Python 的，你用起来一样）。

一叠模块放在一个文件夹里，这个文件夹叫包。你可以 `import 文件夹.文件`。阶段 0 的脚本没有写成包，`config.py` 和 `01_hello_llm.py` 只是同一个文件夹里的两个模块。

## 打个比方

你的脚本是一张新菜谱。`import` 是在说：盐的用量不要重写，去标准调料表那一页把「盐」这个名字借来。借来之后，这张新菜谱可以直接写「盐」，不必每次写「见标准调料表的盐」。

借的动作会发生：那一页会被读一遍。不是把纸剪下来贴上那么安静。对方文件顶层有 `print`，导入的瞬间就会打印。

## 标准库和第三方库

有些模块跟着 Python 一起安装，不用你再下载。这叫标准库。我们用到的 `os`、`pathlib`、`sys`、`traceback` 都是。

有些模块不在安装包里。`openai` 和 `dotenv` 就是。它们叫第三方库，要用 pip 装进你当前这个 Python。虚拟环境和 pip 的完整课是[下一课](09_venv_pip.md)。导入失败时如果你还没读过它，先去读，再回来。

自己写的 `config.py` 既不是标准库，也不是用 pip 装的。它就放在脚本旁边。

## 三种写法

在交互模式或临时文件里试。`math` 是标准库，一定存在，适合练语法。

### `import 模块`

```python
import math
print(math.sqrt(16))
```

预期：

```text
4.0
```

你得到的名字是 `math`。要用里面的 `sqrt`，就写 `math.sqrt`。点号的意思是「这个模块里面的」。

### `from 模块 import 名字`

```python
from math import sqrt
print(sqrt(16))
```

预期同样是：

```text
4.0
```

名字 `sqrt` 直接拿进来了，不用写 `math.`。我们的脚本用的就是这种：导入之后直接写 `require_settings()`，而不是 `config.require_settings()`。

一次拿好几个名字，用逗号：

```python
from math import sqrt, pi
print(sqrt(16))
print(pi)
```

预期第二行是 `3.141592653589793`（小数位数以你的 Python 为准，开头是 3.14 即可）。

如果写成 `import config`，下面就要写 `config.require_settings()`。两种都能跑。我们选 `from ... import ...`，是为了脚本读起来是动作本身，而不是每行都带着 `config.`。

### `import 模块 as 简称`

```python
import math as m
print(m.sqrt(9))
```

预期：

```text
3.0
```

`as` 只是给拿进来的名字起个别名。模块原来的文件名不会改。名字很长、或者和你自己的变量撞车时才需要。阶段 0 的脚本没有用 `as`。

`from math import sqrt as square_root` 也可以，意思是拿 `sqrt` 进来，但在这个文件里叫 `square_root`。

## Python 去哪些地方找模块

可以想成一张按顺序翻的文件夹清单。找到第一个同名模块就停。大致顺序是：

1. 你正在运行的那个脚本所在的文件夹。不是你终端「当前目录」一定优先，而是脚本文件自己坐落的文件夹。
2. 标准库所在的位置。
3. 当前这个 Python 的第三方安装目录，名字经常叫 `site-packages`。虚拟环境里的 Python，和系统里的 Python，这张清单不是同一张。

所以在项目根目录运行：

```bash
python stage0_basics/01_hello_llm.py
```

脚本位于 `stage0_basics` 文件夹。Python 会把这个文件夹放进查找清单的前面。`from config import ...` 就能找到旁边的 `config.py`。你即使站在别的目录，只要用路径指对了这个脚本，`config` 仍然找得到。

反过来，如果你在一个完全无关的文件夹里打开交互模式，输入 `import config`，清单里没有我们的项目，就会失败。那不代表 `config.py` 丢了，只代表这次的查找清单里没有它。

可以亲眼看清单（输出很长，每个人路径不同）：

```python
import sys
print(sys.path)
```

你会看到方括号包住很多路径。方括号是列表，[列表课](13_lists_dicts.md)再学。现在只需要在输出里找：有没有脚本所在的文件夹，有没有 `site-packages`。

导入成功后，Python 会记住这个模块。同一个程序里第二次 `import config` 不会把 `config.py` 从头再执行一遍。改了 `config.py` 却没重新运行脚本，你看到的还是旧的，因为整个程序还没重新开始。

导入时，Python 可能在旁边生成 `__pycache__` 文件夹，里面是加速用的缓存。不要手改，也不要提交。它不是第二份程序。

## 失败时长什么样

模块根本找不到：

```python
import not_a_real_module
```

```text
ModuleNotFoundError: No module named 'not_a_real_module'
```

模块找到了，但里面没有你要的名字：

```python
from math import not_a_name
```

```text
ImportError: cannot import name 'not_a_name' from 'math'
```

后面还会跟一个路径，告诉你它实际找到的 `math` 在哪个文件。读这个路径，可以判断你是不是导入了一个同名的自己的文件。

自己写了一个 `math.py` 放在脚本旁边，再 `import math`，Python 会先找到你的文件，标准库的 `math` 就被挡住。这叫遮蔽。不要给自己的文件起 `math.py`、`os.py`、`json.py`、`openai.py` 这种名字。

`config.py` 里如果连 `openai` 都还没安装，要到真正执行 `from openai import OpenAI` 时才失败。我们把这句放在函数里面，就是为了在失败时改成中文说明，而不是只留一行英文 `ModuleNotFoundError`。那是虚拟环境课要接上的情节。

## 常见错误

把 `from config import require_settings` 写成 `import require_settings`。Python 会去找名叫 `require_settings.py` 的文件，找不到：

```text
ModuleNotFoundError: No module named 'require_settings'
```

`require_settings` 是 `config.py` 里面的函数名，不是文件名。

在 `config.py` 里又去 `import` 正在运行的脚本，形成互相导入。初学者阶段不要这么写。两个文件互相在顶层导入，经常会得到「名字还不存在」的 `ImportError`。

## 练习

1. 用 `from math import sqrt` 计算 25 的平方根并打印。预期输出是什么？
2. `import math` 之后写 `print(sqrt(16))`，为什么会 `NameError`？怎样改一行就能过？
3. 为什么 `python stage0_basics/01_hello_llm.py` 找得到 `config`，而在别的文件夹的交互模式里 `import config` 常常找不到？

## 答案

1. `from math import sqrt` 然后 `print(sqrt(25))`。预期是 `5.0`。
2. `import math` 只带来名字 `math`，没有带来名字 `sqrt`。改成 `print(math.sqrt(16))`，或者改用 `from math import sqrt`。
3. 运行脚本时，查找清单的前面有 `stage0_basics` 这个文件夹，`config.py` 在里面。交互模式如果是从别的地方启动的，清单最前面是那个启动位置，没有我们的 `config.py`。
