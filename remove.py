import os
from bs4 import BeautifulSoup

# Path to your backup
ROOT_DIR = r"C:\Users\Bodia\OneDrive\Робочий стіл\myipnow-main-17.10"

# Get all article folders in order (sorted by name or your preferred logic)
article_folders = sorted([f for f in os.listdir(ROOT_DIR) if os.path.isdir(os.path.join(ROOT_DIR, f))])

# Create mapping for next/previous
for i, folder in enumerate(article_folders):
    folder_path = os.path.join(ROOT_DIR, folder, "index.html")
    if not os.path.exists(folder_path):
        continue

    with open(folder_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Find pagination links
    pag_div = soup.find("div", class_="article-pagination")
    if not pag_div:
        continue

    # Previous article
    prev_a = pag_div.find("a", string=lambda t: t and "Previous Article" in t)
    if prev_a and i > 0:
        prev_a["href"] = f"/{article_folders[i-1]}/"

    # Next article
    next_a = pag_div.find("a", string=lambda t: t and "Next Article" in t)
    if next_a and i < len(article_folders)-1:
        next_a["href"] = f"/{article_folders[i+1]}/"

    # Save changes
    with open(folder_path, "w", encoding="utf-8") as f:
        f.write(str(soup))

print("✅ Next/Previous article links updated for all articles.")
