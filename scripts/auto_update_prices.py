#!/usr/bin/env python3
"""
ELEITOS — Auto Update Prices
Pesquisa diretamente na Amazon.es via SerpAPI — preços exatos sem ruído.
Fallback: Google Shopping com filtro de outliers.
"""

import re, time, random, os, sys, requests
from bs4 import BeautifulSoup
from datetime import datetime

HTML_FILE   = os.path.join(os.path.dirname(__file__), '..', 'index.html')
SERPAPI_KEY = os.environ.get("SERPAPI_KEY", "")
SERPAPI_URL = "https://serpapi.com/search.json"

PRODUCTS = [
    {"title": "Sony WH-1000XM5",                 "search": "Sony WH-1000XM5"},
    {"title": "Bose QuietComfort Ultra",          "search": "Bose QuietComfort Ultra Headphones"},
    {"title": "Samsung Neo QLED QN90D 55",        "search": "Samsung Neo QLED QN90D 55"},
    {"title": "LG C4 OLED 55",                    "search": "LG OLED55C44LA"},
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
    {"title": "Sony Bravia XR A95L",             "search": "Sony XR-55A95L"},
    {"title": "Apple iPhone 16 Pro Max",          "search": "Apple iPhone 16 Pro Max 256GB"},
    {"title": "Samsung Galaxy S25 Ultra",         "search": "Samsung Galaxy S25 Ultra 256GB"},
    {"title": "Google Pixel 9 Pro",              "search": "Google Pixel 9 Pro 128GB"},
    {"title": "Elgato Stream Deck MK.2",         "search": "Elgato Stream Deck MK.2"},
    {"title": "Logitech MX Master 3S",           "search": "Logitech MX Master 3S"},
    {"title": "Amazon Echo Show",                "search": "Amazon Echo Show 10"},
    {"title": "Philips Hue Gradient Lightstrip", "search": "Philips Hue Gradient Lightstrip"},
    {"title": "Apple Watch Ultra 2",             "search": "Apple Watch Ultra 2"},
    {"title": "Garmin",                          "search": "Garmin Fenix 7X Pro Solar"},
    {"title": "Arc'teryx Beta AR Jacket",        "search": "Arcteryx Beta AR Jacket"},
    {"title": "Patagonia Nano Puff",             "search": "Patagonia Nano Puff"},
    {"title": "Levi's 501 Original Fit",         "search": "Levis 501 Original Fit"},
    {"title": "New Balance 990v6",               "search": "New Balance 990v6"},
    {"title": "Adidas Samba OG",                 "search": "Adidas Samba OG"},
    {"title": "Salomon XT-6",                    "search": "Salomon XT-6"},
    {"title": "Geox J Perth Boy A",              "search": "Geox Perth Boy"},
    {"title": "LIONELO MIKA PLUS",               "search": "Lionelo Mika Plus"},
]

# ── Utilitários ────────────────────────────────────────────────────────────────
def converter_preco(raw):
    try:
        raw = str(raw).replace('\xa0','').replace('\u202f','').replace(' ','').strip()
        raw = re.sub(r'[€$£]', '', raw).strip()
        if ',' in raw and '.' in raw:
            raw = raw.replace('.','').replace(',','.')
        elif ',' in raw:
            raw = raw.replace(',','.')
        v = float(raw)
        return v if 1 < v < 100000 else None
    except:
        return None

def formatar_preco(valor):
    i = round(valor)
    return f"≈ €{i:,}".replace(",",".") if i >= 1000 else f"≈ €{i}"

