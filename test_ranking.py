import requests
from bs4 import BeautifulSoup

url = "https://www.dlsite.com/maniax/ranking/day?category=voice"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print("ページを取得中...")
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# work_nameを全て取得
work_names = soup.select('dt.work_name a')

print(f"\n取得した作品数: {len(work_names)}件\n")
print("=== 最初の5件 ===")
for i, work in enumerate(work_names[:5], 1):
    print(f"{i}位: {work.get_text(strip=True)}")