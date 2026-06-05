import os

ROOT_DIR = r"C:\Users\Bodia\OneDrive\Робочий стіл\myipnow-main"

OLD = '  border-bottom:1px solid var(--border);\n\n}'
NEW = '}'

fixed = 0
skipped = 0
errors = 0

for root, dirs, files in os.walk(ROOT_DIR):
    for fname in files:
        if not fname.endswith('.html'):
            continue
        path = os.path.join(root, fname)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()

            if OLD not in content:
                skipped += 1
                continue

            content = content.replace(OLD, NEW, 1)

            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)

            fixed += 1

        except Exception as e:
            print(f"ERROR: {path} — {e}")
            errors += 1

print(f"Done. Fixed: {fixed}  Skipped: {skipped}  Errors: {errors}")
