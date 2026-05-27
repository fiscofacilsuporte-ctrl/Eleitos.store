import re
import requests
from bs4 import BeautifulSoup
import time
import os

# Configurações
HTML_PATH = os.path.join(os.path.dirname(__file__), '..', 'index.html')
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

def get_amazon_price(url):
    """Tenta obter o preço de um link da Amazon (incluindo amzn.to)"""
    headers = {"User-Agent": USER_AGENT, "Accept-Language": "pt-PT,pt;q=0.9,en-US;q=0.8,en;q=0.7"}
    try:
        # Seguir redirecionamento se for amzn.to
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Seletores comuns para preço na Amazon (.es, .com, .br)
        price_selectors = [
            ".a-price-whole", 
            "#priceblock_ourprice", 
            "#priceblock_dealprice",
            "span.a-offscreen"
        ]
        
        for selector in price_selectors:
            price_el = soup.select_one(selector)
            if price_el:
                price_text = price_el.get_text().strip()
                # Limpar o texto para manter apenas números e separadores decimais
                # Ex: "1.429,00€" -> "1.429"
                match = re.search(r'(\d+[\.,]\d+|\d+)', price_text)
                if match:
                    val = match.group(1).replace(',', '.')
                    # Arredondar ou formatar como inteiro se for o caso
                    try:
                        float_val = float(val)
                        return int(float_val)
                    except:
                        return val
        return None
    except Exception as e:
        print(f"Erro ao aceder a {url}: {e}")
        return None

def update_html():
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex para encontrar blocos de produtos que têm link da Amazon e preço
    # Vamos procurar por padrões de card-price seguidos de cta-btn com link amzn.to
    # Ou vice-versa. No index.html o preço vem antes do botão.
    
    # Padrão: <span class="card-price">≈ €VALOR</span> ... <a href="LINK_AMAZON"
    pattern = re.compile(r'(<span class="card-price">≈ €)([\d\.,]+)(</span>.*?<a href="(https?://amzn\.to/[\w-]+)")', re.DOTALL)
    
    matches = pattern.findall(content)
    print(f"Encontrados {len(matches)} produtos para atualizar.")
    
    new_content = content
    for prefix, old_price, suffix, url in matches:
        print(f"A verificar preço para: {url} (Preço atual: {old_price})")
        new_price = get_amazon_price(url)
        
        if new_price and str(new_price) != old_price:
            print(f"  -> Novo preço encontrado: €{new_price}")
            # Substituir apenas esta ocorrência específica
            old_segment = f"{prefix}{old_price}{suffix}"
            new_segment = f"{prefix}{new_price}{suffix}"
            new_content = new_content.replace(old_segment, new_segment)
            # Pausa para evitar bloqueio da Amazon
            time.sleep(2)
        else:
            print(f"  -> Preço mantido ou não encontrado.")

    with open(HTML_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Atualização concluída.")

if __name__ == "__main__":
    update_html()
