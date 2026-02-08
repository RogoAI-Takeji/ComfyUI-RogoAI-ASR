# ComfyUI-RogoAI-ASR

**Qwen3-ASRを使った長時間音声の文字起こし・日本語SRT出力対応 ComfyUIカスタムノード**

[![YouTube](https://img.shields.io/badge/YouTube-老後AI-red?logo=youtube)](あなたの動画URL)
[![GitHub](https://img.shields.io/github/stars/RogoAI-Takeji/ComfyUI-RogoAI-ASR?style=social)](https://github.com/RogoAI-Takeji/ComfyUI-RogoAI-ASR)

---

## 概要

このカスタムノードは、Alibaba Cloudが2026年1月29日にリリースした**Qwen3-ASR**をComfyUIで実用的に使えるようにしたものです。

### 公式版の制限を解決
- ❌ 公式サンプル：トークン数256制限 → **1分程度の音声のみ**
- ❌ 標準ノード：Load Videoでメモリ不足 → **5分でクラッシュ**
- ❌ SRT出力：単語単位のみ → **YouTube用日本語文節に非対応**

### RogoAI版の特長
- ✅ **長時間音声対応**：11分以上の動画も処理可能
- ✅ **自動音声抽出**：動画から音声を自動分離（ffmpeg手動操作不要）
- ✅ **日本語文節SRT**：YouTube字幕に最適化
- ✅ **精度評価機能**：原稿と比較して客観的に数値評価

---

## 動作環境

- **ComfyUI**: 最新版
- **Python**: 3.10以上
- **VRAM**: 12GB以上推奨（Qwen3-ASR単独なら8GB可）
- **OS**: Windows/Linux

---

## インストール

### 1. リポジトリのクローン

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/RogoAI-Takeji/ComfyUI-RogoAI-ASR.git
cd ComfyUI-RogoAI-ASR
```

### 2. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 3. ComfyUIを再起動

---

## 使い方

### 基本ワークフロー

1. **動画読み込み** → `RogoAI Extract Audio` ノード
2. **音声抽出** → 自動でTEMPフォルダに展開
3. **Load Audio** → 文字起こし対象時間を設定
4. **RogoAI Qwen3 ASR Loader** → モデル読み込み
5. **RogoAI Qwen3 ASR Transcribe** → 文字起こし実行
6. **Words to Segments** → 日本語文節SRT生成

### サンプルワークフロー

動画で紹介したワークフローは[こちら](workflows/)からダウンロードできます。

---

## ノード一覧

| ノード名 | 機能 |
|---------|------|
| **RogoAI Extract Audio** | 動画から音声を自動抽出（TEMP展開） |
| **RogoAI Extract Audio v2** | 音声抽出＋保存機能付き |
| **RogoAI Qwen3 ASR Loader** | Qwen3-ASRモデルの読み込み |
| **RogoAI Qwen3 ASR Transcribe** | 長時間音声の文字起こし |
| **RogoAI Words to Segments** | 日本語文節SRT生成 |
| **RogoAI Load Text File** | テキストファイル読み込み |
| **RogoAI Compare Three Texts** | 精度評価（3ファイル比較） |

---

## 注意事項

### VRAM管理
- Qwen3-ASR（0.6B/1.7B）とWhisper（Large V3）の同時実行は困難
- **Group Bypasser**で処理を切り替えてください
- メモリオーバー時は**ComfyUI再起動**でメモリ解放

### SRT日本語文節の調整
- デフォルト：最大秒数8秒、最大文字数50文字
- 違和感がある場合：**最大秒数6秒、最大文字数40文字**に下げる

### 音声形式
- Sample Rate: **16000Hz**推奨
- フォーマット: WAV/MP3対応

---

## 実測性能（動画で検証）

**テスト条件**: 11分27秒の動画（3786文字）

| モデル | 処理時間 | 精度 | 文字数 |
|--------|---------|------|--------|
| **Qwen3-ASR** | 2分30秒 | 73.6% | 削除率高 |
| **Whisper** | 4分52秒 | 80.6% | 負荷率高 |
| **Faster Whisper** | 4分56秒 | 高精度 | 削除率高 |

### 使い分けの目安
- **速度重視** → Qwen3-ASR
- **精度重視** → Whisper/Faster Whisper
- **既に原稿がある** → Qwen3-ASR（タイムスタンプ取得のみ）

---

## トラブルシューティング

### Q: モデル読み込みが遅い
**A**: 初回起動時は正常です（Hugging Faceから自動ダウンロード）

### Q: メモリ不足エラー
**A**: 
1. Group Bypasserで片方のモデルをバイパス
2. ComfyUI再起動
3. VRAM確認（12GB未満の場合は0.6Bモデル使用）

### Q: SRTが出力されない
**A**: `forced_aligner`を**0.6B**に設定してください

---

## 開発者情報

**老後AI（RogoAI）/ たけ爺**
- YouTube: [老後AI チャンネル](あなたのチャンネルURL)
- コンセプト：「高齢者は時間がない。完璧な状態で公開する」

年金生活でもローカルAIに挑戦する、アラセブンティーの技術ドキュメントです。

---

## ライセンス

MIT License

---

## 更新履歴

- **2026/02/08**: 初回リリース
  - 長時間音声対応
  - 日本語文節SRT出力
  - 精度評価機能

---

**English Documentation**: [README.md](README.md)
