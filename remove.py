import os
from bs4 import BeautifulSoup

ROOT = r"C:\Users\Bodia\OneDrive\Робочий стіл\myipnow-main-17.10"
CATEGORY = "ip-addresses"

SCRIPT_ID = "fix-ip-scroll"
NEW_SCRIPT = f"""
<script id="{SCRIPT_ID}">
document.addEventListener("DOMContentLoaded", function () {{
  // Save scroll position when leaving the IP Addresses category
  if (window.location.pathname.startsWith("/{CATEGORY}/")) {{
    window.addEventListener("beforeunload", function () {{
      sessionStorage.setItem("scrollPos_{CATEGORY}", window.scrollY);
    }});
    // Restore scroll position when returning to the IP Addresses category
    const pos = sessionStorage.getItem("scrollPos_{CATEGORY}");
    if (pos) {{
      window.scrollTo(0, parseInt(pos, 10));
      sessionStorage.removeItem("scrollPos_{CATEGORY}");
    }}
  }}
}});
</script>
""".strip()

def patch_html(path):
    with open(path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # remove old scroll scripts
    for s in soup.find_all("script", id=SCRIPT_ID):
        s.decompose()

    # inject only once
    body = soup.find("body")
    if body:
        body.append(BeautifulSoup(NEW_SCRIPT, "html.parser"))
        with open(path, "w", encoding="utf-8") as f:
            f.write(str(soup))
        return True
    return False


updated = 0

# 1️⃣ Fix category pages (index.html, page2.html, page3.html, etc.)
cat_dir = os.path.join(ROOT, CATEGORY)
for fname in os.listdir(cat_dir):
    if fname.endswith(".html"):
        full_path = os.path.join(cat_dir, fname)
        if patch_html(full_path):
            updated += 1

# 2️⃣ Fix article pages that belong to IP Addresses
for name in os.listdir(ROOT):
    folder = os.path.join(ROOT, name)
    if not os.path.isdir(folder) or name in [
        "online-safety", "online-privacy", "networking",
        "home-computing", "general-topics"
    ]:
        continue

    index_path = os.path.join(folder, "index.html")
    if not os.path.exists(index_path):
        continue

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read().lower()

    # skip if not an IP-related article
    if CATEGORY not in html and not any(k in html for k in ["ip address", "proxy", "geolocation", "dns"]):
        continue

    if patch_html(index_path):
        updated += 1

print(f"✅ Scroll memory fix applied for '{CATEGORY}': {updated} files updated.")
