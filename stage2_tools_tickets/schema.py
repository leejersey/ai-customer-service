# -*- coding: utf-8 -*-
"""交给模型的 tools 参数。

这是说明书，不是函数本身。模型只能看见名字、说明和参数形状，
看不见 Python 函数，更不能自己去碰数据库。
"""

from states import STATUS_NAMES
from tools import TICKET_TYPES


def _function(name: str, description: str, properties: dict, required: list[str]) -> dict:
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        },
    }


# 列表的顺序不表示优先级。模型看说明来选，不靠「写在前面就先用」。
TOOLS = [
    _function(
        "query_order",
        "按订单号查询星河数码的一张订单。没有订单号时不要调用，先向顾客追问。",
        {
            "order_id": {
                "type": "string",
                "description": "订单号，一串数字，例如 10086",
            },
        },
        ["order_id"],
    ),
    _function(
        "create_ticket",
        "创建一张工单。退款必须有真实存在的订单号。投诉和转人工可以没有订单号。不会真的打款。",
        {
            "ticket_type": {
                "type": "string",
                "enum": list(TICKET_TYPES),
                "description": "工单类型",
            },
            "description": {
                "type": "string",
                "description": "顾客原话或事情经过，不要留空",
            },
            "user_name": {
                "type": "string",
                "description": "顾客称呼。不知道就省略，程序会用「演示用户」",
            },
            "order_id": {
                "type": "string",
                "description": "相关订单号。退款时必填，投诉可以省略",
            },
        },
        ["ticket_type", "description"],
    ),
    _function(
        "update_ticket_status",
        "把已有工单推进到下一个状态。只能前进一步：待处理到处理中，处理中到已解决，已解决到已关闭。",
        {
            "ticket_id": {
                "type": "integer",
                "description": "工单编号",
            },
            "status": {
                "type": "string",
                "enum": list(STATUS_NAMES),
                "description": "要改成的状态",
            },
        },
        ["ticket_id", "status"],
    ),
    _function(
        "get_ticket",
        "按工单编号查询一张工单的类型、状态和描述。",
        {
            "ticket_id": {
                "type": "integer",
                "description": "工单编号",
            },
        },
        ["ticket_id"],
    ),
]
