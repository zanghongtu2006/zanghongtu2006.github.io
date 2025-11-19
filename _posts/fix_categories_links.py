from pathlib import Path
import re

# 根据实际路径调整
ROOT = Path("./_posts")

# 匹配 (categories-xxx) 或 (/categories-xxx)
pattern = re.compile(r"\((/?)categories-([a-zA-Z0-9_-]+)\)")

for md in ROOT.glob("*.md"):
    text = md.read_text(encoding="utf-8")
    new_text, n = pattern.subn(r"(/categories/#\2)", text)
    if n:
        print(f"{md} -> fixed {n} link(s)")
        md.write_text(new_text, encoding="utf-8")

print("done.")
