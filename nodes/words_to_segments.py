"""
RogoAI Words To Segments
単語タイムスタンプから文節セグメントを生成

機能:
- Qwen3-ASR/Whisperのwords_timestampsからYouTube最適化セグメント生成
- 句点・疑問符での自動区切り
- 時間・文字数制限での強制区切り
- SRT字幕直接出力
"""

import json
import re

class RogoAI_WordsToSegments:
    """
    単語タイムスタンプから文節セグメントを生成
    
    【特徴】
    ・YouTube字幕最適化（3〜7秒）
    ・句点・疑問符での自然な区切り
    ・時間・文字数での自動調整
    ・SRT形式直接出力
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "words_timestamps_json": ("STRING", {
                    "default": "",
                    "multiline": True
                }),
                "mode": (["youtube", "subtitle", "precise"], {
                    "default": "youtube"
                }),
            },
            "optional": {
                "max_duration": ("FLOAT", {
                    "default": 7.0,
                    "min": 1.0,
                    "max": 30.0,
                    "step": 0.5
                }),
                "max_chars": ("INT", {
                    "default": 80,
                    "min": 20,
                    "max": 200,
                    "step": 10
                }),
                "sentence_end_marks": ("STRING", {
                    "default": "。?!？！…",
                    "multiline": False
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING", "INT")
    RETURN_NAMES = ("segments_text", "segments_json", "srt_content", "segment_count")
    FUNCTION = "generate_segments"
    CATEGORY = "RogoAI/ASR"
    
    DESCRIPTION = """
単語タイムスタンプから文節セグメント生成

【モード】
・youtube: 3〜7秒の視聴しやすいセグメント
・subtitle: 標準的な字幕（5〜10秒）
・precise: 精密な区切り（句読点厳密）

【入力フォーマット】
Qwen3-ASR/Whisperのタイムスタンプ:
[
  {"word": "こんにちは", "start": 0.5, "end": 1.2},
  {"word": "老後AI", "start": 1.3, "end": 2.0},
  ...
]

