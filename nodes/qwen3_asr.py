"""
RogoAI Qwen3-ASR Long Audio Edition
公式Qwen3-ASRノードの改良版：長尺音声対応 + プログレスバー + デバッグモード

主な改良点:
- max_new_tokens を大幅に拡張 (256 → 8192デフォルト、最大32768)
- 音声長に応じた推奨値の自動計算
- プログレスバー表示 (処理状況を可視化)
- デバッグモード (トークン消費量などの詳細情報)
- エラーハンドリング強化
"""

import os
import shutil
import torch
import numpy as np
import folder_paths
import comfy.model_management as mm
# from comfy.utils import ProgressBar  # 一時的に無効化 - ComfyUI 0.11.1バグ対策
from qwen_asr import Qwen3ASRModel


# Register Qwen3-ASR models folder with ComfyUI
QWEN3_ASR_MODELS_DIR = os.path.join(folder_paths.models_dir, "Qwen3-ASR")
os.makedirs(QWEN3_ASR_MODELS_DIR, exist_ok=True)
folder_paths.add_model_folder_path("Qwen3-ASR", QWEN3_ASR_MODELS_DIR)

# Model repo mappings
QWEN3_ASR_MODELS = {
    "Qwen/Qwen3-ASR-1.7B": "Qwen3-ASR-1.7B",
    "Qwen/Qwen3-ASR-0.6B": "Qwen3-ASR-0.6B",
}

QWEN3_FORCED_ALIGNERS = {
    "None": None,
    "Qwen/Qwen3-ForcedAligner-0.6B": "Qwen3-ForcedAligner-0.6B",
}

# Supported languages
SUPPORTED_LANGUAGES = [
    "auto",
    "Chinese", "English", "Cantonese", "Arabic", "German", "French", "Spanish",
    "Portuguese", "Indonesian", "Italian", "Korean", "Russian", "Thai",
    "Vietnamese", "Japanese", "Turkish", "Hindi", "Malay", "Dutch", "Swedish",
    "Danish", "Finnish", "Polish", "Czech", "Filipino", "Persian", "Greek",
    "Hungarian", "Macedonian", "Romanian"
]


def get_local_model_path(repo_id: str) -> str:
    folder_name = QWEN3_ASR_MODELS.get(repo_id) or QWEN3_FORCED_ALIGNERS.get(repo_id) or repo_id.replace("/", "_")
    return os.path.join(QWEN3_ASR_MODELS_DIR, folder_name)


def migrate_cached_model(repo_id: str, target_path: str) -> bool:
    if os.path.exists(target_path) and os.listdir(target_path):
        return True
    
    hf_cache = os.path.join(os.path.expanduser("~"), ".cache", "huggingface", "hub")
    hf_model_dir = os.path.join(hf_cache, f"models--{repo_id.replace('/', '--')}")
    if os.path.exists(hf_model_dir):
        snapshots_dir = os.path.join(hf_model_dir, "snapshots")
        if os.path.exists(snapshots_dir):
            snapshots = os.listdir(snapshots_dir)
            if snapshots:
                source = os.path.join(snapshots_dir, snapshots[0])
                print(f"Migrating model from HuggingFace cache: {source} -> {target_path}")
                shutil.copytree(source, target_path, dirs_exist_ok=True)
                return True
    
    ms_cache = os.path.join(os.path.expanduser("~"), ".cache", "modelscope", "hub")
    ms_model_dir = os.path.join(ms_cache, repo_id.replace("/", os.sep))
    if os.path.exists(ms_model_dir):
        print(f"Migrating model from ModelScope cache: {ms_model_dir} -> {target_path}")
        shutil.copytree(ms_model_dir, target_path, dirs_exist_ok=True)
        return True
    
    return False


