import os, re, json, time, urllib.request, urllib.error, urllib.parse

DEEPL_KEY = "c1102701-960d-435e-adf6-8ca0a4412e06"
DEEPL_URL = "https://api.deepl.com/v2/translate"

LANGUAGES = {"de": "DE", "es": "ES", "fr": "FR", "it": "IT"}
LANG_NAMES = {"de": "German", "es": "Spanish", "fr": "French", "it": "Italian"}

TOOL_PAGES = [
    ("index.html", ""),
    ("dns-lookup.html", "dns-lookup"),
    ("whois-lookup.html", "whois-lookup"),
    ("ip-blacklist.html", "ip-blacklist"),
    ("asn-lookup.html", "asn-lookup"),
    ("internet-speed-test.html", "internet-speed-test"),
    ("generate-password.html", "generate-password"),
    ("ip-subnet-calculator.html", "ip-subnet-calculator"),
    ("cidr-to-ip-range-calculator.html", "cidr-to-ip-range-calculator"),
    ("ip-range-to-cidr-calculator.html", "ip-range-to-cidr-calculator"),
]

ROUTER_IPS = [
    "10.0.0.1", "10.11.12.1", "192.168.0.100", "192.168.0.254",
    "192.168.100.1", "192.168.10.1", "192.168.11.1", "192.168.1.11",
    "192.168.12.1", "192.168.1.250", "192.168.1.2", "192.168.1.254",
    "192.168.188.1", "192.168.2.1", "192.168.223.1", "192.168.254.254",
    "192.168.4.1", "192.168.7.1", "192.168.8.1"
]

PROTECTED_TERMS = sorted([
    "IP Subnet Calculator", "DNS Lookup", "WHOIS Lookup", "ASN Lookup",
    "IP Blacklist Checker",
    "CIDR to IP Range Calculator", "IP Range to CIDR Calculator",
    "CIDR Calculator", "IP Range to CIDR", "CIDR to IP Range",
    "What Is My IP", "IP Address Lookup", "IP Lookup",
    "IPv4", "IPv6", "CIDR", "TTL", "ASN", "BGP", "ISP",
    "VPN", "DNS", "HTTP", "HTTPS", "SSL", "TLS", "TCP", "UDP",
    "PTR record", "MX record", "NS record", "AAAA record", "CNAME record",
    "A record", "SOA record", "DKIM", "SPF", "DMARC",
    "subnet mask", "default gateway", "MAC address",
    "ping", "traceroute", "reverse DNS", "WHOIS", "RIPE", "ARIN", "APNIC",
    "MyIPNow",
], key=len, reverse=True)

def protect_technical(text):
    placeholders = {}
    counter = [0]
    def replace(m):
        key = "<x%d/>" % counter[0]
        placeholders[key] = m.group(0)
        counter[0] += 1
        return key
    for term in PROTECTED_TERMS:
        if term.lower() in text.lower():
            key = "<x%d/>" % counter[0]
            placeholders[key] = term
            counter[0] += 1
            text = re.sub(re.escape(term), key, text, flags=re.IGNORECASE)
    text = re.sub(r'<code>[^<]+</code>', replace, text)
    text = re.sub(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?:/\d+)?', replace, text)
    text = re.sub(r'(example\.com|example\.org|google\.com|myipnow\.net)', replace, text)
    return text, placeholders

def restore_technical(text, placeholders):
    for key, val in placeholders.items():
        text = text.replace(key, val)
    return text

def deepl_call(text, target_lang):
    if not text or not text.strip() or len(text.strip()) < 3:
        return text
    payload = {"text": [text.strip()], "target_lang": target_lang, "source_lang": "EN"}
    req = urllib.request.Request(DEEPL_URL, data=json.dumps(payload).encode(), method="POST")
    req.add_header("Authorization", "DeepL-Auth-Key " + DEEPL_KEY)
    req.add_header("Content-Type", "application/json")
    time.sleep(0.4)
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())["translations"][0]["text"]
        except urllib.error.HTTPError as e:
            if e.code == 429:
                print("  Rate limited, waiting 10s...")
                time.sleep(10)
            else:
                print("  DeepL error %d: %s" % (e.code, e))
                return text
        except Exception as e:
            print("  DeepL error: %s" % e)
            return text
    return text

