import os
import re

# Root folder of your project
ROOT = os.getcwd()

# Category folder names
CATEGORIES = [
    "networking",
    "ip-addresses",
    "general-topics",
    "home-computing",
    "online-safety",
    "online-privacy"
]

# Clean footer (exactly as main page)
CLEAN_FOOTER = """
<footer class="footer">
<ul class="footer-nav">
<li><a href="/about.html">About</a></li>
<li><a href="/contact.html">Contact</a></li>
<li><a href="/privacy-policy.html">Privacy Policy</a></li>
<li><a href="/terms-of-use.html">Terms of Use</a></li>
<li><a href="/affiliate-disclosure.html">Affiliate Disclosure</a></li>
</ul>
<div class="footer-copyright">
    © 2025 myipnow. All Rights Reserved.
</div>
</footer>
"""

for root, _, files in os.walk(ROOT):
    for file in files:
        if file.endswith(".html") and any(cat in root.replace("\\","/") for cat in CATEGORIES):
            path = os.path.join(root, file)

            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Replace everything from first <footer> to last </footer>
            new_content = re.sub(
                r"<footer class=\"footer\">.*</footer>",
                CLEAN_FOOTER,
                content,
                flags=re.DOTALL
            )

            if new_content != content:
                with open(path, "w", encoding="utf-8", errors="ignore") as f:
                    f.write(new_content)
                print(f"✅ Fixed footer in {path}")
