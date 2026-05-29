#!/usr/bin/env python3
"""
ELEITOS — Auto Update Prices via SerpAPI (Google Shopping)
v3 — filtragem de outliers para preços mais precisos
"""

import re, time, random, os, sys, requests
from bs4 import BeautifulSoup
from datetime import datetime

HTML_FILE   = os.path.join(os.path.dirname(__file__), '..', 'index.html')
SERPAPI_KEY = os.environ.get("SERPAPI_KEY", "")
SERPAPI_URL = "https://serpapi.com/search.json"

PRODUCTS = [
    {"title": "Sony WH-1000XM5",                 "search": "Sony WH-1000XM5 headphones"},
    {"title": "Bose QuietComfort Ultra",          "search": "Bose QuietComfort Ultra Headphones"},
    {"title": "Samsung Neo QLED QN90D 55",        "search": "Samsung Neo QLED QN90D 55 polegadas"},
    {"title": "LG C4 OLED 55",                    "search": "LG C4 OLED 55 televisao"},
    {"title": "Apple iPhone 17 Pro Max",          "search": "Apple iPhone 17 Pro Max 256GB"},
    {"title": "Samsung Galaxy S26 Ultra",         "search": "Samsung Galaxy S26 Ultra"},
    {"title": "Sony WH-1000XM6",                  "search": "Sony WH-1000XM6"},
    {"title": "Apple Watch Ultra 3",              "search": "Apple Watch Ultra 3"},
    {"title": "DJI Osmo Pocket 4",               "search": "DJI Osmo Pocket 4"},
    {"title": "Bose QC Ultra Earbuds II",         "search": "Bose QuietComfort Ultra Earbuds"},
    {"title": "Logitech MX Mechanical Mini V2",   "search": "Logitech MX Mechanical Mini V2 teclado"},
    {"title": "LG UltraGear OLED 32",             "search": "LG UltraGear OLED 32 monitor 2024"},
    {"title": "Anker Nebula Capsule 3 Laser",     "search": "Anker Nebula Capsule 3 Laser projetor"},
    {"title": "Shargeek 140W GaN",               "search": "Shargeek 140W GaN carregador"},
    {"title": "Sony Bravia XR A95L",             "search": "Sony Bravia XR A95L QD-OLED televisao"},
    {"title": "Apple iPhone 16 Pro Max",          "search": "Apple iPhone 16 Pro Max 256GB novo"},
    {"title": "Samsung Galaxy S25 Ultra",         "search": "Samsung Galaxy S25 Ultra 256GB"},
    {"title": "Google Pixel 9 Pro",              "search": "Google Pixel 9 Pro 128GB novo"},
    {"title": "Elgato Stream Deck MK.2",         "search": "Elgato Stream Deck MK2"},
    {"title": "Logitech MX Master 3S",           "search": "Logitech MX Master 3S rato"},
    {"title": "Amazon Echo Show",                "search": "Amazon Echo Show 10 3rd gen"},
    {"title": "Philips Hue Gradient Lightstrip", "search": "Philips Hue Gradient Lightstrip 2m"},
    {"title": "Apple Watch Ultra 2",             "search": "Apple Watch Ultra 2 novo"},
    {"title": "Garmin",                          "search": "Garmin Fenix 7X Pro Solar"},
    {"title": "Arc'teryx Beta AR Jacket",        "search": "Arcteryx Beta AR Jacket"},
    {"title": "Patagonia Nano Puff",             "search": "Patagonia Nano Puff Jacket"},
    {"title": "Levi's 501 Original Fit",         "search": "Levis 501 Original Fit jeans"},
    {"title": "New Balance 990v6",               "search": "New Balance 990v6"},
    {"title": "Adidas Samba OG",                 "search": "Adidas Samba OG novo"},
    {"title": "Salomon XT-6",                    "search": "Salomon XT-6 sapatilhas"},
    {"title": "Geox J Perth Boy A",              "search": "Geox Perth Boy sapatilhas crianca"},
    {"title": "LIONELO MIKA PLUS",               "search": "Lionelo Mika Plus carrinho bebe"},
]

def converter_preco(raw):
    try:
        raw = str(raw).replace('\xa0','').replace('\u202f','').replace(' ','').strip()
        raw = re.sub(r'[€$£]', '', raw).strip()
        if ',' in raw and '.' in raw:
            raw = raw.replace('.','').replace(',','.')
        elif ',' in raw:
            raw = raw.replace(',','.')
        return float(raw)
    except:
        return None

def formatar_preco(valor):
    inteiro = round(valor)
    return f"≈ €{inteiro:,}".replace(",", ".") if inteiro >= 1000 else f"≈ €{inteiro}"

def preco_representativo(precos_raw):
    """
    Filtra outliers e devolve um preço representativo.
    - Remove preços abaixo de 50% da mediana (segunda mão / erros)
    - Remove preços acima de 300% da mediana (bundles / erros)
    - Devolve a mediana dos restantes
    """
    precos = sorted([p for p in precos_raw if p and 1 < p < 50000])
    if not precos:
        return None

    # Mediana inicial (sem filtrar)
    n = len(precos)
    mediana_inicial = precos[n // 2]

    # Filtrar outliers
    filtrados = [p for p in precos if mediana_inicial * 0.5 <= p <= mediana_inicial * 3.0]
    if not filtrados:
        filtrados = precos  # fallback sem filtro

    # Mediana final
    f = len(filtrados)
    mediana_final = filtrados[f // 2]
    return mediana_final

def obter_preco(search_query):
    params = {
        "engine":   "google_shopping",
        "q":        search_query,
        "api_key":  SERPAPI_KEY,
        "gl":       "pt",
        "hl":       "pt",
        "currency": "EUR",
        "num":      "20",   # mais resultados = mediana mais fiável
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

        precos = []
        for item in resultados:
            valor = converter_preco(item.get("price", ""))
            if valor:
                precos.append(valor)

        if not precos:
            print(f"    ⚠ Nenhum preço válido")
            return None

        representativo = preco_representativo(precos)
        if not representativo:
            return None

        print(f"    📊 {len(precos)} preços | min ≈ €{round(min(precos))} | mediana filtrada: {formatar_preco(representativo)}")
        return formatar_preco(representativo)

    except requests.exceptions.Timeout:
        print(f"    ✗ Timeout")
        return None
    except Exception as e:
        print(f"    ✗ Erro: {e}")
        return None

def atualizar_html(soup, titulo, novo_preco):
    for h2 in soup.find_all("h2", class_="card-title"):
        h2_texto = h2.get_text(strip=True)
        if titulo.lower() in h2_texto.lower() or h2_texto.lower() in titulo.lower():
            card_body = h2.find_parent("div", class_="card-body")
            if card_body:
                span = card_body.find("span", class_="card-price")
                if span:
                    antigo = span.get_text(strip=True)
                    span.string = novo_preco
                    return True, h2_texto, antigo
    return False, titulo, None

def main():
    if not SERPAPI_KEY:
        print("❌ SERPAPI_KEY não encontrada.")
        sys.exit(1)

    print("=" * 60)
    print(f"  ELEITOS — Auto Update Prices v3")
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
            time.sleep(random.uniform(1.0, 2.0))

        preco = obter_preco(search)

        if not preco:
            print(f"    ✗ Sem preço")
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
        for l in atualizados:
            print(f"    · {l}")
    if sem_preco:
        print("\n  Verificar manualmente:")
        for p in sem_preco:
            print(f"    · {p}")
    print("=" * 60)

if __name__ == "__main__":
    main()
