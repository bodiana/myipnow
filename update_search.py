import json
from pathlib import Path
from bs4 import BeautifulSoup

# ===== CONFIG =====
SITE_ROOT = Path(".")              # where HTML files live
SEARCH_INDEX = Path("search_index.json")
IGNORE_FILES = {
    "index.html",
    "404.html"
}
# ==================

def html_to_url(path: Path) -> str:
    return "/" + path.relative_to(SITE_ROOT).as_posix()

def extract_meta(html_path: Path):
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")

    title = soup.title.string.strip() if soup.title else html_path.stem
    desc_tag = soup.find("meta", attrs={"name": "description"})
    description = desc_tag["content"].strip() if desc_tag else title

    return title, description

def main():
    # Load existing index
    with SEARCH_INDEX.open("r", encoding="utf-8") as f:
        index = json.load(f)

    existing_urls = {item["url"] for item in index}
    max_id = max(item["id"] for item in index) if index else 0

    added = 0

    for html_file in SITE_ROOT.rglob("*.html"):
        if html_file.name in IGNORE_FILES:
            continue

        url = html_to_url(html_file)

        if url in existing_urls:
            continue

        title, description = extract_meta(html_file)

        max_id += 1
        index.append({
            "id": max_id,
            "title": title,
            "url": url,
            "content": description
        })

        added += 1
        print(f"➕ Added: {url}")

    with SEARCH_INDEX.open("w", encoding="utf-8") as f:
        json.dump(index, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Done. Added {added} new pages.")

if __name__ == "__main__":
    main()
