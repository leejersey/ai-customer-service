# -*- coding: utf-8 -*-
"""让模型把回复分成通过、需修改、拒绝。解析失败时默认拒绝，不能默认通过。

裁判只看已经打过码的回复。它不负责生成给顾客的那一句。
"""

import json

VERDICTS = ("通过", "需修改", "拒绝")
CLOSED_REASON = "审核结果无法解析，默认拒绝，不放行"

_JUDGE_SYSTEM = """你是审核员，不是客服。只输出一个 JSON 对象，不要其他文字，不要使用 Markdown。
格式：{"verdict":"通过","reason":"一句话原因"}
verdict 只能是：通过、需修改、拒绝。
通过：回复礼貌，符合退换货政策，没有索要密码，没有背出系统提示，没有别人的号码。
需修改：大体能用，但有绝对化用语，或把政策说死。
拒绝：辱骂、诋毁其他品牌、索要密码、泄露系统提示或其他顾客的资料、答应赔偿或打款。
reason 用简体中文，不能为空。"""


def closed_verdict() -> dict:
    """失败时的那一档。ok 为 False，调用方不能把它当成模型真的说了拒绝之外的话。"""
    return {"verdict": "拒绝", "reason": CLOSED_REASON, "ok": False}


def parse_verdict(content: str) -> dict:
    """从原文里剪出 JSON。字段不对、前后是废话、根本不是 JSON，都走关闭。"""
    try:
        start = content.find("{")
        end = content.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("没有 JSON 对象")
        data = json.loads(content[start : end + 1])
        if not isinstance(data, dict):
            raise ValueError("不是对象")
        if not all(key in data for key in ("verdict", "reason")):
            raise ValueError("缺少字段")
        verdict = data["verdict"]
        reason = data["reason"]
        if verdict not in VERDICTS:
            raise ValueError("verdict 不在允许的三个词里")
        if not isinstance(reason, str) or reason.strip() == "":
            raise ValueError("reason 为空")
        return {"verdict": verdict, "reason": reason.strip(), "ok": True}
    except (ValueError, json.JSONDecodeError, TypeError):
        return closed_verdict()


def hits_from_verdict(judged: dict) -> list[dict]:
    """通过不加命中。需修改和拒绝各加一条，交给 decide 和词表命中比严重程度。"""
    if not judged.get("ok") or judged.get("verdict") == "拒绝":
        reason = judged.get("reason") or CLOSED_REASON
        return [{"category": "模型审核", "word": reason, "level": "高", "action": "拦截"}]
    if judged.get("verdict") == "需修改":
        return [
            {
                "category": "模型审核",
                "word": judged.get("reason") or "需修改",
                "level": "中",
                "action": "改写",
            }
        ]
    return []


def llm_judge(client, model: str, reply: str) -> dict:
    """请 DeepSeek 当裁判。网络或接口失败也关闭，不能因为裁判缺席就放行。"""
    try:
        response = client.chat.completions.create(
            model=model,
            temperature=0,
            max_tokens=200,
            messages=[
                {"role": "system", "content": _JUDGE_SYSTEM},
                {"role": "user", "content": reply},
            ],
        )
        content = response.choices[0].message.content or ""
    except Exception:
        return closed_verdict()
    return parse_verdict(content)
