# -*- coding: utf-8 -*-
"""阶段 6 · 示例 3：用正则认出四类个人信息，并打码。

练习号码都是假的。打码后再写日志、再送进长期记忆、再送给模型。
订单号 10086 只有 5 位，不应被当成手机号或卡号。

    python stage6_compliance/03_mask_pii.py

导读：stage6_compliance/docs/03_pii.md
"""

import re

from pii import BANK_RE, EMAIL_RE, ID_RE, PHONE_RE, find_phones, mask_text

SAMPLE = (
    "订单号 10086，手机13800138000，"
    "身份证110101199001011234，"
    "另一张证件11010119900307777X，"
    "卡号6222021234567890，"
    "邮箱xinghe@example.com，"
    "密码是abc12345"
)


def main() -> None:
    print("打码前：")
    print(f"  {SAMPLE}")
    print("打码后：")
    print(f"  {mask_text(SAMPLE)}")
    print()
    print("findall 在模式带分组时，交回的是分组而不是整段。")
    print(f"  手机号分组：{re.findall(PHONE_RE, SAMPLE)}")
    print(f"  整段手机号：{find_phones(SAMPLE)}")
    print(f"  身份证分组：{re.findall(ID_RE, SAMPLE)}")
    print(f"  邮箱分组：{re.findall(EMAIL_RE, SAMPLE)}")
    print("银行卡规则如果直接搜原文，18 位身份证也符合「一长串数字」。")
    print(f"  原文上的银行卡分组：{re.findall(BANK_RE, SAMPLE)}")
    without_id = ID_RE.sub(" ", SAMPLE)
    print(f"  先拿掉身份证再找卡号：{re.findall(BANK_RE, without_id)}")
    print()
    print("再打一次码，结果应和第一次相同。日志里可以放心多走一遍。")
    once = mask_text(SAMPLE)
    print(f"  两次相同：{mask_text(once) == once}")
    print()

    print("—— 太宽的正则会误伤订单号 ——")
    wide = re.findall(r"\d+", "订单号 10086")
    print(f"  \\d+ 找到：{wide}")
    print(f"  本课的手机号规则找到：{find_phones('订单号 10086')}")
    print("  10086 不是 11 位手机号，正式规则应交出空列表。")
    print()

    print("—— 太严或没写进模式的形状会漏 ——")
    spaced = "我的手机是 138 0013 8000"
    print(f"  句子：{spaced}")
    print(f"  打码后：{mask_text(spaced)}")
    print("  数字被空格切开，11 位规则对不上。这是漏报。")
    print("  15 位的老身份证同样不在本课的 18 位模式里。")
    print()
    print("打码要发生在写日志、写长期记忆、把句子送给模型之前。")
    print("示例 3 看完了。下一课看提示注入的短语。")


if __name__ == "__main__":
    main()
