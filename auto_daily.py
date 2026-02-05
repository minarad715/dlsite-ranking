import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import ollama
import os
import time

def scrape_dlsite_ranking():
    """DLsiteのランキングをスクレイピング"""
    
    url = "https://www.dlsite.com/maniax/ranking/day?category=voice"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print("🔍 DLsiteランキングを取得中...")
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        ranking_data = []
        
        # work_nameから取得
        work_names = soup.select('dt.work_name a')
        
        print(f"   見つかった作品数: {len(work_names)}件")
        
        for idx, work in enumerate(work_names[:30], 1):
            try:
                # タイトル
                title = work.get_text(strip=True)
                work_url = work.get('href', '')
                
                # アフィリエイトID追加
                if work_url and '?' not in work_url:
                    work_url += '/?affiliate_id=realolchan'
                elif work_url and '?' in work_url:
                    work_url += '&affiliate_id=realolchan'
                
                # 親要素から価格を取得
                parent = work.find_parent('dl')
                price = "価格情報なし"
                if parent:
                    price_elem = parent.select_one('.work_price')
                    if price_elem:
                        price = price_elem.get_text(strip=True)
                
                # サムネイル画像
                thumbnail = ""
                # trタグまでさかのぼる
                tr_parent = work
                for _ in range(10):
                    tr_parent = tr_parent.find_parent()
                    if tr_parent and tr_parent.name == 'tr':
                        break
                
                if tr_parent:
                    img_elem = tr_parent.find('img', class_='lazy')
                    if img_elem and 'src' in img_elem.attrs:
                        thumbnail = img_elem['src']
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

