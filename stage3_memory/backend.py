# -*- coding: utf-8 -*-
"""连接 Redis。连不上时改用 fakeredis，再不行就用本文件里的内存实现。

短期记忆要放在进程外面，程序退出后才还在。
内存实现只是为了课堂练习在没有 Redis 时仍能把命令跑完，它做不到这件事。
"""

import os
import time

import stage3_link

stage3_link.enable()

from dataclasses import dataclass

DEFAULT_REDIS_URL = "redis://localhost:6379/0"
DEFAULT_TTL_SECONDS = 1800


@dataclass
class ConnectedRedis:
    """手里的客户端，加上它到底连的是谁。

    kind 用来在屏幕上说明数据会不会随着进程一起消失。
    """

    client: object
    kind: str
    detail: str


class InMemoryRedis:
    """只实现本阶段用到的命令。数据放在这个对象里，进程结束就没了。

    过期靠 time.time() 自己算。真正的 Redis 会在服务端倒计时，不占用这门课的进程。
    """

    def __init__(self) -> None:
        self._items: dict[str, tuple[object, float | None]] = {}

    def ping(self) -> bool:
        return True

    def close(self) -> None:
        """关上把手。内存里的键还在这个对象上，直到对象被丢掉。"""
        return None

    def set(self, name: str, value, ex: int | None = None) -> bool:
        self._items[str(name)] = (str(value), _deadline(ex))
        return True

    def get(self, name: str):
        value = self._alive(str(name))
        return value

    def expire(self, name: str, seconds: int) -> bool:
        key = str(name)
        value = self._alive(key)
        if value is None:
            return False
        self._items[key] = (value, _deadline(seconds))
        return True

    def ttl(self, name: str) -> int:
        key = str(name)
        item = self._items.get(key)
        if item is None:
            return -2
        value, deadline = item
        if deadline is None:
            return -1
        remaining = int(deadline - time.time())
        if remaining <= 0:
            self._items.pop(key, None)
            return -2
        return remaining

    def delete(self, *names: str) -> int:
        removed = 0
        for name in names:
            key = str(name)
            if self._alive(key) is None:
                continue
            self._items.pop(key, None)
            removed = removed + 1
        return removed

    def exists(self, name: str) -> int:
        if self._alive(str(name)) is None:
            return 0
        return 1

    def rpush(self, name: str, *values) -> int:
        key = str(name)
        current = self._alive(key)
        deadline = self._deadline_of(key)
        if not isinstance(current, list):
            current = []
            deadline = None
        for value in values:
            current.append(str(value))
        self._items[key] = (current, deadline)
        return len(current)

    def lrange(self, name: str, start: int, end: int) -> list:
        current = self._alive(str(name))
        if not isinstance(current, list):
            return []
        start_index, end_index = _inclusive_range(len(current), start, end)
        if start_index > end_index:
            return []
        return current[start_index : end_index + 1]

    def ltrim(self, name: str, start: int, end: int) -> bool:
        key = str(name)
        kept = self.lrange(key, start, end)
        if not kept:
            self._items.pop(key, None)
            return True
        self._items[key] = (kept, self._deadline_of(key))
        return True

    def hset(self, name: str, key=None, value=None, mapping=None) -> int:
        hash_key = str(name)
        current = self._alive(hash_key)
        deadline = self._deadline_of(hash_key)
        if not isinstance(current, dict):
            current = {}
            deadline = None
        added = 0
        if isinstance(mapping, dict):
            for field, field_value in mapping.items():
                field_name = str(field)
                if field_name not in current:
                    added = added + 1
                current[field_name] = "" if field_value is None else str(field_value)
        if key is not None:
            field_name = str(key)
            if field_name not in current:
                added = added + 1
            current[field_name] = "" if value is None else str(value)
        self._items[hash_key] = (current, deadline)
        return added

    def hget(self, name: str, key: str):
        current = self._alive(str(name))
        if not isinstance(current, dict):
            return None
        return current.get(str(key))

    def hgetall(self, name: str) -> dict:
        current = self._alive(str(name))
        if not isinstance(current, dict):
            return {}
        copied = {}
        for key, value in current.items():
            copied[key] = value
        return copied

    def _alive(self, key: str):
        item = self._items.get(key)
        if item is None:
            return None
        value, deadline = item
        if deadline is not None and time.time() >= deadline:
            self._items.pop(key, None)
            return None
        return value

    def _deadline_of(self, key: str) -> float | None:
        item = self._items.get(key)
        if item is None:
            return None
        return item[1]


def load_project_env() -> None:
    """读 .env，但不因为没有 API 密钥而退出。Redis 地址和模型密钥是两件事。"""
    from config import ENV_PATH

    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    try:
        load_dotenv(ENV_PATH, override=False, encoding="utf-8")
    except UnicodeError:
        print(f"{ENV_PATH} 不是 UTF-8。Redis 地址和 TTL 将使用代码里的默认值。")


def configured_text(name: str, fallback: str) -> str:
    """名字不存在，或者值是空的，都用 fallback。

    os.environ.get(name, fallback) 只覆盖「名字不存在」。
    .env 里写成 REDIS_URL= 时，拿到的是空字符串，不能拿去连接。
    """
    raw = os.environ.get(name)
    if raw is None:
        return fallback
    text = str(raw).strip()
    if text == "":
        return fallback
    return text


