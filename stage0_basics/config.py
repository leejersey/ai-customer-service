# -*- coding: utf-8 -*-
"""阶段 0 的公共配置。

四个脚本都要读密钥。如果各写一套，漏改一个脚本就会连到错误的地址。
本文件只准备配置和客户端，不负责把问题发给模型。

教程：stage0_basics/docs/00_config.md
"""

import os
import traceback
from pathlib import Path

# 按这个文件的位置找项目根目录，而不是按你执行命令时的当前目录。
# 否则在 stage0_basics 里运行脚本时，会去错误的地方找 .env。
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"

# 只在 .env 和环境变量都没写时使用。和 .env.example 保持一致，避免两处默认值悄悄分叉。
DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-chat"

# 用来认出「人把模板抄过来了，但还没换成自己的密钥」。
# 这种字符串如果真的拿去请求，只会得到一串难懂的 401。
_PLACEHOLDER_MARKERS = (
    "在这里",
    "粘贴你的",
    "替换成",
    "your_api_key",
    "your-api-key",
    "sk-your",
    "changeme",
)


class Settings:
    """把一次调用要用的三项配置捆在一起。

    分开传三个字符串时，调用的人容易把地址和模型名的位置写反。
    打印这个对象时不能带出密钥，所以下面单独写了 __repr__。
    """

    def __init__(self, api_key: str, base_url: str, model: str) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

    def __repr__(self) -> str:
        # 学习者常会 print(settings) 来排查。默认打印会把密钥一起带出来。
        return (
            f"Settings(base_url={self.base_url!r}, model={self.model!r}, api_key='***')"
        )


def _clean(value: str) -> str:
    """清掉复制密钥时容易带上的空白和一层引号。"""
    text = value.strip()
    # python-dotenv 通常会去掉引号。这里再防一次，是因为有人会在系统环境变量里写成带引号的字符串。
    if len(text) >= 2 and text[0] == text[-1] and text[0] in {'"', "'"}:
        text = text[1:-1].strip()
    return text


def _is_placeholder(api_key: str) -> bool:
    """模板里的假密钥不能拿去请求。"""
    lowered = api_key.lower()
    for marker in _PLACEHOLDER_MARKERS:
        # 中文标记大小写不会变；英文标记要忽略大小写，否则 Your_API_Key 会漏过去。
        if marker in api_key or marker.lower() in lowered:
            return True
    return False


def _exit_because_package_missing(import_name: str, pip_name: str) -> None:
    """缺库时告诉人下一步，而不是先抛出一段英文追溯。"""
    print("缺少 Python 库，脚本还不能运行。")
    print(f"导入失败的名字：{import_name}")
    print("请先激活虚拟环境（命令行前面通常会出现 (.venv)），再在项目根目录执行：")
    print("    pip install -r requirements.txt")
    print(f"依赖清单里的安装名是：{pip_name}")
    print("完整步骤写在 stage0_basics/README.md。")
    raise SystemExit(1)


def _load_dotenv():
    """延后导入 dotenv，这样「没安装」能走我们自己的中文说明。"""
    try:
        from dotenv import load_dotenv
    except ImportError:
        _exit_because_package_missing("dotenv", "python-dotenv")
    return load_dotenv


def _print_missing_key_help(env_file_exists: bool, placeholder: bool) -> None:
    """按「假密钥」和「根本没有文件」分开提示，两种失败的下一步不一样。"""
    print("还不能调用大模型：没有可用的 DEEPSEEK_API_KEY。")
    print()
    if placeholder:
        # 先判断占位符。否则人已经在环境变量里导出了示例文字时，会误以为只是没找到文件。
        if env_file_exists:
            print(f"已经找到 {ENV_PATH}，但密钥仍是示例里的占位文字。")
        else:
            print("当前读到的 DEEPSEEK_API_KEY 仍是示例里的占位文字。")
        print("请换成你在 DeepSeek 控制台创建的真实密钥。")
    elif not env_file_exists:
        print(f"没有找到配置文件：{ENV_PATH}")
        print("在项目根目录（和 README.md 同一层）执行：")
        print("    cp .env.example .env")
        print("Windows 命令提示符可以改用：copy .env.example .env")
        print("然后打开 .env，把 DEEPSEEK_API_KEY 换成你自己的密钥。")
    else:
        print(f"已经找到 {ENV_PATH}，但 DEEPSEEK_API_KEY 是空的。")
        print("请在等号后面填上密钥，等号两边不要加空格。")
    print()
    print("获取密钥：打开 https://platform.deepseek.com 登录，创建一个 API Key。")
    print("密钥只留在你自己的 .env 里。不要提交到 Git，也不要贴到聊天或截图里。")
    print("没有密钥也可以阅读代码和文档；python -m py_compile 检查语法同样不需要密钥。")
    print("详细步骤见 stage0_basics/README.md。")


