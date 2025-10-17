import os
from bs4 import BeautifulSoup

# ✅ Root folder of your website
ROOT_DIR = r"C:\Users\Bodia\OneDrive\Робочий стіл\myipnow-main-17.10"

# ✅ AdSense script to check / add
ADSENSE_SNIPPET = (
    '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1226342433058379" '
    'crossorigin="anonymous"></script>'
)

# Categories for broken link detection
CATEGORIES = [
    "online-safety",
    "online-privacy",
    "networking",
    "ip-addresses",
    "home-computing",
    "general-topics"
]

# --- Results tracking
broken_links = []
adsense_added = []
adsense_already = []
adsense_missing_nohead = []


def process_html(file_path):
    """Check and fix each HTML file."""
    global broken_links, adsense_added, adsense_already, adsense_missing_nohead

    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    # --- Check for AdSense presence
    if "pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1226342433058379" in html:
        adsense_already.append(file_path)
    else:
        head_tag = soup.find("head")
        if head_tag:
            # Add AdSense script just before </head>
            script_tag = BeautifulSoup(ADSENSE_SNIPPET, "html.parser")
            head_tag.append("\n")
            head_tag.append(script_tag)

            # Save changes
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(str(soup))
            adsense_added.append(file_path)
        else:
            adsense_missing_nohead.append(file_path)

    # --- Check for broken article links (like /general-topics/page22/)
    file_broken_links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if any(f"/{cat}/page" in href and not href.endswith(".html") for cat in CATEGORIES):
            file_broken_links.append(href)

    if file_broken_links:
        broken_links.append((file_path, file_broken_links))


# --- Walk all project files
for root, _, files in os.walk(ROOT_DIR):
    for file in files:
        if file.endswith(".html"):
            process_html(os.path.join(root, file))


# --- Print report
print("\n=== 🔍 Full Website Verification + AdSense Fix ===\n")

if broken_links:
    print("⚠️ Broken Links Found (old /category/pageX/ paths):")
    for file, links in broken_links:
        print(f"\n  {file}")
        for link in links:
            print(f"    → {link}")
else:
    print("✅ No broken article links found.")

if adsense_added:
    print(f"\n🩵 AdSense script was ADDED to {len(adsense_added)} files:")
    for f in adsense_added:
        print(f"  {f}")

if adsense_already:
    print(f"\n✅ {len(adsense_already)} files already had AdSense script.")

if adsense_missing_nohead:
    print(f"\n⚠️ {len(adsense_missing_nohead)} files have NO <head> tag — cannot insert AdSense:")
    for f in adsense_missing_nohead:
        print(f"  {f}")

print("\n✅ Scan + Auto-fix complete.")
