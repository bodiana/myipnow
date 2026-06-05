import os

BASE = r"C:\Users\Bodia\OneDrive\Робочий стіл\myipnow-main"

MAIN_PAGES = [
    os.path.join(BASE, "index.html"),
    os.path.join(BASE, "de", "index.html"),
    os.path.join(BASE, "es", "index.html"),
    os.path.join(BASE, "fr", "index.html"),
    os.path.join(BASE, "it", "index.html"),
    os.path.join(BASE, "pt", "index.html"),
    os.path.join(BASE, "pl", "index.html"),
    os.path.join(BASE, "nl", "index.html"),
]

FIXES = [
    (
        '  .info-table .row span:first-child{font-size: 12px; color: var(--text-secondary);}',
        '  .info-table .row span:first-child{font-size: 12px; color: var(--text);}'
    ),
    (
        '  .info-table .row > span:first-child{display: block; font-size: 12px; color: var(--text-secondary); margin-bottom: 4px;}',
        '  .info-table .row > span:first-child{display: block; font-size: 12px; color: var(--text); margin-bottom: 4px;}'
    ),
    # Also fix the already-patched version from previous script
    (
        '  .info-table .row > span:first-child{display: block; font-size: 12px; color: var(--text); margin-bottom: 4px;}',
        '  .info-table .row > span:first-child{display: block; font-size: 12px; color: var(--text); margin-bottom: 4px;}'
    ),
]

for path in MAIN_PAGES:
    if not os.path.exists(path):
        print(f"NOT FOUND: {path}")
        continue
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        changed = False
        for old, new in FIXES[:2]:  # only first two actual replacements
            if old in content:
                content = content.replace(old, new)
                changed = True

        if not changed:
            print(f"Nothing to fix: {path}")
            continue

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Fixed: {path}")

    except Exception as e:
        print(f"ERROR: {path} — {e}")
