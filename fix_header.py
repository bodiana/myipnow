import os
import re
from bs4 import BeautifulSoup

BASE_URL = "https://myipnow.net"
SITE_NAME = "MyIPNow"

SITE_FOLDER = r"C:\Users\Bodia\OneDrive\Робочий стіл\myipnow-main"


# ---------- helpers ----------

def clean_text(text):
    return re.sub(r"\s+", " ", text.strip())


def build_description(text):
    text = clean_text(text)
    if len(text) > 155:
        text = text[:155].rsplit(" ", 1)[0]
    return text


def remove_old_seo(soup):
    for tag in soup.find_all(["title", "meta"]):
        if tag is None:
            continue

        if tag.name == "title":
            tag.decompose()
            continue

        name = tag.get("name")
        prop = tag.get("property")

        if name in ["description"]:
            tag.decompose()

        if prop in ["og:title", "og:description", "og:url"]:
            tag.decompose()


def is_article_page(file_path, root_folder):
    rel = os.path.relpath(file_path, root_folder).replace("\\", "/")

    # Must be /folder/index.html (article)
    if not rel.endswith("index.html"):
        return False

    # Skip main root index
    if rel == "index.html":
        return False

    # Ensure it's inside a folder (article slug)
    if "/" not in rel:
        return False

    return True


def process_article(file_path, root_folder):
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    if not soup.head:
        return

    # --- extract article title from H1 ---
    h1 = soup.find("h1")
    if not h1:
        return

    title_text = clean_text(h1.get_text())
    if not title_text:
        return

    full_title = f"{title_text} | {SITE_NAME}"

    # --- description from first paragraph ---
    first_p = soup.find("article")
    if first_p:
        first_p = first_p.find("p")

    if first_p:
        desc = build_description(first_p.get_text())
    else:
        desc = f"{title_text}. Learn more with {SITE_NAME}. Accurate, fast, and privacy-focused internet tools."

    # --- URL ---
    rel = os.path.relpath(file_path, root_folder).replace("\\", "/")
    slug = rel.replace("index.html", "").rstrip("/")
    url = f"{BASE_URL}/{slug}"

    # --- remove broken / duplicate SEO ---
    remove_old_seo(soup)

    # --- TITLE ---
    title_tag = soup.new_tag("title")
    title_tag.string = full_title
    soup.head.append(title_tag)

    # --- META DESCRIPTION ---
    meta_desc = soup.new_tag("meta", attrs={"name": "description", "content": desc})
    soup.head.append(meta_desc)

    # --- OG TITLE ---
    og_title = soup.new_tag("meta", attrs={"property": "og:title", "content": full_title})
    soup.head.append(og_title)

    # --- OG DESCRIPTION ---
    og_desc = soup.new_tag("meta", attrs={"property": "og:description", "content": desc})
    soup.head.append(og_desc)

    # --- OG URL ---
    og_url = soup.new_tag("meta", attrs={"property": "og:url", "content": url})
    soup.head.append(og_url)

    # --- Save ---
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(str(soup))

    print("✔ Fixed article:", slug)


def scan_site(root_folder):
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            if not file.endswith(".html"):
                continue

            full_path = os.path.join(root, file)

            if is_article_page(full_path, root_folder):
                process_article(full_path, root_folder)


# ---------- RUN ----------
scan_site(SITE_FOLDER)

print("\nDONE. Only article pages were fixed.")
