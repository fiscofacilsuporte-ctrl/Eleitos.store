#!/usr/bin/env python3
"""
ELEITOS — Auto Update Prices via kuantokusta.pt
Corre via GitHub Actions: scripts/auto_update_prices.py
Pesquisa o preço mais baixo em kuantokusta.pt pelo nome do produto
e atualiza os preços em index.html.
"""

import re
import time
import random
import os
import sys
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import quote_plus

# ── Ficheiro HTML (relativo à raiz do repo) ────────────────────────────────────
HTML_FILE = os.path.join(os.path.dirname(__file__), '..', 'index.html')

# ── Produtos: title = card-title no HTML | search = query de pesquisa ──────────
PRODUCTS = [
    {"title": "Sony WH-1000XM5",                 "search": "Sony WH-1000XM5"},
    {"title": "Bose QuietComfort Ultra",          "search": "Bose QuietComfort Ultra Headphones"},
    {"title": "Samsung Neo QLED QN90D 55",        "search": "Samsung QN90D 55"},
    {"title": "LG C4 OLED 55",                    "search": "LG C4 OLED 55"},
    {"title": "Apple iPhone 17 Pro Max",          "search": "Apple iPhone 17 Pro Max"},
    {"title": "Samsung Galaxy S26 Ultra",         "search": "Samsung Galaxy S26 Ultra"},
    {"title": "Sony WH-1000XM6",                  "search": "Sony WH-1000XM6"},
    {"title": "Apple Watch Ultra 3",              "search": "Apple Watch Ultra 3"},
    {"title": "DJI Osmo Pocket 4",               "search": "DJI Osmo Pocket 4"},
    {"title": "Bose QC Ultra Earbuds II",         "search": "Bose QuietComfort Ultra Earbuds"},
    {"title": "Logitech MX Mechanical Mini V2",   "search": "Logitech MX Mechanical Mini V2"},
    {"title": "LG UltraGear OLED 32",             "search": "LG UltraGear OLED 32 2024"},
    {"title": "Anker Nebula Capsule 3 Laser",     "search": "Anker Nebula Capsule 3 Laser"},
    {"title": "Shargeek 140W GaN",               "search": "Shargeek 140W GaN"},
    {"title": "Sony Bravia XR A95L",             "search": "Sony Bravia A95L"},
    {"title": "Apple iPhone 16 Pro Max",          "search": "Apple iPhone 16 Pro Max"},
    {"title": "Samsung Galaxy S25 Ultra",         "search": "Samsung Galaxy S25 Ultra"},
    {"title": "Google Pixel 9 Pro",              "search": "Google Pixel 9 Pro"},
    {"title": "Elgato Stream Deck MK.2",         "search": "Elgato Stream Deck MK2"},
    {"title": "Logitech MX Master 3S",           "search": "Logitech MX Master 3S"},
    {"title": "Amazon Echo Show",                "search": "Amazon Echo Show 10"},
    {"title": "Philips Hue Gradient Lightstrip", "search": "Philips Hue Gradient Lightstrip"},
    {"title": "Apple Watch Ultra 2",             "search": "Apple Watch Ultra 2"},
    {"title": "Garmin",                          "search": "Garmin Fenix 7X Pro"},
    {"title": "Arc'teryx Beta AR Jacket",        "search": "Arcteryx Beta AR"},
    {"title": "Patagonia Nano Puff",             "search": "Patagonia Nano Puff"},
    {"title": "Levi's 501 Original Fit",         "search": "Levis 501 Original"},
    {"title": "New Balance 990v6",               "search": "New Balance 990v6"},
    {"title": "Adidas Samba OG",                 "search": "Adidas Samba OG"},
    {"title": "Salomon XT-6",                    "search": "Salomon XT-6"},
    {"title": "Geox J Perth Boy A",              "search": "Geox Perth Boy"},
    {"title": "LIONELO MIKA PLUS",               "search": "Lionelo Mika Plus"},
]

BASE_URL   = "https://www.kuantokusta.pt/search?search_query={query}&sort_by=preco_asc"
IDEALO_URL = "https://www.idealo.pt/pesquisa/{query}"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
]

def get_headers(referer="https://www.kuantokusta.pt/"):
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "pt-PT,pt;q=0.9,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": referer,
    }

def converter_preco(raw):
    try:
        raw = raw.replace('\xa0', '').replace('\u202f', '').replace(' ', '').strip()
        if ',' in raw and '.' in raw:
            raw = raw.replace('.', '').replace(',', '.')
        elif ',' in raw:
            raw = raw.replace(',', '.')
        return float(raw)
    except (ValueError, AttributeError):
        return None

def formatar_preco(valor_float):
    inteiro = round(valor_float)
    if inteiro >= 1000:
        formatado = f"{inteiro:,}".replace(",", ".")
    else:
        formatado = str(inteiro)
    return f"≈ €{formatado}"

