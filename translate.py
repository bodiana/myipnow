import os, re, json, time, urllib.request, urllib.error

DEEPL_KEY = ""
DEEPL_URL = "https://api.deepl.com/v2/translate"

LANGUAGES = {"pl": "PL", "nl": "NL"}
LANG_NAMES = {"de": "German", "es": "Spanish", "fr": "French", "it": "Italian", "pt": "Portuguese", "pl": "Polish", "nl": "Dutch"}

# Source language to translate FROM (always DE as it's our cleanest template)
SOURCE_LANG = "de"
SOURCE_DEEPL = "DE"

TOOL_PAGES = [
    ("", ""),           # homepage: de/index.html -> pl/index.html
    ("dns-lookup", "dns-lookup"),
    ("whois-lookup", "whois-lookup"),
    ("ip-blacklist", "ip-blacklist"),
    ("asn-lookup", "asn-lookup"),
    ("internet-speed-test", "internet-speed-test"),
    ("generate-password", "generate-password"),
    ("ip-subnet-calculator", "ip-subnet-calculator"),
    ("cidr-to-ip-range-calculator", "cidr-to-ip-range-calculator"),
    ("ip-range-to-cidr-calculator", "ip-range-to-cidr-calculator"),
    ("hide-my-ip", "hide-my-ip"),
    ("ping-test", "ping-test"),
]

ROUTER_IPS = [
    "10.0.0.1", "10.11.12.1", "192.168.0.100", "192.168.0.254",
    "192.168.100.1", "192.168.10.1", "192.168.11.1", "192.168.1.11",
    "192.168.12.1", "192.168.1.250", "192.168.1.2", "192.168.1.254",
    "192.168.188.1", "192.168.2.1", "192.168.223.1", "192.168.254.254",
    "192.168.4.1", "192.168.7.1", "192.168.8.1",
    "192.168.1.1", "192.168.0.1"
]

ALL_LANGS = ["de", "es", "fr", "it", "pt", "pl", "nl"]

SEARCH_PLACEHOLDER = {
    "de": "Suchen...",
    "es": "Buscar...",
    "fr": "Rechercher...",
    "it": "Cerca...",
    "pt": "Pesquisar...",
    "pl": "Szukaj...",
    "nl": "Zoeken...",
}

LANG_FLAG = {
    "de": "🇩🇪", "es": "🇪🇸", "fr": "🇫🇷", "it": "🇮🇹",
    "pt": "🇧🇷", "pl": "🇵🇱", "nl": "🇳🇱",
}
LANG_LABEL = {
    "de": "Deutsch", "es": "Español", "fr": "Français", "it": "Italiano",
    "pt": "Português", "pl": "Polski", "nl": "Nederlands",
}

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
    text = re.sub(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?:/\d+)?', replace, text)
    text = re.sub(r'(example\.com|example\.org|google\.com|myipnow\.net)', replace, text)
    return text, placeholders

def restore_technical(text, placeholders):
    for key, val in placeholders.items():
        text = text.replace(key, val)
    return text

def deepl_call(text, target_lang, source_lang="DE"):
    if not text or not text.strip() or len(text.strip()) < 3:
        return text
    payload = {"text": [text.strip()], "target_lang": target_lang, "source_lang": source_lang}
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

def build_hreflang(slug):
    """Correct hreflang - en and x-default always point to English URL"""
    en_url = 'https://myipnow.net/' + slug
    lines = [
        '<link rel="alternate" hreflang="en" href="%s"/>' % en_url,
        '<link rel="alternate" hreflang="x-default" href="%s"/>' % en_url,
    ]
    for l in ALL_LANGS:
        url = 'https://myipnow.net/%s/' % l + slug
        lines.append('<link rel="alternate" hreflang="%s" href="%s"/>' % (l, url))
    return '\n'.join(lines)

def build_nav(lang):
    base = 'https://myipnow.net/%s' % lang
    return '''<li class="nav-tools"><a href="https://myipnow.net/#/">Tools ▾</a>
<ul>
<li><a href="%s/">IP Lookup</a></li>
<li><a href="%s/dns-lookup/">DNS Lookup</a></li>
<li><a href="%s/whois-lookup/">WHOIS Lookup</a></li>
<li><a href="%s/internet-speed-test/">Internet Speed Test</a></li>
<li><a href="%s/ping-test/">Ping Test</a></li>
<li><a href="%s/generate-password/">Generate Password</a></li>
<li><a href="%s/ip-blacklist/">IP Blacklist</a></li>
</ul>
</li>''' % (base, base, base, base, base, base, base)

