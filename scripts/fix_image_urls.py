import json
import os

def main():
    json_path = 'products.json'
    
    if not os.path.exists(json_path):
        print(f"Erro: {json_path} não encontrado.")
        return
        
    with open(json_path, 'r', encoding='utf-8') as f:
        products = json.load(f)
        
    updated_count = 0
    for product in products:
        image_url = product.get('image', '')
        
        # Se for uma URL da Amazon ou similar que costuma bloquear hotlinking
        if 'amazon.com' in image_url or 'ssl-images-amazon.com' in image_url:
            # Usar wsrv.nl como proxy (gratuito e eficiente para este propósito)
            # Ele ajuda a contornar bloqueios de referer e serve imagens em formatos otimizados
            proxy_url = f"https://wsrv.nl/?url={image_url}&output=webp"
            
            if product['image'] != proxy_url:
                product['image'] = proxy_url
                updated_count += 1
                print(f"Atualizado: {product['name']}")
                
    if updated_count > 0:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(products, f, indent=2, ensure_ascii=False)
        print(f"\nSucesso: {updated_count} URLs de imagem atualizadas para usar proxy.")
    else:
        print("\nNenhuma URL precisava de atualização.")

if __name__ == "__main__":
    main()