def extrair_precos_da_pagina(html):
    soup = BeautifulSoup(html, "html.parser")
    precos = []

    seletores = [
        ".kk-product-price", ".product-price", ".preco", ".price",
        "[class*='price']", "[class*='preco']", "[itemprop='price']",
        ".best-price", ".lowest-price", ".sr-detailedItem__price",
        ".offerList-item__priceMin", ".price__top",
    ]

    for seletor in seletores:
        for el in soup.select(seletor):
            texto = el.get_text(strip=True)
            match = re.search(r'(\d[\d.,\s]*)\s*€|€\s*(\d[\d.,\s]*)', texto)
            if match:
                raw = (match.group(1) or match.group(2)).strip()
                valor = converter_preco(raw)
                if valor and 1 < valor < 50000:
                    precos.append(valor)

    return min(precos) if precos else None

def obter_preco(search_query):
    # — Tentativa 1: kuantokusta.pt
    url = BASE_URL.format(query=quote_plus(search_query))
    try:
        r = requests.get(url, headers=get_headers(), timeout=20)
        if r.status_code == 200:
            valor = extrair_precos_da_pagina(r.text)
            if valor:
                print(f"    📍 kuantokusta.pt → {formatar_preco(valor)}")
                return formatar_preco(valor)
        print(f"    ⚠ kuantokusta: sem resultado (HTTP {r.status_code})")
    except Exception as e:
        print(f"    ⚠ kuantokusta: {e}")

    time.sleep(random.uniform(2, 4))

    # — Tentativa 2: idealo.pt
    print(f"    🔄 A tentar idealo.pt...")
    url2 = IDEALO_URL.format(query=quote_plus(search_query))
    try:
        r2 = requests.get(url2, headers=get_headers("https://www.idealo.pt/"), timeout=20)
        if r2.status_code == 200:
            valor = extrair_precos_da_pagina(r2.text)
            if valor:
                print(f"    📍 idealo.pt → {formatar_preco(valor)}")
                return formatar_preco(valor)
        print(f"    ⚠ idealo: sem resultado (HTTP {r2.status_code})")
    except Exception as e:
        print(f"    ⚠ idealo: {e}")

    return None

def atualizar_html(soup, titulo, novo_preco):
    for h2 in soup.find_all("h2", class_="card-title"):
        h2_texto = h2.get_text(strip=True)
        if titulo.lower() in h2_texto.lower() or h2_texto.lower() in titulo.lower():
            card_body = h2.find_parent("div", class_="card-body")
            if card_body:
                span = card_body.find("span", class_="card-price")
                if span:
                    preco_antigo = span.get_text(strip=True)
                    span.string  = novo_preco
                    return True, h2_texto, preco_antigo
    return False, titulo, None

def main():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    print("=" * 60)
    print(f"  ELEITOS — Auto Update Prices (kuantokusta.pt)")
    print(f"  {timestamp}")
    print("=" * 60)

    html_path = os.path.abspath(HTML_FILE)
    if not os.path.exists(html_path):
        print(f"❌ Ficheiro não encontrado: {html_path}")
        sys.exit(1)

    with open(html_path, "r", encoding="utf-8") as f:
        conteudo = f.read()

    soup = BeautifulSoup(conteudo, "html.parser")

    atualizados    = []
    sem_preco      = []
    sem_alteracao  = []
    nao_encontrado = []
    total = len(PRODUCTS)

    for i, produto in enumerate(PRODUCTS, 1):
        titulo = produto["title"]
        search = produto["search"]

        print(f"\n[{i:02d}/{total}] {titulo}")
        print(f"    🔍 '{search}'")

        if i > 1:
            pausa = random.uniform(2.0, 4.0)
            print(f"    ⏳ {pausa:.1f}s...")
            time.sleep(pausa)

        preco = obter_preco(search)

        if preco is None:
            print(f"    ✗ Sem preço — mantido o atual")
            sem_preco.append(titulo)
            continue

        ok, h2_real, preco_antigo = atualizar_html(soup, titulo, preco)

        if ok:
            if preco_antigo != preco:
                print(f"    ✅ {preco_antigo} → {preco}")
                atualizados.append(f"{h2_real}: {preco_antigo} → {preco}")
            else:
                print(f"    ✓ Igual ({preco})")
                sem_alteracao.append(titulo)
        else:
            print(f"    ⚠ Título não encontrado no HTML")
            nao_encontrado.append(titulo)

    if atualizados:
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(str(soup))
        print(f"\n✅ index.html guardado com {len(atualizados)} atualização(ões)")
    else:
        print(f"\n✓ Sem alterações — index.html não modificado")

    print("\n" + "=" * 60)
    print(f"  ✅ Atualizados:   {len(atualizados)}")
    print(f"  ✓ Sem alteração: {len(sem_alteracao)}")
    print(f"  ⚠ Sem preço:     {len(sem_preco)}")
    print(f"  ✗ Não no HTML:   {len(nao_encontrado)}")

    if atualizados:
        print("\n  Alterações:")
        for l in atualizados:
            print(f"    · {l}")

    if sem_preco:
        print("\n  Verificar manualmente:")
        for p in sem_preco:
            print(f"    · {p}")

    print("=" * 60)

if __name__ == "__main__":
    main()
