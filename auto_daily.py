import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import ollama
import os
import time

def scrape_dlsite_ranking():
    """DLsiteのランキングをスクレイピング"""
    
    url = "https://www.dlsite.com/maniax/ranking/=/term/daily/type/voice"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print("🔍 DLsiteランキングを取得中...")
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        ranking_data = []
        work_names = soup.select('dt.work_name a')
        
        print(f"   見つかった作品数: {len(work_names)}件")
        
        for idx, work in enumerate(work_names[:30], 1):
            try:
                title = work.get_text(strip=True)
                work_url = work.get('href', '')
                
                parent = work.find_parent('dl', class_='work_2col')
                price = "価格情報なし"
                if parent:
                    price_elem = parent.select_one('.work_price')
                    if price_elem:
                        price = price_elem.get_text(strip=True)
                # サムネイル画像を取得
                thumbnail = ""
                if parent:
                    grand_parent = parent.find_parent()
                    if grand_parent:
                        img_elem = grand_parent.find('img', class_='lazy')
                        if img_elem and 'src' in img_elem.attrs:
                            thumbnail = img_elem['src']
                            # // で始まる場合は https: を追加
                            if thumbnail.startswith('//'):
                                thumbnail = "https:" + thumbnail
                                
                ranking_data.append({
                    'rank': idx,
                    'title': title,
                    'url': work_url,
                    'price': price,
                    'thumbnail': thumbnail,
                    'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
                
            except Exception as e:
                continue
        
        print(f"   ✅ {len(ranking_data)}件取得完了")
        return ranking_data
        
    except Exception as e:
        print(f"   ❌ エラー: {e}")
        return []

def generate_article_with_ai(ranking_data):
    """AIを使ってランキング記事を生成"""
    
    print("\n🤖 AIで記事を生成中...")
    
    top10 = ranking_data[:10]
    ranking_text = "\n".join([
        f"{item['rank']}位: {item['title']} - {item['price']}"
        for item in top10
    ])
    
    prompt = f"""以下のDLsite音声作品ランキングTOP10をもとに、ブログ記事を書いてください。

ランキングデータ:
{ranking_text}

記事の要件:
- タイトルは「【{datetime.now().strftime('%Y年%m月%d日')}】DLsite音声作品デイリーランキングTOP10」
- 各作品について簡潔に紹介
- 読者が興味を持つような文章
- 300-500文字程度

日本語で記事を書いてください:"""
    
    try:
        response = ollama.chat(
            model='llama3.2',
            messages=[{
                'role': 'user',
                'content': prompt
            }]
        )
        
        article = response['message']['content']
        
        # HTMLファイルとして保存
        html_content = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>【{datetime.now().strftime('%Y年%m月%d日')}】DLsite音声作品ランキング</title>
    <meta name="description" content="DLsite音声作品のデイリーランキングTOP30を毎日更新">
    <style>
        body {{
            font-family: 'Segoe UI', 'Hiragino Sans', sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
            line-height: 1.8;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 30px;
        }}
        .article {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .ranking-item {{
            border: 1px solid #e0e0e0;
            padding: 20px;
            margin: 15px 0;
            border-radius: 8px;
            background: white;
            transition: transform 0.2s;
        }}
        .ranking-item:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        .rank {{
            font-size: 28px;
            font-weight: bold;
            color: #ff6b6b;
            margin-bottom: 10px;
        }}
        .title {{
            font-size: 18px;
            font-weight: bold;
            margin: 10px 0;
            color: #333;
        }}
        .price {{
            color: #666;
            font-size: 16px;
            margin: 10px 0;
        }}
        .thumbnail {{
            max-width: 200px;
            border-radius: 5px;
            margin-bottom: 10px;
        }}
        .affiliate-link {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 25px;
            margin-top: 10px;
            transition: all 0.3s;
        }}
        .affiliate-link:hover {{
            transform: scale(1.05);
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }}
        .footer {{
            text-align: center;
            padding: 20px;
            color: #666;
            margin-top: 50px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎵 DLsite音声作品ランキング</h1>
        <p>{datetime.now().strftime('%Y年%m月%d日')} 更新</p>
    </div>
    
    <div class="article">
        {article.replace(chr(10), '<br>')}
    </div>
    
    <h2 style="text-align: center; margin: 40px 0 20px;">📊 詳細ランキングTOP30</h2>
"""
        
        # 各作品の詳細
        for item in ranking_data[:30]:
            thumbnail_html = ""
            if item.get('thumbnail'):
                thumbnail_html = f'<img src="{item["thumbnail"]}" alt="{item["title"]}" class="thumbnail">'
            
            html_content += f"""
    <div class="ranking-item">
        <div class="rank">🏆 {item['rank']}位</div>
        {thumbnail_html}
        <div class="title">{item['title']}</div>
        <div class="price">💰 {item['price']}</div>
        <a href="{item['url']}" class="affiliate-link" target="_blank">この作品をチェック →</a>
    </div>
"""
        
        html_content += f"""
    <div class="footer">
        <p>毎日更新 | 最終更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
</body>
</html>
"""
        
        # ファイル保存
        filename = f"index.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"   ✅ 記事を生成しました: {filename}")
        
        return filename
        
    except Exception as e:
        print(f"   ❌ エラー: {e}")
        return None

def main():
    """メイン処理"""
    print("=" * 60)
    print("🚀 DLsiteランキング記事自動生成ツール")
    print("=" * 60)
    
    # ランキング取得
    ranking_data = scrape_dlsite_ranking()
    
    if not ranking_data:
        print("\n❌ ランキングデータの取得に失敗しました")
        return
    
    # 記事生成
    article_file = generate_article_with_ai(ranking_data)
    
    if article_file:
        print("\n" + "=" * 60)
        print("✅ すべての処理が完了しました！")
        print(f"📄 生成されたファイル: {article_file}")
        print("=" * 60)

if __name__ == "__main__":
    main()