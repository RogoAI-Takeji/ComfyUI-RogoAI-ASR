# ComfyUI-RogoAI-ASR

**RogoAI Audio処理ノード集** - 動画から音声抽出 + 長尺音声対応ASR

## 🎯 特徴

### 1. RogoAI Extract Audio from Video
- 動画ファイルから音声を高速抽出
- 外部プロセスで実行（ComfyUIに負担なし）
- WAV/MP3出力対応
- キャッシュ機能付き

### 2. RogoAI Qwen3-ASR Long Audio Edition ⭐NEW
**公式Qwen3-ASRノードの改良版**

#### 主な改良点:
- ✅ **長尺音声対応**: max_new_tokens を 256 → 8192 (デフォルト)
- ✅ **プログレスバー表示**: 処理状況を可視化
- ✅ **推奨値自動計算**: 音声長に応じた最適設定を提案
- ✅ **デバッグモード**: トークン消費量などの詳細情報
- ✅ **32倍の拡張性**: 最大32768トークン対応

#### 公式との比較:
| 項目 | 公式ノード | RogoAI版 |
|------|-----------|----------|
| max_new_tokens | 256 (固定) | 256〜32768 (調整可能) |
| デフォルト値 | 256 | 8192 (32倍) |
| 対応音声長 | ~30秒 | ~20分以上 |
| プログレスバー | なし | あり |
| 推奨値表示 | なし | あり |
| デバッグ情報 | なし | あり |

## 📦 インストール

### 必須要件
```bash
# Qwen3-ASR本体
pip install qwen-asr

# ffmpeg (音声抽出用)
# Windowsの場合: https://ffmpeg.org/download.html からダウンロード
```

### ComfyUI Manager経由
1. ComfyUI Manager を開く
2. "Install Custom Nodes" で検索: `RogoAI-ASR`
3. Install をクリック

### 手動インストール
```bash
cd ComfyUI/custom_nodes/
git clone https://github.com/[your-repo]/ComfyUI-RogoAI-ASR.git
cd ComfyUI-RogoAI-ASR
pip install -r requirements.txt
```

## 🚀 使い方

### 基本ワークフロー

```
[動画ファイル]
    ↓
[RogoAI Extract Audio from Video]
    ↓ audio_file_path
[VHS Load Audio Upload] (音声読み込み)
    ↓ audio
[RogoAI Qwen3-ASR Loader] (max_new_tokens=8192)
    ↓ model
[RogoAI Qwen3-ASR Transcribe] (debug_mode=True)
    ↓ text
[Show Text]
```

### パラメータガイド

#### max_new_tokens の設定目安:
| 音声長 | 推奨値 | 説明 |
|--------|--------|------|
| ~1分 | 512 | 短い音声 |
| 1-5分 | 2048 | 標準的な長さ |
| 5-10分 | 4096 | 中尺動画 |
| 10-20分 | 8192 | 長尺動画 (デフォルト) |
| 20-40分 | 16384 | 超長尺 |
| 40分以上 | 32768 | 最大値 |

💡 **自動計算機能**: Transcribeノード実行時に、音声長に応じた推奨値がコンソールに表示されます。

## 📊 デバッグモード

`debug_mode=True` で詳細情報を表示:

```
🎤 RogoAI Qwen3-ASR Long Audio Edition
================================================================================
📊 音声情報:
   - 長さ: 750.0秒 (12.5分)
   - サンプルレート: 48000 Hz
   - 言語: Japanese
💡 推奨 max_new_tokens: 5,625
⚙️  現在の max_new_tokens: 8,192
================================================================================
[プログレスバー表示]
文字起こし中... 100% ████████████████████ 750.0秒の音声を処理
================================================================================
✅ RogoAI Qwen3-ASR 処理完了
📊 結果:
   - 音声長: 750.0秒 (12.5分)
   - 文字数: 12,487 chars
   - 検出言語: Japanese
   - 処理時間: 28.3秒
   - 処理速度: 26.5x リアルタイム
================================================================================
```

## ⚠️ トラブルシューティング

### Q: 文字起こしが途中で止まる
**A:** max_new_tokens が不足しています
- Loaderノードの `max_new_tokens` を増やしてください
- コンソールの「推奨値」を参考に設定

### Q: メモリ不足エラー
**A:** max_new_tokens を下げるか、音声を分割
- 16GB VRAM: max_new_tokens=8192 推奨
- 8GB VRAM: max_new_tokens=4096 推奨

### Q: プログレスバーが動かない
**A:** 正常です
- Qwen3-ASRは内部処理が高速なため、バーは瞬間的に完了します
- バーは「処理中」か「フリーズ」かの判別に使用

### Q: ffmpegが見つからない
**A:** ffmpegをインストールしてください
1. https://ffmpeg.org/download.html からダウンロード
2. C:\ffmpeg\ に解凍
3. システム環境変数PATHに `C:\ffmpeg\bin` を追加

## 🔧 技術仕様

### RogoAI Qwen3-ASR Loader
- **入力**: repo_id, precision, max_new_tokens など
- **出力**: QWEN3_ASR_MODEL
- **デフォルト設定**:
  - max_new_tokens: 8192 (公式の32倍)
  - precision: fp16 (VRAM節約)

### RogoAI Qwen3-ASR Transcribe
- **入力**: model, audio, language, debug_mode
- **出力**: text, language, timestamps
- **機能**:
  - 自動言語検出
  - タイムスタンプ生成
  - プログレスバー表示
  - 詳細統計情報

## 📝 更新履歴

### v1.0.0 (2026-02-06)
- 🎉 初回リリース
- ✨ RogoAI Extract Audio from Video
- ⭐ RogoAI Qwen3-ASR Long Audio Edition
  - max_new_tokens 拡張 (256→8192)
  - プログレスバー実装
  - デバッグモード追加
  - 推奨値自動計算

## 👤 作者

**たけ爺 (Take-jii)** - [老後AI YouTube Channel](https://youtube.com/@rogoai)

- GitHub: [ComfyUI-RogoAI-ASR](https://github.com/[your-repo])
- YouTube: チュートリアル動画公開中

## 📄 ライセンス

MIT License

## 🙏 謝辞

- Qwen3-ASR開発チーム
- ComfyUI開発者の皆様
- 老後AIコミュニティ

---

**🎬 YouTube動画で詳しい使い方を解説しています！**

[老後AIチャンネル](https://youtube.com/@rogoai) でチェック！