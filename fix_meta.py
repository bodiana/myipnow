#!/usr/bin/env python3
import os
import re
import time
import anthropic

pages_dir = '/var/www/html'
DELAY = 1.0
MODEL = "claude-haiku-4-5-20251001"

# Skip these pages
SKIP = {'about.html', 'contact.html', 'privacy-policy.html', 'terms-of-use.html',
        'affiliate-disclosure.html', 'article_template.html', 'search.html', '404.html'}

PROMPT = """Generate a unique SEO title and meta description for this webpage.

Page slug: {slug}

Rules:
- Title: max 60 characters, compelling, includes main keyword naturally, no "| MyIPNow" yet
- Description: max 155 characters, answers what the page is about, includes a benefit or fact
- Do NOT use generic phrases like "fast, accurate, privacy-focused"
- Make it specific to the topic
- Return ONLY in this exact format:
TITLE: your title here | MyIPNow
DESC: your description here"""

def fix_file(client, filepath, slug):
    with open(filepath, 'r') as f:
        content = f.read()

    message = client.messages.create(
        model=MODEL,
        max_tokens=300,
        messages=[{"role": "user", "content": PROMPT.format(slug=slug.replace('-', ' ').replace('.html', ''))}]
    )

    result = message.content[0].text.strip()
    title_match = re.search(r'TITLE: (.+)', result)
    desc_match = re.search(r'DESC: (.+)', result)

    if not title_match or not desc_match:
        print(f"  SKIP (bad response): {slug}")
        return False

    new_title = title_match.group(1).strip()
    new_desc = desc_match.group(1).strip()

    # Get current title to replace
    current_title_match = re.search(r'<title>([^<]+)</title>', content)
    if not current_title_match:
        print(f"  SKIP (no title): {slug}")
        return False

    current_title = current_title_match.group(1)

    # Replace title
    content = content.replace(f'<title>{current_title}</title>', f'<title>{new_title}</title>')

    # Replace og:title
    content = re.sub(r'content="[^"]*" property="og:title"',
                     f'content="{new_title}" property="og:title"', content)

    # Replace description
    content = re.sub(r'content="[^"]*Fast, accurate and privacy-focused[^"]*" name="description"',
                     f'content="{new_desc}" name="description"', content)

    # Replace og:description
    content = re.sub(r'content="[^"]*Fast, accurate and privacy-focused[^"]*" property="og:description"',
                     f'content="{new_desc}" property="og:description"', content)

    with open(filepath, 'w') as f:
        f.write(content)

    return new_title

def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: export ANTHROPIC_API_KEY=your_key_here")
        return

    client = anthropic.Anthropic(api_key=api_key)

    files = []
    for f in os.listdir(pages_dir):
        if f.endswith('.html') and f not in SKIP:
            path = os.path.join(pages_dir, f)
            with open(path, 'r') as fh:
                if 'Fast, accurate and privacy-focused' in fh.read():
                    files.append(f)

    files = sorted(files)
    print(f"Fixing {len(files)} pages\n")

    for i, filename in enumerate(files, 1):
        filepath = os.path.join(pages_dir, filename)
        slug = filename.replace('.html', '')
        print(f"[{i}/{len(files)}] {slug} ... ", end="", flush=True)
        result = fix_file(client, filepath, slug)
        if result:
            print(f"OK: {result[:50]}")
        time.sleep(DELAY)

    print("\nDone!")

if __name__ == "__main__":
    main()
