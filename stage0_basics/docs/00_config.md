# 顺着 `config.py` 逐行读

## 本课需要的基础课

这一页不重讲语法。注释、字符串和 import 在回到这里之前，[第 1 个脚本](01_hello_llm.md) 已经让你读过。下面是本文件会用到的课。

- [基础课 · 注释](../../00_python_basics/04_comments.md)
- [基础课 · 字符串](../../00_python_basics/07_strings.md)
- [基础课 · import](../../00_python_basics/08_import.md)
- [基础课 · 变量](../../00_python_basics/05_variables.md)
- [基础课 · 对象和方法](../../00_python_basics/21_objects.md)
- [基础课 · for](../../00_python_basics/14_for.md)
- [基础课 · 虚拟环境](../../00_python_basics/09_venv_pip.md)
- [基础课 · try/except](../../00_python_basics/16_try_except.md)
- [基础课 · if](../../00_python_basics/12_if.md)
- [基础课 · 环境变量](../../00_python_basics/20_env.md)

你是从 `01_hello_llm.py` 第 10 行的 `from config import ...` 被送到这里的。那一行会先把本文件从头加载到尾。函数里面的行先被记住，要等 `01` 调用了才会执行。导读仍然按文件顺序讲，并标明哪些行是「加载时就发生」的。

加载本文件不会访问 DeepSeek，也不会读 `.env`。读 `.env` 发生在有人调用 `require_settings()` 的时候。

## 第 1 到 8 行

第 1 行是[基础课 · 注释](../../00_python_basics/04_comments.md)。第 2 到 7 行是三引号[基础课 · 字符串](../../00_python_basics/07_strings.md)，不打印，不联网。它告诉读文件的人：四个脚本共用这里，是为了不要各写一套密钥。

## 第 10 到 12 行：导入标准库

```python
import os
import traceback
from pathlib import Path
```

[基础课 · import](../../00_python_basics/08_import.md) 已经讲过三种写法。这里两种都有。

`os`、`traceback`、`pathlib` 都是标准库，跟着 Python 一起安装，不用 pip。`os` 用来读环境变量。`traceback` 用来在「这不是接口错误」时把调用过程打印出来。`Path` 是 `pathlib` 里的一个名字，专门拼文件路径。

如果改成 `import Path`，会 `ModuleNotFoundError`，因为没有 `Path.py` 这个模块。`Path` 住在 `pathlib` 里面。

## 第 14 到 17 行：不管你站在哪个目录，都去项目根找 `.env`

```python
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"
```

👉 不懂变量？先看 [基础课 · 变量](../../00_python_basics/05_variables.md)。👉 不懂对象？先看 [基础课 · 对象和方法](../../00_python_basics/21_objects.md) 里「点号是往里面取」。

`__file__` 是 Python 给的字符串：本文件自己的路径。`Path(...)` 把它变成路径对象。`.resolve()` 换成不含 `..` 的绝对路径。`.parent` 是上一层文件夹。`config.py` 在 `stage0_basics` 里，所以一个 `.parent` 是 `stage0_basics`，再一个 `.parent` 才是项目根。

`/` 在这里不是除法。路径对象用 `/` 拼接下一段。结果是「项目根目录里的 `.env`」。

这些行在 `import config` 时就会执行。此时还没打开文件，只是算好了路径。

如果改成「当前目录下的 `.env`」，你在 `stage0_basics` 里面运行脚本就会找错地方。这就是注释里说的原因。

## 第 19 到 21 行：没人设置时用的默认值

```python
DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-chat"
```

两个字符串变量。只有后面发现环境变量是空的，才会用它们。和 `.env.example` 写成一样，避免一处改了另一处忘了。

## 第 23 到 33 行：怎样认出「这还是说明书上的假密钥」

```python
_PLACEHOLDER_MARKERS = (
    "在这里",
    ...
)
```

圆括号把几段字符串捆成元组。列表课里讲过：元组这里只是一份不打算改的清单。名字以一个下划线开头，是在说「这是本文件自己用的」。别的文件仍可以导入它，只是约定上不要依赖它。

