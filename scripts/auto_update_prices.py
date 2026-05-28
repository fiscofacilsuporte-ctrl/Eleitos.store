#!/usr/bin/env python3
"""
ELEITOS — Auto Update Prices
Corre via GitHub Actions: scripts/auto_update_prices.py
Atualiza os preços em index.html com base nos links de afiliado Amazon.
"""

import re
import time
import random
import os
import sys
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# ── Ficheiro HTML (relativo à raiz do repo) ────────────────────────────────────
HTML_FILE = os.path.join(os.path.dirname(__file__), '..', 'index.html')

# ── Mapeamento produto → link de afiliado ──────────────────────────────────────
PRODUCTS = [
    {"title": "Sony WH-1000XM5",                 "url": "https://amzn.to/4wRY3ZY"},
    {"title": "Bose QuietComfort Ultra",          "url": "https://amzn.to/4tXG4yG"},
    {"title": "Samsung Neo QLED QN90D 55",        "url": "https://amzn.to/4dORajG"},
    {"title": "LG C4 OLED 55",                    "url": "https://amzn.to/3PsmXPk"},
    {"title": "Apple iPhone 17 Pro Max",          "url": "https://amzn.to/4uzhNA6"},
    {"title": "Samsung Galaxy S26 Ultra",         "url": "https://amzn.to/4tWJ9iw"},
    {"title": "Sony WH-1000XM6",                  "url": "https://amzn.to/4vgAKHW"},
    {"title": "Apple Watch Ultra 3",              "url": "https://amzn.to/4dyUeBt"},
    {"title": "DJI Osmo Pocket 4",               "url": "https://amzn.to/4fKuAet"},
    {"title": "Bose QC Ultra Earbuds II",         "url": "https://amzn.to/4nVIGMf"},
    {"title": "Logitech MX Mechanical Mini V2",   "url": "https://amzn.to/4dxdgbv"},
    {"title": "LG UltraGear OLED 32",             "url": "https://amzn.to/4e7JaLO"},
    {"title": "Anker Nebula Capsule 3 Laser",     "url": "https://amzn.to/4uzImoX"},
    {"title": "Shargeek 140W GaN",               "url": "https://amzn.to/4wT8Ovk"},
    {"title": "Sony Bravia XR A95L",             "url": "https://amzn.to/4e9g9iM"},
    {"title": "Apple iPhone 16 Pro Max",          "url": "https://amzn.to/4u2Rvp4"},
    {"title": "Samsung Galaxy S25 Ultra",         "url": "https://amzn.to/4dvGg3m"},
    {"title": "Google Pixel 9 Pro",              "url": "https://amzn.to/43jkbPL"},
    {"title": "Elgato Stream Deck MK.2",         "url": "https://amzn.to/3RO6k14"},
    {"title": "Logitech MX Master 3S",           "url": "https://amzn.to/43vEmtB"},
    {"title": "Amazon Echo Show",                "url": "https://amzn.to/4ujlqcN"},
    {"title": "Philips Hue Gradient Lightstrip", "url": "https://amzn.to/4faKmzd"},
    {"title": "Apple Watch Ultra 2",             "url": "https://amzn.to/4dIGUL7"},
    {"title": "Garmin",                          "url": "https://amzn.to/4fI82ej"},
    {"title": "Arc'teryx Beta AR Jacket",        "url": "https://amzn.to/43jlXAp"},
    {"title": "Patagonia Nano Puff",             "url": "https://amzn.to/3Q77DHZ"},
    {"title": "Levi's 501 Original Fit",         "url": "https://amzn.to/43zw0Be"},
    {"title": "New Balance 990v6",               "url": "https://amzn.to/4uAAV0y"},
    {"title": "Adidas Samba OG",                 "url": "https://amzn.to/4e84vVo"},
    {"title": "Salomon XT-6",                    "url": "https://amzn.to/3PGxl67"},
    {"title": "Geox J Perth Boy A",              "url": "https://amzn.to/3Q3bQwm"},
    {"title": "LIONELO MIKA PLUS",               "url": "https://amzn.to/3RMeOpt"},
]

# ── Headers que imitam um browser real ────────────────────────────────────────
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
]

def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "pt-PT,pt;q=0.9,es;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }

# ── Extrai preço da página Amazon ─────────────────────────────────────────────
def extrair_preco(html):
    soup = BeautifulSoup(html, "html.parser")

    seletores = [
        "#corePrice_feature_div .a-price .a-offscreen",
        "#apex_offerDisplay_desktop .a-price .a-offscreen",
        "#corePriceDisplay_desktop_feature_div .a-price .a-offscreen",
        "#price_inside_buybox",
        "#priceblock_ourprice",
        "#priceblock_dealprice",
        ".a-price.a-text-price.a-size-medium .a-offscreen",
        ".a-price .a-offscreen",
        "#tp_price_block_total_price_ww .a-offscreen",
    ]

    for seletor in seletores:
        el = soup.select_one(seletor)
        if el:
            texto = el.get_text(strip=True)
            if texto and any(c.isdigit() for c in texto):
                return texto

    return None

