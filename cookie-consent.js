(function(){
  var KEY='myipnow_consent';
  function get(){return localStorage.getItem(KEY);}
  function set(v){localStorage.setItem(KEY,v);}
  function loadGTM(){
    window.dataLayer=window.dataLayer||[];
    window.dataLayer.push({'gtm.start':new Date().getTime(),event:'gtm.js'});
    var f=document.getElementsByTagName('script')[0],j=document.createElement('script');
    j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id=GTM-T6F8FV6T';
    f.parentNode.insertBefore(j,f);
  }
  function showBanner(){
    var b=document.createElement('div');
    b.id='cookie-banner';
    b.innerHTML='<div style="max-width:800px;margin:0 auto;display:flex;align-items:center;flex-wrap:wrap;gap:12px;">'
      +'<p style="flex:1;min-width:200px;margin:0;font-size:0.9rem;color:#f1f5f9;">We use cookies for analytics and advertising. <a href="/privacy-policy/" style="color:#a5b4fc;text-decoration:underline;">Learn more</a></p>'
      +'<div style="display:flex;gap:8px;flex-shrink:0;">'
      +'<button id="cookie-accept" style="padding:8px 20px;background:#4f46e5;color:#fff;border:none;border-radius:8px;cursor:pointer;font-weight:600;">Accept</button>'
      +'<button id="cookie-decline" style="padding:8px 20px;background:transparent;color:#94a3b8;border:1px solid #475569;border-radius:8px;cursor:pointer;">Decline</button>'
      +'</div></div>';
    Object.assign(b.style,{position:'fixed',bottom:'0',left:'0',right:'0',background:'#1e293b',padding:'16px 24px',zIndex:'99999',boxShadow:'0 -4px 20px rgba(0,0,0,0.25)'});
    document.body.appendChild(b);
    document.getElementById('cookie-accept').onclick=function(){set('accepted');b.remove();loadGTM();};
    document.getElementById('cookie-decline').onclick=function(){set('declined');b.remove();};
  }
  var c=get();
  if(c==='accepted'){loadGTM();}
  else if(!c){document.readyState==='loading'?document.addEventListener('DOMContentLoaded',showBanner):showBanner();}
})();
