"""
RogoAI Compare Three Texts (改良版レイアウト)
任意の3つのテキストを自由に比較

レイアウト改良:
- 基準文字数を最初に単独表示
- 各テキストの統計を横並びで比較しやすく
- 3カラムテキスト表示を常に維持
"""

import difflib
import os
from pathlib import Path
from html import escape as html_escape

class RogoAI_CompareThreeTexts:
    """
    3つのテキストを比較してHTML比較レポートを生成
    
    【特徴】
    ・任意の3つのテキストを比較可能
    ・基準テキストを選択可能
    ・カスタムラベル対応
    ・削除率・付加率の分析
    ・見やすい横並び比較レイアウト
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                # テキストA
                "text_a": ("STRING", {
                    "default": "",
                    "multiline": True
                }),
                "text_a_label": ("STRING", {
                    "default": "Text A",
                    "multiline": False
                }),
                
                # テキストB
                "text_b": ("STRING", {
                    "default": "",
                    "multiline": True
                }),
                "text_b_label": ("STRING", {
                    "default": "Text B",
                    "multiline": False
                }),
                
                # テキストC
                "text_c": ("STRING", {
                    "default": "",
                    "multiline": True
                }),
                "text_c_label": ("STRING", {
                    "default": "Text C",
                    "multiline": False
                }),
                
                # 基準テキスト選択
                "baseline": (["text_a", "text_b", "text_c"], {
                    "default": "text_a"
                }),
                
                # 出力設定
                "output_filename": ("STRING", {
                    "default": "comparison_3way_report.html",
                    "multiline": False
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "FLOAT", "FLOAT", "FLOAT")
    RETURN_NAMES = ("html_path", "summary", "accuracy_a", "accuracy_b", "accuracy_c")
    FUNCTION = "compare_texts"
    CATEGORY = "RogoAI/Analysis"
    
    DESCRIPTION = """
任意の3つのテキストを比較（改良版レイアウト）

【使用例】
1. Original vs Qwen3-ASR vs Whisper
2. Qwen3-ASR vs Whisper vs FasterWhisper
3. 手動修正版 vs AI版1 vs AI版2

