# -*- coding: utf-8 -*-
"""把工具结果说成客服的话。工具仍然在阶段 2 里执行，这里只组织发给模型的 messages。

不从 06_cli_with_tools.py 导入：那个文件名以数字开头，import 不能把它当成模块名。
"""

from summary import SUMMARY_PREFIX

SYSTEM_PROMPT = """你是「星河数码」的在线客服，名字叫小星。
请用简体中文回答，语气礼貌，句子短。
程序会在系统消息里给你工具的真实结果。金额、订单状态、工单编号只能引用结果里有的内容。
如果另一条系统消息以「此前对话摘要：」开头，那是更早的对话，不要把它当成顾客刚刚说的话。
不要编造物流单号、到货时间或退款金额。
不要索要密码、短信验证码或完整银行卡号。
退款只是记下工单，不要说已经打款。"""


def build_model_messages(summary: str, transcript: list[dict]) -> list[dict]:
    """岗位说明永远在最前。摘要其次。最近几轮跟在后面。"""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    text = summary.strip()
    if text != "":
        messages.append({"role": "system", "content": SUMMARY_PREFIX + text})
    for message in transcript:
        messages.append(message)
    return messages


def request_reply(client, model: str, messages: list[dict]) -> str:
    """和阶段 2 一样，这一次请求不再附带 tools。工具已经执行过了。"""
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.3,
        max_tokens=512,
        stream=False,
    )
    if not response.choices:
        raise RuntimeError("响应里没有 choices。")
    reply = response.choices[0].message.content
    if not isinstance(reply, str) or reply.strip() == "":
        raise RuntimeError("模型没有返回文本内容。")
    return reply


def phrase(client, model: str, messages: list[dict], user_text: str, fact: str) -> str:
    messages.append({"role": "user", "content": user_text})
    note = (
        "下面是程序刚刚得到的结果。请只根据这些内容回复顾客，"
        "不要补充结果里没有的单号、金额或时间。\n"
        + fact
    )
    messages.append({"role": "system", "content": note})
    try:
        reply = request_reply(client, model, messages)
    except Exception:
        # 先弹出这一轮的说明，再弹出顾客的话。顺序反了会把更早的回复弹掉。
        if messages and messages[-1]["role"] == "system":
            messages.pop()
        if messages and messages[-1]["role"] == "user":
            messages.pop()
        raise
    messages.append({"role": "assistant", "content": reply})
    return reply
