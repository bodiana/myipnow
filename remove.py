import os
from bs4 import BeautifulSoup

ROOT = r"C:\Users\Bodia\OneDrive\Робочий стіл\myipnow-main-17.10"

# Topic-based reference sets
TOPIC_REFERENCES = {
    "vpn": [
        ("https://www.eff.org/issues/privacy", "Electronic Frontier Foundation – Online Privacy"),
        ("https://protonvpn.com/blog/", "ProtonVPN Blog"),
        ("https://duckduckgo.com/privacy", "DuckDuckGo Privacy Resources"),
        ("https://www.mozilla.org/en-US/privacy/", "Mozilla Privacy Blog"),
        ("https://nordvpn.com/blog/", "NordVPN Learn Center"),
    ],
    "fraud": [
        ("https://staysafeonline.org/", "StaySafeOnline.org (NCA)"),
        ("https://safety.google/", "Google Safety Center"),
        ("https://www.microsoft.com/en-us/safety/family-online-safety", "Microsoft Online Safety"),
        ("https://www.cisa.gov/topics/cybersecurity", "CISA – Cybersecurity Resources"),
        ("https://us.norton.com/blog", "Norton Cyber Safety Blog"),
    ],
    "malware": [
        ("https://www.kaspersky.com/resource-center/", "Kaspersky Resource Center"),
        ("https://www.malwarebytes.com/blog", "Malwarebytes Security Blog"),
        ("https://www.cisa.gov/", "CISA Cybersecurity Hub"),
        ("https://news.sophos.com/en-us/", "Sophos Threat Research Blog"),
        ("https://www.microsoft.com/en-us/security/blog/", "Microsoft Security Blog"),
    ],
    "ip": [
        ("https://www.iana.org/", "IANA – Internet Assigned Numbers Authority"),
        ("https://www.arin.net/", "ARIN – American Registry for Internet Numbers"),
        ("https://www.ripe.net/", "RIPE NCC – Network Coordination Centre"),
        ("https://www.cloudflare.com/learning/dns/what-is-dns/", "Cloudflare DNS Learning"),
        ("https://en.wikipedia.org/wiki/IP_address", "Wikipedia – IP Address"),
    ],
    "ai": [
        ("https://openai.com/blog", "OpenAI Blog"),
        ("https://www.technologyreview.com/", "MIT Technology Review – AI"),
        ("https://www.wired.com/category/ai/", "WIRED AI Section"),
        ("https://www.theverge.com/ai-artificial-intelligence", "The Verge AI Coverage"),
        ("https://techcrunch.com/category/artificial-intelligence/", "TechCrunch AI News"),
    ],
    "iot": [
        ("https://www.tomshardware.com/", "Tom’s Hardware"),
        ("https://www.howtogeek.com/", "How-To Geek"),
        ("https://www.pcmag.com/", "PCMag"),
        ("https://spectrum.ieee.org/", "IEEE Spectrum – IoT"),
        ("https://support.apple.com/", "Apple Support"),
    ],
    "social": [
        ("https://privacyinternational.org/", "Privacy International"),
        ("https://transparency.fb.com/", "Meta Transparency Center"),
        ("https://safety.google/", "Google Safety Center"),
        ("https://foundation.mozilla.org/", "Mozilla Foundation"),
        ("https://www.pewresearch.org/", "Pew Research Center – Internet & Tech"),
    ],
    "default": [
        ("https://www.techradar.com/", "TechRadar – Tech News and Reviews"),
        ("https://www.wired.com/", "WIRED – Technology Insights"),
        ("https://www.theverge.com/", "The Verge – Technology and Culture"),
        ("https://www.cnet.com/", "CNET – Tech How-To and Reviews"),
        ("https://en.wikipedia.org/wiki/Technology", "Wikipedia – Technology Overview"),
    ],
}

# Simple keyword matching for topics
def detect_topic(text):
    text = text.lower()
    if any(k in text for k in ["vpn", "encryption", "privacy"]):
        return "vpn"
    if any(k in text for k in ["phishing", "fraud", "scam", "social engineering"]):
        return "fraud"
    if any(k in text for k in ["malware", "virus", "ransomware", "trojan"]):
        return "malware"
    if any(k in text for k in ["ip address", "dns", "routing", "network"]):
        return "ip"
    if any(k in text for k in ["ai", "machine learning", "deepfake", "artificial intelligence"]):
        return "ai"
    if any(k in text for k in ["iot", "smart home", "device", "automation"]):
        return "iot"
    if any(k in text for k in ["social media", "tracking", "analytics", "facebook", "twitter"]):
        return "social"
    return "default"

updated = 0
for folder in os.listdir(ROOT):
    folder_path = os.path.join(ROOT, folder)
    index_path = os.path.join(folder_path, "index.html")

    if not os.path.isdir(folder_path) or not os.path.exists(index_path):
        continue

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    # Detect article topic
    title = (soup.title.string if soup.title else "") + " " + " ".join([h.get_text() for h in soup.find_all(["h1", "h2", "h3"])])
    topic = detect_topic(title)

    # Build new references block
    new_refs = BeautifulSoup("<div class='references'><p>References:</p><ul></ul></div>", "html.parser")
    ul = new_refs.find("ul")
    for url, label in TOPIC_REFERENCES[topic]:
        li = soup.new_tag("li")
        a = soup.new_tag("a", href=url, target="_blank", rel="noopener noreferrer")
        a.string = label
        li.append(a)
        ul.append(li)

    # Replace old block
    old_ref = soup.find("div", class_="references")
    if old_ref:
        old_ref.replace_with(new_refs)
        updated += 1
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(str(soup))

print(f"✅ Updated references in {updated} articles.")
