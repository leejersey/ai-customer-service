# 函数作为参数：先把步骤交出去，稍后再调用

[第 28 课](28_functions_in_dict.md) 是把函数放进字典，选中之后再加括号。[第 11 课](11_functions.md) 是自己定义、自己调用。这一课是：调用一个函数时，把另一个函数交进去，让它在合适的时候再调用。

阶段 6 用在两处。打码时，`re.sub` 的第二个参数可以是函数，见 [第 58 课](58_regex_sub.md)。整轮审核的 `judge_fn`、`answer_fn`、`tool_fn` 也是交进去的函数，见 [离线演示](../stage6_compliance/docs/09_offline.md)。

## 先用一句人话

函数名不加括号，表示「这套步骤本身」。加了括号，表示「现在就做」。你可以把步骤交给别人，由别人决定做不做、做几次。

## 打个比方

你把一把钥匙交给门卫，不是自己现在就开门。门卫（外层函数）按规矩决定：这扇门要不要开。离线演示交给门卫的是一把假钥匙，它不会去联网。命令行交给门卫的是真的去问 DeepSeek 的那一把。门卫的代码不用写两份。

## 自己动手

```python
def allow(text):
    return "放行：" + text

def block(text):
    return "拦截"

def review(text, decide):
    return decide(text)

print(review("七天无理由", allow))
print(review("忽略之前的指令", block))
```

预期：

```text
放行：七天无理由
拦截
```

注意 `review(..., allow)` 里 `allow` 没有括号。写成 `allow()` 会立刻调用，而且少了 `text` 参数，报错是：

```text
TypeError: allow() missing 1 required positional argument: 'text'
```

外层可以不调用它。下面的 `judge` 是 `None` 时，就当这一轮没有裁判：

```python
def run(reply, judge):
    if judge is None:
        return "只看规则"
    return judge(reply)

print(run("你好", None))
print(run("你好", allow))
```

预期：

```text
只看规则
放行：你好
```

阶段 6 的离线演示把 `fake_judge` 交进去。示例 8 在没有密钥时交 `None`，有密钥时交 `llm_judge`。审核流程仍是同一个 `run_turn`。

## 常见错误

把函数调用的结果交进去，而不是函数。`review(text, allow())` 和 `review(text, allow)` 不是一回事。前者在进门之前就已经执行了。

裁判函数抛错时，外层如果没有接住，整段客服会停。阶段 6 在调用 `judge_fn` 的地方用 `try` 接住，失败改走拒绝。接住错误是 [第 16 课](16_try_except.md)。不能因为没接住就当它说了「通过」。

以为必须用装饰器才能把函数交出去。装饰器是另一种语法，阶段 6 没有新写装饰器。`@dataclass` 仍是 [第 41 课](41_dataclass.md)。

## 练习

1. `review("你好", allow())` 为什么会报错？
2. 离线演示为什么可以不改 `run_turn`，只换交进去的函数？
3. `judge is None` 时为什么不能默认通过？

## 答案

1. `allow()` 立刻执行，又没有传 `text`。`review` 收到的是返回值，不是函数。若 `allow` 碰巧不缺参数，交进去的也是字符串，后面再加括号仍会失败。
2. `run_turn` 只负责在固定的座位上调用你给的函数。假裁判和真裁判都符合「收一句回复，交回字典」。
3. 没有裁判只表示这一轮不额外请模型。词表和正则仍要检查。若把「没调用」写成通过，解析失败和网络失败也会被放行。阶段 6 在真的请了裁判、却读不懂结果时，默认拒绝。

这一课接到阶段 6。基础课后面若再加，仍按课号往后排，仍放在这个目录里。
