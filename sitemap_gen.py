import json
import os
from datetime import datetime

def generate_perfect_sitemap(domain="https://myipnow.net"):
    index_file = 'search_index.json'
    sitemap_file = 'sitemap.xml'
    
    if not os.path.exists(index_file):
        print(f"Error: {index_file} not found.")
        return

    with open(index_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Keywords for pages to EXCLUDE (categories, tags, etc.)
    exclude = ['/page/', '/category/', '/tag/']
    
    now = datetime.now().strftime('%Y-%m-%d')
    
    # We use a set to prevent duplicate URLs
    final_urls = set()

    # 1. MANUALLY ADD THE HOMEPAGE FIRST to ensure it's never missing
    final_urls.add("/")

    # 2. Process the JSON data
    for item in data:
        url_path = item.get('url', '')
        
        # Skip if it's in the exclude list
        if any(x in url_path for x in exclude):
            continue

        # Clean the URL (remove .html and trailing slashes)
        clean_path = url_path.replace('.html', '').rstrip('/')
        
        # If it's empty after stripping, it's the root/homepage
        if clean_path == "":
            clean_path = "/"
            
        final_urls.add(clean_path)

    # 3. Build the XML structure
    xml_content = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]

    # Sort URLs so Homepage is at the top
    sorted_urls = sorted(list(final_urls), key=lambda x: (x != "/", x))

    for path in sorted_urls:
        full_url = f"{domain}{path}"
        # Homepage gets 1.0 priority, others get 0.8
        priority = "1.0" if path == "/" else "0.8"
        
        xml_content.append('  <url>')
        xml_content.append(f'    <loc>{full_url}</loc>')
        xml_content.append(f'    <lastmod>{now}</lastmod>')
        xml_content.append('    <changefreq>weekly</changefreq>')
        xml_content.append(f'    <priority>{priority}</priority>')
        xml_content.append('  </url>')

    xml_content.append('</urlset>')

    with open(sitemap_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(xml_content))
    
    print(f"✅ SUCCESS: {sitemap_file} generated with {len(sorted_urls)} URLs.")
    print(f"🏠 Homepage included: {domain}/")

if __name__ == "__main__":
    generate_perfect_sitemap()