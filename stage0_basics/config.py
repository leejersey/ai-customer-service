# -*- coding: utf-8 -*-
"""阶段 0 的公共配置。

四个示例脚本都从这里读取密钥、接口地址和模型名，避免每份代码各写一套。
这个文件被别的脚本 import，一般不要直接运行。
"""

import os
import traceback
from pathlib import Path

# 本文件在 stage0_basics/ 目录里，再往上一级就是仓库根目录（和 README.md、.env 放在一起）。
# 用文件位置拼路径，这样无论你在哪个目录执行 python，都能找到同一个 .env。
PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = PROJECT_ROOT / ".env"

# 和 .env.example 里的默认值保持一致。只有当环境变量没写时才会用到它们。
DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-chat"

# 这些字样出现在密钥里，说明用户还没把 .env.example 里的占位文字换成真实密钥。
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
    """一次调用所需的三项配置。

    用一个对象装起来，是为了函数之间传递时不容易把参数顺序传错。
    打印这个对象时不会带出密钥。
    """

    def __init__(self, api_key: str, base_url: str, model: str) -> None:
        # 三行赋值分别保存：密钥、接口根地址、模型名。
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

    def __repr__(self) -> str:
        # 初学者如果写了 print(settings)，这里保证屏幕上只有掩码，没有密钥本身。
        return (
            f"Settings(base_url={self.base_url!r}, model={self.model!r}, api_key='***')"
        )


def _clean(value: str) -> str:
    """去掉首尾空白；如果整段被引号包住，再去掉一层引号。"""
    # .env 里偶尔会多写一对引号，python-dotenv 通常会处理，这里再防一次。
    text = value.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in {'"', "'"}:
        text = text[1:-1].strip()
    return text


def _is_placeholder(api_key: str) -> bool:
    """判断这串字符是不是模板里的假密钥。"""
    lowered = api_key.lower()
    for marker in _PLACEHOLDER_MARKERS:
        # 标记本身可能是中文，中文用原文比较；英文标记再用小写比较，避免大小写漏网。
        if marker in api_key or marker.lower() in lowered:
            return True
    return False


def _exit_because_package_missing(import_name: str, pip_name: str) -> None:
    """依赖没装好时，用中文说明下一步，而不是只甩出英文追溯。"""
    print("缺少 Python 库，脚本还不能运行。")
    print(f"导入失败的名字：{import_name}")
    print("请先激活虚拟环境（命令行前面通常会出现 (.venv)），再在项目根目录执行：")
    print("    pip install -r requirements.txt")
    print(f"依赖清单里的安装名是：{pip_name}")
    print("完整步骤写在 stage0_basics/README.md。")
    raise SystemExit(1)


def _load_dotenv():
    """导入并返回 load_dotenv。没安装 python-dotenv 时直接退出。"""
    try:
        # 放在函数里导入，是为了把「没装库」变成上面的中文说明。
        from dotenv import load_dotenv
    except ImportError:
        _exit_because_package_missing("dotenv", "python-dotenv")
    return load_dotenv


def _print_missing_key_help(env_file_exists: bool, placeholder: bool) -> None:
    """没有可用密钥时打印可以照着做的短说明。"""
    print("还不能调用大模型：没有可用的 DEEPSEEK_API_KEY。")
    print()
    if not env_file_exists:
        # 最常见的情况：仓库里只有 .env.example，用户还没复制。
        print(f"没有找到配置文件：{ENV_PATH}")
        print("在项目根目录（和 README.md 同一层）执行：")
        print("    cp .env.example .env")
        print("然后打开 .env，把 DEEPSEEK_API_KEY 换成你自己的密钥。")
    elif placeholder:
        print(f"已经找到 {ENV_PATH}，但密钥仍是示例里的占位文字。")
        print("请换成你在 DeepSeek 控制台创建的真实密钥。")
    else:
        print(f"已经找到 {ENV_PATH}，但 DEEPSEEK_API_KEY 是空的。")
        print("请在等号后面填上密钥，等号两边不要加空格。")
    print()
    print("获取密钥：打开 https://platform.deepseek.com 登录，创建一个 API Key。")
    print("密钥只留在你自己的 .env 里。不要提交到 Git，也不要贴到聊天或截图里。")
    print("没有密钥也可以阅读代码和文档；python -m py_compile 检查语法同样不需要密钥。")
    print("详细图文步骤见 stage0_basics/README.md。")


def require_settings() -> Settings:
    """读取配置。密钥缺失或仍是占位符时，打印说明并退出。"""
    load_dotenv = _load_dotenv()
    try:
        # override=False：如果系统环境变量里已经有同名的值，以系统的为准，不拿 .env 覆盖。
        load_dotenv(ENV_PATH, override=False, encoding="utf-8")
    except UnicodeError:
        print(f"{ENV_PATH} 不是 UTF-8 编码，读取失败。")
        print("请用编辑器把 .env 另存为 UTF-8 后再运行。")
        raise SystemExit(1)

    # 三个配置都从环境变量读。load_dotenv 已经把 .env 里的行写进环境变量。
    api_key = _clean(os.environ.get("DEEPSEEK_API_KEY", ""))
    base_url = _clean(os.environ.get("DEEPSEEK_BASE_URL", "")) or DEFAULT_BASE_URL
    model = _clean(os.environ.get("DEEPSEEK_MODEL", "")) or DEFAULT_MODEL

    if not api_key or _is_placeholder(api_key):
        _print_missing_key_help(ENV_PATH.exists(), placeholder=bool(api_key))
        # 退出码 1 表示这次运行没有完成。它不是 Python 崩溃，是我们主动停下来。
        raise SystemExit(1)

    if not (base_url.startswith("https://") or base_url.startswith("http://")):
        print(f"DEEPSEEK_BASE_URL 看起来不对：{base_url}")
        print(f"阶段 0 请使用：{DEFAULT_BASE_URL}")
        raise SystemExit(1)

    return Settings(api_key=api_key, base_url=base_url, model=model)


def describe_settings(settings: Settings) -> None:
    """运行前在屏幕上确认地址和模型。故意不打印密钥。"""
    print(f"接口地址：{settings.base_url}")
    print(f"模型名称：{settings.model}")
    print("API 密钥：已读取，屏幕上不显示。")


def create_client(settings: Settings):
    """用配置创建一个 OpenAI 兼容客户端。创建本身不会联网。"""
    try:
        from openai import OpenAI
    except ImportError:
        _exit_because_package_missing("openai", "openai")

    # timeout：单次请求最多等多少秒。max_retries：遇到网络抖动时额外重试的次数。
    # 重试会让失败时多等一会儿，所以次数只留 1 次，避免初学者以为程序卡死。
    return OpenAI(
        api_key=settings.api_key,
        base_url=settings.base_url,
        timeout=60.0,
        max_retries=1,
    )


def print_api_error(error: BaseException) -> None:
    """把常见 API 异常翻译成中文。本函数不退出，由每个脚本自己决定是停止还是继续聊。"""
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

    # 子类要写在父类前面。例如 AuthenticationError 也是 APIStatusError，
    # 如果先判断父类，后面的分支就永远不会执行。
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
        print("- 这不是典型的 API 拒绝。下面附上详细跟踪，方便对照代码：")
        traceback.print_exc()
    else:
        print("- 这是 SDK 抛出的其他错误。请先阅读上面的原始信息。")
