# -*- coding: utf-8 -*-
"""工作记忆：这一单办到哪了。

对话历史是 messages 列表，记录谁说过什么。
工作记忆是另一份小表：意图、槽位、正在等的那一项、手头的工单。
历史可以被窗口切短，订单号仍然要留在这张表上。
"""

from dataclasses import asdict, dataclass, field


@dataclass
class WorkingMemory:
    """手头任务的小表。messages 不放在这里。

    槽位用 default_factory。若写成 slots: dict = {}，所有对象会共用同一个字典。
    """

    intent: str | None = None
    slots: dict[str, str] = field(default_factory=dict)
    pending_slot: str | None = None
    pending_text: str = ""
    ticket_id: str = ""
    task_status: str = "idle"

    def to_dict(self) -> dict:
        """变成普通字典，后面才能交给 json.dumps。dataclass 本身不能直接序列化。"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "WorkingMemory":
        """从字典收回来。JSON 读回来的是字典，不会自动变回这个类。"""
        slots_raw = data.get("slots") if isinstance(data, dict) else None
        slots: dict[str, str] = {}
        if isinstance(slots_raw, dict):
            for key, value in slots_raw.items():
                slots[str(key)] = "" if value is None else str(value)
        return cls(
            intent=_blank_to_none(data.get("intent") if isinstance(data, dict) else None),
            slots=slots,
            pending_slot=_blank_to_none(
                data.get("pending_slot") if isinstance(data, dict) else None
            ),
            pending_text=_text(data.get("pending_text") if isinstance(data, dict) else ""),
            ticket_id=_text(data.get("ticket_id") if isinstance(data, dict) else ""),
            task_status=_text(data.get("task_status") if isinstance(data, dict) else "")
            or "idle",
        )

    def to_fields(self) -> dict[str, str]:
        """Redis HASH 的值只能是字符串。None 写成空字符串，槽位加上前缀以免和栏目重名。"""
        fields = {
            "intent": self.intent or "",
            "pending_slot": self.pending_slot or "",
            "pending_text": self.pending_text,
            "ticket_id": self.ticket_id,
            "task_status": self.task_status or "idle",
        }
        for name, value in self.slots.items():
            fields["slot." + str(name)] = "" if value is None else str(value)
        return fields

    @classmethod
    def from_fields(cls, fields: dict) -> "WorkingMemory":
        """从 HASH 的字符串栏目收回来。没有这张表时，调用方会传入空字典。"""
        slots: dict[str, str] = {}
        if isinstance(fields, dict):
            for key, value in fields.items():
                name = str(key)
                if name.startswith("slot."):
                    slots[name[len("slot.") :]] = "" if value is None else str(value)
        return cls(
            intent=_blank_to_none(fields.get("intent") if isinstance(fields, dict) else None),
            slots=slots,
            pending_slot=_blank_to_none(
                fields.get("pending_slot") if isinstance(fields, dict) else None
            ),
            pending_text=_text(fields.get("pending_text") if isinstance(fields, dict) else ""),
            ticket_id=_text(fields.get("ticket_id") if isinstance(fields, dict) else ""),
            task_status=_text(fields.get("task_status") if isinstance(fields, dict) else "")
            or "idle",
        )

    def to_stage2_session(self) -> dict:
        """阶段 2 只认识 session["pending"]。这里把小表翻译成它要的形状。"""
        if self.pending_slot:
            return {"pending": {"intent": self.intent, "text": self.pending_text}}
        return {"pending": None}

    def observe(self, session: dict, outcome: dict) -> None:
        """看完一轮工具之后，把「办到哪了」写回这张小表。"""
        intent = outcome.get("intent") if isinstance(outcome, dict) else None
        if isinstance(intent, str) and intent != "":
            self.intent = intent
        pending = session.get("pending") if isinstance(session, dict) else None
        if isinstance(pending, dict):
            pending_intent = pending.get("intent")
            if isinstance(pending_intent, str) and pending_intent != "":
                self.intent = pending_intent
            self.pending_text = _text(pending.get("text"))
            self.pending_slot = "order_id"
            self.task_status = "waiting"
            return
        self.pending_slot = None
        self.pending_text = ""
        if _remember_result(self, outcome):
            self.task_status = "done"
        elif self.task_status == "waiting":
            self.task_status = "idle"


def _blank_to_none(value) -> str | None:
    """HASH 里没有 None。空字符串读回来，仍然表示这项还没有。"""
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    return text


def _text(value) -> str:
    if value is None:
        return ""
    return str(value)


def _remember_result(memory: WorkingMemory, outcome: dict) -> bool:
    """只在工具真正成功时记下订单号和工单编号。失败的结果不能覆盖手头这一单。"""
    if not isinstance(outcome, dict):
        return False
    result = outcome.get("result")
    if not isinstance(result, dict) or not result.get("ok"):
        return False
    remembered = False
    order = result.get("order")
    if isinstance(order, dict) and order.get("order_id"):
        memory.slots["order_id"] = str(order["order_id"])
        remembered = True
    ticket = result.get("ticket")
    if isinstance(ticket, dict):
        if ticket.get("id") is not None:
            memory.ticket_id = str(ticket["id"])
            remembered = True
        if ticket.get("order_id"):
            memory.slots["order_id"] = str(ticket["order_id"])
            remembered = True
    return remembered
