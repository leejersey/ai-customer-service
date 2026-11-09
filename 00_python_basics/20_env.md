# 环境变量和 `.env`：密钥放在程序外面

`config.py` 不把密钥写成 `api_key = "sk-..."`。它写的是：

```python
api_key = _clean(os.environ.get("DEEPSEEK_API_KEY", ""))
```

## 先用一句人话

环境变量是操作系统交给这个进程的一组名字和值，不是 `.py` 文件里的变量。进程结束，这些值就从进程里消失。`.env` 文件则把它们记在磁盘上。Python 不会自动读 `.env`。是 `python-dotenv` 的 `load_dotenv()` 在启动时把文件抄进环境变量。

## 打个比方

`.py` 文件是会进版本库的菜谱，可以给人看。密钥是保险箱密码。密码写进菜谱，菜谱一分享，密码就走了。密码写在抽屉便签 `.env` 上，菜谱里只写「去抽屉里找名叫 `DEEPSEEK_API_KEY` 的便签」。

`.env.example` 是便签的空白格式，上面写着栏名，值是假的。它可以提交。`.env` 不能提交。

## 环境变量不是 Python 赋值

在交互模式里：

```python
import os
os.environ["DEMO_SHOP"] = "星河数码"
print(os.environ["DEMO_SHOP"])
print(os.environ.get("没有这个名字", ""))
```

预期：

```text
星河数码

```

第二行是空行。`get` 的第二个参数是「找不到时给我什么」。我们用 `""`，这样后面只要判断字符串空不空，不用先接 `KeyError`。

直接用方括号取一个不存在的名字：

```text
KeyError: '没有这个名字'
```

终端里也可以在启动前临时放一个值。macOS 或 Linux：

```bash
export DEMO_SHOP=星河
python -c "import os; print(os.environ.get('DEMO_SHOP', ''))"
```

预期：

```text
星河
```

这个 `export` 只影响当前终端里以后启动的进程。它不会写进 `.env`，也不会改 `.py` 文件。

Windows PowerShell：

```powershell
$env:DEMO_SHOP="星河"
python -c "import os; print(os.environ.get('DEMO_SHOP', ''))"
```

## `.env` 要有人去读

文件内容类似：

```text
DEEPSEEK_API_KEY=sk-你的密钥
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

等号两边不要空格，值不要加引号。这不是 Python 语法。

`load_dotenv(路径, override=False)` 的意思是：文件里有、而环境里还没有的名字，抄进去。环境里已经有的，不覆盖。所以你为了做一次实验在终端里 `export` 了模型名，不会被旧的 `.env` 悄悄改回去。

`override=True` 则是文件优先。实验时你会觉得「我明明 export 了，怎么没生效」。

我们还用文件位置找 `.env`，不靠你当前站在哪个目录。否则你从 `stage0_basics` 里运行脚本，就会去错误的层找便签。

## 常见错误

只创建了 `.env`，但运行的是一段自己写的、没有 `load_dotenv` 的代码。环境变量里仍然没有密钥。文件不会自己跳进进程。

把 `.env.example` 当成已经填好的密钥。占位文字会被 `config.py` 拒绝，避免你看见一串难懂的 401。

密钥写进 `.py` 然后 `git add`。即使下一分钟删掉，历史里还在。不要这样做。

`os.getenv` 和 `os.environ.get` 是同一件事的两种写法。`os.getenv("DEEPSEEK_API_KEY", "")` 同样是「没有就给空字符串」。我们的代码用的是后一种。你在别的教程看到前一种，不要以为那是另一个系统。

## 练习

1. 为什么 `.env.example` 可以提交，`.env` 不可以？
2. 终端里已经 `export DEEPSEEK_MODEL=deepseek-flash`，`.env` 里仍然是 `deepseek-chat`。按我们的 `override=False`，程序用哪一个？
3. `os.environ.get("DEEPSEEK_API_KEY", "")` 在完全没设置时，得到什么？它是 `None` 吗？

## 答案

1. 示例文件只有栏名和假占位符，用来告诉别人要准备哪些名字。`.env` 里是真密钥，提交等于把密码公开。
2. 用终端里的 `deepseek-flash`。已经存在的环境变量不会被文件盖掉。
3. 得到空字符串 `""`，不是 `None`。第二个参数决定了找不到时给什么。