def configured_redis_url() -> str:
    load_project_env()
    return configured_text("REDIS_URL", DEFAULT_REDIS_URL)


def configured_ttl() -> int:
    """TTL 在环境变量里也是文本。要先变成整数，Redis 的 EXPIRE 才认。"""
    load_project_env()
    raw = configured_text("STAGE3_SESSION_TTL_SECONDS", str(DEFAULT_TTL_SECONDS))
    try:
        value = int(raw)
    except ValueError:
        print(f"STAGE3_SESSION_TTL_SECONDS={raw} 不是整数，改用 {DEFAULT_TTL_SECONDS}。")
        return DEFAULT_TTL_SECONDS
    if value < 1:
        print(f"STAGE3_SESSION_TTL_SECONDS 需要至少 1 秒，改用 {DEFAULT_TTL_SECONDS}。")
        return DEFAULT_TTL_SECONDS
    return value


def configured_session_id() -> str:
    load_project_env()
    return configured_text("STAGE3_SESSION_ID", "local")


def public_redis_target(url: str) -> str:
    """地址里若带密码，屏幕上不能把它打出来。"""
    if "@" in url:
        return "已隐藏（地址里含有密码）"
    return url


def explain(connected: ConnectedRedis) -> None:
    """告诉学习者这一次的数据会活在哪里。不说明的话，重启后『记不住』会像是程序坏了。"""
    if connected.kind == "redis":
        print("已连接 Redis。键存在另一个进程里，这个程序退出后还在，直到 TTL 到期。")
        print(f"地址：{public_redis_target(connected.detail)}")
        return
    if connected.kind == "fakeredis":
        print("没有使用本机 Redis，改用 fakeredis。")
        print(f"原因：{connected.detail}")
        print("fakeredis 的方法名和 redis-py 一样，所以后面的命令不用改。")
        print("它的数据在这个进程的内存里。程序一退出，键就没了，重启后接不上同一段会话。")
        print("要跨进程记住，请先按 README 启动 Redis，再重新运行。")
        return
    print("没有使用本机 Redis，fakeredis 也不可用，改用 backend.py 里的内存实现。")
    print(f"原因：{connected.detail}")
    print("这份实现只认识本阶段用到的命令，用来让练习在缺少库时仍能跑完。")
    print("数据同样只活在这个进程里。退出程序之后不会留下会话。")


def open_client(prefer_real: bool = True) -> ConnectedRedis:
    """prefer_real 为假时不去碰本机 6379。离线演示要结果稳定，走这条。"""
    if prefer_real:
        connected, reason = _try_real_redis()
        if connected is not None:
            return connected
    else:
        reason = "这一次要求不连接本机 Redis"
    fake = _try_fakeredis(reason)
    if fake is not None:
        return fake
    return ConnectedRedis(
        client=InMemoryRedis(),
        kind="memory",
        detail=reason + "；fakeredis 也没有安装",
    )


def open_fake_server():
    """两个客户端共用一台假的服务器，用来在一个进程里模拟『重新连上』。"""
    import fakeredis

    server = fakeredis.FakeServer()
    client = fakeredis.FakeRedis(server=server, decode_responses=True)
    return server, client


def client_on_fake_server(server):
    import fakeredis

    return fakeredis.FakeRedis(server=server, decode_responses=True)


def _try_real_redis() -> tuple[ConnectedRedis | None, str]:
    url = configured_redis_url()
    shown = public_redis_target(url)
    try:
        import redis
    except ImportError:
        return None, "没有安装 redis 这个库"
    client = None
    try:
        client = redis.Redis.from_url(
            url,
            decode_responses=True,
            socket_connect_timeout=1,
            socket_timeout=1,
        )
        client.ping()
    except Exception as error:
        if client is not None:
            try:
                client.close()
            except Exception:
                # 连都没连上时，close 也可能失败。后面会改用替身，这里不用再抛。
                pass
        return None, f"连接 {shown} 失败：{type(error).__name__}: {error}"
    return ConnectedRedis(client=client, kind="redis", detail=url), ""


def _try_fakeredis(reason: str) -> ConnectedRedis | None:
    try:
        import fakeredis
    except ImportError:
        return None
    client = fakeredis.FakeRedis(decode_responses=True)
    return ConnectedRedis(client=client, kind="fakeredis", detail=reason)


def _deadline(seconds: int | None) -> float | None:
    if seconds is None:
        return None
    return time.time() + int(seconds)


def _inclusive_range(length: int, start: int, end: int) -> tuple[int, int]:
    """Redis 的 LRANGE 两端都包含。Python 切片的右端不包含，所以这里先换算。

    起点已经越过末尾时，交回一对 start > end 的下标，调用方得到空列表。
    """
    if length == 0:
        return 0, -1
    start_index = start if start >= 0 else length + start
    end_index = end if end >= 0 else length + end
    if start_index < 0:
        start_index = 0
    if end_index >= length:
        end_index = length - 1
    if start_index >= length or start_index > end_index:
        return 0, -1
    return start_index, end_index