【baseline設定】
比較の基準とするテキストを選択
    """
    
    def _compare_with_baseline(self, baseline: str, text: str, label: str):
        """
        基準テキストと比較して統計を計算
        """
        matcher = difflib.SequenceMatcher(None, baseline, text)
        similarity = matcher.ratio() * 100
        
        stats = {
            "equal": 0, 
            "replace": 0, 
            "delete": 0, 
            "insert": 0,
            "deleted_chars": 0,
            "added_chars": 0
        }
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            stats[tag] += 1
            
            if tag == 'delete':
                stats['deleted_chars'] += (i2 - i1)
            elif tag == 'insert':
                stats['added_chars'] += (j2 - j1)
        
        baseline_len = len(baseline)
        stats['deletion_rate'] = (stats['deleted_chars'] / baseline_len * 100) if baseline_len > 0 else 0
        stats['addition_rate'] = (stats['added_chars'] / baseline_len * 100) if baseline_len > 0 else 0
        
        return similarity, stats, matcher
    
    def _generate_html_report(self, texts, labels, baseline_idx, 
                             accuracies, all_stats, output_path):
        """
        HTML比較レポート生成（改良版レイアウト）
        """
        baseline_label = labels[baseline_idx]
        
        # 基準以外のインデックス
        other_indices = [i for i in range(3) if i != baseline_idx]
        
        html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3方向テキスト比較 - {baseline_label} 基準</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Meiryo, sans-serif;
            padding: 20px;
            background: #f5f5f5;
            max-width: 1600px;
            margin: 0 auto;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}
        .baseline-info {{
            background: rgba(255,255,255,0.2);
            padding: 10px;
            border-radius: 5px;
            margin-top: 10px;
        }}
        
        /* 基準文字数カード（単独） */
        .baseline-card-container {{
            margin-bottom: 30px;
        }}
        .baseline-card {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border: 3px solid #667eea;
            text-align: center;
        }}
        .baseline-card h3 {{
            color: #667eea;
            font-size: 16px;
            margin-bottom: 15px;
        }}
        .baseline-card .value {{
            font-size: 48px;
            font-weight: bold;
            color: #667eea;
        }}
        
        /* 統計グリッド（横4列） */
        .stats-row {{
            margin-bottom: 20px;
        }}
        .stats-row h4 {{
            color: #333;
            margin-bottom: 10px;
            padding-left: 5px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .stat-card h3 {{
            color: #666;
            font-size: 13px;
            margin-bottom: 10px;
        }}
        .stat-card .value {{
            font-size: 28px;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-card .subtext {{
            font-size: 11px;
            color: #999;
            margin-top: 5px;
        }}
        .stat-card.winner {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }}
        .stat-card.winner h3 {{
            color: white;
        }}
        .stat-card.winner .value {{
            color: white;
        }}
        .stat-card.winner .subtext {{
            color: rgba(255,255,255,0.8);
        }}
        
        /* 削除率・付加率の色分け */
        .deletion-card {{
            background: #fff3cd;
        }}
        .deletion-card .value {{
            color: #dc3545;
        }}
        .addition-card {{
            background: #d4edda;
        }}
        .addition-card .value {{
            color: #28a745;
        }}
        
        /* 凡例 */
        .legend {{
            background: white;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        .legend-item {{
            display: inline-block;
            margin-right: 20px;
            padding: 5px 10px;
            border-radius: 4px;
        }}
        
        /* 3カラムテキスト比較（常に3列） */
        .comparison {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 15px;
            margin-bottom: 20px;
        }}
        .column {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            min-height: 400px;
        }}
        .column.baseline {{
            background: #f8f9fa;
            border: 2px solid #667eea;
        }}
        .column h2 {{
            margin: 0 0 15px 0;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
            color: #333;
            font-size: 18px;
            position: sticky;
            top: 0;
            background: inherit;
            z-index: 10;
        }}
        .text-content {{
            line-height: 1.8;
            font-size: 15px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        .same {{
            background-color: transparent;
        }}
        .diff {{
            background-color: #fff3cd;
            padding: 2px 4px;
            border-radius: 3px;
            border-left: 3px solid #ffc107;
        }}
        .added {{
            background-color: #d4edda;
            padding: 2px 4px;
            border-radius: 3px;
            border-left: 3px solid #28a745;
        }}
        .removed {{
            background-color: #f8d7da;
            padding: 2px 4px;
            border-radius: 3px;
            border-left: 3px solid #dc3545;
            text-decoration: line-through;
        }}
        
        /* レスポンシブ（小画面では1列に） */
        @media (max-width: 1200px) {{
            .stats-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
            .comparison {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 3方向テキスト比較レポート</h1>
        <p>{labels[0]} vs {labels[1]} vs {labels[2]}</p>
        <div class="baseline-info">
            📌 基準テキスト: <strong>{baseline_label}</strong>
        </div>
    </div>
    
    <!-- 基準文字数（単独表示） -->
    <div class="baseline-card-container">
        <div class="baseline-card">
            <h3>📝 {baseline_label} 文字数（基準）</h3>
            <div class="value">{len(texts[baseline_idx]):,}</div>
        </div>
    </div>
"""
        
        # 各テキストの統計を行ごとに表示
        for idx in other_indices:
            label = labels[idx]
            acc = accuracies[idx]
            stats = all_stats[idx]
            is_winner = acc == max([accuracies[i] for i in other_indices])
            winner_class = " winner" if is_winner else ""
            
            html += f"""
    <!-- {label} の統計 -->
    <div class="stats-row">
        <h4>🎤 {label}</h4>
        <div class="stats-grid">
            <div class="stat-card{winner_class}">
                <h3>精度</h3>
                <div class="value">{acc:.1f}%</div>
                <div class="subtext">vs {baseline_label}</div>
            </div>
            <div class="stat-card{winner_class}">
                <h3>文字数</h3>
                <div class="value">{len(texts[idx]):,}</div>
                <div class="subtext">{len(texts[idx]) - len(texts[baseline_idx]):+,}</div>
            </div>
            <div class="stat-card deletion-card">
                <h3>削除率</h3>
                <div class="value">{stats['deletion_rate']:.1f}%</div>
                <div class="subtext">{stats['deleted_chars']} 文字</div>
            </div>
            <div class="stat-card addition-card">
                <h3>付加率</h3>
                <div class="value">{stats['addition_rate']:.1f}%</div>
                <div class="subtext">{stats['added_chars']} 文字</div>
            </div>
        </div>
    </div>
"""
        
        html += """
    <!-- 凡例 -->
    <div class="legend">
        <strong>凡例:</strong>
        <span class="legend-item same">⚪ 基準と一致</span>
        <span class="legend-item diff">🟡 差異</span>
        <span class="legend-item added">🟢 追加</span>
        <span class="legend-item removed">🔴 削除</span>
    </div>
    
    <!-- 3カラムテキスト比較（常に3列） -->
    <div class="comparison">
"""
        
        # テキスト比較カラム生成
        baseline_text = texts[baseline_idx]
        
        # 基準カラム
        html += f"""
        <div class="column baseline">
            <h2>📄 {baseline_label} (基準)</h2>
            <div class="text-content">{html_escape(baseline_text)}</div>
        </div>
"""
        
        # 他のカラム
        for idx in other_indices:
            matcher = difflib.SequenceMatcher(None, baseline_text, texts[idx])
            
            html += f"""
        <div class="column">
            <h2>📄 {labels[idx]}</h2>
            <div class="text-content">
"""
            
            for tag, i1, i2, j1, j2 in matcher.get_opcodes():
                chunk = html_escape(texts[idx][j1:j2])
                
                if tag == 'equal':
                    html += f'<span class="same">{chunk}</span>'
                elif tag == 'replace':
                    html += f'<span class="diff">{chunk}</span>'
                elif tag == 'insert':
                    html += f'<span class="added">{chunk}</span>'
                elif tag == 'delete':
                    removed_text = html_escape(baseline_text[i1:i2][:20])
                    html += f'<span class="removed">[削除: {removed_text}...]</span>'
            
            html += """
            </div>
        </div>
"""
        
        html += """
    </div>
</body>
</html>
"""
        
        # ファイル保存
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        
        return output_path
    
    def compare_texts(self, text_a, text_a_label, text_b, text_b_label, 
                     text_c, text_c_label, baseline, output_filename):
        """
        3つのテキストを比較
        """
        print("\n" + "="*80)
        print("📊 RogoAI Compare Three Texts")
        print("="*80)
        
        texts = [text_a, text_b, text_c]
        labels = [text_a_label, text_b_label, text_c_label]
        
        baseline_map = {"text_a": 0, "text_b": 1, "text_c": 2}
        baseline_idx = baseline_map[baseline]
        baseline_text = texts[baseline_idx]
        baseline_label = labels[baseline_idx]
        
        print(f"\n📌 基準テキスト: {baseline_label}")
        print(f"📝 文字数: {len(baseline_text):,} characters")
        print()
        
        accuracies = [100.0, 0.0, 0.0]
        all_stats = [None, None, None]
        
        for i, (text, label) in enumerate(zip(texts, labels)):
            if i == baseline_idx:
                all_stats[i] = {
                    'equal': 1,
                    'replace': 0,
                    'delete': 0,
                    'insert': 0,
                    'deleted_chars': 0,
                    'added_chars': 0,
                    'deletion_rate': 0.0,
                    'addition_rate': 0.0
                }
                continue
            
            print("="*80)
            print(f"🎤 {label} の精度")
            print("="*80)
            
            similarity, stats, _ = self._compare_with_baseline(
                baseline_text, text, label
            )
            
            accuracies[i] = similarity
            all_stats[i] = stats
            
            print(f"📈 {baseline_label}との一致率: {similarity:.2f}%")
            print(f"📝 文字数: {len(text):,} characters ({len(text) - len(baseline_text):+,})")
            print(f"❌ 削除率: {stats['deletion_rate']:.2f}%")
            print(f"➕ 付加率: {stats['addition_rate']:.2f}%")
            print()
        
        non_baseline_accs = [(i, acc) for i, acc in enumerate(accuracies) if i != baseline_idx]
        winner_idx, winner_acc = max(non_baseline_accs, key=lambda x: x[1])
        
        print("="*80)
        print("🏆 比較結果")
        print("="*80)
        print(f"🥇 最高精度: {labels[winner_idx]} ({winner_acc:.2f}%)")
        print()
        
        import folder_paths
        output_dir = folder_paths.get_output_directory()
        output_path = os.path.join(output_dir, output_filename)
        
        self._generate_html_report(
            texts, labels, baseline_idx,
            accuracies, all_stats, output_path
        )
        
        print(f"📄 HTMLレポート生成: {output_path}")
        print("="*80 + "\n")
        
        summary = (
            f"基準: {baseline_label}\n"
            f"{labels[0]}: {accuracies[0]:.2f}%\n"
            f"{labels[1]}: {accuracies[1]:.2f}%\n"
            f"{labels[2]}: {accuracies[2]:.2f}%\n"
            f"最高精度: {labels[winner_idx]}"
        )
        
        return (output_path, summary, accuracies[0], accuracies[1], accuracies[2])


# ノード登録
NODE_CLASS_MAPPINGS = {
    "RogoAI_CompareThreeTexts": RogoAI_CompareThreeTexts,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RogoAI_CompareThreeTexts": "RogoAI Compare Three Texts 📊",
}
