# 顺着模型分类逐行读

先运行：

```bash
python stage1_intent/02_llm_classifier.py
```

没有密钥时，前三段坏文本仍会解析，然后程序说明跳过模型并正常结束。不要把它当成安装失败。

这一课先读 `stage0_link.py`，再读 `llm_intent.py`，最后读演示脚本。

## `stage0_link.py`

先停下来读 [从另一个文件夹导入](../../stage0_basics/python_basics/26_import_other_folder.md)。

`STAGE0_DIR` 用 `__file__` 找到仓库根，再进入 `stage0_basics`。`enable` 里如果路径已经在 `sys.path` 就返回。否则 `insert(0, ...)`。

导入这个文件不会改清单。`llm_intent.py` 第 8 到 10 行是：

```python
import stage0_link
stage0_link.enable()
from config import ENV_PATH, _clean, _is_placeholder
```

三行的顺序不能颠倒。`config` 里以下划线开头的函数，阶段 0 约定别人别依赖。这里仍然用它们，是因为要做和 `require_settings` 相同的「这是不是占位密钥」判断，又不想把它的「打印并退出」带过来。导读把这当作例外写明，不要在新代码里随便调用别人的下划线名字。

## `api_key_ready`

```python
try:
    from dotenv import load_dotenv
except ImportError:
    return False
```

`import` 写在函数里，和阶段 0 把 `import openai` 放进函数是同一理由：失败时由我们决定怎么办。这里的决定是返回 `False`，不是 `SystemExit`。规则打分和坏 JSON 演示必须继续。

后面 `load_dotenv`、`_clean`、`_is_placeholder` 复习 [环境变量](../../stage0_basics/python_basics/20_env.md)。空密钥和占位符都返回 `False`。

## 兜底字典

`_fallback` 永远交回同样的键：意图「其他」、置信度 0、订单号 `None`、`source` 为 `"fallback"`，外加 `error` 说明原因。成功的结果没有 `error` 这个键。演示脚本用 `.get("error")`，没有这个键就得到 `None`，不会 `KeyError`。

## 把 JSON 从原文里剪出来再解析

先停下来读 [json.loads 和解析失败](../../stage0_basics/python_basics/27_json_parse.md)。

`_extract_json_text` 用 `find` 和 `rfind`。找不到花括号就把原文交给 `loads`，让它失败。失败被 `except json.JSONDecodeError` 接住，变成兜底，不往外抛。

`parse_model_output` 在 `loads` 成功之后还做这些检查，每一条失败都是兜底：

- 必须是字典，不能是列表。
- `intent` 必须在 `INTENTS` 里。模型写「生气」是合法 JSON，但是我们的路由器没有这个按钮。
- `confidence` 先拒绝布尔值。在 Python 里 `True` 也算整数，不先排除的话，`true` 会被当成置信度 1。
- 数字要在 0 和 1 之间。
- `slots` 必须是字典。`order_id` 只能是字符串或 `None`。空字符串改成 `None`，和「没抽到」同一种空。

这些检查删掉任何一条，坏结果都会流进路由器，后面的 `.get` 或字符串拼接会在离真正原因很远的地方爆炸。

通过检查的结果 `source` 是 `"llm"`。哪怕 JSON 是我们从废话中间剪出来的，来源仍然记成模型，因为数字是模型写的，不是规则写的。

## `classify_by_llm`

这一函数会联网。复习阶段 0 的 `create`：关键字参数、`temperature`、`messages`。这里温度是 0，因为我们要表格，不要文采。系统提示把格式和六个意图写死。它仍然只是文字，模型可能不遵守，所以才有 `parse_model_output`。

网络失败不在这里兜底。没有响应和「响应里的字不是 JSON」是两件事。前者抛出去，演示脚本打印中文后继续下一句。后者变成 `fallback`。

没有 choices 或没有文本时，这个函数自己返回兜底。调用方不用区分「解析失败」和「空响应」，键是一样的。

## 演示脚本 `02_llm_classifier.py`

它也先 `enable()`，再导入 `config` 里的 `create_client` 等。然后导入 `llm_intent`。`llm_intent` 被加载时会再 `enable()` 一次，清单里不会重复，这是 `enable` 里的判断。

`BROKEN_SAMPLES` 三条对应三种结果：完全不是 JSON、前后有废话但中间合法、意图不在名单里。你运行后应看到第一条 `fallback`，第二条 `llm` 且意图是查订单，第三条 `fallback` 且错误信息里有「不存在的意图」。

`api_key_ready()` 为假就打印两行并 `return`。`return` 结束 `main`，不是异常。退出码是 0。

有密钥时才 `require_settings`。这里才允许它在密钥突然无效时退出，因为人已经明确在跑模型演示。循环里的 `except` 用阶段 0 的 `print_api_error`，然后 `continue`，一句失败不挡住后面的句子。

下一课把意图交给不同的函数：[路由器](03_router.md)。
