import json
import ollama
from datetime import datetime
import os

def generate_article_with_ai(ranking_data):
    """AIを使ってランキング記事を生成"""
    
    print("AIで記事を生成中...")
    
    # ランキングTOP10のデータを整形
    top10 = ranking_data[:10]
    ranking_text = "\n".join([
        f"{item['rank']}位: {item['title']} - {item['price']}"
        for item in top10
    ])
    
    # AIへのプロンプト
    prompt = f"""以下のDLsite音声作品ランキングTOP10をもとに、ブログ記事を書いてください。

ランキングデータ:
{ranking_text}

記事の要件:
- タイトルは「【{datetime.now().strftime('%Y年%m月%d日')}】DLsite音声作品デイリーランキングTOP10」
- 各作品について簡潔に紹介
- 読者が興味を持つような文章
- 300-500文字程度

記事を書いてください:"""
    
    try:
        # Ollamaで記事生成
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
    <style>
        body {{
            font-family: 'Segoe UI', sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }}
        .ranking-item {{
            border: 1px solid #ddd;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
        }}
        .rank {{
            font-size: 24px;
            font-weight: bold;
            color: #ff6b6b;
        }}
        .affiliate-link {{
            display: inline-block;
            background: #4CAF50;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            margin-top: 10px;
        }}
        .affiliate-link:hover {{
            background: #45a049;
        }}
    </style>
</head>
<body>
    <div class="article">
        {article.replace(chr(10), '<br>')}
    </div>
    
    <h2>詳細ランキング</h2>
"""
        
        # 各作品の詳細とアフィリエイトリンク追加
        for item in top10:
            html_content += f"""
    <div class="ranking-item">
        <div class="rank">{item['rank']}位</div>
        <h3>{item['title']}</h3>
        <p>価格: {item['price']}</p>
        <a href="{item['url']}" class="affiliate-link" target="_blank">この作品をチェック →</a>
    </div>
"""
        
        html_content += """
</body>
</html>
"""
        
        # ファイル保存
        filename = f"article_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\n✅ 記事を生成しました: {filename}")
        print(f"📝 記事プレビュー:\n{article[:200]}...\n")
        
        return filename
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # 最新のランキングファイルを読み込む
    json_files = [f for f in os.listdir('.') if f.startswith('ranking_') and f.endswith('.json')]
    
    if not json_files:
        print("❌ ランキングファイルが見つかりません")
        print("先に python scraper.py を実行してください")
    else:
        latest_file = sorted(json_files)[-1]
        print(f"📂 {latest_file} を読み込みます")
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            ranking_data = json.load(f)
        
        generate_article_with_ai(ranking_data)