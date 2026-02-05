import requests
from bs4 import BeautifulSoup

urls = [
    'https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG01059653.html',
    'https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG01020625.html'
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

for idx, url in enumerate(urls, 1):
    print(f"ダウンロード中: {url}")
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    
    filename = f"circle_page_{idx}.html"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    print(f"保存完了: {filename}")
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    print(f"\n=== HTMLセレクタテスト ===")
    
    selectors = [
        'dt.work_name a',
        'a[href*="/work/"]',
        'div.work_1col a',
        'div.work_thumb a',
        'li a[href*="RJ"]',
        'a[href*="product_id"]',
        'td a[href*="/work/"]'
    ]
    
    for selector in selectors:
        elements = soup.select(selector)
        print(f"{selector}: {len(elements)}件")
        if len(elements) > 0:
            print(f"  最初の作品: {elements[0].get('href', 'N/A')}")
    
    print("=" * 50)
    print()

print("完了！")
