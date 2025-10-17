import os
from bs4 import BeautifulSoup

# === CONFIG ===
ROOT_PATH = r"C:\Users\Bodia\OneDrive\Робочий стіл\myipnow-main"
CATEGORIES = [
    "online-safety",
    "online-privacy",
    "networking",
    "ip-addresses",
    "home-computing",
    "general-topics"
]

# Number of pages per category will be counted automatically
def get_html_pages(category_path):
    """Return sorted list of HTML files in folder."""
    pages = [f for f in os.listdir(category_path) if f.endswith(".html")]
    # Ensure index.html is first
    pages.sort(key=lambda x: (0 if x == "index.html" else 1, x))
    return pages

def generate_pagination(current_index, total_pages, pages):
    """Return desktop + mobile pagination HTML as string."""
    # Desktop pagination: show previous, next, and some page numbers
    desktop_html = '<nav aria-label="Page navigation" class="pagination desktop-pagination">\n'

    if current_index > 0:
        desktop_html += f'<a href="{pages[current_index-1]}">← Previous</a> '
    else:
        desktop_html += f'<span class="disabled">← Previous</span> '

    # Show first, last, current +-2, with ellipsis if needed
    for i, page in enumerate(pages):
        page_num = i + 1
        if page_num == 1 or page_num == total_pages or abs(i - current_index) <= 2:
            if i == current_index:
                desktop_html += f'<span class="current">{page_num}</span> '
            else:
                desktop_html += f'<a href="{page}">{page_num}</a> '
        elif i == 1 and current_index > 3:
            desktop_html += '<span>…</span> '
        elif i == total_pages - 2 and current_index < total_pages - 4:
            desktop_html += '<span>…</span> '

    if current_index < total_pages - 1:
        desktop_html += f'<a href="{pages[current_index+1]}">Next →</a>'
    else:
        desktop_html += f'<span class="disabled">Next →</span>'
    desktop_html += '</nav>\n'

    # Mobile pagination: only prev / current / next
    mobile_html = '<nav aria-label="Page navigation" class="pagination mobile-pagination">\n'
    if current_index > 0:
        mobile_html += f'<a href="{pages[current_index-1]}">← Prev</a>'
    else:
        mobile_html += f'<span class="disabled">← Prev</span>'
    mobile_html += f'<span class="current">{current_index+1} / {total_pages}</span>'
    if current_index < total_pages - 1:
        mobile_html += f'<a href="{pages[current_index+1]}">Next →</a>'
    else:
        mobile_html += f'<span class="disabled">Next →</span>'
    mobile_html += '\n</nav>'

    return desktop_html + mobile_html

def update_pagination_in_file(file_path, pagination_html):
    """Replace existing pagination with new HTML."""
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    # Remove existing <nav> with class pagination
    for nav in soup.find_all("nav", class_="pagination"):
        nav.decompose()

    # Insert new pagination before </main>
    main_tag = soup.find("main")
    if main_tag:
        main_tag.append(BeautifulSoup(pagination_html, "html.parser"))

    # Save back
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(str(soup))

def process_category(category_name):
    category_path = os.path.join(ROOT_PATH, category_name)
    pages = get_html_pages(category_path)
    total_pages = len(pages)

    for i, page_file in enumerate(pages):
        file_path = os.path.join(category_path, page_file)
        pagination_html = generate_pagination(i, total_pages, pages)
        update_pagination_in_file(file_path, pagination_html)
        print(f"Updated pagination in {file_path}")

if __name__ == "__main__":
    for cat in CATEGORIES:
        process_category(cat)
    print("✅ All categories updated with correct desktop & mobile pagination.")
