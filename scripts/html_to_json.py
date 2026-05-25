import json
from bs4 import BeautifulSoup
import os

def extract_products(html_path):
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    products = []
    grid = soup.find('div', id='product-grid')
    if not grid:
        return []
        
    articles = grid.find_all('article', class_='product-card')
    for article in articles:
        category = article.get('data-category', '')
        
        media_area = article.find('div', class_='media-area')
        img_tag = media_area.find('img') if media_area else None
        img_url = img_tag['src'] if img_tag else ''
        
        name_tag = article.find('h2', class_='product-name')
        name = name_tag.get_text(strip=True) if name_tag else ''
        
        verdict_tag = article.find('p', class_='verdict-text')
        verdict = verdict_tag.get_text(strip=True) if verdict_tag else ''
        
        price_tag = article.find('span', class_='price-label')
        price = price_tag.get_text(strip=True) if price_tag else ''
        
        stars_tag = article.find('span', class_='stars')
        stars = stars_tag.get_text(strip=True) if stars_tag else ''
        
        count_tag = article.find('span', class_='stars-count')
        stars_count = count_tag.get_text(strip=True) if count_tag else ''
        
        cta_tag = article.find('a', class_='cta-btn')
        cta_link = cta_tag['href'] if cta_tag else ''
        
        products.append({
            'name': name,
            'category': category,
            'image': img_url,
            'verdict': verdict,
            'price': price,
            'stars': stars,
            'stars_count': stars_count,
            'cta_link': cta_link,
            'brand_site': '' # To be filled
        })
    
    return products

if __name__ == "__main__":
    html_file = '/home/ubuntu/Eleitos/index.html'
    output_file = '/home/ubuntu/Eleitos/products.json'
    
    if not os.path.exists('/home/ubuntu/Eleitos/scripts'):
        os.makedirs('/home/ubuntu/Eleitos/scripts')
        
    prods = extract_products(html_file)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(prods, f, indent=2, ensure_ascii=False)
    
    print(f"Extraídos {len(prods)} produtos para {output_file}")
