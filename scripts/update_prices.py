#!/usr/bin/env python3
"""
Script para atualizar preços e dados de produtos automaticamente.
Pode ser executado via cron job ou webhook.

Exemplo de uso:
    python3 update_prices.py
    
Exemplo de cron job (executar diariamente às 6 da manhã):
    0 6 * * * /usr/bin/python3 /home/ubuntu/Eleitos/scripts/update_prices.py
"""

import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os

# Mapeamento de produtos para URLs de referência
PRODUCT_URLS = {
    "Sony WH-1000XM5": "https://www.worten.pt/produtos/auscultadores-bluetooth-sony-wh-1000xm5-headband-premium-over-ear-microfone-noise-cancelling-preto-7588185",
    "Apple Watch Ultra 2": "https://www.fnac.pt/Espaco-Apple/Apple-Watch-Ultra-2/n1489729",
    # Adicionar mais mapeamentos conforme necessário
}

def get_worten_price(url):
    """Extrai preço de um produto da Worten"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Procura pelo padrão de preço na Worten
        price_text = soup.find(string=lambda text: text and '€' in text and ',' in text)
        if price_text:
            return f"≈ {price_text.strip()}"
        return None
    except Exception as e:
        print(f"Erro ao obter preço de {url}: {e}")
        return None

def get_fnac_price(url):
    """Extrai preço de um produto da FNAC"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Procura pelo padrão de preço na FNAC
        price_text = soup.find(string=lambda text: text and '€' in text)
        if price_text:
            return f"≈ {price_text.strip()}"
        return None
    except Exception as e:
        print(f"Erro ao obter preço de {url}: {e}")
        return None

def update_products_json(json_path):
    """Atualiza o ficheiro JSON com os preços mais recentes"""
    
    if not os.path.exists(json_path):
        print(f"Ficheiro {json_path} não encontrado")
        return False
    
    with open(json_path, 'r', encoding='utf-8') as f:
        products = json.load(f)
    
    updated_count = 0
    
    for product in products:
        product_name = product.get('name', '')
        
        # Se temos uma URL mapeada, tentar atualizar
        if product_name in PRODUCT_URLS:
            url = PRODUCT_URLS[product_name]
            print(f"Atualizando {product_name}...")
            
            # Determinar qual scraper usar baseado na URL
            if 'worten' in url:
                new_price = get_worten_price(url)
            elif 'fnac' in url:
                new_price = get_fnac_price(url)
            else:
                new_price = None
            
            if new_price:
                product['price'] = new_price
                product['last_updated'] = datetime.now().isoformat()
                updated_count += 1
                print(f"  ✓ Preço atualizado para {new_price}")
            else:
                print(f"  ✗ Não foi possível atualizar o preço")
    
    # Guardar o ficheiro atualizado
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    
    print(f"\nAtualização concluída: {updated_count} produtos atualizados")
    return True

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, '..', 'products.json')
    
    print(f"Iniciando atualização de preços em {datetime.now().isoformat()}")
    update_products_json(json_path)
    print("Concluído!")
