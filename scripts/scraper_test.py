import requests
from bs4 import BeautifulSoup
import json

def get_worten_price(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Worten price selector (can change, this is a guess based on common patterns)
        price_tag = soup.find('span', class_='w-product__price__current')
        if not price_tag:
            price_tag = soup.select_one('.price__current')
            
        if price_tag:
            return price_tag.get_text(strip=True)
        return "Preço não encontrado"
    except Exception as e:
        return f"Erro: {str(e)}"

if __name__ == "__main__":
    # Test with a known URL from search results
    sony_url = "https://www.worten.pt/produtos/auscultadores-bluetooth-sony-wh-1000xm5-headband-premium-over-ear-microfone-noise-cancelling-preto-7588185"
    print(f"Testando Worten (Sony): {get_worten_price(sony_url)}")
