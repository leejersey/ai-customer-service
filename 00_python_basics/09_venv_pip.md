# 虚拟环境和 pip：第三方库装进哪一个 Python

[导入课](08_import.md) 说过：`openai` 和 `dotenv` 不是随 Python 自带的。要先安装。安装到「哪一个 Python」比安装本身更容易错。

`config.py` 在 `from openai import OpenAI` 失败时，会打印「请先激活虚拟环境，再 pip install」。这一课解释那两句话在做什么。

## 先用一句人话

电脑上可以有好几个 Python。`pip install` 只把库装进「你敲 pip 时那个 Python」。虚拟环境是项目文件夹里的一个独立 Python，加上它自己的库目录。激活，就是让接下来的 `python` 和 `pip` 都指向这一个。

## 打个比方

系统 Python 是楼里的公共工具箱。`.venv` 是这个项目抽屉里的私人工具箱。你在公共工具箱里放了锤子，回到私人工具箱仍然找不到锤子。报错 `No module named 'openai'` 经常不是「没装过」，而是「装到了另一个箱子」。

## 自己动手

在项目根目录（能看见 `requirements.txt` 的那一层）：

macOS 或 Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell：

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

成功的标志是提示符前面多了 `(.venv)`。

`python3 -m venv .venv` 的意思是：请这个 Python 执行自带的 `venv` 模块，在当前文件夹创建名叫 `.venv` 的环境。这只需要做一次。`.venv` 已经在 `.gitignore` 里，不要提交。

激活不是把环境「打开成一个窗口」。它只改当前这个终端。你新开一个终端，`(.venv)` 会消失，需要再执行一次 `source .venv/bin/activate`。

看当前 `python` 到底是哪一个：

macOS 或 Linux：

```bash
which python
which pip
```

路径里应该含有 `.venv`。Windows PowerShell 用 `Get-Command python`。

然后安装本阶段的库：

```bash
pip install -r requirements.txt
```

`requirements.txt` 是一张购物清单。pip 按清单下载 `openai` 和 `python-dotenv`，放进当前环境的 `site-packages`。

装完自测：

```bash
python -c "import openai, dotenv; print('依赖已安装')"
```

预期：

```text
依赖已安装
```

`python -c` 表示不写文件，直接运行引号里的那一句。这里用它只是检查导入能不能成功。

离开环境：

```bash
deactivate
```

提示符里的 `(.venv)` 消失。库还在 `.venv` 文件夹里，没有被卸载。

## 和导入查找清单的关系

激活之后，你运行的 `python` 换了，`sys.path` 里的 `site-packages` 也换成 `.venv` 里面的那一个。所以同一个 `import openai`，激活前可能失败，激活后成功。

包在 pip 里的安装名，和 import 时的名字，可以不一样。清单上写的是 `python-dotenv`，代码里写的是 `import dotenv`。这就是 `config.py` 报错时同时告诉你两个名字的原因。

## 常见错误

没激活就安装，然后激活后再运行：

```text
ModuleNotFoundError: No module named 'openai'
```

处理：确认提示符有 `(.venv)`，再执行一次 `pip install -r requirements.txt`，并用 `which python` 确认路径在 `.venv` 里。

把 `pip install dotenv` 当成安装方法。正确的安装名是 `python-dotenv`。装错名字时，要么装到一个无关的包，要么仍然 `No module named 'dotenv'`。

在虚拟环境里用 `sudo pip install`。不需要管理员权限，而且可能会装到系统 Python。不要加 `sudo`。

## 练习

1. 新开一个终端后，为什么昨天装过的 `openai` 又提示找不到？写出你要检查的一个现象。
2. `pip install` 和 `import` 的名字，以 `python-dotenv` 为例，分别是什么？
3. `deactivate` 会把 `.venv` 文件夹删掉吗？

## 答案

1. 新终端没有 `(.venv)`。激活只对当时那个终端有效。看到提示符前面没有 `(.venv)`，就先重新激活。
2. 安装名是 `python-dotenv`。导入名是 `dotenv`。
3. 不会。它只是让当前终端改回用别的 Python。文件夹还在。
