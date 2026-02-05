import requests
from bs4 import BeautifulSoup

circle_id = 'RG01059653'
url = f"https://www.dlsite.com/maniax/circle/profile/=/maker_id/{circle_id}.html"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print(f"サークルページを取得中: {url}")
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# work_nameを検索
work_names = soup.select('dt.work_name a')

print(f"\n見つかった作品数: {len(work_names)}件\n")

if work_names:
    print("=== 最初の3作品 ===")
    for i, work in enumerate(work_names[:3], 1):
        title = work.get_text(strip=True)
        url = work.get('href', '')
        print(f"\n{i}. {title}")
        print(f"   URL: {url}")
        
        # 予約作品かチェック
        if '/announce/' in url:
            print("   → 予約作品（除外対象）")
        elif '/girls/' in url:
            print("   → 女性向け作品（除外対象）")
        else:
            print("   → 発売済み男性向け作品（表示対象）")
else:
    print("作品が見つかりませんでした")
    print("\nHTMLの最初の500文字:")
    print(response.text[:500])