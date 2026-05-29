#!/usr/bin/env python3
"""
ELEITOS — Auto Update Prices
Google Shopping filtrado para amazon.es — preços reais sem ruído.
"""

import re, time, random, os, sys, requests
from bs4 import BeautifulSoup
from datetime import datetime

HTML_FILE   = os.path.join(os.path.dirname(__file__), '..', 'index.html')
SERPAPI_KEY = os.environ.get("SERPAPI_KEY", "")
SERPAPI_URL = "https://serpapi.com/search.json"

PRODUCTS = [
    {"title": "Sony WH-1000XM5",                 "search": "Sony WH-1000XM5 site:amazon.es"},
    {"title": "Bose QuietComfort Ultra",          "search": "Bose QuietComfort Ultra Headphones site:amazon.es"},
    {"title": "Samsung Neo QLED QN90D 55",        "search": "Samsung Neo QLED QN90D 55 site:amazon.es"},
    {"title": "LG C4 OLED 55",                    "search": "LG OLED55C44 site:amazon.es"},
    {"title": "Apple iPhone 17 Pro Max",          "search": "Apple iPhone 17 Pro Max site:amazon.es"},
    {"title": "Samsung Galaxy S26 Ultra",         "search": "Samsung Galaxy S26 Ultra site:amazon.es"},
    {"title": "Sony WH-1000XM6",                  "search": "Sony WH-1000XM6 site:amazon.es"},
    {"title": "Apple Watch Ultra 3",              "search": "Apple Watch Ultra 3 site:amazon.es"},
    {"title": "DJI Osmo Pocket 4",               "search": "DJI Osmo Pocket 4 site:amazon.es"},
    {"title": "Bose QC Ultra Earbuds II",         "search": "Bose QuietComfort Ultra Earbuds site:amazon.es"},
    {"title": "Logitech MX Mechanical Mini V2",   "search": "Logitech MX Mechanical Mini V2 site:amazon.es"},
    {"title": "LG UltraGear OLED 32",             "search": "LG UltraGear OLED 32 2024 site:amazon.es"},
    {"title": "Anker Nebula Capsule 3 Laser",     "search": "Anker Nebula Capsule 3 Laser site:amazon.es"},
    {"title": "Shargeek 140W GaN",               "search": "Shargeek 140W GaN site:amazon.es"},
    {"title": "Sony Bravia XR A95L",             "search": "Sony Bravia XR A95L site:amazon.es"},
    {"title": "Apple iPhone 16 Pro Max",          "search": "Apple iPhone 16 Pro Max 256GB site:amazon.es"},
    {"title": "Samsung Galaxy S25 Ultra",         "search": "Samsung Galaxy S25 Ultra 256GB site:amazon.es"},
    {"title": "Google Pixel 9 Pro",              "search": "Google Pixel 9 Pro 128GB site:amazon.es"},
    {"title": "Elgato Stream Deck MK.2",         "search": "Elgato Stream Deck MK.2 site:amazon.es"},
    {"title": "Logitech MX Master 3S",           "search": "Logitech MX Master 3S site:amazon.es"},
    {"title": "Amazon Echo Show",                "search": "Amazon Echo Show 10 site:amazon.es"},
    {"title": "Philips Hue Gradient Lightstrip", "search": "Philips Hue Gradient Lightstrip site:amazon.es"},
    {"title": "Apple Watch Ultra 2",             "search": "Apple Watch Ultra 2 site:amazon.es"},
    {"title": "Garmin",                          "search": "Garmin Fenix 7X Pro Solar site:amazon.es"},
    {"title": "Arc'teryx Beta AR Jacket",        "search": "Arcteryx Beta AR Jacket site:amazon.es"},
    {"title": "Patagonia Nano Puff",             "search": "Patagonia Nano Puff site:amazon.es"},
    {"title": "Levi's 501 Original Fit",         "search": "Levis 501 Original Fit site:amazon.es"},
    {"title": "New Balance 990v6",               "search": "New Balance 990v6 site:amazon.es"},
    {"title": "Adidas Samba OG",                 "search": "Adidas Samba OG site:amazon.es"},
    {"title": "Salomon XT-6",                    "search": "Salomon XT-6 site:amazon.es"},
    {"title": "Geox J Perth Boy A",              "search": "Geox Perth Boy site:amazon.es"},
    {"title": "LIONELO MIKA PLUS",               "search": "Lionelo Mika Plus site:amazon.es"},
]

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
    precos = sorted([p for p in lista if p])
    if not precos:
        return None
    med = precos[len(precos) // 2]
    limpos = [p for p in precos if med * 0.6 <= p <= med * 2.0]
    if not limpos:
        limpos = precos
    return limpos[len(limpos) // 2]

def obter_preco(search_query):
    params = {
        "engine":   "google_shopping",
        "q":        search_query,
        "api_key":  SERPAPI_KEY,
        "gl":       "es",       # Espanha — amazon.es
        "hl":       "es",
        "currency": "EUR",
        "num":      "10",
    }
    try:
        r = requests.get(SERPAPI_URL, params=params, timeout=30)
        data = r.json()

        if "error" in data:
            print(f"    ✗ SerpAPI: {data['error']}")
            return None

        resultados = data.get("shopping_results", [])
        if not resultados:
            print(f"    ⚠ Sem resultados")
            return None

        precos = [converter_preco(i.get("price","")) for i in resultados]
        precos = [p for p in precos if p]

        if not precos:
            print(f"    ⚠ Nenhum preço extraído")
            return None

        resultado = mediana_filtrada(precos)
        if resultado:
            print(f"    ✅ {len(precos)} preços | min ≈€{round(min(precos))} max ≈€{round(max(precos))} | escolhido: {formatar_preco(resultado)}")
        return formatar_preco(resultado) if resultado else None

    except Exception as e:
        print(f"    ✗ Erro: {e}")
        return None

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

def main():
    if not SERPAPI_KEY:
        print("❌ SERPAPI_KEY não encontrada.")
        sys.exit(1)

    print("=" * 60)
    print(f"  ELEITOS — Auto Update Prices (amazon.es via Google Shopping)")
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
        print(f"\n✓ Sem alterações")

    print("\n" + "=" * 60)
    print(f"  ✅ Atualizados:   {len(atualizados)}")
    print(f"  ✓ Sem alteração: {len(sem_alteracao)}")
    print(f"  ⚠ Sem preço:     {len(sem_preco)}")
    print(f"  ✗ Não no HTML:   {len(nao_encontrado)}")
    if atualizados:
        print("\n  Alterações:")
        for l in atualizados: print(f"    · {l}")
    if sem_preco:
        print("\n  Verificar:")
        for p in sem_preco: print(f"    · {p}")
    print("=" * 60)

if __name__ == "__main__":
    main()
