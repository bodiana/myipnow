import os
from bs4 import BeautifulSoup

ROOT = r"C:\Users\Bodia\OneDrive\Робочий стіл\myipnow-main-17.10"

CATEGORIES = {
    "online-safety",
    "online-privacy",
    "networking",
    "ip-addresses",
    "home-computing",
    "general-topics",
}

CAT_SCRIPT_ID = "cat-return-v3"
ART_SCRIPT_ID = "article-return-v3"

# Injected on category list pages (index.html, pageN.html inside a category folder)
CAT_SCRIPT = r"""
<script id="cat-return-v3">
(function(){
  var KEY='catStateV3'; // { url, scroll }
  // Save scroll + current URL right before we navigate to an article
  function saveState(){
    try {
      var state = { url: location.pathname + location.search + location.hash,
                    scroll: (window.scrollY || window.pageYOffset || 0) };
      sessionStorage.setItem(KEY, JSON.stringify(state));
    } catch(e){}
  }
  function restore(){
    try{
      var raw = sessionStorage.getItem(KEY);
      if (!raw) return;
      var st = JSON.parse(raw);
      if (st && typeof st.scroll === 'number') {
        window.scrollTo(0, st.scroll);
      }
    }catch(e){}
  }
  function init(){
    // Only run on pages that have article listings
    var list = document.querySelector('.article-list');
    if (list){
      // Capture click as early as possible
      list.addEventListener('mousedown', function(e){
        var a = e.target && e.target.closest && e.target.closest('a');
        if (!a) return;
        // internal links only
        try { if (a.origin && a.origin !== location.origin) return; } catch(e){}
        saveState();
      }, true);
      list.addEventListener('click', function(e){
        var a = e.target && e.target.closest && e.target.closest('a');
        if (!a) return;
        try { if (a.origin && a.origin !== location.origin) return; } catch(e){}
        saveState();
      }, true);
    }
    // Restore scroll on load and bfcache
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', restore);
    } else {
      restore();
    }
    window.addEventListener('pageshow', function(ev){
      if (ev && ev.persisted) restore();
    });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
</script>
""".strip()

# Injected on article pages (index.html inside article folders)
ART_SCRIPT = r"""
<script id="article-return-v3">
(function(){
  var KEY='catStateV3'; // { url, scroll }
  var CAT_RE=/^\/(online-safety|online-privacy|networking|ip-addresses|home-computing|general-topics)\//;

  function init(){
    var btn = document.getElementById('returnToCategory');
    if (!btn) return;

    var raw = null, url=null;
    try {
      raw = sessionStorage.getItem(KEY);
      if (raw){
        var st = JSON.parse(raw);
        url = st && st.url;
      }
    } catch(e){}

    // If we have a stored category URL, use it
    if (url && CAT_RE.test(url)) {
      btn.setAttribute('href', url);
      return;
    }

    // Fallback: deduce category from article path and use /<cat>/index.html
    var parts = location.pathname.split('/').filter(Boolean);
    if (parts.length > 0) {
      var cat = '/' + parts[0] + '/';
      if (CAT_RE.test(cat)) {
        btn.setAttribute('href', cat + 'index.html');
      }
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
</script>
""".strip()

# Heuristic: category listing files
def is_category_file(dirpath, filename):
    base = os.path.basename(dirpath)
    if base not in CATEGORIES:
        return False
    if not filename.lower().endswith(".html"):
        return False
    if filename.lower() == "index.html":
        return True
    if filename.lower().startswith("page") and filename.lower().endswith(".html"):
        return True
    return False

# Heuristic: article pages are index.html in non-category folders
def is_article_index(dirpath, filename):
    if filename.lower() != "index.html":
        return False
    base = os.path.basename(dirpath)
    if base in CATEGORIES:
        return False
    return True

# Remove ONLY older return-to-category scripts we previously sprinkled
KILL_IDS = {
    "cat-return-v1","article-return-v1",
    "cat-return-v2","article-return-v2"
}
KILL_SNIPPETS = [
    "lastCategoryPath","lastCategoryScroll","lastCategoryURL",
    "backLink.setAttribute","Return to Category",
    "document.referrer","scrollPos_"
]

def tidy_old_return_scripts(soup):
    removed = 0
    for s in list(soup.find_all("script")):
        sid = s.get("id","")
        if sid in KILL_IDS:
            s.decompose()
            removed += 1
            continue
        # light heuristic
        txt = (s.string or "") + (s.get_text(strip=False) or "")
        if any(sn in txt for sn in KILL_SNIPPETS):
            s.decompose()
            removed += 1
    return removed

def ensure_script(soup, html, script_id):
    # Drop any existing same-id script
    for s in soup.find_all("script", id=script_id):
        s.decompose()
    body = soup.find("body")
    if not body:
        return False
    body.append(BeautifulSoup(html, "html.parser"))
    return True

patched_cats = 0
patched_articles = 0
removed_total = 0
touched = 0

for dirpath, _, filenames in os.walk(ROOT):
    for fn in filenames:
        full = os.path.join(dirpath, fn)
        try:
            if not (is_category_file(dirpath, fn) or is_article_index(dirpath, fn)):
                continue
            with open(full, "r", encoding="utf-8") as f:
                html = f.read()
            soup = BeautifulSoup(html, "html.parser")
            # remove old conflicting return scripts only (leave other scripts alone)
            removed_total += tidy_old_return_scripts(soup)
            if is_category_file(dirpath, fn):
                if ensure_script(soup, CAT_SCRIPT, CAT_SCRIPT_ID):
                    patched_cats += 1
                    touched += 1
            else:
                if ensure_script(soup, ART_SCRIPT, ART_SCRIPT_ID):
                    patched_articles += 1
                    touched += 1
            with open(full, "w", encoding="utf-8") as f:
                f.write(str(soup))
        except Exception:
            # keep going on parse/write issues
            pass

print(f"✅ Patched category listing pages: {patched_cats}")
print(f"✅ Patched article pages:         {patched_articles}")
print(f"🧹 Removed old return scripts:     {removed_total}")
print(f"📦 Files written:                  {touched}")
