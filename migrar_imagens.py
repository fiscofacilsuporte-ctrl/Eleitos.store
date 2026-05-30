import re, json, base64, os
from pathlib import Path

HTML_FILE = "index.html"
JSON_FILE = "products.json"
IMAGES_DIR = "images"

with open(HTML_FILE, "r", encoding="utf-8", errors="ignore") as f:
    html = f.read()

padrao = r'src=["\']?(data:image/([\w+]+);base64,([A-Za-z0-9+/=\s]+?))["\'\s>]'
matches = re.findall(padrao, html, re.DOTALL)

Path(IMAGES_DIR).mkdir(parents=True, exist_ok=True)
mapeamento = {}
vistos = set()
i = 0

for src_completo, mime, b64 in matches:
    b64_limpo = b64.replace("\n","").replace("\r","").replace(" ","")
    if b64_limpo in vistos:
        continue
    vistos.add(b64_limpo)
    ext = "jpg" if mime == "jpeg" else mime.split("+")[0]
    try:
        dados = base64.b64decode(b64_limpo)
        nome = f"produto_{i+1:03d}.{ext}"
        caminho = f"{IMAGES_DIR}/{nome}"
        with open(caminho, "wb") as f:
            f.write(dados)
        print(f"✅ {nome} ({len(dados)//1024} KB)")
        mapeamento[src_completo.strip()] = caminho
        i += 1
    except Exception as e:
        print(f"⚠️ Erro: {e}")

with open(JSON_FILE, "r", encoding="utf-8") as f:
    conteudo = f.read()
for orig, novo in mapeamento.items():
    conteudo = conteudo.replace(orig, novo)
with open(JSON_FILE, "w", encoding="utf-8") as f:
    f.write(conteudo)

print(f"\n✅ Feito! {i} imagens extraídas.")