加载时这份清单就被建好。还没有拿它去比较密钥。

## 第 36 到 52 行：Settings 这个模具

```python
class Settings:
    def __init__(self, api_key, base_url, model):
        self.api_key = api_key
        ...
    def __repr__(self):
        return f"Settings(..., api_key='***')"
```

加载到 `class` 时，Python 把里面的函数登记到模具上，不会做出一个具体的配置。要等最后 `return Settings(...)` 才做出一个。

`self` 是「正在被做出的那一个对象」。`self.model = model` 把参数收进对象，以后写 `settings.model` 就能取出。

`__repr__` 决定 `print(settings)` 时显示什么。默认会把密钥也显示出来，所以我们改成星号。这是给学习者误写 `print(settings)` 时的防护。你可以在读完环境变量课之后，自己在交互模式里只构造一个假的 `Settings("秘密", "https://api.deepseek.com", "deepseek-chat")` 并打印，确认屏幕上没有「秘密」二字。不要把真密钥拿来试。

## 第 55 到 71 行：两个小函数先被记住

`_clean` 去掉首尾空白，如果整段被一对引号包住，再剥掉一层。这是在防「人把密钥连引号一起复制进环境变量」。函数体在加载时不运行。

`_is_placeholder` 把密钥转成小写再和清单比较。👉 不懂 for？先看 [基础课 · for](../../00_python_basics/14_for.md)。这个循环在这里第一次出现在本文件。中文标记没有大小写，所以同时用原文比一次。找到就 `return True`，函数立刻结束，不再看后面的标记。一个都没有就 `return False`。

加载时这两个函数都不执行。

## 第 74 到 81 行：缺库时的说明

`_exit_because_package_missing` 里面全是 `print`，最后 `raise SystemExit(1)`。它不返回。谁调用它，程序就在这里结束。文案里同时写出导入名和 pip 安装名，因为 `dotenv` 和 `python-dotenv` 不是同一个字符串。👉 不懂虚拟环境？先看 [基础课 · 虚拟环境](../../00_python_basics/09_venv_pip.md)。如果导入课里已经读过，看一眼「两个名字」那一节即可。

## 第 85 到 90 行：为什么 import dotenv 写在函数里面

```python
def _load_dotenv():
    try:
        from dotenv import load_dotenv
    except ImportError:
        _exit_because_package_missing("dotenv", "python-dotenv")
    return load_dotenv
```

如果这行 `from dotenv import ...` 写在文件第 10 行，那么 `import config` 的瞬间就会失败，`01` 连自己的中文说明都来不及组织。放进函数后，只有真的要读 `.env` 时才导入。没安装时走 `except ImportError`，那是「模块找到了但名字不对」或者「包不存在」时都可能出现的一类错误。对 `dotenv` 来说，没安装就是这个失败。

👉 不懂 try/except？先看 [基础课 · try/except](../../00_python_basics/16_try_except.md)。这里用来接住「预计之中的没装库」，而不是接住密钥错误。

`return load_dotenv` 交回去的是函数本身，不是调用它的结果。调用方还要自己加括号。

## 第 94 到 118 行：三种「没有密钥」不是同一句话

`_print_missing_key_help` 只打印，不退出。退出是调用者做的。

先看 `placeholder`。👉 不懂 if？先看 [基础课 · if](../../00_python_basics/12_if.md)。`if` / `elif` / `else` 按顺序只进一支。先问是不是假密钥，是因为「环境变量里导出了说明书上的那句话、同时磁盘上没有 `.env`」时，真正该做的是换掉假密钥，而不是只去找文件。

这个函数在加载时不执行。没有密钥时你才会在屏幕上看到这些句子。

## 第 121 到 146 行：require_settings 是第一次碰 `.env` 的地方

谁调用 `require_settings()`，下面这些才发生。

```python
load_dotenv = _load_dotenv()
load_dotenv(ENV_PATH, override=False, encoding="utf-8")
```

