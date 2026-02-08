"""
ComfyUI-RogoAI-ASR
RogoAI Audio処理ノード集

含まれるノード:
1. RogoAI Extract Audio from Video - 動画から音声抽出
2. RogoAI Extract Audio v2 📁 - 動画から音声抽出（保存先選択可能）
3. RogoAI Qwen3-ASR Loader (Long Audio) - 長尺音声対応ASRモデルローダー
4. RogoAI Qwen3-ASR Transcribe (Long Audio) - 長尺音声対応文字起こし
5. RogoAI Compare Three Texts 📊 - 3つのテキスト精度比較ツール
6. RogoAI Load Text File 📄 - 自動エンコーディング検出テキスト読み込み
7. RogoAI Words To Segments 📝 - YouTube字幕セグメント生成
"""

# Extract Audio v1（既存）
from .nodes.extract_audio import NODE_CLASS_MAPPINGS as EXTRACT_MAPPINGS
from .nodes.extract_audio import NODE_DISPLAY_NAME_MAPPINGS as EXTRACT_DISPLAY_MAPPINGS

# Extract Audio v2（保存先選択機能付き）
from .nodes.extract_audio_v2 import NODE_CLASS_MAPPINGS as EXTRACT_V2_MAPPINGS
from .nodes.extract_audio_v2 import NODE_DISPLAY_NAME_MAPPINGS as EXTRACT_V2_DISPLAY_MAPPINGS

# Qwen3-ASRノード（オプション）
try:
    from .nodes.qwen3_asr import NODE_CLASS_MAPPINGS as QWEN_MAPPINGS
    from .nodes.qwen3_asr import NODE_DISPLAY_NAME_MAPPINGS as QWEN_DISPLAY_MAPPINGS
    print("✅ [RogoAI-ASR] Qwen3-ASR Long Audio Edition loaded")
except ImportError as e:
    print(f"⚠️  [RogoAI-ASR] Qwen3-ASRノードは利用できません: {e}")
    QWEN_MAPPINGS = {}
    QWEN_DISPLAY_MAPPINGS = {}

# Compare Three Texts（精度比較ツール）
try:
    from .nodes.compare_three_texts import NODE_CLASS_MAPPINGS as COMPARE_MAPPINGS
    from .nodes.compare_three_texts import NODE_DISPLAY_NAME_MAPPINGS as COMPARE_DISPLAY_MAPPINGS
    print("✅ [RogoAI-ASR] Compare Three Texts loaded")
except ImportError as e:
    print(f"⚠️  [RogoAI-ASR] Compare Three Textsノードは利用できません: {e}")
    COMPARE_MAPPINGS = {}
    COMPARE_DISPLAY_MAPPINGS = {}

# Load Text File（自動エンコーディング検出）
try:
    from .nodes.load_text_file import NODE_CLASS_MAPPINGS as LOAD_TEXT_MAPPINGS
    from .nodes.load_text_file import NODE_DISPLAY_NAME_MAPPINGS as LOAD_TEXT_DISPLAY_MAPPINGS
    print("✅ [RogoAI-ASR] Load Text File loaded")
except ImportError as e:
    print(f"⚠️  [RogoAI-ASR] Load Text Fileノードは利用できません: {e}")
    LOAD_TEXT_MAPPINGS = {}
    LOAD_TEXT_DISPLAY_MAPPINGS = {}

# Words To Segments（YouTube字幕生成）
try:
    from .nodes.words_to_segments import NODE_CLASS_MAPPINGS as SEGMENTS_MAPPINGS
    from .nodes.words_to_segments import NODE_DISPLAY_NAME_MAPPINGS as SEGMENTS_DISPLAY_MAPPINGS
    print("✅ [RogoAI-ASR] Words To Segments loaded")
except ImportError as e:
    print(f"⚠️  [RogoAI-ASR] Words To Segmentsノードは利用できません: {e}")
    SEGMENTS_MAPPINGS = {}
    SEGMENTS_DISPLAY_MAPPINGS = {}

# ノード登録（辞書の結合）
NODE_CLASS_MAPPINGS = {
    **EXTRACT_MAPPINGS,
    **EXTRACT_V2_MAPPINGS,
    **QWEN_MAPPINGS,
    **COMPARE_MAPPINGS,
    **LOAD_TEXT_MAPPINGS,
    **SEGMENTS_MAPPINGS,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    **EXTRACT_DISPLAY_MAPPINGS,
    **EXTRACT_V2_DISPLAY_MAPPINGS,
    **QWEN_DISPLAY_MAPPINGS,
    **COMPARE_DISPLAY_MAPPINGS,
    **LOAD_TEXT_DISPLAY_MAPPINGS,
    **SEGMENTS_DISPLAY_MAPPINGS,
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
