# ELEITOS — A Seleção Cinco Estrelas

Um site de curadoria de produtos de alta qualidade com design minimalista e luxuoso, com sistema automático de atualização de preços.

## 📋 Estrutura do Projeto

```
Eleitos/
├── index.html                 # Versão estática original
├── index_dynamic.html         # Versão dinâmica (recomendada)
├── products.json              # Base de dados de produtos
├── styles/
│   └── product-variants.css   # Estilos por categoria
├── scripts/
│   ├── html_to_json.py        # Converter HTML para JSON
│   ├── scraper_v2.py          # Scraper de produtos
│   └── update_prices.py       # Atualizar preços automaticamente
└── assets/
    └── [imagens e recursos]
```

## 🚀 Como Usar

### Versão Dinâmica (Recomendada)

1. **Usar `index_dynamic.html` em vez de `index.html`:**
   - O ficheiro carrega produtos dinamicamente do `products.json`
   - Mantém todo o design visual luxuoso
   - Permite atualizações sem editar HTML

2. **Estrutura do `products.json`:**
   ```json
   [
     {
       "name": "Sony WH-1000XM5",
       "category": "audio",
       "image": "https://...",
       "verdict": "Descrição do produto...",
       "price": "≈ €349",
       "stars": "★★★★★",
       "stars_count": "4.7 | +24.000 avaliações",
       "cta_link": "https://www.amazon.com.br/s?k=Sony+WH-1000XM5",
       "brand_site": ""
     }
   ]
   ```

### Atualizar Preços Automaticamente

1. **Executar manualmente:**
   ```bash
   python3 scripts/update_prices.py
   ```

2. **Configurar cron job (Linux/Mac):**
   ```bash
   # Editar crontab
   crontab -e
   
   # Adicionar linha para executar diariamente às 6 da manhã
   0 6 * * * /usr/bin/python3 /caminho/para/Eleitos/scripts/update_prices.py
   ```

3. **Adicionar URLs de referência:**
   - Editar `scripts/update_prices.py`
   - Adicionar mapeamentos no dicionário `PRODUCT_URLS`
   - Exemplo:
     ```python
     PRODUCT_URLS = {
         "Sony WH-1000XM5": "https://www.worten.pt/...",
         "Apple Watch Ultra 2": "https://www.fnac.pt/...",
     }
     ```

## 🎨 Design e Estilo

### Paleta de Cores
- **Fundo:** `#181618` (cinzento muito escuro)
- **Destaque:** `#c6a97a` (ouro metálico)
- **Texto principal:** `#f0ece6` (quase branco quente)
- **Texto secundário:** `#aeaec0` (cinza médio)

### Tipografia
- **Display:** Cormorant Garamond (serif elegante)
- **Body:** Montserrat (sans-serif moderno)

### Variações por Categoria
Cada categoria tem uma cor de destaque subtil:
- **Áudio:** Rosa quente
- **Domótica:** Azul claro
- **Setups:** Verde claro
- **Wearables:** Roxo
- **Roupas:** Rosa
- **Calçado:** Verde menta
- **TVs:** Dourado quente
- **Smartphones:** Azul

## 🔄 Fluxo de Atualização

```
┌─────────────────────┐
│  products.json      │  ← Base de dados central
└──────────┬──────────┘
           │
           ├─→ index_dynamic.html (carrega dinamicamente)
           │
           └─→ update_prices.py (atualiza preços)
                    ↓
           Scraping de sites de marcas
                    ↓
           Atualiza products.json
```

## 📝 Adicionar Novos Produtos

1. Editar `products.json` e adicionar um novo objeto:
   ```json
   {
     "name": "Novo Produto",
     "category": "audio",
     "image": "https://...",
     "verdict": "Descrição...",
     "price": "≈ €XXX",
     "stars": "★★★★★",
     "stars_count": "4.X | +X.000 avaliações",
     "cta_link": "https://...",
     "brand_site": "https://..."
   }
   ```

2. A página atualiza automaticamente ao recarregar.

## 🛠️ Personalização

### Modificar Cores por Categoria
Editar `styles/product-variants.css` e ajustar os valores de cor para cada categoria.

### Adicionar Novas Categorias
1. Adicionar botão de filtro em `index_dynamic.html`
2. Adicionar estilos em `product-variants.css`
3. Usar o novo valor em `data-category` nos produtos

## 🔐 Segurança e Boas Práticas

- Não incluir chaves de API no repositório
- Usar variáveis de ambiente para URLs sensíveis
- Validar dados antes de guardar em JSON
- Implementar rate limiting ao fazer scraping

## 📱 Responsividade

O site é totalmente responsivo:
- Desktop: 3 colunas
- Tablet: 2 colunas
- Mobile: 1 coluna

## 🚀 Deploy

Para usar em produção:

1. **Renomear `index_dynamic.html` para `index.html`** (ou configurar servidor web)
2. **Garantir que `products.json` está acessível**
3. **Configurar cron job para atualizar preços**
4. **Testar em diferentes navegadores**

## 📞 Suporte

Para dúvidas ou melhorias, consultar a documentação do código ou criar uma issue no repositório.

---

**Última atualização:** 2025-05-25
**Versão:** 2.0 (Dinâmica)
