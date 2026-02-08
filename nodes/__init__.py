"""
ComfyUI-RogoAI-ASR nodes module
"""

# Extract Audio v1 (既存)
from .extract_audio import RogoAI_ExtractAudioFromVideo

# Extract Audio v2 (保存先選択機能付き)
from .extract_audio_v2 import RogoAI_ExtractAudioFromVideo_v2

# Qwen3-ASR
from .qwen3_asr import (
    RogoAI_Qwen3ASRLoader,
    RogoAI_Qwen3ASRTranscribe
)

# Compare Three Texts (精度比較ツール)
from .compare_three_texts import RogoAI_CompareThreeTexts

# Load Text File (自動エンコーディング検出)
from .load_text_file import RogoAI_LoadTextFile

# Words To Segments (YouTube字幕生成)
from .words_to_segments import RogoAI_WordsToSegments

# ノードマッピング
NODE_CLASS_MAPPINGS = {
    # Extract Audio
    "RogoAI_ExtractAudioFromVideo": RogoAI_ExtractAudioFromVideo,
    "RogoAI_ExtractAudioFromVideo_v2": RogoAI_ExtractAudioFromVideo_v2,
    
    # Qwen3-ASR
    "RogoAI_Qwen3ASRLoader": RogoAI_Qwen3ASRLoader,
    "RogoAI_Qwen3ASRTranscribe": RogoAI_Qwen3ASRTranscribe,
    
    # Analysis
    "RogoAI_CompareThreeTexts": RogoAI_CompareThreeTexts,
    
    # IO
    "RogoAI_LoadTextFile": RogoAI_LoadTextFile,
    
    # Subtitle
    "RogoAI_WordsToSegments": RogoAI_WordsToSegments,
}

# 表示名マッピング
NODE_DISPLAY_NAME_MAPPINGS = {
    # Extract Audio
    "RogoAI_ExtractAudioFromVideo": "RogoAI Extract Audio from Video",
    "RogoAI_ExtractAudioFromVideo_v2": "RogoAI Extract Audio v2 📁",
    
    # Qwen3-ASR
    "RogoAI_Qwen3ASRLoader": "RogoAI Qwen3-ASR Loader (Long Audio)",
    "RogoAI_Qwen3ASRTranscribe": "RogoAI Qwen3-ASR Transcribe (Long Audio)",
    
    # Analysis
    "RogoAI_CompareThreeTexts": "RogoAI Compare Three Texts 📊",
    
    # IO
    "RogoAI_LoadTextFile": "RogoAI Load Text File 📄",
    
    # Subtitle
    "RogoAI_WordsToSegments": "RogoAI Words To Segments 📝",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
