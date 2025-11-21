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

# 搜尋邏輯 (DuckDuckGo)
def find_product_url(product_name, platform_domain):
    query = f"{product_name} site:{platform_domain}"
    print(f"🔍 Searching on DDG: {query}")
    
    try:
        # 使用 DuckDuckGo 搜尋
        results = DDGS().text(query, max_results=1)
        
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

    if not platforms:
        print("No platforms config found.")
        return

    # --- 修正重點開始 ---
    # 判斷 platforms 是 List 還是 Dict，統一轉換成 List 進行迴圈
    # 這樣無論你的 JSON 是 [{}, {}] 還是 {"p1": {}, "p2": {}} 都能跑
    if isinstance(platforms, dict):
        platform_list = list(platforms.values())
    elif isinstance(platforms, list):
        platform_list = platforms
    else:
        print("Error: platforms.json format is not recognized (must be list or dict).")
        return
    # --- 修正重點結束 ---

    # 迴圈遍歷每個產品
    for product in products:
        sku = product.get('sku')
        name = product.get('name')
        
        print(f"\n--- Processing Product: {name} ---")

        # 迴圈遍歷每個平台
        for platform_info in platform_list:
            
            # --- 安全檢查 ---
            # 確保 platform_info 是字典，如果它是 List (例如 ["Fortress", "..."])，這裡會跳過並警告
            if not isinstance(platform_info, dict):
                print(f"⚠️ Skipping invalid platform format (expected dict, got {type(platform_info).__name__}): {platform_info}")
                continue
            
            domain = platform_info.get('domain')
            platform_name = platform_info.get('name')
            
            if not domain:
                print(f"⚠️ Skipping platform with no domain: {platform_name}")
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
            
            # 休息一下，避免被封鎖
            time.sleep(random.uniform(2, 5))

    # 儲存結果
    with open('generated_config.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    
    print(f"\n🎉 Configuration generated with {len(results)} items! Check 'generated_config.json'.")

if __name__ == "__main__":
    main()
