# -*- coding: utf-8 -*-
"""按 session_id 把消息、摘要和工作记忆放进 Redis。

消息用 LIST，一条一个 JSON。摘要用字符串。工作记忆用 HASH。
每次读写都把这三把键的 TTL 重新拨到满，空闲超过 TTL 才消失。
"""

import json

from working import WorkingMemory

# 前缀固定，避免和这台 Redis 里别人的键撞在一起。不要对整个库执行 FLUSHDB。
SESSION_PREFIX = "stage3:session:"


class SessionStore:
    """会话记忆。client 可以是 redis、fakeredis，或 backend.InMemoryRedis。

    这个类不关心数据在另一台机器上还是在本进程里。命令名字相同就可以。
    """

    def __init__(self, client, ttl_seconds: int = 1800, prefix: str = SESSION_PREFIX) -> None:
        if ttl_seconds < 1:
            raise ValueError("TTL 至少是 1 秒")
        self.client = client
        self.ttl_seconds = ttl_seconds
        self.prefix = prefix

    def key(self, session_id: str, suffix: str) -> str:
        _require_session_id(session_id)
        return f"{self.prefix}{session_id}:{suffix}"

    def touch(self, session_id: str) -> None:
        """访问任意一块，三把键都续期。只续其中一把，另外两把会先过期，会话就残了。"""
        for suffix in ("messages", "summary", "working"):
            name = self.key(session_id, suffix)
            if self.client.exists(name):
                self.client.expire(name, self.ttl_seconds)

    def append_message(self, session_id: str, message: dict) -> None:
        name = self.key(session_id, "messages")
        self.client.rpush(name, _dump_message(message))
        self.touch(session_id)

    def replace_messages(self, session_id: str, messages: list[dict]) -> None:
        """压缩之后整表换成「摘要之外的最近几轮」。先删再推，避免旧消息还留在列表尾部前面。"""
        name = self.key(session_id, "messages")
        self.client.delete(name)
        for message in messages:
            self.client.rpush(name, _dump_message(message))
        self.touch(session_id)

    def all_messages(self, session_id: str) -> list[dict]:
        raw_items = self.client.lrange(self.key(session_id, "messages"), 0, -1)
        self.touch(session_id)
        return _load_messages(raw_items)

    def recent_messages(self, session_id: str, limit: int) -> list[dict]:
        """只读最近 limit 条。负数下标从列表末尾数，不必先问一共有多长。"""
        if limit < 1:
            self.touch(session_id)
            return []
        raw_items = self.client.lrange(self.key(session_id, "messages"), -limit, -1)
        self.touch(session_id)
        return _load_messages(raw_items)

    def save_summary(self, session_id: str, summary: str) -> None:
        name = self.key(session_id, "summary")
        self.client.set(name, summary, ex=self.ttl_seconds)
        self.touch(session_id)

    def load_summary(self, session_id: str) -> str:
        value = self.client.get(self.key(session_id, "summary"))
        self.touch(session_id)
        if value is None:
            return ""
        return str(value)

    def save_working(self, session_id: str, memory: WorkingMemory) -> None:
        """先删掉旧 HASH。否则上一轮的 slot.order_id 会在这一轮清空后仍然留着。"""
        name = self.key(session_id, "working")
        self.client.delete(name)
        self.client.hset(name, mapping=memory.to_fields())
        self.touch(session_id)

    def load_working(self, session_id: str) -> WorkingMemory:
        fields = self.client.hgetall(self.key(session_id, "working"))
        self.touch(session_id)
        if not fields:
            return WorkingMemory()
        return WorkingMemory.from_fields(fields)

    def clear_session(self, session_id: str) -> None:
        """只删这一会话的三把键。不要清空整台 Redis。"""
        self.client.delete(
            self.key(session_id, "messages"),
            self.key(session_id, "summary"),
            self.key(session_id, "working"),
        )


def _require_session_id(session_id: str) -> None:
    if not isinstance(session_id, str) or session_id.strip() == "":
        raise ValueError("session_id 不能是空的")
    if "\n" in session_id or "\r" in session_id:
        raise ValueError("session_id 不能换行")


def _dump_message(message: dict) -> str:
    """Redis 的列表成员是文本。字典要先变成 JSON，读的时候再变回来。"""
    return json.dumps(message, ensure_ascii=False)


def _load_messages(raw_items) -> list[dict]:
    messages = []
    for raw in raw_items:
        if not isinstance(raw, str):
            continue
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            # 人手改错一条时，跳过它，其余消息还要能读。
            continue
        if isinstance(data, dict):
            messages.append(data)
    return messages