def build_lang_links(current_lang, slug):
    links = ['<a href="https://myipnow.net/%s">🇺🇸 English</a>' % (slug if slug else '')]
    for l in ALL_LANGS:
        if l == current_lang:
            continue
        url = 'https://myipnow.net/%s/' % l + slug
        links.append('<a href="%s">%s %s</a>' % (url, LANG_FLAG[l], LANG_LABEL[l]))
    return '<div class="lang-links">\n' + '\n'.join(links) + '\n</div>'

def build_lang_switcher_js():
    langs_js = '[' + ', '.join(
        "{code:'%s', flag:'%s', label:'%s', base:'https://myipnow.net/%s/'}" % (
            l, l.upper(), LANG_LABEL[l], l
        ) for l in ALL_LANGS
    ) + ']'
    langs_js = "[{code:'en', flag:'EN', label:'English', base:'https://myipnow.net/'}, " + \
               ', '.join(
        "{code:'%s', flag:'%s', label:'%s', base:'https://myipnow.net/%s/'}" % (
            l, l.upper(), LANG_LABEL[l], l
        ) for l in ALL_LANGS
    ) + "]"
    all_langs_str = "['%s']" % "','".join(ALL_LANGS)
    return langs_js, all_langs_str

def build_lang_redirect(translated_slugs):
    slugs_js = json.dumps(translated_slugs)
    all_langs_str = "['%s']" % "','".join(ALL_LANGS)
    return '''<script>/*lang-redirect*/</script>
<script>
(function(){
  var lang = location.pathname.split('/').filter(Boolean)[0];
  if (!%s.includes(lang)) return;
  var translated = %s;
  function isTranslated(path) {
    path = path.replace(/\\/$/, '');
    return translated.some(function(s){ return path === s || path.endsWith('/'+s); });
  }
  document.querySelectorAll('a[href]').forEach(function(a){
    var href = a.getAttribute('href');
    if (!href || !href.startsWith('https://myipnow.net/')) return;
    if (href.includes('/'+lang+'/')) return;
    var path = href.replace('https://myipnow.net/', '').replace(/\\/$/, '');
    if (path && isTranslated(path)) {
      a.setAttribute('href', 'https://myipnow.net/' + lang + '/' + path + '/');
    }
  });
  document.querySelectorAll('button[onclick]').forEach(function(btn){
    var oc = btn.getAttribute('onclick');
    if (!oc || !oc.includes('myipnow.net/')) return;
    var m = oc.match(/myipnow\\.net\\/([^']+)/);
    if (!m) return;
    var path = m[1].replace(/\\/$/, '');
    if (path && isTranslated(path) && !oc.includes('/'+lang+'/')) {
      btn.setAttribute('onclick', oc.replace('myipnow.net/', 'myipnow.net/' + lang + '/'));
    }
  });
})();
</script>''' % (all_langs_str, slugs_js)

