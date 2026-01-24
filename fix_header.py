import os
import re
from bs4 import BeautifulSoup

def clean_css(css: str) -> str:
    # 1. Remove animation declarations
    css = re.sub(r'animation\s*:[^;]+;', '', css, flags=re.I)
    css = re.sub(r'@keyframes\s+[^{]+\{.*?\}', '', css, flags=re.S | re.I)

    # 2. Remove duplicate properties INSIDE the same rule
    def dedupe_rule(match):
        selector = match.group(1)
        body = match.group(2)

        seen = {}
        lines = []
        for line in body.split(";"):
            line = line.strip()
            if not line or ":" not in line:
                continue
            prop, val = map(str.strip, line.split(":", 1))
            key = (prop.lower(), val)
            if key not in seen:
                seen[key] = True
                lines.append(f"{prop}: {val}")
        return f"{selector}{{{'; '.join(lines)};}}"

    css = re.sub(r'([^{]+)\{([^}]+)\}', dedupe_rule, css)

    return css

def process_html(path):
    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Remove duplicate <style> blocks (exact matches only)
    seen_styles = set()
    for style in soup.find_all("style"):
        content = style.string or ""
        content = content.strip()
        if not content:
            style.decompose()
            continue
        if content in seen_styles:
            style.decompose()
        else:
            seen_styles.add(content)
            style.string.replace_with(clean_css(content))

    with open(path, "w", encoding="utf-8") as f:
        f.write(str(soup))

def run(root="."):
    for root_dir, _, files in os.walk(root):
        for name in files:
            if name.endswith(".html"):
                full = os.path.join(root_dir, name)
                process_html(full)
                print("Cleaned safely:", full)

if __name__ == "__main__":
    run()