# ── Converte preço Amazon → formato ELEITOS (≈ €1.299) ───────────────────────
def formatar_preco(preco_raw):
    # Normalizar espaços e caracteres especiais
    preco_raw = preco_raw.replace('\xa0', '').replace('\u202f', '').strip()

    # Extrair sequência numérica
    match = re.search(r'[\d.,]+', preco_raw)
    if not match:
        return None

    raw = match.group(0)

    try:
        if ',' in raw and '.' in raw:
            # Formato europeu: 1.299,99
            inteiro = int(raw.split(',')[0].replace('.', ''))
        elif ',' in raw:
            # Só vírgula: 349,99
            inteiro = int(raw.split(',')[0])
        elif '.' in raw:
            partes = raw.split('.')
            if len(partes[-1]) == 2 and len(partes) == 2:
                # Decimal inglês: 299.99
                inteiro = int(partes[0])
            else:
                # Separador de milhares: 1.299
                inteiro = int(raw.replace('.', ''))
        else:
            inteiro = int(raw)
    except ValueError:
        return None

    # Formatar com ponto como separador de milhares (PT)
    if inteiro >= 1000:
        formatado = f"{inteiro:,}".replace(",", ".")
    else:
        formatado = str(inteiro)

    return f"≈ €{formatado}"

# ── Vai buscar preço com retry ────────────────────────────────────────────────
def obter_preco(url, tentativas=3):
    for tentativa in range(1, tentativas + 1):
        try:
            session = requests.Session()
            r = session.get(
                url,
                headers=get_headers(),
                timeout=20,
                allow_redirects=True
            )

            if r.status_code == 503:
                print(f"    ⚠ Bloqueado (503) — tentativa {tentativa}/{tentativas}")
                time.sleep(random.uniform(10, 20))
                continue

            if r.status_code != 200:
                print(f"    ⚠ HTTP {r.status_code}")
                return None

            preco_raw = extrair_preco(r.text)
            if not preco_raw:
                print(f"    ⚠ Preço não encontrado (tentativa {tentativa}/{tentativas})")
                if tentativa < tentativas:
                    time.sleep(random.uniform(5, 10))
                continue

            return formatar_preco(preco_raw)

        except requests.exceptions.Timeout:
            print(f"    ⚠ Timeout (tentativa {tentativa}/{tentativas})")
        except Exception as e:
            print(f"    ⚠ Erro: {e}")

        if tentativa < tentativas:
            time.sleep(random.uniform(5, 10))

    return None

# ── Atualiza preço no HTML por título de card ─────────────────────────────────
def atualizar_html(soup, titulo, novo_preco):
    """
    Localiza o card pelo h2.card-title (match parcial) e
    atualiza o span.card-price dentro do mesmo card-body.
    """
    for h2 in soup.find_all("h2", class_="card-title"):
        h2_texto = h2.get_text(strip=True)
        # Match parcial bidirecional (cobre aspas, acentos, etc.)
        titulo_lower  = titulo.lower()
        h2_lower      = h2_texto.lower()
        if titulo_lower in h2_lower or h2_lower in titulo_lower:
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
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M UTC")
    print("=" * 60)
    print(f"  ELEITOS — Auto Update Prices")
    print(f"  {timestamp}")
    print("=" * 60)

    # Ler HTML
    html_path = os.path.abspath(HTML_FILE)
    if not os.path.exists(html_path):
        print(f"❌ Ficheiro não encontrado: {html_path}")
        sys.exit(1)

    with open(html_path, "r", encoding="utf-8") as f:
        conteudo_original = f.read()

    soup = BeautifulSoup(conteudo_original, "html.parser")

    atualizados    = []
    sem_preco      = []
    nao_encontrado = []
    total = len(PRODUCTS)

    for i, produto in enumerate(PRODUCTS, 1):
        titulo = produto["title"]
        url    = produto["url"]

        print(f"\n[{i:02d}/{total}] {titulo}")

        # Pausa aleatória entre pedidos (evita bloqueio)
        if i > 1:
            pausa = random.uniform(4.0, 9.0)
            print(f"    ⏳ {pausa:.1f}s...")
            time.sleep(pausa)

        preco = obter_preco(url)

        if preco is None:
            print(f"    ✗ Sem preço — mantido o atual")
            sem_preco.append(titulo)
            continue

        print(f"    💰 {preco}")

        ok, h2_real, preco_antigo = atualizar_html(soup, titulo, preco)

        if ok:
            if preco_antigo != preco:
                print(f"    ✅ {preco_antigo} → {preco}")
                atualizados.append(f"{h2_real}: {preco_antigo} → {preco}")
            else:
                print(f"    ✓ Sem alteração ({preco})")
        else:
            print(f"    ⚠ Título não encontrado no HTML")
            nao_encontrado.append(titulo)

    # Guardar HTML apenas se houve alterações
    conteudo_novo = str(soup)
    if atualizados:
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(conteudo_novo)
        print(f"\n✅ index.html guardado com {len(atualizados)} atualização(ões)")
    else:
        print(f"\n✓ Sem alterações — index.html não foi modificado")

    # Resumo final
    print("\n" + "=" * 60)
    print(f"  ✅ Atualizados:     {len(atualizados)}")
    print(f"  ✓ Sem alteração:   {total - len(atualizados) - len(sem_preco) - len(nao_encontrado)}")
    print(f"  ⚠ Sem preço:       {len(sem_preco)}")
    print(f"  ✗ Não no HTML:     {len(nao_encontrado)}")

    if atualizados:
        print("\n  Preços alterados:")
        for linha in atualizados:
            print(f"    · {linha}")

    if sem_preco:
        print("\n  Verificar manualmente:")
        for p in sem_preco:
            print(f"    · {p}")

    print("=" * 60)

if __name__ == "__main__":
    main()
