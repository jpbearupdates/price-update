import requests
from bs4 import BeautifulSoup
import json
import datetime
import random

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def clean_price(price_str):
    if not price_str: return 0
    clean = price_str.replace('$', '').replace(',', '').replace('HKD', '').strip()
    try:
        return float(clean)
    except:
        return 0

# 模擬爬蟲 (你需要針對這 5 個網站寫具體的 Selector，這裡用模擬數據代替以展示邏輯)
def fetch_data(url):
    if not url:
        return {"price": 0, "stock": False}
    
    # --- 實際專案中，這裡要針對不同 Domain 寫解析邏輯 ---
    # 為了讓你能馬上看到 Dashboard 效果，這裡我隨機生成數據
    # 請在正式版替換為真實 requests + BeautifulSoup 邏輯
    mock_price = random.randint(3000, 5000)
    mock_stock = random.choice([True, True, True, False]) # 75% 機率有貨
    
    return {"price": mock_price, "stock": mock_stock}

def main():
    with open('generated_config.json', 'r', encoding='utf-8') as f:
        products = json.load(f)

    matrix_data = []
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    for p in products:
        row = {
            "sku": p['sku_name'],
            "platforms": [],
            "action": "Monitor",
            "action_color": "gray"
        }

        client_price = 0
        client_stock = False
        competitor_prices = []
        competitor_stocks = []

        # 1. 爬取所有平台
        for plat_name, data in p['urls'].items():
            result = fetch_data(data['url'])
            
            is_client = (data['role'] == 'client')
            if is_client:
                client_price = result['price']
                client_stock = result['stock']

            if not is_client and result['price'] > 0:
                competitor_prices.append(result['price'])
                competitor_stocks.append(result['stock'])

            row['platforms'].append({
                "name": plat_name,
                "role": data['role'],
                "price": result['price'],
                "stock": result['stock'],
                "url": data['url']
            })

        # 2. 商業邏輯判斷 (Action Logic)
        min_comp_price = min(competitor_prices) if competitor_prices else 0
        all_comp_oos = all(not s for s in competitor_stocks) if competitor_stocks else False

        # 邏輯 A: Client 缺貨 -> 暫停
        if not client_stock:
            row['action'] = "🔴 STOP (OOS)"
            row['action_color'] = "red"
        
        # 邏輯 B: 價格太貴 (比最低競品貴 $300)
        elif min_comp_price > 0 and client_price > (min_comp_price + 300):
            diff = client_price - min_comp_price
            row['action'] = f"🔴 STOP (Price +${diff})"
            row['action_color'] = "red"

        # 邏輯 C: 競品全缺貨，我有貨 -> 加大預算
        elif client_stock and all_comp_oos:
            row['action'] = "🟢 PUSH (Comp OOS)"
            row['action_color'] = "green"

        # 邏輯 D: 價格優勢 (比最低競品便宜)
        elif client_stock and min_comp_price > 0 and client_price < min_comp_price:
            row['action'] = "🟢 PUSH (Best Price)"
            row['action_color'] = "green"
            
        matrix_data.append(row)

    final_output = {
        "updated_at": timestamp,
        "data": matrix_data
    }

    with open('dashboard_data.json', 'w', encoding='utf-8') as f:
        json.dump(final_output, f, ensure_ascii=False, indent=2)
    
    print("✅ Dashboard data updated.")

if __name__ == "__main__":
    main()
