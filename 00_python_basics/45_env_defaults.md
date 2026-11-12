# 环境变量的默认值：没有这个名字，和值是空的

[环境变量](20_env.md) 讲过 `os.environ.get("DEEPSEEK_API_KEY", "")`：名字不存在时，给你第二个参数。阶段 3 的 Redis 地址不能在「没写」时变成空字符串，否则没有地址可以连。空着的 `REDIS_URL=` 同样不能拿去连接。

阶段 3 用在 [Redis 入门](../stage3_memory/docs/04_redis.md) 的 `configured_text`。密钥为什么放在 `.env`，仍以第 20 课为准，这里不重复。

## 先用一句人话

`get` 的第二个参数只在「这个名字根本没有」时使用。名字在，值是空字符串，你得到的就是空字符串。想把「没写」和「写了但为空」都换成一个能用的地址，要自己再判断一次。从环境变量读到的 TTL 也是文本，交给 Redis 之前要 `int`。

## 打个比方

抽屉里没有便签，你就用柜台上贴着的默认地址。抽屉里有一张空白便签，你不能假装没看见，然后去用柜台地址。空白便签是「有这张纸，上面没字」。连接需要一个真正的地址，所以空白也要退回柜台地址。这和 [默认参数](37_default_args.md) 里「空字符串不算没传」是同一类事，只是发生在环境变量上。

## 自己动手

```python
import os

print(os.environ.get("STAGE3_DEMO_URL", "redis://localhost:6379/0"))
os.environ["STAGE3_DEMO_URL"] = ""
print(os.environ.get("STAGE3_DEMO_URL", "redis://localhost:6379/0"))
```

预期：第一行是 `redis://localhost:6379/0`。第二行是空行。名字已经存在，第二个参数不会再生效。

把两种空都收成默认值：

```python
def configured_text(name, fallback):
    raw = os.environ.get(name)
    if raw is None:
        return fallback
    text = str(raw).strip()
    if text == "":
        return fallback
    return text

os.environ.pop("STAGE3_DEMO_URL", None)
print(configured_text("STAGE3_DEMO_URL", "redis://localhost:6379/0"))
os.environ["STAGE3_DEMO_URL"] = "   "
print(configured_text("STAGE3_DEMO_URL", "redis://localhost:6379/0"))
os.environ["STAGE3_DEMO_URL"] = "redis://127.0.0.1:6379/0"
print(configured_text("STAGE3_DEMO_URL", "redis://localhost:6379/0"))
```

预期：

```text
redis://localhost:6379/0
redis://localhost:6379/0
redis://127.0.0.1:6379/0
```

TTL 在环境变量里也是一段文字。`int` 才变成秒数。不是整数时要接住：

```python
print(int("1800"))
try:
    int("半小时")
except ValueError as error:
    print(type(error).__name__)
```

预期：

```text
1800
ValueError
```

阶段 3 遇到这种 `ValueError`，会打印一句中文并改用 1800，而不是让客服在启动时崩溃。`try` 的用法在 [第 16 课](16_try_except.md)。

跑完示例，可以执行 `os.environ.pop("STAGE3_DEMO_URL", None)`，免得这个名字留在当前进程里影响你的下一个实验。它不会写进 `.env`。

## 常见错误

只写 `os.environ.get("REDIS_URL", "redis://localhost:6379/0")`，同时 `.env` 里有 `REDIS_URL=`。你得到空字符串，连接失败，屏幕上的原因会很难懂。阶段 3 把空白也当成「用默认地址」。

把 `"1800"` 直接交给需要整数的参数。有的接口会拒绝，有的会把这段文字当成别的含义。先 `int`。

默认值写成真实密钥。默认值会进仓库。Redis 的默认地址 `redis://localhost:6379/0` 没有密码，可以写在代码里。API 密钥没有安全的默认值，所以第 20 课用空字符串，空了就停止，而不是编一个密钥。

## 练习

1. 名字不存在时，`os.environ.get("REDIS_URL", "redis://localhost:6379/0")` 得到什么？
2. 名字存在且值是 `""` 时，上一题那个 `get` 得到什么？
3. `int("1800")` 和字符串 `"1800"` 有什么差别？

## 答案

1. `redis://localhost:6379/0`。第二个参数派上用场。
2. 空字符串。名字在，默认值不再生效。
3. `int` 得到整数 1800，可以和秒数比较、可以交给 `EXPIRE`。字符串只能当文字显示，不能当秒数相加。
