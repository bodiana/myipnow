from pathlib import Path
from datetime import datetime
import xml.etree.ElementTree as ET

# ====== CONFIG ======
BASE_DIR = Path(__file__).parent  # root of your project
DOMAIN = "https://myipnow.net"    # change if needed
SITEMAP_FILE = BASE_DIR / "sitemap.xml"
# ====================

def generate_sitemap():
    html_files = sorted(BASE_DIR.rglob("*.html"))
    print(f"🧭 Found {len(html_files)} HTML files to include in sitemap...")

    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    for f in html_files:
        # Skip templates, drafts, or hidden files
        if any(skip in f.name.lower() for skip in ["template", "draft", "backup"]):
            continue

        rel_path = str(f.relative_to(BASE_DIR)).replace("\\", "/")
        loc = f"{DOMAIN}/{rel_path}"
        lastmod = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d")

        url_el = ET.SubElement(urlset, "url")
        ET.SubElement(url_el, "loc").text = loc
        ET.SubElement(url_el, "lastmod").text = lastmod
        ET.SubElement(url_el, "changefreq").text = "weekly"
        ET.SubElement(url_el, "priority").text = "0.8"

    tree = ET.ElementTree(urlset)
    tree.write(SITEMAP_FILE, encoding="utf-8", xml_declaration=True)

    print(f"✅ Sitemap generated successfully at: {SITEMAP_FILE}")

if __name__ == "__main__":
    generate_sitemap()
