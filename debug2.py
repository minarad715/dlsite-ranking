import requests
from bs4 import BeautifulSoup

url = "https://www.dlsite.com/maniax/ranking/day?category=voice"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

print("ページを取得中...")
response = requests.get(url, headers=headers)

# HTMLを保存
with open('voice_page.html', 'w', encoding='utf-8') as f:
    f.write(response.text)

print("✅ voice_page.html に保存しました")
print(f"HTML長さ: {len(response.text)} 文字")