def translate_page(content, src_lang, tgt_lang, tgt_deepl, slug, translated_slugs):
    """Translate a page from src_lang to tgt_lang"""

    # 1. HTML lang attribute
    content = re.sub(r'<html lang="[^"]*"', '<html lang="%s"' % tgt_lang, content)

    # 2. Canonical
    canon_url = 'https://myipnow.net/%s/' % tgt_lang + slug
    content = re.sub(r'<link href="[^"]*" rel="canonical"/>', 
                     '<link href="%s" rel="canonical"/>' % canon_url, content)
    content = re.sub(r'<link rel="canonical" href="[^"]*"',
                     '<link rel="canonical" href="%s"' % canon_url, content)

    # 3. Remove all existing hreflang and add correct ones
    content = re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*"/>\n?', '', content)
    content = content.replace('</head>', build_hreflang(slug) + '\n</head>', 1)

    # 4. Fix og:url
    content = re.sub(
        r'<meta content="https://myipnow\.net/[^"]*" property="og:url"/>',
        '<meta content="%s" property="og:url"/>' % canon_url, content)
    content = re.sub(
        r'<meta content="https://myipnow\.net/[^"]*" property="og:url">',
        '<meta content="%s" property="og:url">' % canon_url, content)

    # 5. Translate title
    m = re.search(r'<title>([^<]+)</title>', content)
    if m:
        trans = translate_text(m.group(1), tgt_deepl)
        content = content.replace(m.group(0), '<title>%s</title>' % trans)
        print("  Title: %s" % trans)

    # 6. Translate meta description
    for pattern in [
        r'(<meta content=")([^"]+)(" name="description"/>)',
        r'(<meta name="description" content=")([^"]+)(")',
    ]:
        m = re.search(pattern, content)
        if m:
            trans = translate_text(m.group(2), tgt_deepl)
            content = content.replace(m.group(0), m.group(1) + trans + m.group(3))
            break

    # 7. Translate og:title and og:description
    for prop in ['og:title', 'og:description']:
        m = re.search(r'(<meta content=")([^"]+)(" property="%s"/>)' % prop, content)
        if m:
            trans = translate_text(m.group(2), tgt_deepl)
            content = content.replace(m.group(0), m.group(1) + trans + m.group(3))

    # 8. Fix nav - replace src_lang URLs with tgt_lang
    content = re.sub(
        r'<li class="nav-tools">[\s\S]*?</ul>\s*</li>',
        build_nav(tgt_lang), content, count=1)

    # 9. Fix logo link
    content = content.replace(
        'href="https://myipnow.net/%s/"' % src_lang + '><img',
        'href="https://myipnow.net/%s/"' % tgt_lang + '><img')
    content = re.sub(
        r'(<a class="logo" href="https://myipnow\.net/)[^/]*/(")',
        r'\g<1>%s/\2' % tgt_lang, content)

    # 10. Fix search placeholder
    for old_ph in SEARCH_PLACEHOLDER.values():
        content = content.replace(
            'placeholder="%s"' % old_ph,
            'placeholder="%s"' % SEARCH_PLACEHOLDER[tgt_lang])

    # 11. Translate headings
    def trans_heading(m):
        inner = m.group(2)
        if inner.strip() and len(inner.strip()) > 2 and '<' not in inner:
            return m.group(1) + translate_text(inner.strip(), tgt_deepl) + m.group(3)
        return m.group(0)
    content = re.sub(r'(<h1[^>]*>)(.*?)(</h1>)', trans_heading, content, flags=re.DOTALL)
    content = re.sub(r'(<h2[^>]*>)(.*?)(</h2>)', trans_heading, content, flags=re.DOTALL)
    content = re.sub(r'(<h3[^>]*>)(.*?)(</h3>)', trans_heading, content, flags=re.DOTALL)

    # 12. Translate body content
    def translate_body(body):
        def trans_p(m):
            inner = m.group(2)
            if inner.strip() and len(inner.strip()) > 5:
                return m.group(1) + translate_html(inner, tgt_deepl) + m.group(3)
            return m.group(0)
        body = re.sub(r'(<p[^>]*>)(.*?)(</p>)', trans_p, body, flags=re.DOTALL)

        def trans_elem(m):
            inner = m.group(2)
            if inner.strip() and len(inner.strip()) > 2:
                return m.group(1) + translate_text(inner, tgt_deepl) + m.group(3)
            return m.group(0)
        body = re.sub(r'(<div class="faq-question">)(.*?)(</div>)', trans_elem, body, flags=re.DOTALL)
        body = re.sub(r'(<div class="faq-answer">)(.*?)(</div>)', trans_elem, body, flags=re.DOTALL)
        body = re.sub(r'(<summary>)(.*?)(</summary>)', trans_elem, body, flags=re.DOTALL)

        def trans_li(m):
            inner = m.group(2)
            if 'myipnow.net' in inner or 'href=' in inner:
                return m.group(0)
            if inner.strip() and len(inner.strip()) > 2:
                return m.group(1) + translate_text(inner, tgt_deepl) + m.group(3)
            return m.group(0)
        body = re.sub(r'(<li>)(.*?)(</li>)', trans_li, body, flags=re.DOTALL)
        body = re.sub(r'(<p class="snippet-answer[^"]*">)(.*?)(</p>)', trans_p, body, flags=re.DOTALL)
        return body

    m = re.search(r'(<article[^>]*>)(.*?)(</article>)', content, re.DOTALL)
    if m:
        content = content.replace(m.group(0), m.group(1) + translate_body(m.group(2)) + m.group(3))
        print("  Article translated")
    else:
        for cls in ["snippet-section", "faq-snippet", "guide-section", "affiliate-banner", "card-section"]:
            m = re.search(r'(<section[^>]*%s[^>]*>)(.*?)(</section>)' % cls, content, re.DOTALL)
            if m:
                content = content.replace(m.group(0), m.group(1) + translate_body(m.group(2)) + m.group(3))
        print("  Sections translated")

    # 13. Translate page-header subtitle
    m = re.search(r'(<header class="page-header">.*?<p>)(.*?)(</p>)', content, re.DOTALL)
    if m:
        content = content.replace(m.group(0), m.group(1) + translate_html(m.group(2), tgt_deepl) + m.group(3))

    # 13b. Translate info table labels (they come from DE source)
    label_translations = {
        "pl": {"Stadt": "Miasto", "Bundesland/Region": "Województwo/Region",
               "Postleitzahl": "Kod pocztowy", "Land": "Kraj",
               "Zeitzone": "Strefa czasowa", "Breitengrad": "Szerokość geograficzna",
               "Längengrad": "Długość geograficzna",
               "IP-Adresse eingeben (IPv4 oder IPv6)": "Wprowadź adres IP (IPv4 lub IPv6)",
               "Meine Verbindung mit einem VPN sichern": "Zabezpiecz moje połączenie przez VPN"},
        "nl": {"Stadt": "Stad", "Bundesland/Region": "Staat/Regio",
               "Postleitzahl": "Postcode", "Land": "Land",
               "Zeitzone": "Tijdzone", "Breitengrad": "Breedtegraad",
               "Längengrad": "Lengtegraad",
               "IP-Adresse eingeben (IPv4 oder IPv6)": "Voer een IP-adres in (IPv4 of IPv6)",
               "Meine Verbindung mit einem VPN sichern": "Beveilig mijn verbinding met een VPN"},
    }
    for de_text, pl_text in label_translations.get(tgt_lang, {}).items():
        content = content.replace(de_text, pl_text)

    # 13c. Translate subtitle (snippet-answer) if still in German
    m = re.search(r'(<p class="snippet-answer[^"]*">)(.*?)(</p>)', content, re.DOTALL)
    if m and any(german in m.group(2) for german in ['Ihre', 'dieses', 'Ihrem', 'zeigt']):
        trans = translate_html(m.group(2), tgt_deepl)
        content = content.replace(m.group(0), m.group(1) + trans + m.group(3))

    # 13b. Translate info table labels (they come from DE source)
    label_translations = {
        "pl": {"Stadt": "Miasto", "Bundesland/Region": "Województwo/Region",
               "Postleitzahl": "Kod pocztowy", "Land": "Kraj",
               "Zeitzone": "Strefa czasowa", "Breitengrad": "Szerokość geograficzna",
               "Längengrad": "Długość geograficzna",
               "IP-Adresse eingeben (IPv4 oder IPv6)": "Wprowadź adres IP (IPv4 lub IPv6)",
               "Meine Verbindung mit einem VPN sichern": "Zabezpiecz moje połączenie przez VPN"},
        "nl": {"Stadt": "Stad", "Bundesland/Region": "Staat/Regio",
               "Postleitzahl": "Postcode", "Land": "Land",
               "Zeitzone": "Tijdzone", "Breitengrad": "Breedtegraad",
               "Längengrad": "Lengtegraad",
               "IP-Adresse eingeben (IPv4 oder IPv6)": "Voer een IP-adres in (IPv4 of IPv6)",
               "Meine Verbindung mit einem VPN sichern": "Beveilig mijn verbinding met een VPN"},
    }
    for de_text, pl_text in label_translations.get(tgt_lang, {}).items():
        content = content.replace(de_text, pl_text)

    # 13c. Translate subtitle (snippet-answer) if still in German
    m = re.search(r'(<p class="snippet-answer[^"]*">)(.*?)(</p>)', content, re.DOTALL)
    if m and any(german in m.group(2) for german in ['Ihre', 'dieses', 'Ihrem', 'zeigt']):
        trans = translate_html(m.group(2), tgt_deepl)
        content = content.replace(m.group(0), m.group(1) + trans + m.group(3))

    # 14. Fix ALL internal links from src_lang to tgt_lang
    content = content.replace(
        'https://myipnow.net/%s/' % src_lang,
        'https://myipnow.net/%s/' % tgt_lang)

    # 15. Fix lang-switcher JS - replace src_lang refs with tgt_lang
    langs_js, all_langs_str = build_lang_switcher_js()
    # Replace LANGS array
    content = re.sub(
        r'var LANGS = \[[\s\S]*?\];',
        'var LANGS = %s;' % langs_js, content, count=1)
    # Replace getSlug indexOf check
    content = re.sub(
        r"if\(\[['a-z,]+\]\.indexOf\(parts\[0\]\) !== -1\) parts\.shift\(\);",
        "if(%s.indexOf(parts[0]) !== -1) parts.shift();" % all_langs_str, content)
    # Replace getCurrentLang indexOf check
    content = re.sub(
        r"if\(\[['a-z,]+\]\.indexOf\(parts\[0\]\) !== -1\) return parts\[0\];",
        "if(%s.indexOf(parts[0]) !== -1) return parts[0];" % all_langs_str, content)

    # 16. Fix lang-redirect script
    if '/*lang-redirect*/' in content:
        content = re.sub(
            r'<script>/\*lang-redirect\*/</script>[\s\S]*?</script>',
            build_lang_redirect(translated_slugs), content, count=1)
    else:
        content = content.replace('</body>', build_lang_redirect(translated_slugs) + '\n</body>', 1)

    # 17. Fix lang-links
    lang_links = build_lang_links(tgt_lang, slug)
    if '<div class="lang-links">' in content:
        content = re.sub(r'<div class="lang-links">[\s\S]*?</div>', lang_links, content, count=1)
    else:
        content = content.replace('<footer', lang_links + '\n<footer', 1)

    # 18. Fix ASN lookup href in JS
    content = content.replace(
        'asnEl.href = "https://myipnow.net/%s/asn-lookup/?asn="' % src_lang,
        'asnEl.href = "https://myipnow.net/%s/asn-lookup/?asn="' % tgt_lang)

    return content

