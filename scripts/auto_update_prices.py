#!/usr/bin/env python3
"""
ELEITOS — Auto Update Prices via SerpAPI (Google Shopping)
Corre via GitHub Actions: scripts/auto_update_prices.py
"""

import re
import time
import random
import os
import sys
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# ── Configuração ───────────────────────────────────────────────────────────────
HTML_FILE   = os.path.join(os.path.dirname(__file__), '..', 'index.html')
SERPAPI_KEY = os.environ.get("SERPAPI_KEY", "")
SERPAPI_URL = "https://serpapi.com/search.json"

# ── Produtos ───────────────────────────────────────────────────────────────────
PRODUCTS = [
    {"title": "Sony WH-1000XM5",                 "search": "Sony WH-1000XM5"},
    {"title": "Bose QuietComfort Ultra",          "search": "Bose QuietComfort Ultra Headphones"},
    {"title": "Samsung Neo QLED QN90D 55",        "search": "Samsung Neo QLED QN90D 55"},
    {"title": "LG C4 OLED 55",                    "search": "LG C4 OLED 55 polegadas"},
    {"title": "Apple iPhone 17 Pro Max",          "search": "Apple iPhone 17 Pro Max"},
    {"title": "Samsung Galaxy S26 Ultra",         "search": "Samsung Galaxy S26 Ultra"},
    {"title": "Sony WH-1000XM6",                  "search": "Sony WH-1000XM6"},
    {"title": "Apple Watch Ultra 3",              "search": "Apple Watch Ultra 3"},
    {"title": "DJI Osmo Pocket 4",               "search": "DJI Osmo Pocket 4"},
    {"title": "Bose QC Ultra Earbuds II",         "search": "Bose QuietComfort Ultra Earbuds"},
    {"title": "Logitech MX Mechanical Mini V2",   "search": "Logitech MX Mechanical Mini V2"},
    {"title": "LG UltraGear OLED 32",             "search": "LG UltraGear OLED 32 2024"},
    {"title": "Anker Nebula Capsule 3 Laser",     "search": "Anker Nebula Capsule 3 Laser"},
    {"title": "Shargeek 140W GaN",               "search": "Shargeek 140W GaN charger"},
    {"title": "Sony Bravia XR A95L",             "search": "Sony Bravia XR A95L QD-OLED"},
    {"title": "Apple iPhone 16 Pro Max",          "search": "Apple iPhone 16 Pro Max"},
    {"title": "Samsung Galaxy S25 Ultra",         "search": "Samsung Galaxy S25 Ultra"},
    {"title": "Google Pixel 9 Pro",              "search": "Google Pixel 9 Pro"},
    {"title": "Elgato Stream Deck MK.2",         "search": "Elgato Stream Deck MK2"},
    {"title": "Logitech MX Master 3S",           "search": "Logitech MX Master 3S"},
    {"title": "Amazon Echo Show",                "search": "Amazon Echo Show 10"},
    {"title": "Philips Hue Gradient Lightstrip", "search": "Philips Hue Gradient Lightstrip"},
    {"title": "Apple Watch Ultra 2",             "search": "Apple Watch Ultra 2"},
    {"title": "Garmin",                          "search": "Garmin Fenix 7X Pro Solar"},
    {"title": "Arc'teryx Beta AR Jacket",        "search": "Arcteryx Beta AR Jacket"},
    {"title": "Patagonia Nano Puff",             "search": "Patagonia Nano Puff Jacket"},
    {"title": "Levi's 501 Original Fit",         "search": "Levis 501 Original Fit jeans"},
    {"title": "New Balance 990v6",               "search": "New Balance 990v6"},
    {"title": "Adidas Samba OG",                 "search": "Adidas Samba OG"},
    {"title": "Salomon XT-6",                    "search": "Salomon XT-6"},
    {"title": "Geox J Perth Boy A",              "search": "Geox Perth Boy sneakers"},
    {"title": "LIONELO MIKA PLUS",               "search": "Lionelo Mika Plus stroller"},
]

# ── Vai buscar preço via SerpAPI Google Shopping ───────────────────────────────
def obter_preco(search_query):
    params = {
        "engine":   "google_shopping",
        "q":        search_query,
        "api_key":  SERPAPI_KEY,
        "gl":       "pt",        # Portugal
        "hl":       "pt",        # Português
        "currency": "EUR",
    }

    try:
        r = requests.get(SERPAPI_URL, params=params, timeout=30)
        data = r.json()

        if "error" in data:
            print(f"    ✗ SerpAPI erro: {data['error']}")
            return None

        resultados = data.get("shopping_results", [])
        if not resultados:
            print(f"    ⚠ Sem resultados Google Shopping")
            return None

        # Recolher todos os preços válidos
        precos = []
        for item in resultados[:10]:  # Top 10 resultados
            preco_raw = item.get("price", "")
            if not preco_raw:
                continue
            valor = converter_preco(preco_raw)
            if valor and 1 < valor < 50000:
                precos.append(valor)

        if not precos:
            print(f"    ⚠ Nenhum preço válido nos resultados")
            return None

        # Usar a mediana dos 3 preços mais baixos (evita outliers)
        precos.sort()
        amostra = precos[:3]
        mediana = sorted(amostra)[len(amostra) // 2]

        print(f"    📊 Preços encontrados: {[formatar_preco(p) for p in amostra]}")
        return formatar_preco(mediana)

    except requests.exceptions.Timeout:
        print(f"    ✗ Timeout")
        return None
    except Exception as e:
        print(f"    ✗ Erro: {e}")
        return None

# ── Converte string de preço para float ───────────────────────────────────────
def converter_preco(raw):
    try:
        raw = str(raw).replace('\xa0', '').replace('\u202f', '').replace(' ', '').strip()
        # Remover símbolo de moeda
        raw = re.sub(r'[€$£]', '', raw).strip()
        if ',' in raw and '.' in raw:
            # 1.299,99 → 1299.99
            raw = raw.replace('.', '').replace(',', '.')
        elif ',' in raw:
            # 349,99 → 349.99
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

# ── Atualiza preço no HTML ────────────────────────────────────────────────────
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

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    if not SERPAPI_KEY:
        print("❌ SERPAPI_KEY não encontrada. Adiciona o secret no GitHub.")
        sys.exit(1)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    print("=" * 60)
    print(f"  ELEITOS — Auto Update Prices (Google Shopping)")
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

        # Pequena pausa para não exceder rate limit da SerpAPI
        if i > 1:
            time.sleep(random.uniform(1.0, 2.0))

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
                print(f"    ✓ Sem alteração ({preco})")
                sem_alteracao.append(titulo)
        else:
            print(f"    ⚠ Título não encontrado no HTML")
            nao_encontrado.append(titulo)

    # Guardar HTML se houve alterações
    if atualizados:
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(str(soup))
        print(f"\n✅ index.html guardado com {len(atualizados)} atualização(ões)")
    else:
        print(f"\n✓ Sem alterações — index.html não modificado")

    # Resumo final
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