def mediana_filtrada(lista):
    """Remove outliers (<50% ou >250% da mediana bruta) e devolve mediana limpa."""
    precos = sorted([p for p in lista if p])
    if not precos:
        return None
    med_bruta = precos[len(precos) // 2]
    limpos = [p for p in precos if med_bruta * 0.5 <= p <= med_bruta * 2.5]
    if not limpos:
        limpos = precos
    return limpos[len(limpos) // 2]

# ── Engine 1: Amazon.es direto ─────────────────────────────────────────────────
def preco_amazon(search_query):
    params = {
        "engine":        "amazon",
        "k":             search_query,
        "api_key":       SERPAPI_KEY,
        "amazon_domain": "amazon.es",
        "language":      "es_ES",
    }
    try:
        r = requests.get(SERPAPI_URL, params=params, timeout=30)
        data = r.json()

        if "error" in data:
            print(f"    ⚠ Amazon engine: {data['error']}")
            return None

        resultados = data.get("organic_results", [])
        if not resultados:
            print(f"    ⚠ Amazon.es: sem resultados")
            return None

        precos = []
        for item in resultados[:8]:
            # O campo price pode ser dict ou string consoante a versão da API
            p = item.get("price")
            if isinstance(p, dict):
                valor = p.get("value") or converter_preco(p.get("raw", ""))
            else:
                valor = converter_preco(str(p)) if p else None
            if valor:
                precos.append(float(valor))

        if not precos:
            print(f"    ⚠ Amazon.es: preços não extraídos")
            return None

        resultado = mediana_filtrada(precos)
        if resultado:
            print(f"    🛒 Amazon.es | {len(precos)} resultados | mediana: {formatar_preco(resultado)}")
        return formatar_preco(resultado) if resultado else None

    except Exception as e:
        print(f"    ⚠ Amazon engine erro: {e}")
        return None

# ── Engine 2: Google Shopping (fallback) ──────────────────────────────────────
def preco_google_shopping(search_query):
    params = {
        "engine":   "google_shopping",
        "q":        search_query,
        "api_key":  SERPAPI_KEY,
        "gl":       "pt",
        "hl":       "pt",
        "currency": "EUR",
        "num":      "20",
    }
    try:
        r = requests.get(SERPAPI_URL, params=params, timeout=30)
        data = r.json()

        if "error" in data:
            return None

        resultados = data.get("shopping_results", [])
        precos = [converter_preco(i.get("price","")) for i in resultados]
        precos = [p for p in precos if p]

        if not precos:
            return None

        resultado = mediana_filtrada(precos)
        if resultado:
            print(f"    🛍 Google Shopping | {len(precos)} resultados | mediana: {formatar_preco(resultado)}")
        return formatar_preco(resultado) if resultado else None

    except Exception as e:
        print(f"    ⚠ Google Shopping erro: {e}")
        return None

# ── Orquestrador ──────────────────────────────────────────────────────────────
def obter_preco(search_query):
    # Tenta Amazon.es primeiro — fonte mais fiável e coerente com os links
    preco = preco_amazon(search_query)
    if preco:
        return preco

    print(f"    🔄 Fallback → Google Shopping")
    time.sleep(random.uniform(1.0, 2.0))
    return preco_google_shopping(search_query)

# ── Atualiza HTML ─────────────────────────────────────────────────────────────
def atualizar_html(soup, titulo, novo_preco):
    for h2 in soup.find_all("h2", class_="card-title"):
        txt = h2.get_text(strip=True)
        if titulo.lower() in txt.lower() or txt.lower() in titulo.lower():
            cb = h2.find_parent("div", class_="card-body")
            if cb:
                span = cb.find("span", class_="card-price")
                if span:
                    antigo = span.get_text(strip=True)
                    span.string = novo_preco
                    return True, txt, antigo
    return False, titulo, None

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    if not SERPAPI_KEY:
        print("❌ SERPAPI_KEY não encontrada.")
        sys.exit(1)

    print("=" * 60)
    print(f"  ELEITOS — Auto Update Prices (Amazon.es)")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)

    html_path = os.path.abspath(HTML_FILE)
    with open(html_path, "r", encoding="utf-8") as f:
        conteudo = f.read()
    soup = BeautifulSoup(conteudo, "html.parser")

    atualizados, sem_preco, sem_alteracao, nao_encontrado = [], [], [], []

    for i, produto in enumerate(PRODUCTS, 1):
        titulo, search = produto["title"], produto["search"]
        print(f"\n[{i:02d}/{len(PRODUCTS)}] {titulo}")
        print(f"    🔍 '{search}'")

        if i > 1:
            time.sleep(random.uniform(1.5, 2.5))

        preco = obter_preco(search)

        if not preco:
            print(f"    ✗ Sem preço — mantido")
            sem_preco.append(titulo)
            continue

        ok, h2_real, antigo = atualizar_html(soup, titulo, preco)
        if ok:
            if antigo != preco:
                print(f"    ✅ {antigo} → {preco}")
                atualizados.append(f"{h2_real}: {antigo} → {preco}")
            else:
                print(f"    ✓ Igual ({preco})")
                sem_alteracao.append(titulo)
        else:
            print(f"    ⚠ Não encontrado no HTML")
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
        for l in atualizados: print(f"    · {l}")
    if sem_preco:
        print("\n  Verificar manualmente:")
        for p in sem_preco: print(f"    · {p}")
    print("=" * 60)

if __name__ == "__main__":
    main()
