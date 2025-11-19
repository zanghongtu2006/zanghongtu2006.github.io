from pathlib import Path
from slugify import slugify
import yaml

ROOT = Path(__file__).resolve().parent
POSTS_DIR = ROOT / "_posts"
DATA_DIR = ROOT / "_data"
DATA_DIR.mkdir(exist_ok=True)

def normalize_categories(raw):
    if raw is None:
        return []
    if isinstance(raw, list):
        return [str(c).strip() for c in raw if str(c).strip()]
    if isinstance(raw, str):
        parts = [p.strip() for p in raw.split(",")]
        return [p for p in parts if p]
    return []

def collect_categories():
    """
    返回 dict: { 分类名(含中文) -> slug(ASCII, 用于 URL) }
    """
    name_to_slug = {}

    for md in POSTS_DIR.glob("*.md"):
        text = md.read_text(encoding="utf-8", errors="ignore")

        if not text.lstrip().startswith("---"):
            continue

        try:
            parts = text.split("---", 2)
            if len(parts) < 3:
                continue
            fm_text = parts[1]
            data = yaml.safe_load(fm_text) or {}
        except Exception as e:
            print(f"[WARN] front-matter 解析失败: {md} -> {e}")
            continue

        cats = normalize_categories(data.get("categories"))
        for c in cats:
            if c not in name_to_slug:
                # 这里用 Python 的 slugify，对中文会转拼音
                name_to_slug[c] = slugify(c)

    return name_to_slug

def generate_category_pages(name_to_slug):
    for name, slug in name_to_slug.items():
        filename = ROOT / f"categories-{slug}.md"
        if filename.exists():
            print(f"[SKIP] {filename.name} 已存在，跳过")
            continue

        permalink = f"/categories-{slug}"

        fm = (
            "---\n"
            "layout: category_index\n"
            f"title: {name}\n"
            f"category: {name}\n"
            f"permalink: {permalink}\n"
            "---\n"
        )

        filename.write_text(fm, encoding="utf-8")
        print(f"[OK] 生成分类页: {filename.name}  →  {permalink}  （分类名: {name}）")

def write_category_slugs(name_to_slug):
    """
    生成 _data/category_slugs.yml，让 Jekyll 模板能查到每个分类对应的 slug
    """
    data_file = DATA_DIR / "category_slugs.yml"
    with data_file.open("w", encoding="utf-8") as f:
        yaml.dump(
            name_to_slug,
            f,
            allow_unicode=True,
            default_flow_style=False
        )
    print(f"[OK] 写入分类映射表: {data_file}")

def main():
    if not POSTS_DIR.exists():
        print(f"_posts 目录不存在: {POSTS_DIR}")
        return

    cats = collect_categories()
    print(f"共发现 {len(cats)} 个分类: {list(cats.keys())}")

    generate_category_pages(cats)
    write_category_slugs(cats)

if __name__ == "__main__":
    main()
