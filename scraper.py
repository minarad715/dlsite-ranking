import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time

def scrape_dlsite_ranking():
    """DLsiteのランキングをスクレイピング"""
    
    # DLsiteランキングページのURL
    url = "https://www.dlsite.com/maniax/ranking/=/term/daily/type/voice"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print("DLsiteランキングを取得中...")
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # ランキングデータを格納するリスト
        ranking_data = []
        
        # 作品名を検索
        work_names = soup.select('dt.work_name a')
        
        print(f"見つかった作品数: {len(work_names)}件")
        
        for idx, work in enumerate(work_names[:30], 1):  # 上位30件
            try:
                # タイトル
                title = work.get_text(strip=True)
                
                # 作品URL
                work_url = work.get('href', '')
                
                # 親要素から価格などの情報を取得
                parent = work.find_parent('dl', class_='work_2col')
                
                price = "価格情報なし"
                if parent:
                    price_elem = parent.select_one('.work_price')
                    if price_elem:
                        price = price_elem.get_text(strip=True)
                
                ranking_data.append({
                    'rank': idx,
                    'title': title,
                    'url': work_url,
                    'price': price,
                    'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                
                print(f"{idx}位: {title} - {price}")
                
            except Exception as e:
                print(f"エラー（{idx}位）: {e}")
                continue
        
        # JSONファイルに保存
        output_file = f"ranking_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(ranking_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ ランキングデータを {output_file} に保存しました！")
        print(f"取得件数: {len(ranking_data)}件")
        
        return ranking_data
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    scrape_dlsite_ranking()