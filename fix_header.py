import os
import re

# --- Corrected dropdown script that ensures visibility ---
FIXED_SCRIPT = """<script id="mobile-header-fix-final">
(function(){
  const tools = document.querySelector('.nav-tools');
  if(!tools) return;
  const trigger = tools.querySelector(':scope > a');
  const dropdown = tools.querySelector(':scope > ul');
  if(!trigger || !dropdown) return;

  let menu=null, backdrop=null, open=false;

  // Desktop hover
  tools.addEventListener('mouseenter',()=>{ if(window.innerWidth>768) dropdown.style.display='block'; });
  tools.addEventListener('mouseleave',()=>{ if(window.innerWidth>768) dropdown.style.display='none'; });

  function closeMenu(){
    if(menu){ menu.remove(); menu=null; }
    if(backdrop){ backdrop.remove(); backdrop=null; }
    dropdown.style.display='none';
    document.body.classList.remove('menu-open');
    open=false;
  }

  function openMenu(e){
    e.preventDefault(); e.stopPropagation();
    if(window.innerWidth>768) return;

    dropdown.style.display='none'; // hide original header dropdown

    if(open){ closeMenu(); return; }

    const rect = trigger.getBoundingClientRect();
    backdrop = document.createElement('div');
    Object.assign(backdrop.style,{
      position:'fixed',top:0,left:0,width:'100vw',height:'100vh',
      background:'transparent',zIndex:9998
    });
    backdrop.addEventListener('click', closeMenu);
    document.body.appendChild(backdrop);

    menu = dropdown.cloneNode(true);
    Object.assign(menu.style,{
      position:'absolute',
      top:`${rect.bottom + window.scrollY + 8}px`,
      left:`${rect.left + window.scrollX}px`,
      minWidth:`${Math.max(rect.width,200)}px`,
      background:'#fff',
      border:'1px solid #e2e8f0',
      borderRadius:'10px',
      boxShadow:'0 10px 30px rgba(0,0,0,0.15)',
      listStyle:'none',
      padding:'.5rem 0',
      margin:0,
      zIndex:9999,
      maxHeight:'70vh',
      overflowY:'auto',
      display:'block',        /* ✅ ensures visible */
      visibility:'visible',   /* ✅ fixes Safari hover ghost */
      opacity:'1'             /* ✅ fully visible */
    });
    menu.querySelectorAll('a').forEach(a=>{
      a.style.display='block';
      a.style.padding='.6rem 1.2rem';
      a.style.color='#1e293b';
      a.style.textDecoration='none';
      a.style.fontWeight='500';
      a.addEventListener('mouseenter',()=>a.style.color='#4f46e5');
      a.addEventListener('mouseleave',()=>a.style.color='#1e293b');
    });

    document.body.appendChild(menu);
    document.body.classList.add('menu-open');
    open=true;
  }

  window.addEventListener('scroll',()=>{ if(!open||!menu)return;
    const rect=trigger.getBoundingClientRect();
    menu.style.top=`${rect.bottom + window.scrollY + 8}px`;
    menu.style.left=`${rect.left + window.scrollX}px`;
  });
  window.addEventListener('resize',closeMenu);
  trigger.addEventListener('click',openMenu);
  trigger.addEventListener('touchstart',openMenu,{passive:false});
})();
</script>"""

# --- Regex to detect and replace old script ---
PATTERN = re.compile(
    r'<script[^>]+id=["\']mobile-header-fix-final["\'][^>]*>.*?</script>',
    re.DOTALL | re.IGNORECASE
)

# --- Root path of your project ---
ROOT = r"C:\Users\Bodia\OneDrive\Робочий стіл\myipnow-main"

def replace_dropdown_script(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            html = f.read()
    except Exception as e:
        print(f"⚠️ Could not read {filepath}: {e}")
        return False

    if "mobile-header-fix-final" not in html:
        return False

    new_html = re.sub(PATTERN, FIXED_SCRIPT, html)
    if new_html != html:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_html)
        print(f"✅ Fixed: {filepath}")
        return True
    return False

def main():
    fixed_count = 0
    for root, _, files in os.walk(ROOT):
        for name in files:
            if not name.endswith(".html"):
                continue
            full = os.path.join(root, name)
            if replace_dropdown_script(full):
                fixed_count += 1
    print(f"\n🎯 Done. Updated {fixed_count} HTML file(s) with visible mobile dropdown fix.")

if __name__ == "__main__":
    main()