先拿到 `load_dotenv` 这个函数，再调用它。`override=False` 和 `encoding="utf-8"` 是[基础课 · 对象和方法](../../00_python_basics/21_objects.md)里的关键字参数。

👉 不懂环境变量？先看 [基础课 · 环境变量](../../00_python_basics/20_env.md)。

`encoding="utf-8"` 表示按 UTF-8 读那个文件。文件如果是别的编码，会抛出 `UnicodeError`，被下面的 `except` 接住，提示你另存为 UTF-8，然后 `SystemExit`。不接住的话，你看到的是一串编码错误，不知道要改保存格式。

```python
api_key = _clean(os.environ.get("DEEPSEEK_API_KEY", ""))
base_url = _clean(os.environ.get("DEEPSEEK_BASE_URL", "")) or DEFAULT_BASE_URL
model = _clean(os.environ.get("DEEPSEEK_MODEL", "")) or DEFAULT_MODEL
```

`os.environ.get` 在 [基础课 · 环境变量](../../00_python_basics/20_env.md) 里。第二个参数 `""` 保证找不到时是空字符串，不是 `None`。

`or` 在这里的意思是：左边清洗后如果是空的，就用右边的默认值。空字符串在这种写法里会被当成「没有」，于是换成 `DEFAULT_BASE_URL`。

```python
if not api_key or _is_placeholder(api_key):
    _print_missing_key_help(...)
    raise SystemExit(1)
```

空的，或者仍是占位文字，就打印对应说明并结束。如果删掉 `raise SystemExit(1)`，函数还会继续往下，拿着空密钥去造 `Settings`，接下来的请求变成难读的 401。

后面的 `if` 检查地址是不是以 `https://` 或 `http://` 开头。`api.deepseek.com` 这种缺了协议的字符串在这里就被拦住，到不了网络。

最后 `return Settings(...)` 做出一个对象。三个关键字参数把钥匙、地址、模型名放进对应的格子。

## 第 149 到 169 行：describe 和 create

`describe_settings` 三条 `print`。f-string 把 `settings.base_url` 嵌进去。没有打印 `api_key`。

`create_client` 里才 `from openai import OpenAI`。没安装就走和 dotenv 一样的中文退出。安装了就：

```python
return OpenAI(
    api_key=settings.api_key,
    base_url=settings.base_url,
    timeout=60.0,
    max_retries=1,
)
```

这是在做对象，不是在 `create()` 一次聊天。`timeout=60.0` 是一次尝试最多等 60 秒。`max_retries=1` 是失败后再试一次。试太多次，人会以为程序死了。注释写的就是这个原因。

`OpenAI` 这个名字来自第三方库。它是模具，`OpenAI(...)` 是做出一个客户端实例。

## 第 172 行到文件末尾：print_api_error

这个函数只在请求已经失败之后才被调用。加载文件时不执行。

它先打印错误类型和原始英文，再 `from openai import` 一串具体的错误名字。那些名字是类。`AuthenticationError` 是密钥被拒绝。它同时也是更笼统的 `APIStatusError`。所以 `if` / `elif` 把具体的放在前面。这就是 if 课里「问到第一个成立的就停」。

`isinstance(error, AuthenticationError)` 问「这个失败是不是这一类」。是，就打印「重新粘贴密钥」。

`status_code == 402` 对上 HTTP 课里的「没钱了」。

最后一支 `not isinstance(error, OpenAIError)`：失败不是这个 SDK 抛的，多半是我们自己的代码写错了，于是 `traceback.print_exc()` 把过程打出来。`traceback` 就是第 11 行导入的那个模块。

这个函数不 `raise`。第 1 课的调用者自己结束程序。第 4 课的调用者回到循环。如果在这里结束，客服就没法「失败一轮、窗口还在」。

## 读完回到哪里

回到 [01 导读的第 12 行](01_hello_llm.md)。`config.py` 已经加载完，四个函数可以调用了，但 `.env` 还没读，模型也还没被叫到。
