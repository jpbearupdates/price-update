import json
import time
import random
from duckduckgo_search import DDGS

# 讀取輸入檔案
def load_inputs():
    try:
        with open('inputs.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: inputs.json not found.")
        return []

# 讀取平台設定
def load_platforms():
    try:
        with open('platforms.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: platforms.json not found.")
        return {}

# 搜尋邏輯 (改用 DuckDuckGo)
def find_product_url(product_name, platform_domain):
    query = f"{product_name} site:{platform_domain}"
    print(f"🔍 Searching on DDG: {query}")
    
    try:
        # 使用 DuckDuckGo 搜尋
        # max_results=1 代表只拿第一個結果
        results = DDGS().text(query, max_results=1)
        
        # DDGS 回傳的是一個 List of Dictionaries
        # 格式類似: [{'title': '...', 'href': 'https://...', 'body': '...'}]
        if results:
            first_result = results[0]
            url = first_result.get('href')
            print(f"✅ Found: {url}")
            return url
        else:
            print(f"❌ No results found for {product_name} on {platform_domain}")
            return None

    except Exception as e:
        print(f"⚠️ Error searching for {product_name}: {e}")
        return None

def main():
    products = load_inputs()
    platforms = load_platforms()
    results = []

    if not products:
        print("No products to search.")
        return

    # 迴圈遍歷每個產品
    for product in products:
        sku = product.get('sku')
        name = product.get('name')
        
        # 迴圈遍歷每個平台 (Client, Comp1, Comp2...)
        for key, platform_info in platforms.items():
            domain = platform_info.get('domain')
            platform_name = platform_info.get('name')
            
            if not domain:
                continue

            # 執行搜尋
            url = find_product_url(name, domain)
            
            if url:
                # 成功搵到，加入結果
                entry = {
                    "sku": sku,
                    "name": name,
                    "platform": platform_name,
                    "type": platform_info.get('type'), # client or competitor
                    "url": url,
                    "selector": platform_info.get('price_selector')
                }
                results.append(entry)
            
            # 休息一下，避免被封鎖 (DuckDuckGo 雖然寬鬆，但太快都會封)
            time.sleep(random.uniform(2, 5))

    # 儲存結果
    with open('generated_config.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    
    print(f"🎉 Configuration generated with {len(results)} items! Check 'generated_config.json'.")

if __name__ == "__main__":
    main()