【出力】
・segments_text: 読みやすいテキスト
・segments_json: JSON形式セグメント
・srt_content: YouTube用SRT字幕
    """
    
    def _parse_words_timestamps(self, json_str):
        """
        タイムスタンプをパース（複数形式対応）
        
        対応形式:
        1. JSON形式: [{"word": "...", "start": 0.5, "end": 1.2}, ...]
        2. テキスト形式: "0.32-0.64: おはよう\n0.64-0.96: ござい\n..."
        """
        try:
            # 形式1: 既にリストやdictの場合（ComfyUIが自動変換）
            if isinstance(json_str, list):
                words = json_str
            elif isinstance(json_str, dict):
                if "words" in json_str:
                    words = json_str["words"]
                elif "timestamps" in json_str:
                    words = json_str["timestamps"]
                else:
                    raise ValueError(f"Unknown dict format: {list(json_str.keys())}")
            else:
                # 文字列の場合、形式を判定
                json_str = json_str.strip()
                
                # 形式2: テキスト形式（Qwen3-ASR）
                if '\n' in json_str or '-' in json_str[:20]:
                    # テキスト形式をパース
                    words = []
                    for line in json_str.split('\n'):
                        line = line.strip()
                        if not line:
                            continue
                        
                        # "0.32-0.64: おはよう" 形式をパース
                        try:
                            if ':' not in line:
                                continue
                            
                            time_part, word_text = line.split(':', 1)
                            word_text = word_text.strip()
                            
                            if '-' in time_part:
                                start_str, end_str = time_part.split('-')
                                start_time = float(start_str.strip())
                                end_time = float(end_str.strip())
                                
                                words.append({
                                    "word": word_text,
                                    "start": start_time,
                                    "end": end_time
                                })
                        except (ValueError, AttributeError) as e:
                            print(f"⚠️  Skipping malformed line: {line[:50]}")
                            continue
                else:
                    # 形式3: JSON形式
                    try:
                        words = json.loads(json_str)
                    except json.JSONDecodeError:
                        # 改行区切りのJSONオブジェクト
                        lines = json_str.split('\n')
                        words = []
                        for line in lines:
                            if line.strip():
                                words.append(json.loads(line))
            
            # リスト化（dict形式の可能性）
            if isinstance(words, dict):
                if "words" in words:
                    words = words["words"]
                elif "timestamps" in words:
                    words = words["timestamps"]
            
            # フォーマット検証
            if not isinstance(words, list):
                raise ValueError(f"Expected list, got {type(words)}: {str(words)[:100]}")
            
            # 各要素を検証・変換
            processed_words = []
            for i, word in enumerate(words):
                if not isinstance(word, dict):
                    print(f"⚠️  Word {i} is not a dict: {word}")
                    continue
                
                # 必須フィールド確認（柔軟に対応）
                word_text = word.get("word") or word.get("text") or ""
                start_time = word.get("start") or word.get("start_time") or 0.0
                end_time = word.get("end") or word.get("end_time") or 0.0
                
                if not word_text:
                    print(f"⚠️  Word {i} missing text field")
                    continue
                
                processed_words.append({
                    "word": word_text,
                    "start": float(start_time),
                    "end": float(end_time)
                })
            
            if not processed_words:
                raise ValueError("No valid words found after processing")
            
            print(f"✅ Parsed {len(processed_words)} words from timestamps")
            
            return processed_words
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
        except Exception as e:
            raise ValueError(f"Error parsing timestamps: {e}")
    
    def _create_segments(self, words, max_duration, max_chars, sentence_end_marks):
        """
        単語リストからセグメントを生成
        """
        if not words:
            return []
        
        segments = []
        current_segment = {
            "text": "",
            "start": None,
            "end": None,
            "words": []
        }
        
        for word in words:
            word_text = word["word"]
            word_start = float(word["start"])
            word_end = float(word["end"])
            
            # 最初の単語
            if current_segment["start"] is None:
                current_segment["start"] = word_start
            
            # 文末記号チェック
            is_sentence_end = any(mark in word_text for mark in sentence_end_marks)
            
            # 現在のセグメントに追加した場合の長さをチェック
            new_text = current_segment["text"] + word_text
            new_duration = word_end - current_segment["start"]
            
            # セグメント区切り判定
            should_break = False
            
            # 1. 文末記号で区切り（優先度高）
            if is_sentence_end:
                current_segment["text"] += word_text
                current_segment["end"] = word_end
                current_segment["words"].append(word)
                should_break = True
            
            # 2. 時間制限超過
            elif new_duration > max_duration:
                # 現在のセグメントを確定（最後の単語を含まない）
                if current_segment["text"]:
                    segments.append(current_segment.copy())
                
                # 新しいセグメント開始
                current_segment = {
                    "text": word_text,
                    "start": word_start,
                    "end": word_end,
                    "words": [word]
                }
                should_break = False
            
            # 3. 文字数制限超過
            elif len(new_text) > max_chars:
                # 現在のセグメントを確定
                if current_segment["text"]:
                    segments.append(current_segment.copy())
                
                # 新しいセグメント開始
                current_segment = {
                    "text": word_text,
                    "start": word_start,
                    "end": word_end,
                    "words": [word]
                }
                should_break = False
            
            # 4. 通常の単語追加
            else:
                current_segment["text"] += word_text
                current_segment["end"] = word_end
                current_segment["words"].append(word)
            
            # 文末で区切った場合、次のセグメント開始
            if should_break:
                segments.append(current_segment.copy())
                current_segment = {
                    "text": "",
                    "start": None,
                    "end": None,
                    "words": []
                }
        
        # 最後のセグメント追加
        if current_segment["text"]:
            segments.append(current_segment)
        
        return segments
    
    def _format_timestamp_srt(self, seconds):
        """
        秒数をSRT形式のタイムスタンプに変換
        
        例: 65.5 → "00:01:05,500"
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def _generate_srt(self, segments):
        """
        セグメントからSRT字幕を生成
        """
        srt_lines = []
        
        for i, segment in enumerate(segments, 1):
            # セグメント番号
            srt_lines.append(str(i))
            
            # タイムスタンプ
            start_time = self._format_timestamp_srt(segment["start"])
            end_time = self._format_timestamp_srt(segment["end"])
            srt_lines.append(f"{start_time} --> {end_time}")
            
            # テキスト
            srt_lines.append(segment["text"])
            
            # 空行
            srt_lines.append("")
        
        return "\n".join(srt_lines)
    
    def generate_segments(self, words_timestamps_json, mode="youtube",
                         max_duration=7.0, max_chars=80, sentence_end_marks="。?!？！…"):
        """
        単語タイムスタンプから文節セグメントを生成
        """
        print("\n" + "="*80)
        print("📝 RogoAI Words To Segments")
        print("="*80)
        
        # モード別のデフォルト設定
        if mode == "youtube":
            max_duration = 7.0
            max_chars = 80
            print("📺 Mode: YouTube (3〜7秒最適化)")
        elif mode == "subtitle":
            max_duration = 10.0
            max_chars = 100
            print("💬 Mode: Subtitle (標準字幕)")
        elif mode == "precise":
            max_duration = 30.0
            max_chars = 200
            print("🎯 Mode: Precise (精密区切り)")
        
        # タイムスタンプJSONをパース
        try:
            words = self._parse_words_timestamps(words_timestamps_json)
            print(f"✅ Parsed {len(words)} words")
        except ValueError as e:
            print(f"❌ Error parsing timestamps: {e}")
            return ("", "[]", "", 0)
        
        # セグメント生成
        segments = self._create_segments(words, max_duration, max_chars, sentence_end_marks)
        
        print(f"\n📊 Segment Statistics:")
        print(f"   Total segments: {len(segments)}")
        
        if segments:
            durations = [seg["end"] - seg["start"] for seg in segments]
            char_counts = [len(seg["text"]) for seg in segments]
            
            print(f"   Average duration: {sum(durations)/len(durations):.1f}s")
            print(f"   Average chars: {sum(char_counts)/len(char_counts):.0f}")
            print(f"   Duration range: {min(durations):.1f}s 〜 {max(durations):.1f}s")
            print(f"   Char range: {min(char_counts)} 〜 {max(char_counts)}")
        
        # 出力フォーマット生成
        
        # 1. 読みやすいテキスト
        segments_text = "\n".join([
            f"[{seg['start']:.1f}s - {seg['end']:.1f}s] {seg['text']}"
            for seg in segments
        ])
        
        # 2. JSON形式
        segments_for_json = [
            {
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"],
                "duration": seg["end"] - seg["start"],
                "char_count": len(seg["text"])
            }
            for seg in segments
        ]
        segments_json = json.dumps(segments_for_json, ensure_ascii=False, indent=2)
        
        # 3. SRT形式
        srt_content = self._generate_srt(segments)
        
        print(f"\n✅ Generation completed")
        print(f"   Total duration: {segments[-1]['end']:.1f}s" if segments else "   No segments")
        print("="*80 + "\n")
        
        return (segments_text, segments_json, srt_content, len(segments))


# ノード登録
NODE_CLASS_MAPPINGS = {
    "RogoAI_WordsToSegments": RogoAI_WordsToSegments,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RogoAI_WordsToSegments": "RogoAI Words To Segments 📝",
}
