import json
from pathlib import Path
from bs4 import BeautifulSoup

SITE_ROOT = Path(".")
SEARCH_INDEX = Path("search_index.json")
IP_FOLDER = SITE_ROOT / "ip"

def extract_meta(html_path: Path):
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")

    title = soup.title.string.strip() if soup.title else html_path.stem
    desc_tag = soup.find("meta", attrs={"name": "description"})
    description = desc_tag["content"].strip() if desc_tag else title

    return title, description

def main():
    with SEARCH_INDEX.open("r", encoding="utf-8") as f:
        index = json.load(f)

    existing_urls = {item["url"] for item in index}
    max_id = max(item["id"] for item in index) if index else 0

    added = 0

    for html_file in IP_FOLDER.glob("*.html"):
        url = "/ip/" + html_file.name.replace(".html", "/")

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

    print(f"\n✅ Done. Added {added} IP pages.")

if __name__ == "__main__":
    main()