# HTTP、API、JSON：一次网络请求里有什么

到 `create(...)` 为止，事情都发生在你的电脑里。这一行跨过网络。对方不认识 Python 变量。双方交换的是按规矩写的文本。这个规矩里，你现在要认识三个词：HTTP、API、JSON。

## 先用一句人话

HTTP 是送表格的方式：去哪个地址、用哪种动词、表格放在正文里、工牌放在信封上。

API 是对方公布的「我接受哪些表格」。不是一个 Python 函数，虽然 SDK 把它包装成了函数。

JSON 是表格的一种写法，用花括号、方括号、引号和冒号。字典和列表写成文本之后，看起来就是 JSON。

## 打个比方

你填写一张纸质申请表（JSON）。信封上写收件地址和你的工牌（HTTP 的地址和请求头）。窗口只收他们公布过的那种表（API）。窗口不收你的 Python 笔记本。SDK 是代你抄表、送信、再把回执抄回 Python 对象的人。

## JSON 长什么样

下面是一段 JSON 文本。它不是 Python 程序，所以不要在前面加 `print`。

```json
{
  "model": "deepseek-chat",
  "stream": false
}
```

和 Python 字典很像，差别是：JSON 的键必须是双引号字符串；真假写成 `true` 和 `false` 全小写；空值写成 `null`，不是 `None`。SDK 负责这些翻译。你在 Python 里写 `False`，送出去变成 `false`。

可以自己做一次翻译，用标准库就行，不用密钥：

```python
import json
text = json.dumps({"model": "deepseek-chat", "stream": False}, ensure_ascii=False)
print(text)
```

预期：

```text
{"model": "deepseek-chat", "stream": false}
```

`ensure_ascii=False` 是为了中文还是中文，而不是一串 `\uXXXX`。没有中文时看不出差别。

再翻译回来：

```python
import json
data = json.loads('{"finish_reason": "stop"}')
print(data["finish_reason"])
```

预期：

```text
stop
```

## 一次聊天请求在路上是什么样

地址分成三截：

- `https://`：加密的 HTTP。
- `api.deepseek.com`：哪一台服务。这是我们 `.env` 里的 `DEEPSEEK_BASE_URL`。
- `/chat/completions`：哪一个窗口。SDK 根据你调用的是 `chat.completions` 把这截补上。不要自己把这截再写进 `base_url`，否则路会重复。

动词用 `POST`，表示「我送来一份正文」，不是「我只是来取一个网页」。

信封上有请求头，其中一行类似：

```text
Authorization: Bearer sk-你的密钥
```

工牌不在 JSON 正文里。所以我们打印 `messages` 时看不到密钥。它仍然出了你的电脑。不要把密钥打印出来「核对一下」。

正文就是那份有 `model`、`messages`、`temperature`、`max_tokens`、`stream` 的 JSON。导读里会按我们的脚本把一份示例全文写出来。

对方回一张 HTTP 状态码，再加一份 JSON。

| 状态码 | 人话 |
| --- | --- |
| 200 | 请求被接受，再去读 JSON 里有没有正文 |
| 401 | 工牌被拒绝 |
| 402 | 账户没钱了（有的服务用这个码） |
| 404 | 地址或要找的东西不存在 |
| 429 | 你来得太勤 |
| 500 | 对方服务器自己出错 |

200 只表示快递送到了并被收下。JSON 里的 `content` 仍可能是空的。所以脚本先看有没有抛错，再看 `choices`，再看正文。

回执 JSON 里，你现在要对得上的栏是：`choices` 这叠纸的第 0 张、那张纸的 `message.content`（正文）、`finish_reason`（为什么停）、`usage`（token 数量）。其余栏是编号和时间，导读走到打印它们时再看。

流式时，HTTP 正文不是一份完整 JSON，而是很多段 SSE：一行行以 `data: ` 开头的小 JSON，最后一行常常是 `data: [DONE]`。SDK 把每一段变成循环里的 `chunk`。你在 Python 里看不到 `data: ` 这几个字符，不代表网上没有它们。

## 常见错误

把 Python 的 `False`、`None` 写进一个 `.json` 文件。那不是合法 JSON。合法的是 `false`、`null`。

把密钥放进 JSON 还打印出来。接口不需要你这么做，SDK 已经放进请求头。

`base_url` 写成整段 `https://api.deepseek.com/chat/completions`。SDK 再拼一次路径，窗口就错了，常见结果是 404。

把状态码 200 理解成「这句话是真的」。200 只说明这次通话完成。模型仍然可以编一个运单号。真假不是 HTTP 管的。

## 练习

1. Python 里的 `False`，写成 JSON 时是什么？
2. 密钥应该出现在 JSON 正文里，还是请求头里？
3. 为什么 `base_url` 停在 `https://api.deepseek.com` 就够了？

## 答案

1. `false`。小写，而且没有引号。
2. 请求头。正文只放模型、消息和采样参数。
3. 最后一截 `/chat/completions` 由 SDK 根据 `chat.completions.create` 这个方法补上。你再写一次就会重复。
