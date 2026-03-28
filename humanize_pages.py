#!/usr/bin/env python3
import os
import time
import shutil
import re
import anthropic
from pathlib import Path
from bs4 import BeautifulSoup

PAGES_DIR = "/var/www/html"
BACKUP_DIR = "/var/www/html/backups"
SITEMAP_FILE = "/var/www/html/sitemap.xml"
LOG_FILE = "/var/www/html/humanize_log.txt"
DELAY = 2.0
MODEL = "claude-haiku-4-5-20251001"

HUMANIZE_PROMPT = """Rewrite the text in this HTML to sound like a real person wrote it.

IMPORTANT:
- Keep every HTML tag, attribute, URL, class name, href exactly as-is
- Only change the words between tags
- Do NOT touch FAQ questions or answers
- Do NOT wrap output in backticks or markdown
- Return ONLY the raw HTML

Writing style:
- Conversational, like explaining to a colleague
- Use contractions: don't, it's, you'll, can't
- Short sentences. Mix in longer ones.
- Start sentences with But, And, So when natural
- Say things like "Honestly", "Here's the thing", "In reality"
- Never use: crucial, delve, comprehensive, furthermore, moreover, utilize, leverage, robust, seamless, it's worth noting

HTML:
{content}"""

def get_pages_from_sitemap():
    with open(SITEMAP_FILE, "r") as f:
        content = f.read()
    urls = re.findall(r'<loc>https://myipnow\.net/([^<]+)/</loc>', content)
    pages = []
    for slug in urls:
        if slug.startswith("ip/") or slug == "":
            continue
        slug = slug.rstrip("/")
        flat = os.path.join(PAGES_DIR, slug + ".html")
        folder = os.path.join(PAGES_DIR, slug, "index.html")
        if os.path.exists(flat):
            pages.append(flat)
        elif os.path.exists(folder):
            pages.append(folder)
    return pages

def rewrite_content(client, html_content):
    message = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        messages=[{"role": "user", "content": HUMANIZE_PROMPT.format(content=html_content)}]
    )
    text = message.content[0].text.strip()
    text = re.sub(r'^```html\s*', '', text)
    text = re.sub(r'^```\s*', '', text)
    text = re.sub(r'\s*```$', '', text)
    return text.strip()

def get_content(soup):
    return (
        soup.find(class_="article-body") or
        soup.find(class_="guide-content") or
        soup.find("article") or
        soup.find("main")
    )

def process_file(client, filepath, log):
    filename = os.path.basename(filepath)

    with open(filepath, "r", encoding="utf-8") as f:
        original_html = f.read()

    soup = BeautifulSoup(original_html, "html.parser")
    content_el = get_content(soup)

    if not content_el:
        msg = f"SKIP (no content): {filename}"
        print(msg); log.write(msg + "\n")
        return False

    content_html = str(content_el)

    if len(content_html) < 300:
        msg = f"SKIP (too short): {filename}"
        print(msg); log.write(msg + "\n")
        return False

    shutil.copy2(filepath, os.path.join(BACKUP_DIR, filename))

    try:
        rewritten = rewrite_content(client, content_html)
        new_html = original_html.replace(content_html, rewritten)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_html)
        msg = f"OK: {filename}"
        print(msg); log.write(msg + "\n")
        return True
    except Exception as e:
        msg = f"ERROR: {filename} — {e}"
        print(msg); log.write(msg + "\n")
        shutil.copy2(os.path.join(BACKUP_DIR, filename), filepath)
        return False

def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: export ANTHROPIC_API_KEY=your_key_here")
        return

    client = anthropic.Anthropic(api_key=api_key)
    os.makedirs(BACKUP_DIR, exist_ok=True)

    pages = get_pages_from_sitemap()
    print(f"Found {len(pages)} pages\n")

    processed = skipped = errors = 0

    with open(LOG_FILE, "w") as log:
        log.write(f"Humanize run — {len(pages)} pages\n\n")
        for i, filepath in enumerate(pages, 1):
            print(f"[{i}/{len(pages)}] ", end="", flush=True)
            result = process_file(client, filepath, log)
            if result is True:
                processed += 1
                time.sleep(DELAY)
            elif result is False:
                skipped += 1
            else:
                errors += 1

    print(f"\nDone!")
    print(f"  Processed: {processed}")
    print(f"  Skipped:   {skipped}")
    print(f"  Errors:    {errors}")
    print(f"  Cost:      ~${processed * 0.002:.2f}")

if __name__ == "__main__":
    main()
