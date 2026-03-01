import os
import re
import json

# === CONFIG ===
BASE_DOMAIN = "https://myipnow.net"
ROOT_FOLDER = r"C:\Users\Bodia\OneDrive\Робочий стіл\myipnow-main"

def ensure_trailing_slash(url):
    if url.startswith(BASE_DOMAIN) and not url.endswith("/"):
        return url + "/"
    return url

def fix_html_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # ----------------------------
    # Fix Canonical Tag
    # ----------------------------
    def fix_canonical(match):
        url = match.group(1)
        return f'<link rel="canonical" href="{ensure_trailing_slash(url)}"/>'

    content = re.sub(
        r'<link\s+rel="canonical"\s+href="([^"]+)"\s*/?>',
        fix_canonical,
        content
    )

    # ----------------------------
    # Fix og:url
    # ----------------------------
    def fix_og(match):
        url = match.group(1)
        return f'<meta property="og:url" content="{ensure_trailing_slash(url)}"/>'

    content = re.sub(
        r'<meta\s+property="og:url"\s+content="([^"]+)"\s*/?>',
        fix_og,
        content
    )

    # ----------------------------
    # Fix JSON-LD URLs
    # ----------------------------
    def fix_json_ld(match):
        try:
            data = json.loads(match.group(1))
        except:
            return match.group(0)

        def recursive_fix(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k == "url" and isinstance(v, str):
                        obj[k] = ensure_trailing_slash(v)
                    else:
                        recursive_fix(v)
            elif isinstance(obj, list):
                for item in obj:
                    recursive_fix(item)

        recursive_fix(data)

        fixed_json = json.dumps(data, ensure_ascii=False)
        return f'<script type="application/ld+json">{fixed_json}</script>'

    content = re.sub(
        r'<script type="application/ld\+json">(.*?)</script>',
        fix_json_ld,
        content,
        flags=re.DOTALL
    )

    # ----------------------------
    # Fix broken <pto> tag
    # ----------------------------
    content = re.sub(r'<pto[^>]*>', '<p>', content)

    # Save only if changed
    if content != original_content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Fixed: {filepath}")
    else:
        print(f"No change: {filepath}")

def scan_folder(folder):
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.endswith(".html"):
                fix_html_file(os.path.join(root, file))

if __name__ == "__main__":
    scan_folder(ROOT_FOLDER)
    print("Done.")