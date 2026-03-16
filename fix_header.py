import os
import re

FOLDER_PATH = r"C:\Users\Bodia\OneDrive\Робочий стіл\myipnow-main"
SITE_DOMAIN = "https://myipnow.net"

# Regex patterns
canonical_pattern = re.compile(r'(<link\s+rel=["\']canonical["\']\s+href=["\'])(https://myipnow\.net[^"\']*?)(["\'])', re.IGNORECASE)
url_pattern = re.compile(r'((?:href|src)=["\'])(https://myipnow\.net[^"\']*?)(["\'])', re.IGNORECASE)

fixed_files = []
correct_files = []

# Walk through all subfolders
for root, dirs, files in os.walk(FOLDER_PATH):
    html_files = [f for f in files if f.lower().endswith(".html")]
    for file in html_files:
        file_path = os.path.join(root, file)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"⚠️ Skipping {file_path}: {e}")
            continue

        original_content = content

        # Fix canonical
        content = canonical_pattern.sub(lambda m: m.group(1) + (m.group(2) if m.group(2).endswith("/") else m.group(2)+"/") + m.group(3), content)

        # Fix href/src URLs
        content = url_pattern.sub(lambda m: m.group(1) + (m.group(2) if m.group(2).endswith("/") else m.group(2)+"/") + m.group(3), content)

        if content != original_content:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                fixed_files.append(file_path)
                print(f"✅ Fixed: {file_path}")
            except Exception as e:
                print(f"⚠️ Could not write {file_path}: {e}")
        else:
            correct_files.append(file_path)
            print(f"✔️ Correct: {file_path}")

# Summary
print("\nDone!")
print(f"Files fixed: {len(fixed_files)}")
print(f"Files correct: {len(correct_files)}")