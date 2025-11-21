import json
import time
import random
from googlesearch import search

def load_inputs():
    with open('inputs.json', 'r', encoding='utf-8') as f:
        skus = json.load(f)
    with open('platforms.json', 'r', encoding='utf-8') as f:
        platforms = json.load(f)
    return skus, platforms

def find_url(sku, platform_name):
    # 注意：如果 platform_name 是一個字典(dict)，這裡搜尋字串可能會變得很亂
    # 建議確認傳進來的是單純的名稱字串
    query = f"{sku} {platform_name}"
    print(f"🔍 Searching: {query}...")
    
    try:
        # 搜尋 Google，取第 1 個結果
        # num_results=1 代表只抓第一條
        results = list(search(query, num_results=1, advanced=True))
        if results:
            url = results[0].url
            print(f"   ✅ Found: {url}")
            return url
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    return ""

def main():
    skus, platforms = load_inputs()
    full_config = []

    all_platforms = [platforms['client']] + platforms['competitors']

    for sku in skus:
        item_entry = {
            "sku_name": sku,
            "urls": {}
        }
        
        for plat in all_platforms:
            # 為了避免被 Google Ban IP，每次搜尋隨機暫停 2-5 秒
            time.sleep(random.uniform(2, 5)) 
            
            # 這裡傳入 plat (它是個字典)，搜尋時可能會有問題
            # 如果搜尋結果不準，請將下一行改成 find_url(sku, plat['name']) (假設你的 json 有 name 欄位)
            url = find_url(sku, plat)
            
            # 標記這是 Client 還是 Competitor
            role = "client" if plat == platforms['client'] else "competitor"
            
            # --- 修正部分開始 ---
            # 這裡原本縮排錯誤，現在已對齊
            item_entry["urls"][plat['id']] = {
                "url": url,
                "role": role
            }
            # --- 修正部分結束 ---
            
        full_config.append(item_entry)

    # 輸出生成的 Config 檔案
    with open('generated_config.json', 'w', encoding='utf-8') as f:
        json.dump(full_config, f, indent=2, ensure_ascii=False)
    
    print("\n🎉 Configuration generated! Check 'generated_config.json'.")

if __name__ == "__main__":
    main()
