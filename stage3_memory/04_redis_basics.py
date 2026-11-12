# -*- coding: utf-8 -*-
"""阶段 3 · 示例 4：Redis 的字符串、过期、列表和哈希。

本机 6379 连得上就用 Redis。连不上就用 fakeredis，并在屏幕上说明原因。
两种客户端的方法名相同，下面的命令不用改。

    python stage3_memory/04_redis_basics.py

导读：stage3_memory/docs/04_redis.md
"""

from backend import explain, open_client

# 只碰这几个键。不要 FLUSHDB，那会删掉这台 Redis 里别人的数据。
DEMO_KEYS = (
    "stage3:demo:greeting",
    "stage3:demo:temp",
    "stage3:demo:turns",
    "stage3:demo:slots",
)


def main() -> None:
    connected = open_client(prefer_real=True)
    explain(connected)
    client = connected.client
    print()
    for key in DEMO_KEYS:
        client.delete(key)

    print("== SET / GET ==")
    client.set("stage3:demo:greeting", "你好，我是小星")
    print("GET greeting =", client.get("stage3:demo:greeting"))
    print("GET 不存在的键 =", client.get("stage3:demo:missing"))
    print("不存在时得到 None，不会抛出 KeyError。")
    print()

    print("== EXPIRE / TTL ==")
    client.set("stage3:demo:temp", "马上会过期", ex=30)
    print("带 ex=30 写入之后，TTL =", client.ttl("stage3:demo:temp"))
    client.set("stage3:demo:greeting", "没有过期时间")
    print("没设过期时，TTL =", client.ttl("stage3:demo:greeting"), "（-1 表示一直留着）")
    client.expire("stage3:demo:greeting", 30)
    print("再 EXPIRE 30 秒，TTL =", client.ttl("stage3:demo:greeting"))
    print("TTL = -2 表示键已经不在。这一课不干等它过期，离线演示会用 1 秒的 TTL 把它等掉。")
    print()

    print("== LIST：RPUSH / LRANGE / LTRIM ==")
    client.rpush("stage3:demo:turns", "user：我要退款", "assistant：请给订单号")
    client.rpush("stage3:demo:turns", "user：订单号 10086")
    print("全部 =", client.lrange("stage3:demo:turns", 0, -1))
    print("最近 2 条 =", client.lrange("stage3:demo:turns", -2, -1))
    client.ltrim("stage3:demo:turns", -2, -1)
    print("LTRIM 只留最近 2 条之后 =", client.lrange("stage3:demo:turns", 0, -1))
    print("RPUSH 加在右边，所以越新的越靠近末尾。最近 N 条用负数下标，不用先数长度。")
    print()

    print("== HASH ==")
    client.hset(
        "stage3:demo:slots",
        mapping={"intent": "退款", "order_id": "10086", "ticket_id": "1"},
    )
    print("HGET order_id =", client.hget("stage3:demo:slots", "order_id"))
    print("HGETALL =", client.hgetall("stage3:demo:slots"))
    print("HASH 适合『一个会话的好几格』。改订单号不用把整段对话重新写一遍。")
    print()

    for key in DEMO_KEYS:
        client.expire(key, 120)
    print("上面这些演示键大约 120 秒后过期。")
    print("短期记忆放 Redis，是因为另一个进程、另一次启动还能读到，并且空闲久了会自己消失。")
    if connected.kind != "redis":
        print("这一次的键不在本机 Redis 里。redis-cli 看不到它们。")
    client.close()


if __name__ == "__main__":
    main()
