import os
from bs4 import BeautifulSoup

# Root directory
BASE_DIR = r"C:\Users\Bodia\OneDrive\Робочий стіл\myipnow-main-17.10"

# Category folders to skip
CATEGORY_FOLDERS = [
    "online-safety",
    "online-privacy",
    "networking",
    "ip-addresses",
    "home-computing",
    "general-topics"
]

# Collect all article folders (everything that’s not a category folder)
article_folders = [
    f for f in os.listdir(BASE_DIR)
    if os.path.isdir(os.path.join(BASE_DIR, f)) and f not in CATEGORY_FOLDERS
]

def fix_related_links(article_folder):
    file_path = os.path.join(BASE_DIR, article_folder, "index.html")
    if not os.path.exists(file_path):
        print(f"Skipped (no index.html): {article_folder}")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    related_section = soup.find("div", class_="related-articles")
    if not related_section:
        print(f"No related-articles section found in {article_folder}")
        return

    links = related_section.find_all("a", href=True)
    for link in links:
        text = link.text.strip().lower().replace(" ", "-").replace("’", "").replace("'", "")
        # Clean punctuation for better match with folder names
        text = "".join(c for c in text if c.isalnum() or c == "-")

        # Try to find the matching folder
        match = next((f for f in article_folders if text.startswith(f.lower()[:20])), None)
        if match:
            link["href"] = f"/{match}/"
        else:
            print(f"⚠️ No match for link '{link.text}' in {article_folder}")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(str(soup))
    print(f"✅ Updated related articles in {article_folder}")

# Process each article folder
for folder in article_folders:
    fix_related_links(folder)

print("\n✅ Done! All related article paths updated correctly.")
