# -*- coding: utf-8 -*-
"""把模型的 tool_calls 变成一次本地函数调用，再收成 role=tool 的消息。

在线示例拿到的是 SDK 对象，离线示例拿到的是普通字典。
执行函数只写一份，两边都先收成名字和参数文本。
"""

import json

from schema import TOOLS
from tools import TOOL_FUNCTIONS

# 工具选择要稳定。这一课不是让模型发挥文采。
TOOL_TEMPERATURE = 0
TOOL_MAX_TOKENS = 512


def arguments_text(arguments) -> str:
    """在线接口给的是 JSON 文本。测试有时直接给字典。统一收成文本，后面只解析一次。"""
    if isinstance(arguments, str):
        return arguments
    return json.dumps(arguments, ensure_ascii=False)


def read_tool_call(tool_call) -> tuple[str, str, str]:
    """取出编号、函数名、参数文本。字典和 SDK 对象字段一样，外壳不一样。"""
    if isinstance(tool_call, dict):
        function = tool_call["function"]
        return tool_call["id"], function["name"], arguments_text(function["arguments"])
    function = tool_call.function
    return tool_call.id, function.name, arguments_text(function.arguments)


def tool_calls_of(message) -> list:
    if isinstance(message, dict):
        return message.get("tool_calls") or []
    return message.tool_calls or []


def message_content(message):
    if isinstance(message, dict):
        return message.get("content")
    return message.content


def assistant_message_dict(message) -> dict:
    """收成普通字典，方便打印，也方便放进下一轮 messages。

    思考模式还会多一个 reasoning_content。请求里已经关掉思考，
    若响应仍带着它，就原样留下。删掉的话，下一轮可能被接口拒绝。
    """
    payload = {"role": "assistant", "content": message_content(message)}
    calls = []
    for tool_call in tool_calls_of(message):
        call_id, name, raw_arguments = read_tool_call(tool_call)
        calls.append(
            {
                "id": call_id,
                "type": "function",
                "function": {"name": name, "arguments": raw_arguments},
            }
        )
    if calls:
        payload["tool_calls"] = calls
    if isinstance(message, dict):
        reasoning = message.get("reasoning_content")
    else:
        reasoning = getattr(message, "reasoning_content", None)
    if reasoning:
        payload["reasoning_content"] = reasoning
    return payload


def run_tool(name: str, raw_arguments: str) -> dict:
    """按登记表执行。表里没有的名字不会被调用。"""
    function = TOOL_FUNCTIONS.get(name)
    if function is None:
        return {"ok": False, "error": f"没有这个工具：{name}"}
    try:
        arguments = json.loads(raw_arguments)
    except json.JSONDecodeError as error:
        return {"ok": False, "error": f"参数不是合法 JSON：{error}"}
    if not isinstance(arguments, dict):
        return {"ok": False, "error": "参数必须是 JSON 对象"}
    try:
        # 两个星号把字典的键变成参数名。键必须和函数定义里的名字一致。
        result = function(**arguments)
    except TypeError as error:
        return {"ok": False, "error": f"参数和工具对不上：{error}"}
    if not isinstance(result, dict):
        return {"ok": False, "error": "工具没有返回字典"}
    return result


def append_tool_results(messages: list, message) -> list[dict]:
    """执行这条助手消息里的每一个 tool_call，并把结果追加到 messages 末尾。

    失败也要追加。模型靠这条 role=tool 的消息知道查没查到，而不是靠程序崩溃。
    """
    results = []
    for tool_call in tool_calls_of(message):
        call_id, name, raw_arguments = read_tool_call(tool_call)
        result = run_tool(name, raw_arguments)
        results.append({"name": name, "result": result})
        messages.append(
            {
                "role": "tool",
                "tool_call_id": call_id,
                # 接口要的是文本。字典先变成 JSON，中文保持中文。
                "content": json.dumps(result, ensure_ascii=False),
            }
        )
    return results


def request_with_tools(client, model: str, messages: list) -> tuple[dict, str]:
    """发一轮带 tools 的请求，把助手消息收成字典。

    stream 必须关掉。参数若只到了一半，就不能拿去执行函数。
    extra_body 关掉思考模式，避免这一课还要处理 reasoning_content 的来回。
    """
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
        temperature=TOOL_TEMPERATURE,
        max_tokens=TOOL_MAX_TOKENS,
        stream=False,
        extra_body={"thinking": {"type": "disabled"}},
    )
    if not response.choices:
        raise RuntimeError("响应里没有 choices。")
    choice = response.choices[0]
    finish_reason = choice.finish_reason or ""
    return assistant_message_dict(choice.message), finish_reason