def translate_text(text, target_lang):
    protected, ph = protect_technical(text)
    translated = deepl_call(protected, target_lang)
    return restore_technical(translated, ph)

def translate_html(text, target_lang):
    protected, ph = protect_technical(text)
    translated = deepl_call(protected, target_lang)
    return restore_technical(translated, ph)

def translate_page(content, lang, deepl_lang, slug, translated_slugs):
    content = re.sub(r'<html lang="[^"]*"', '<html lang="%s"' % lang, content)
    content = re.sub(
        r'<link rel="canonical" href="https://myipnow\.net/([^"]*)"',
        '<link rel="canonical" href="https://myipnow.net/%s/\\1"' % lang,
        content
    )
    hreflang = '<link rel="alternate" hreflang="en" href="https://myipnow.net/%s"/>\n<link rel="alternate" hreflang="%s" href="https://myipnow.net/%s/%s"/>\n<link rel="alternate" hreflang="x-default" href="https://myipnow.net/%s"/>' % (slug, lang, lang, slug, slug)
    content = content.replace('</head>', hreflang + '\n</head>', 1)
    content = re.sub(r'<link[^>]*fonts\.googleapis\.com[^>]*/?>'  , '<link href="/css/fonts.css" rel="stylesheet"/>', content)
    m = re.search(r'<title>([^<]+)</title>', content)
    if m:
        trans = translate_text(m.group(1), deepl_lang)
        content = content.replace('<title>%s</title>' % m.group(1), '<title>%s</title>' % trans)
        print("  Title: %s" % trans)
    m = re.search(r'(<meta content=")([^"]+)(" name="description"/>)', content)
    if m:
        trans = translate_text(m.group(2), deepl_lang)
        content = content.replace(m.group(0), m.group(1) + trans + m.group(3))
    m = re.search(r'(<meta content=")([^"]+)(" property="og:title"/>)', content)
    if m:
        trans = translate_text(m.group(2), deepl_lang)
        content = content.replace(m.group(0), m.group(1) + trans + m.group(3))
    m = re.search(r'(<meta content=")([^"]+)(" property="og:description"/>)', content)
    if m:
        trans = translate_text(m.group(2), deepl_lang)
        content = content.replace(m.group(0), m.group(1) + trans + m.group(3))
    def trans_heading(m):
        inner = m.group(2)
        if inner.strip() and len(inner.strip()) > 2:
            return m.group(1) + translate_text(inner.strip(), deepl_lang) + m.group(3)
        return m.group(0)
    content = re.sub(r'(<h1[^>]*>)(.*?)(</h1>)', trans_heading, content, flags=re.DOTALL)
    content = re.sub(r'(<h2[^>]*>)(.*?)(</h2>)', trans_heading, content, flags=re.DOTALL)
    content = re.sub(r'(<h3[^>]*>)(.*?)(</h3>)', trans_heading, content, flags=re.DOTALL)
    def translate_body(body):
        def trans_p(m):
            inner = m.group(2)
            if inner.strip() and len(inner.strip()) > 5:
                return m.group(1) + translate_html(inner, deepl_lang) + m.group(3)
            return m.group(0)
        body = re.sub(r'(<p[^>]*>)(.*?)(</p>)', trans_p, body, flags=re.DOTALL)
        def trans_div(m):
            inner = m.group(2)
            if inner.strip():
                return m.group(1) + translate_text(inner, deepl_lang) + m.group(3)
            return m.group(0)
        body = re.sub(r'(<div class="faq-question">)(.*?)(</div>)', trans_div, body, flags=re.DOTALL)
        body = re.sub(r'(<div class="faq-answer">)(.*?)(</div>)', trans_div, body, flags=re.DOTALL)
        def trans_li(m):
            inner = m.group(2)
            if 'myipnow.net' in inner or 'href=' in inner:
                return m.group(0)
            if inner.strip() and len(inner.strip()) > 2:
                return m.group(1) + translate_text(inner, deepl_lang) + m.group(3)
            return m.group(0)
        body = re.sub(r'(<li>)(.*?)(</li>)', trans_li, body, flags=re.DOTALL)
        body = re.sub(r'(<p class="snippet-answer[^"]*">)(.*?)(</p>)', trans_p, body, flags=re.DOTALL)
        return body
    m = re.search(r'(<article[^>]*>)(.*?)(</article>)', content, re.DOTALL)
    if m:
        translated_body = translate_body(m.group(2))
        content = content.replace(m.group(0), m.group(1) + translated_body + m.group(3))
        print("  Article translated")
    else:
        for section_class in ["snippet-section", "faq-snippet", "guide-section"]:
            m = re.search(r'(<section[^>]*%s[^>]*>)(.*?)(</section>)' % section_class, content, re.DOTALL)
            if m:
                translated_body = translate_body(m.group(2))
                content = content.replace(m.group(0), m.group(1) + translated_body + m.group(3))
        print("  Sections translated")
    m = re.search(r'(<header class="page-header">.*?<p>)(.*?)(</p>)', content, re.DOTALL)
    if m:
        trans = translate_html(m.group(2), deepl_lang)
        content = content.replace(m.group(0), m.group(1) + trans + m.group(3))
    def fix_link(m):
        href = m.group(1)
        if 'myipnow.net/' not in href:
            return m.group(0)
        for s in translated_slugs:
            if s and (href.endswith('/' + s + '/') or href.endswith('/' + s)):
                return 'href="' + href.replace('myipnow.net/', 'myipnow.net/%s/' % lang) + '"'
        return m.group(0)
    content = re.sub(r'href="(https://myipnow\.net/[^"]+)"', fix_link, content)
    content = re.sub(
        r'(<meta content="https://myipnow\.net/)([^"]*" property="og:url"/>)',
        r'\g<1>' + lang + r'/\2',
        content
    )
    return content