def get_circle_latest_works():
    """サークルの最新作を取得（男性向け・発売済みのみ、必ず2作品）"""
    
    # サークルプロフィールページURL
    circle_urls = [
        'https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG01059653.html',
        'https://www.dlsite.com/maniax/circle/profile/=/maker_id/RG01020625.html'
    ]
    
    latest_works = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    print("\n🎨 サークル作品を取得中...")
    
    for url in circle_urls:
        # 既に2作品取得したら終了
        if len(latest_works) >= 2:
            break
            
        try:
            # URLからcircle_idを抽出
            circle_id = url.split('maker_id/')[1].split('.html')[0]
            
            print(f"   サークル {circle_id} のページを取得中...")
            
            # サークルページにアクセス
            response = requests.get(url, headers=headers)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 正しいセレクタで作品リンクを取得
            work_links = soup.select('a[href*="/work/"]')
            
            print(f"      {len(work_links)}件の作品リンクを発見")
            
            if len(work_links) == 0:
                print(f"      ⚠️ 作品が見つかりませんでした")
                continue
            
            # 最初の5件をチェック
            for work_link in work_links[:5]:
                work_url = work_link.get('href', '')
                
                if not work_url:
                    continue
                
                # 女性向け作品は除外
                if '/girls/' in work_url:
                    print(f"      スキップ: 女性向け作品")
                    continue
                
                # 予約作品を除外
                if '/announce/' in work_url:
                    title_text = work_link.get_text(strip=True)
                    print(f"      スキップ: 予約作品 - {title_text[:40]}")
                    continue
                
                # タイトルを取得
                title = work_link.get_text(strip=True)
                
                # タイトルが空の場合は、近くのテキストを探す
                if not title or len(title) < 3:
                    parent = work_link.find_parent()
                    if parent:
                        title_elem = parent.find('a', href=work_url)
                        if title_elem:
                            title = title_elem.get_text(strip=True)
                
                # それでもタイトルが取れない場合はスキップ
                if not title or len(title) < 3:
                    continue
                
                # 発売済み作品を発見
                print(f"      ✅ 発売済み作品を発見: {title[:40]}")
                
                # 完全なURLにする
                if not work_url.startswith('http'):
                    work_url = 'https://www.dlsite.com' + work_url
                
                # アフィリエイトID追加
                if '?' not in work_url:
                    work_url += '/?affiliate_id=realolchan'
                else:
                    work_url += '&affiliate_id=realolchan'
                
                # サムネイル取得
                thumbnail = ""
                parent = work_link.find_parent()
                for _ in range(5):
                    if parent:
                        img_elem = parent.find('img')
                        if img_elem:
                            img_src = img_elem.get('src') or img_elem.get('data-src')
                            if img_src:
                                thumbnail = img_src
                                if thumbnail.startswith('//'):
                                    thumbnail = "https:" + thumbnail
                                break
                        parent = parent.find_parent()
                
                latest_works.append({
                    'title': title,
                    'url': work_url,
                    'thumbnail': thumbnail,
                    'circle_id': circle_id
                })
                break  # このサークルの1作品だけ
                
        except Exception as e:
            print(f"   ⚠️ サークル取得エラー: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print(f"   ✅ {len(latest_works)}作品取得完了")
    return latest_works

def generate_article_with_ai(ranking_data):
    """AIを使ってランキング記事を生成"""
    
    print("\n🤖 AIで記事を生成中...")
    
    top10 = ranking_data[:10]
    ranking_text = "\n".join([
        f"{item['rank']}位: {item['title']} - {item['price']}"
        for item in top10
    ])
    
    print("\n=== AIに渡すランキングデータ ===")
    print(ranking_text)
    print("=" * 50)
    
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
        
        # サークル作品を取得
        circle_works = get_circle_latest_works()
        
        # サークル作品HTMLを生成
        circle_works_html = ""
        if circle_works:
            circle_works_html = '<div class="sidebar-widget"><h3>🌟 おすすめ新作作品</h3>'
            for work in circle_works:
                thumbnail_html = ""
                if work.get('thumbnail'):
                    thumbnail_html = f'<img src="{work["thumbnail"]}" alt="{work["title"]}" style="width: 100%; border-radius: 5px; margin-bottom: 10px;">'
                
                circle_works_html += f'''
                <div style="margin-bottom: 20px; padding-bottom: 20px; border-bottom: 1px solid #eee;">
                    {thumbnail_html}
                    <div style="font-size: 14px; font-weight: bold; margin-bottom: 5px;">{work['title']}</div>
                    <a href="{work['url']}" target="_blank" style="display: block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 8px; text-align: center; text-decoration: none; border-radius: 5px;">この作品をチェック</a>
                </div>
                '''
            
            circle_works_html += '</div>'
        
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
            max-width: 1200px;
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
        .container {{
            display: flex;
            gap: 30px;
        }}
        .main-content {{
            flex: 2;
        }}
        .sidebar {{
            flex: 1;
            max-height: calc(100vh - 100px);
            overflow-y: auto;
            position: sticky;
            top: 20px;
        }}
        .sidebar::-webkit-scrollbar {{
            width: 8px;
        }}
        .sidebar::-webkit-scrollbar-track {{
            background: #f1f1f1;
            border-radius: 10px;
        }}
        .sidebar::-webkit-scrollbar-thumb {{
            background: #888;
            border-radius: 10px;
        }}
        .sidebar::-webkit-scrollbar-thumb:hover {{
            background: #555;
        }}
        .sidebar-widget {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .sidebar-widget h3 {{
            margin-top: 0;
            color: #667eea;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
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
        @media (max-width: 768px) {{
            .container {{
                flex-direction: column;
            }}
            .sidebar {{
                max-height: none;
                position: relative;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎵 DLsite音声作品ランキング</h1>
        <p>{datetime.now().strftime('%Y年%m月%d日')} 更新</p>
    </div>
    
    <div class="container">
        <div class="main-content">
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
        </div>
        
        <aside class="sidebar">
            {circle_works_html}
            
            <div class="sidebar-widget">
                <h3>📚 おすすめ関連商品</h3>
                <p style="margin-bottom: 15px;">音声作品と一緒に楽しめる関連商品</p>
                <a href="https://amzn.to/4ady7O9" target="_blank" style="display: block; background: #FF9900; color: white; padding: 10px; text-align: center; text-decoration: none; border-radius: 5px; margin-bottom: 10px;">📚 声優写真集を見る</a>
                <a href="https://www.amazon.co.jp/s?k=ASMR+マイク&tag=minarad715-22" target="_blank" style="display: block; background: #FF9900; color: white; padding: 10px; text-align: center; text-decoration: none; border-radius: 5px; margin-bottom: 10px;">🎤 ASMRマイクを探す</a>
                <a href="https://www.amazon.co.jp/s?k=ヘッドホン+ASMR&tag=minarad715-22" target="_blank" style="display: block; background: #FF9900; color: white; padding: 10px; text-align: center; text-decoration: none; border-radius: 5px;">🎧 高音質イヤホン</a>
            </div>
            
            <div class="sidebar-widget">
                <h3>🔥 人気カテゴリ</h3>
                <ul style="list-style: none; padding: 0;">
                    <li style="margin: 10px 0;">🎤 ボイスドラマ</li>
                    <li style="margin: 10px 0;">🎧 ASMR</li>
                    <li style="margin: 10px 0;">💕 乙女向け</li>
                    <li style="margin: 10px 0;">🎮 シチュエーションボイス</li>
                </ul>
            </div>
            
            <div class="sidebar-widget">
                <h3>ℹ️ このサイトについて</h3>
                <p>DLsite音声作品の最新ランキングを毎日自動更新でお届けしています。</p>
            </div>
        </aside>
    </div>
    
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
        print("✅ すべての処理が完了しました!")
        print(f"📄 生成されたファイル: {article_file}")
        print("=" * 60)

if __name__ == "__main__":
    main()