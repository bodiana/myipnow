import os, re, shutil

# --- The working dropdown script ---
FINAL_SCRIPT = """<script id="mobile-header-fix-final">
(function(){
  const tools = document.querySelector('.nav-tools');
  if(!tools) return;
  const trigger = tools.querySelector(':scope > a');
  const dropdown = tools.querySelector(':scope > ul');
  if(!trigger || !dropdown) return;

  let menu=null, backdrop=null, open=false;
  tools.addEventListener('mouseenter',()=>{if(window.innerWidth>768)dropdown.style.display='block';});
  tools.addEventListener('mouseleave',()=>{if(window.innerWidth>768)dropdown.style.display='none';});

  function closeMenu(){ if(menu){menu.remove();menu=null;} if(backdrop){backdrop.remove();backdrop=null;} document.body.classList.remove('menu-open'); open=false; }

  function openMenu(e){
    e.preventDefault(); e.stopPropagation();
    if(window.innerWidth>768) return;
    if(open){ closeMenu(); return; }
    const rect=trigger.getBoundingClientRect();
    backdrop=document.createElement('div');
    Object.assign(backdrop.style,{position:'fixed',top:0,left:0,width:'100vw',height:'100vh',background:'transparent',zIndex:9998});
    backdrop.addEventListener('click',closeMenu);
    document.body.appendChild(backdrop);
    menu=dropdown.cloneNode(true);
    Object.assign(menu.style,{position:'absolute',top:`${rect.bottom + window.scrollY + 8}px`,left:`${rect.left + window.scrollX}px`,minWidth:`${Math.max(rect.width,200)}px`,background:'#fff',border:'1px solid #e2e8f0',borderRadius:'10px',boxShadow:'0 10px 30px rgba(0,0,0,0.15)',listStyle:'none',padding:'.5rem 0',margin:0,zIndex:9999,maxHeight:'70vh',overflowY:'auto'});
    menu.querySelectorAll('a').forEach(a=>{a.style.display='block';a.style.padding='.6rem 1.2rem';a.style.color='#1e293b';a.style.textDecoration='none';a.style.fontWeight='500';a.addEventListener('mouseenter',()=>a.style.color='#4f46e5');a.addEventListener('mouseleave',()=>a.style.color='#1e293b');});
    document.body.appendChild(menu);
    document.body.classList.add('menu-open');
    open=true;
  }

  window.addEventListener('scroll',()=>{if(!open||!menu)return;const rect=trigger.getBoundingClientRect();menu.style.top=`${rect.bottom + window.scrollY + 8}px`;menu.style.left=`${rect.left + window.scrollX}px`;});
  window.addEventListener('resize',closeMenu);
  trigger.addEventListener('click',openMenu);
  trigger.addEventListener('touchstart',openMenu,{passive:false});
})();
</script>"""

# --- Old dropdown fix pattern ---
OLD_SCRIPT_PATTERN = re.compile(
    r'<script[^>]+id=["\']mobile-header-fix-[^>]+>.*?</script>',
    re.DOTALL | re.IGNORECASE
)

# --- CSS structure pattern: must contain both .nav-tools and .category-nav definitions ---
CSS_CHECK_PATTERN = re.compile(r'\.nav-tools|\.category-nav', re.IGNORECASE)

def safe_fix_html(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
    except Exception as e:
        print(f"⚠️ Skipped {path}: read error {e}")
        return False

    # basic validation
    if '<body' not in html or '</body>' not in html:
        print(f"⚠️ Skipped {path}: missing body tags")
        return False
    if '.nav-tools' not in html:
        print(f"⚠️ Skipped {path}: no nav-tools structure")
        return False

    # detect abnormal css (different structure)
    style_blocks = re.findall(r'<style[^>]*>(.*?)</style>', html, re.DOTALL | re.IGNORECASE)
    css_combined = "\n".join(style_blocks)
    if not CSS_CHECK_PATTERN.search(css_combined):
        # mark as different layout
        bak = path + '.checkme.bak'
        shutil.copy2(path, bak)
        print(f"❌ Layout differs, check manually: {path}")
        return False

    # remove old dropdown scripts
    cleaned = re.sub(OLD_SCRIPT_PATTERN, '', html)

    # skip if script already exists
    if 'mobile-header-fix-final' in cleaned:
        return False

    # backup before writing
    backup_path = path + '.bak'
    shutil.copy2(path, backup_path)

    # inject final script safely
    cleaned = cleaned.replace('</body>', FINAL_SCRIPT + '\n</body>')

    with open(path, 'w', encoding='utf-8') as f:
        f.write(cleaned)

    print(f"✅ Updated safely: {path}")
    return True


def main():
    total = 0
    for root, _, files in os.walk('.'):
        for file in files:
            if not file.endswith('.html') or file == 'hide-my-ip.html':
                continue
            full = os.path.join(root, file)
            if safe_fix_html(full):
                total += 1
    print(f"\n🎯 Done. {total} page(s) safely updated (with backups).")

if __name__ == '__main__':
    main()