def main():
    base = "/var/www/html"
    translated_slugs = [slug for _, slug in TOOL_PAGES if slug]
    translated_slugs += ["router/" + ip for ip in ROUTER_IPS]
    for lang, deepl_lang in LANGUAGES.items():
        print("\n" + "="*50)
        print("Translating to %s (%s)..." % (LANG_NAMES[lang], lang))
        print("="*50)
        lang_dir = os.path.join(base, lang)
        os.makedirs(lang_dir, exist_ok=True)
        for filename, slug in TOOL_PAGES:
            src = os.path.join(base, filename)
            if not os.path.exists(src):
                print("  SKIP: %s not found" % filename)
                continue
            print("\n  Translating %s..." % filename)
            with open(src, 'r', errors='ignore') as f:
                content = f.read()
            out_dir = os.path.join(lang_dir, slug) if slug else lang_dir
            os.makedirs(out_dir, exist_ok=True)
            page_slug = slug + "/" if slug else ""
            trans = translate_page(content, lang, deepl_lang, page_slug, translated_slugs)
            out_path = os.path.join(out_dir, "index.html")
            with open(out_path, 'w') as f:
                f.write(trans)
            print("  Saved: %s" % out_path)
            time.sleep(2)
        router_dir = os.path.join(lang_dir, "router")
        os.makedirs(router_dir, exist_ok=True)
        for ip in ROUTER_IPS:
            src = os.path.join(base, "router", ip, "index.html")
            if not os.path.exists(src):
                print("  SKIP: router/%s not found" % ip)
                continue
            print("\n  Translating router/%s..." % ip)
            with open(src, 'r', errors='ignore') as f:
                content = f.read()
            out_dir = os.path.join(router_dir, ip)
            os.makedirs(out_dir, exist_ok=True)
            trans = translate_page(content, lang, deepl_lang, "router/%s/" % ip, translated_slugs)
            with open(os.path.join(out_dir, "index.html"), 'w') as f:
                f.write(trans)
            print("  Saved: %s" % out_dir)
            time.sleep(2)
        print("\n%s done!" % LANG_NAMES[lang])
    print("\n\nAll languages done!")

if __name__ == "__main__":
    main()