def main():
    base = "/var/www/html"
    translated_slugs = [slug for _, slug in TOOL_PAGES if slug]
    translated_slugs += ["router/" + ip for ip in ROUTER_IPS]

    for tgt_lang, tgt_deepl in LANGUAGES.items():
        if tgt_lang == SOURCE_LANG:
            continue  # skip DE since it's the source

        print("\n" + "="*50)
        print("Translating to %s (%s) from %s..." % (LANG_NAMES[tgt_lang], tgt_lang, SOURCE_LANG))
        print("="*50)

        tgt_dir = os.path.join(base, tgt_lang)
        os.makedirs(tgt_dir, exist_ok=True)

        for src_slug, tgt_slug in TOOL_PAGES:
            src_path = os.path.join(base, SOURCE_LANG, src_slug, 'index.html') if src_slug else os.path.join(base, SOURCE_LANG, 'index.html')
            if not os.path.exists(src_path):
                print("  SKIP: %s not found" % src_path)
                continue
            print("\n  Translating %s..." % (src_slug or 'index'))
            with open(src_path, 'r', errors='ignore') as f:
                content = f.read()
            out_dir = os.path.join(tgt_dir, tgt_slug) if tgt_slug else tgt_dir
            os.makedirs(out_dir, exist_ok=True)
            page_slug = tgt_slug + "/" if tgt_slug else ""
            trans = translate_page(content, SOURCE_LANG, tgt_lang, tgt_deepl, page_slug, translated_slugs)
            out_path = os.path.join(out_dir, "index.html")
            with open(out_path, 'w') as f:
                f.write(trans)
            print("  Saved: %s" % out_path)
            time.sleep(2)

        # Router pages
        tgt_router_dir = os.path.join(tgt_dir, "router")
        os.makedirs(tgt_router_dir, exist_ok=True)
        for ip in ROUTER_IPS:
            src_path = os.path.join(base, SOURCE_LANG, "router", ip, "index.html")
            if not os.path.exists(src_path):
                print("  SKIP: router/%s not found" % ip)
                continue
            print("\n  Translating router/%s..." % ip)
            with open(src_path, 'r', errors='ignore') as f:
                content = f.read()
            out_dir = os.path.join(tgt_router_dir, ip)
            os.makedirs(out_dir, exist_ok=True)
            trans = translate_page(content, SOURCE_LANG, tgt_lang, tgt_deepl, "router/%s/" % ip, translated_slugs)
            with open(os.path.join(out_dir, "index.html"), 'w') as f:
                f.write(trans)
            print("  Saved: router/%s" % ip)
            time.sleep(2)

        print("\n%s done!" % LANG_NAMES[tgt_lang])
    print("\n\nAll languages done!")

if __name__ == "__main__":
    main()