def download_model_to_comfyui(repo_id: str, source: str) -> str:
    target_path = get_local_model_path(repo_id)
    
    if migrate_cached_model(repo_id, target_path):
        print(f"Model available at: {target_path}")
        return target_path
    
    os.makedirs(target_path, exist_ok=True)
    
    if source == "ModelScope":
        from modelscope import snapshot_download
        print(f"Downloading {repo_id} from ModelScope to {target_path}...")
        snapshot_download(repo_id, local_dir=target_path)
    else:
        from huggingface_hub import snapshot_download
        print(f"Downloading {repo_id} from HuggingFace to {target_path}...")
        snapshot_download(repo_id, local_dir=target_path)
    
    return target_path


def load_audio_input(audio_input):
    if audio_input is None:
        return None
        
    waveform = audio_input["waveform"]
    sr = audio_input["sample_rate"]
    
    wav = waveform[0]
    
    if wav.shape[0] > 1:
        wav = torch.mean(wav, dim=0)
    else:
        wav = wav.squeeze(0)
        
    return (wav.numpy().astype(np.float32), sr)


def calculate_recommended_tokens(audio_duration_seconds: float, language: str = "Japanese") -> int:
    """
    音声長と言語に基づいて推奨max_new_tokensを計算
    
    経験則:
    - 日本語: 1秒あたり約7文字 → 約5トークン
    - 英語: 1秒あたり約3単語 → 約4トークン
    - 中国語: 1秒あたり約5文字 → 約5トークン
    
    安全マージン: 1.5倍
    """
    tokens_per_second_map = {
        "Japanese": 5,
        "Chinese": 5,
        "English": 4,
        "Cantonese": 5,
        "Korean": 5,
    }
    
    tokens_per_second = tokens_per_second_map.get(language, 4.5)
    
    # 基本計算 + 1.5倍の安全マージン
    recommended = int(audio_duration_seconds * tokens_per_second * 1.5)
    
    # 最小値256、256の倍数に丸める
    recommended = max(256, (recommended + 255) // 256 * 256)
    
    return recommended


class RogoAI_Qwen3ASRLoader:
    """
    RogoAI Qwen3-ASR Model Loader (Long Audio Edition)
    
    改良点:
    - max_new_tokens を 256〜32768 まで調整可能
    - デフォルト 8192 (公式の32倍)
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "repo_id": (list(QWEN3_ASR_MODELS.keys()), {"default": "Qwen/Qwen3-ASR-1.7B"}),
                "source": (["HuggingFace", "ModelScope"], {"default": "HuggingFace"}),
                "precision": (["fp16", "bf16", "fp32"], {"default": "fp16"}),
                "attention": (["auto", "flash_attention_2", "sdpa", "eager"], {"default": "auto"}),
                "max_new_tokens": ("INT", {
                    "default": 8192,
                    "min": 256,
                    "max": 32768,
                    "step": 256,
                    "display": "number",
                    "tooltip": "生成する最大トークン数。長尺音声は大きい値が必要。\n目安: 1分=300, 5分=1500, 10分=3000, 20分=6000"
                }),
            },
            "optional": {
                "forced_aligner": (list(QWEN3_FORCED_ALIGNERS.keys()), {"default": "None"}),
                "local_model_path": ("STRING", {"default": "", "multiline": False}),
            }
        }

    RETURN_TYPES = ("QWEN3_ASR_MODEL",)
    RETURN_NAMES = ("model",)
    FUNCTION = "load_model"
    CATEGORY = "RogoAI/ASR"

    def load_model(self, repo_id, source, precision, attention, max_new_tokens=8192, 
                   forced_aligner="None", local_model_path=""):
        device = mm.get_torch_device()
        
        dtype = torch.float32
        if precision == "bf16":
            if device.type == "mps":
                dtype = torch.float16
                print("[RogoAI Qwen3-ASR] Note: Using fp16 on MPS (bf16 has limited support)")
            else:
                dtype = torch.bfloat16
        elif precision == "fp16":
            dtype = torch.float16
            
        if local_model_path and local_model_path.strip() != "":
            model_path = local_model_path.strip()
            print(f"[RogoAI Qwen3-ASR] Loading from local path: {model_path}")
        else:
            local_path = get_local_model_path(repo_id)
            if os.path.exists(local_path) and os.listdir(local_path):
                model_path = local_path
                print(f"[RogoAI Qwen3-ASR] Loading from ComfyUI models folder: {model_path}")
            else:
                model_path = download_model_to_comfyui(repo_id, source)
        
        # RogoAI改良: max_new_tokens を大幅に拡張
        model_kwargs = dict(
            dtype=dtype,
            device_map=str(device),
            max_inference_batch_size=32,
            max_new_tokens=max_new_tokens,  # 256 → ユーザー指定値 (デフォルト8192)
        )
        
        print(f"[RogoAI Qwen3-ASR] max_new_tokens: {max_new_tokens} (公式の{max_new_tokens//256}倍)")
        
        if attention != "auto":
            model_kwargs["attn_implementation"] = attention
            
        if forced_aligner and forced_aligner != "None":
            aligner_local = get_local_model_path(forced_aligner)
            if not (os.path.exists(aligner_local) and os.listdir(aligner_local)):
                aligner_local = download_model_to_comfyui(forced_aligner, source)
            model_kwargs["forced_aligner"] = aligner_local
            model_kwargs["forced_aligner_kwargs"] = dict(
                dtype=dtype,
                device_map=str(device),
            )
            if attention != "auto":
                model_kwargs["forced_aligner_kwargs"]["attn_implementation"] = attention
        
        print(f"[RogoAI Qwen3-ASR] Loading model from {model_path}...")
        model = Qwen3ASRModel.from_pretrained(model_path, **model_kwargs)
        
        return (model,)


class RogoAI_Qwen3ASRTranscribe:
    """
    RogoAI Qwen3-ASR Transcribe (Long Audio Edition)
    
    改良点:
    - プログレスバー表示
    - デバッグモード (詳細情報出力)
    - 推奨トークン数の自動計算
    - エラーハンドリング強化
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("QWEN3_ASR_MODEL",),
                "audio": ("AUDIO",),
            },
            "optional": {
                "language": (SUPPORTED_LANGUAGES, {"default": "auto"}),
                "context": ("STRING", {
                    "default": "", 
                    "multiline": True,
                    "tooltip": "文字起こしのヒントやコンテキスト（専門用語など）"
                }),
                "return_timestamps": ("BOOLEAN", {"default": False}),
                "debug_mode": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "デバッグ情報を表示（トークン消費量、処理時間など）"
                }),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("text", "language", "timestamps")
    FUNCTION = "transcribe"
    CATEGORY = "RogoAI/ASR"

    def transcribe(self, model, audio, language="auto", context="", 
                   return_timestamps=False, debug_mode=False):
        import time
        start_time = time.time()
        
        # 音声データ読み込み
        audio_data = load_audio_input(audio)
        if audio_data is None:
            return ("", "", "")
        
        wav_array, sr = audio_data
        audio_duration = len(wav_array) / sr
        
        # 言語設定
        lang = None if language == "auto" else language
        ctx = context if context.strip() else ""
        
        # 推奨トークン数を計算
        recommended_tokens = calculate_recommended_tokens(audio_duration, language)
        
        print("=" * 80)
        print("🎤 RogoAI Qwen3-ASR Long Audio Edition")
        print("=" * 80)
        print(f"📊 音声情報:")
        print(f"   - 長さ: {audio_duration:.1f}秒 ({audio_duration/60:.1f}分)")
        print(f"   - サンプルレート: {sr} Hz")
        print(f"   - サンプル数: {len(wav_array):,}")
        print(f"   - 言語: {language}")
        print(f"💡 推奨 max_new_tokens: {recommended_tokens:,}")
        
        # モデルの設定を取得
        try:
            model_max_tokens = model.model.generation_config.max_new_tokens
            print(f"⚙️  現在の max_new_tokens: {model_max_tokens:,}")
            
            if model_max_tokens < recommended_tokens:
                print(f"⚠️  警告: max_new_tokens が推奨値より小さいです")
                print(f"   現在: {model_max_tokens:,} / 推奨: {recommended_tokens:,}")
                print(f"   Loaderノードで max_new_tokens を {recommended_tokens} 以上に設定してください")
        except:
            pass
        
        print("=" * 80)
        
        # プログレスバー初期化（一時的に無効化 - ComfyUI 0.11.1のバグ対策）
        # pbar = ProgressBar(1)
        # pbar.update_absolute(0, 1, ("文字起こし中...", f"{audio_duration:.1f}秒の音声を処理"))
        
        print("⏳ 文字起こし処理中... (プログレスバーは一時的に無効化)")
        
        # 文字起こし実行
        try:
            results = model.transcribe(
                audio=audio_data,
                language=lang,
                context=ctx if ctx else None,
                return_time_stamps=return_timestamps,
            )
        except Exception as e:
            print(f"❌ エラー: {str(e)}")
            raise
        
        # 処理完了
        # pbar.update_absolute(1, 1, ("完了", f"{audio_duration:.1f}秒処理完了"))
        print("✅ 文字起こし処理完了")
        
        # デバッグモード
        if debug_mode:
            print("=" * 80)
            print("🔍 RogoAI デバッグ情報")
            print("=" * 80)
            print(f"📊 Results:")
            print(f"   - type: {type(results)}")
            print(f"   - 件数: {len(results)}")
            
            for i, result in enumerate(results):
                print(f"\n🔍 Result [{i}]:")
                if hasattr(result, 'text'):
                    text_len = len(result.text)
                    # トークン数の推定（日本語: 1トークン ≈ 1.5文字）
                    estimated_tokens = int(text_len / 1.5)
                    print(f"   - 文字数: {text_len:,} chars")
                    print(f"   - 推定トークン数: {estimated_tokens:,}")
                    print(f"   - プレビュー: '{result.text[:100]}...'")
                    if text_len > 100:
                        print(f"   - 末尾: '...{result.text[-100:]}'")
                
                if hasattr(result, 'language'):
                    print(f"   - 検出言語: {result.language}")
                
                if hasattr(result, 'time_stamps') and result.time_stamps:
                    print(f"   - タイムスタンプ: {len(result.time_stamps)} セグメント")
                    if len(result.time_stamps) > 0:
                        first_ts = result.time_stamps[0]
                        last_ts = result.time_stamps[-1]
                        print(f"   - 開始: {first_ts.start_time:.2f}秒")
                        print(f"   - 終了: {last_ts.end_time:.2f}秒")
            
            print("=" * 80)
        
        # 結果取得
        result = results[0]
        text = result.text
        detected_lang = result.language or ""
        
        timestamps_str = ""
        if return_timestamps and result.time_stamps:
            ts_lines = []
            for ts in result.time_stamps:
                ts_lines.append(f"{ts.start_time:.2f}-{ts.end_time:.2f}: {ts.text}")
            timestamps_str = "\n".join(ts_lines)
        
        # 処理時間
        elapsed_time = time.time() - start_time
        
        # 結果サマリー
        print("=" * 80)
        print("✅ RogoAI Qwen3-ASR 処理完了")
        print("=" * 80)
        print(f"📊 結果:")
        print(f"   - 音声長: {audio_duration:.1f}秒 ({audio_duration/60:.1f}分)")
        print(f"   - 文字数: {len(text):,} chars")
        print(f"   - 検出言語: {detected_lang}")
        print(f"   - 処理時間: {elapsed_time:.1f}秒")
        print(f"   - 処理速度: {audio_duration/elapsed_time:.1f}x リアルタイム")
        
        if return_timestamps:
            print(f"   - タイムスタンプ: {len(result.time_stamps) if result.time_stamps else 0} セグメント")
        
        print("=" * 80)
        
        return (text, detected_lang, timestamps_str)


# ノード登録
NODE_CLASS_MAPPINGS = {
    "RogoAI_Qwen3ASRLoader": RogoAI_Qwen3ASRLoader,
    "RogoAI_Qwen3ASRTranscribe": RogoAI_Qwen3ASRTranscribe,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RogoAI_Qwen3ASRLoader": "RogoAI Qwen3-ASR Loader (Long Audio)",
    "RogoAI_Qwen3ASRTranscribe": "RogoAI Qwen3-ASR Transcribe (Long Audio)",
}