def require_settings() -> Settings:
    """读配置。密钥不能用时停下来，不要带着空密钥继续往下走。"""
    load_dotenv = _load_dotenv()
    try:
        # 系统环境变量优先于文件。这样临时 export 一个密钥做实验时，不会被旧的 .env 盖回去。
        load_dotenv(ENV_PATH, override=False, encoding="utf-8")
    except UnicodeError:
        print(f"{ENV_PATH} 不是 UTF-8 编码，读取失败。")
        print("请用编辑器把 .env 另存为 UTF-8 后再运行。")
        raise SystemExit(1)

    api_key = _clean(os.environ.get("DEEPSEEK_API_KEY", ""))
    base_url = _clean(os.environ.get("DEEPSEEK_BASE_URL", "")) or DEFAULT_BASE_URL
    model = _clean(os.environ.get("DEEPSEEK_MODEL", "")) or DEFAULT_MODEL

    if not api_key or _is_placeholder(api_key):
        _print_missing_key_help(ENV_PATH.exists(), placeholder=bool(api_key))
        # 主动结束并返回失败码。如果这里只打印、不退出，后面的脚本仍会去调用接口。
        raise SystemExit(1)

    if not (base_url.startswith("https://") or base_url.startswith("http://")):
        print(f"DEEPSEEK_BASE_URL 看起来不对：{base_url}")
        print(f"阶段 0 请使用：{DEFAULT_BASE_URL}")
        raise SystemExit(1)

    return Settings(api_key=api_key, base_url=base_url, model=model)


def describe_settings(settings: Settings) -> None:
    """运行前让人核对地址和模型。故意不打印密钥。"""
    print(f"接口地址：{settings.base_url}")
    print(f"模型名称：{settings.model}")
    print("API 密钥：已读取，屏幕上不显示。")


def create_client(settings: Settings):
    """准备一个可复用的客户端。这一步不联网，也不会产生费用。"""
    try:
        from openai import OpenAI
    except ImportError:
        _exit_because_package_missing("openai", "openai")

    # 失败时 SDK 还会再试一次，所以人会觉得「卡住了」。次数留 1，避免排错时干等。
    return OpenAI(
        api_key=settings.api_key,
        base_url=settings.base_url,
        timeout=60.0,
        max_retries=1,
    )


def print_api_error(error: BaseException) -> None:
    """把常见的接口失败翻译成下一步。不在这里退出，让聊天循环自己决定要不要继续。"""
    print()
    print("调用模型 API 失败。")
    print(f"错误类型：{type(error).__name__}")
    print(f"原始信息：{error}")
    print("可以这样处理：")

    try:
        from openai import (
            APIConnectionError,
            APIStatusError,
            APITimeoutError,
            AuthenticationError,
            BadRequestError,
            InternalServerError,
            NotFoundError,
            OpenAIError,
            PermissionDeniedError,
            RateLimitError,
        )
    except ImportError:
        print("- openai 库没有安装。请先执行 pip install -r requirements.txt。")
        return

    # 更具体的错误必须写在更笼统的前面。
    # AuthenticationError 同时也是 APIStatusError；如果先判断父类，401 会被说成含糊的「服务器返回了错误」。
    if isinstance(error, AuthenticationError):
        print("- 密钥被拒绝了。常见原因是复制漏了字符、多了空格，或仍在使用别人的示例密钥。")
        print("- 打开 .env，重新粘贴 DEEPSEEK_API_KEY，保存后再运行。")
        print("- 确认这是 DeepSeek 的密钥，不是 OpenAI 的密钥。")
    elif isinstance(error, PermissionDeniedError):
        print("- 密钥没有权限调用这个接口。请到 DeepSeek 控制台确认密钥是否被停用。")
    elif isinstance(error, RateLimitError):
        print("- 请求太频繁，或账户额度暂时用尽。等一会儿再试。")
        print("- 也可以到 https://platform.deepseek.com 查看余额和限流说明。")
    elif isinstance(error, NotFoundError):
        print("- 地址或模型名可能不对。")
        print(f"- DEEPSEEK_BASE_URL 保持 {DEFAULT_BASE_URL}")
        print("- 如果原始信息提到 model，把 .env 里的 DEEPSEEK_MODEL 改成 deepseek-flash 后再试。")
    elif isinstance(error, BadRequestError):
        print("- 服务器认为请求不合法。先看原始信息里有没有提到 model 或 messages。")
        print("- 模型名不可用时，只改 .env 的 DEEPSEEK_MODEL 为 deepseek-flash，代码不用改。")
    elif isinstance(error, InternalServerError):
        print("- 对方服务器暂时出错。这通常不是你的脚本写错了，等一分钟再试。")
    elif isinstance(error, APITimeoutError):
        print("- 等了太久还没有结果。检查网络后重试。")
    elif isinstance(error, APIConnectionError):
        print("- 网络没有连上 API。请检查网络、代理或防火墙。")
        print(f"- 确认 DEEPSEEK_BASE_URL 是 {DEFAULT_BASE_URL}")
        print("- 不要把完整的 /chat/completions 路径写进 base_url，SDK 会自己拼接。")
    elif isinstance(error, APIStatusError):
        status_code = getattr(error, "status_code", None)
        if status_code == 402:
            print("- 账户余额不足（HTTP 402）。请到 DeepSeek 控制台查看余额。")
        else:
            print(f"- 服务器返回了 HTTP {status_code}。可以稍后重试。")
    elif not isinstance(error, OpenAIError):
        # 不是接口拒绝时，中文说明不够用，需要调用栈才能对照是哪一行自己写错了。
        print("- 这不是典型的 API 拒绝。下面附上详细跟踪，方便对照代码：")
        traceback.print_exc()
    else:
        print("- 这是 SDK 抛出的其他错误。请先阅读上面的原始信息。")
