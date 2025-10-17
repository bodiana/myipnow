import os
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, ElementTree

# 1. Set the directory containing your website files
SITE_DIR = "./"  # Change if your HTML files are in a subfolder
BASE_URL = "https://myipnow.net"  # Updated domain
SITEMAP_FILE = "sitemap.xml"

# 2. Collect all HTML files
html_files = []
for root, dirs, files in os.walk(SITE_DIR):
    for file in files:
        if file.endswith(".html"):
            full_path = os.path.join(root, file)
            # Get relative path from SITE_DIR
            rel_path = os.path.relpath(full_path, SITE_DIR)
            html_files.append(rel_path.replace(os.sep, "/"))

# 3. Build XML
urlset = Element("urlset")
urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")

for html_file in html_files:
    url = SubElement(urlset, "url")
    loc = SubElement(url, "loc")
    loc.text = f"{BASE_URL}/{html_file}"

    # Get last modification time
    full_path = os.path.join(SITE_DIR, html_file)
    lastmod = SubElement(url, "lastmod")
    timestamp = os.path.getmtime(full_path)
    lastmod.text = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%dT%H:%M:%SZ")

# 4. Write sitemap.xml
tree = ElementTree(urlset)
tree.write(SITEMAP_FILE, encoding="utf-8", xml_declaration=True)

print(f"Sitemap generated: {SITEMAP_FILE} ({len(html_files)} URLs)")
