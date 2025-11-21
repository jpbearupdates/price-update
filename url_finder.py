import json
import time
import random
from duckduckgo_search import DDGS

def load_inputs():
    try:
        with open('inputs.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: inputs.json not found.")
        return []

def load_platforms():
    try:
        with open('platforms.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Error: platforms.json not found.")
        return {}

# --- 修正後的攤平函數 ---
def flatten_platforms(data):
    flat_list = []
    if isinstance(data, list):
        # 如果是列表，遍歷裡面的每個項目
        for item in data:
            flat_list.extend(flatten_platforms(item))
    elif isinstance(data, dict):
        # 關鍵修正：如果這個字典裡有 'domain'，代表它就是我們要的平台設定，不要再拆了！
        if 'domain' in data:
            flat_list.append(data)
        else:
            # 如果沒有 domain，可能只是分類標籤 (例如 "competitors": {...})，繼續往裡面找
            for value in data.values():
                flat_list.extend(flatten_platforms(value))
    return flat_list

def find_product_url(product_name, platform_domain):
    # 這裡保留上一版修正的 HTML backend 和 region 設定
    query = f"{product_name} site:{platform_domain}"
    print(f"🔍 Searching: {query}")
    
    try:
        with DDGS() as ddgs:
            # 使用 html 模式和香港地區
            results = list(ddgs.text(query, region='hk-tzh', backend='html', max_results=1))
        
        if results:
            first_result = results[0]
            url = first_result.get('href')
            print(f"✅ Found: {url}")
            return url
        else:
            print(f"⚠️ Strict search failed, trying loose search...")
            loose_query = f"{product_name} {platform_domain}"
            with DDGS() as ddgs:
                results = list(ddgs.text(loose_query, region='hk-tzh', backend='html', max_results=1))
            
            if results:
                url = results[0].get('href')
                if platform_domain in url:
                    print(f"✅ Found (Loose): {url}")
                    return url
            
            print(f"❌ No results found for {product_name} on {platform_domain}")
            return None

    except Exception as e:
        print(f"⚠️ Error searching for {product_name}: {e}")
        return None

def main():
    products = load_inputs()
    raw_platforms = load_platforms()
    results = []

    if not products:
        print("No products to search.")
        return

    if not raw_platforms:
        print("No platforms config found.")
        return

    # 處理平台列表
    platform_list = flatten_platforms(raw_platforms)
    print(f"ℹ️ Loaded {len(platform_list)} platforms to search.")

    # Debug: 印出第一個平台長什麼樣子，確保格式正確
    if len(platform_list) > 0:
        print(f"ℹ️ Debug - First platform data: {platform_list[0]}")

    for product in products:
        sku = product.get('sku')
        name = product.get('name')
        
        print(f"\n--- Processing Product: {name} ---")

        for platform_info in platform_list:
            # 這裡應該不會再被跳過了
            if not isinstance(platform_info, dict):
                print(f"⚠️ Skipping invalid data type: {type(platform_info)}")
                continue
            
            domain = platform_info.get('domain')
            platform_name = platform_info.get('name')
            
            if not domain:
                print(f"⚠️ Skipping platform without domain: {platform_info}")
                continue

            url = find_product_url(name, domain)
            
            if url:
                entry = {
                    "sku": sku,
                    "name": name,
                    "platform": platform_name,
                    "type": platform_info.get('type'),
                    "url": url,
                    "selector": platform_info.get('price_selector')
                }
                results.append(entry)
            
            time.sleep(random.uniform(3, 6))

    with open('generated_config.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    
    print(f"\n🎉 Configuration generated with {len(results)} items! Check 'generated_config.json'.")

if __name__ == "__main__":
    main()
