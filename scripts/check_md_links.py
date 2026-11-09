#!/usr/bin/env python3
"""检查仓库里 Markdown 的相对链接：文件要存在，#锚点要对得上标题。"""

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)]+)\)|!\[[^\]]*\]\(([^)]+)\)")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$", re.MULTILINE)
FENCE = re.compile(r"^```.*?^```", re.MULTILINE | re.DOTALL)


def strip_fences(text):
    return FENCE.sub("", text)


def slugify(text):
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = text.strip().lower().replace(" ", "-")
    return re.sub(r"[^\w\-]", "", text, flags=re.UNICODE)


def headings(text):
    found = []
    for match in HEADING.finditer(strip_fences(text)):
        found.append(slugify(match.group(2)))
    return found


def destinations(text):
    for match in LINK.finditer(strip_fences(text)):
        raw = match.group(1) or match.group(2)
        raw = raw.strip()
        if raw.startswith("<") and raw.endswith(">"):
            raw = raw[1:-1].strip()
        yield raw


def main():
    broken = []
    checked = 0
    files = sorted(path for path in ROOT.rglob("*.md") if ".git" not in path.parts)
    cache = {}

    def load(path):
        if path not in cache:
            cache[path] = path.read_text(encoding="utf-8")
        return cache[path]

    for md in files:
        for raw in destinations(load(md)):
            if raw.startswith(("http://", "https://", "mailto:")):
                continue
            checked += 1
            path_part, _, fragment = raw.partition("#")
            path_part = unquote(path_part)
            target = (md.parent / path_part).resolve() if path_part else md.resolve()
            try:
                target.relative_to(ROOT)
            except ValueError:
                broken.append(f"{md.relative_to(ROOT)}: 链接跑出仓库 {raw}")
                continue
            if not target.is_file():
                broken.append(f"{md.relative_to(ROOT)}: 找不到文件 {raw}")
                continue
            if fragment and target.suffix.lower() == ".md":
                if slugify(unquote(fragment)) not in headings(load(target)):
                    broken.append(f"{md.relative_to(ROOT)}: 找不到标题 #{fragment} ← {raw}")

    if broken:
        print(f"检查了 {checked} 条相对链接，{len(broken)} 条失效：")
        for item in broken:
            print(item)
        return 1
    print(f"检查了 {checked} 条相对链接，全部指向存在的文件。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
