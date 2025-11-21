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

# 遞迴攤平平台設定 (解決 JSON 裡面又有 List 的問題)
def flatten_platforms(data):
    flat_list = []
    if isinstance(data, dict):
        # 如果是字典 (例如 {"client": {...}, "comp1": {...}})，取 values
        for key, value in data.items():
            flat_list.extend(flatten_platforms(value))
    elif isinstance(data, list):
        # 如果是列表，檢查裡面的元素
        for item in data:
            flat_list.extend(flatten_platforms(item))
    else:
        # 如果是單個設定物件 (已經是我們要的 dict)，直接加入
        flat_list.append(data)
    return flat_list

# 搜尋邏輯 (針對香港地區優化)
def find_product_url(product_name, platform_domain):
    # 移除 www. 前綴有時候能增加搜尋廣度，這裡先保留完整 domain
    query = f"{product_name} site:{platform_domain}"
    print(f"🔍 Searching: {query}")
    
    try:
        # --- 關鍵修正 ---
        # region='hk-tzh': 強制搜尋香港繁體中文結果 (解決雲端 IP 找不到香港站的問題)
        # backend='html': 使用 HTML 模式，比預設 API 模式更抗封鎖，適合 site: 指令
        with DDGS() as ddgs:
            results = list(ddgs.text(query, region='hk-tzh', backend='html', max_results=1))
        
        if results:
            first_result = results[0]
            url = first_result.get('href')
            print(f"✅ Found: {url}")
            return url
        else:
            # 如果 site: 找不到，嘗試放寬搜尋 (不強制 site: 但加上關鍵字)
            print(f"⚠️ Strict search failed, trying loose search...")
            loose_query = f"{product_name} {platform_domain}"
            with DDGS() as ddgs:
                results = list(ddgs.text(loose_query, region='hk-tzh', backend='html', max_results=1))
            
            if results:
                url = results[0].get('href')
                # 簡單檢查網址是否包含該 domain
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

    # 攤平平台設定，解決 "Skipping invalid platform format" 錯誤
    platform_list = flatten_platforms(raw_platforms)
    print(f"ℹ️ Loaded {len(platform_list)} platforms to search.")

    # 迴圈遍歷每個產品
    for product in products:
        sku = product.get('sku')
        name = product.get('name')
        
        print(f"\n--- Processing Product: {name} ---")

        # 迴圈遍歷每個平台
        for platform_info in platform_list:
            
            # 再次確認格式
            if not isinstance(platform_info, dict):
                continue
            
            domain = platform_info.get('domain')
            platform_name = platform_info.get('name')
            
            if not domain:
                continue

            # 執行搜尋
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
            
            # 隨機休息 3-6 秒 (HTML backend 比較慢，建議休息久一點點)
            time.sleep(random.uniform(3, 6))

    # 儲存結果
    with open('generated_config.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    
    print(f"\n🎉 Configuration generated with {len(results)} items! Check 'generated_config.json'.")

if __name__ == "__main__":
    main()
