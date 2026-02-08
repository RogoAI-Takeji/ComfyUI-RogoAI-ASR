"""
RogoAI Extract Audio from Video - 改良版
保存先選択機能付き

デフォルト動作:
- save_location: temp (ComfyUI/temp フォルダ)
- filename_mode: auto (ランダムUUID)
- subfolder: audio

これにより、デフォルトでは:
ComfyUI/temp/audio/[uuid].wav に保存されます
"""

import os
import subprocess
import shutil
import uuid
from pathlib import Path
import folder_paths

class RogoAI_ExtractAudioFromVideo_v2:
    """
    動画から音声を抽出（改良版）
    
    【デフォルト動作】
    保存先: ComfyUI/temp/audio/
    ファイル名: ランダムUUID
    
    【カスタマイズ可能】
    ✅ 保存場所の選択
    ✅ ファイル名の指定
    ✅ サブフォルダの指定
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_path": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
                "output_format": (["wav", "mp3", "flac"], {
                    "default": "wav"
                }),
                "sample_rate": ([8000, 16000, 22050, 44100, 48000], {
                    "default": 16000
                }),
                "save_location": (["temp", "output", "custom"], {
                    "default": "temp"
                }),
                "filename_mode": (["auto", "video_name", "custom"], {
                    "default": "auto"
                }),
            },
            "optional": {
                "custom_path": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
                "custom_filename": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
                "subfolder": ("STRING", {
                    "default": "audio",
                    "multiline": False
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING")
    RETURN_NAMES = ("audio_file_path", "save_info", "filename")
    FUNCTION = "extract_audio"
    CATEGORY = "RogoAI/Audio"
    
    DESCRIPTION = """
RogoAI Extract Audio v2 - 保存先選択機能付き

【保存場所 (save_location)】
・temp (デフォルト)
  → ComfyUI/temp に保存
  → 一時ファイル（自動削除される可能性あり）
  → 例: D:/ComfyUI/temp/audio/abc123.wav

・output
  → ComfyUI/output に保存
  → 永続保存（ジャンクション対応）
  → 例: G:/for_comfy_ltx2/output/audio/video_name.wav

・custom
  → custom_path で指定したフォルダに保存
  → 任意の場所に保存可能
  → 例: D:/MyAudio/extracted/video_name.wav

【ファイル名 (filename_mode)】
・auto (デフォルト)
  → ランダムUUID
  → 例: 3f8a9b2c-4d5e-6f7g-8h9i-0j1k2l3m4n5o.wav

・video_name
  → 元動画のファイル名を使用
  → 例: my_video.mp4 → my_video.wav

・custom
  → custom_filename で指定した名前
  → 例: extracted_audio.wav

【サブフォルダ (subfolder)】
・デフォルト: "audio"
  → 保存先内にサブフォルダ作成
  → 例: temp/audio/, output/audio/

・空文字にすると直下に保存
    """
    
    def _find_ffmpeg(self):
        """
        ffmpegを検索
        """
        # システムPATHから検索
        ffmpeg = shutil.which('ffmpeg')
        if ffmpeg:
            return ffmpeg
        
        # 既知の場所を検索
        known_paths = [
            os.path.join(os.path.expanduser("~"), "AppData", "Local", "FFmpeg", "bin", "ffmpeg.exe"),
            r"C:\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
            "/usr/bin/ffmpeg",
            "/usr/local/bin/ffmpeg",
            "/opt/homebrew/bin/ffmpeg",
        ]
        
        for path in known_paths:
            if os.path.exists(path):
                return path
        
        raise FileNotFoundError(
            "❌ ffmpeg not found\n\n"
            "Please install ffmpeg:\n"
            "・Windows: https://www.gyan.dev/ffmpeg/builds/\n"
            "・Linux: sudo apt install ffmpeg\n"
            "・Mac: brew install ffmpeg"
        )
    
    def _get_save_directory(self, save_location, custom_path, subfolder):
        """
        保存先ディレクトリを決定
        """
        # ベースディレクトリ
        if save_location == "temp":
            base_dir = folder_paths.get_temp_directory()
            location_name = "temp"
            
        elif save_location == "output":
            base_dir = folder_paths.get_output_directory()
            location_name = "output"
            
        elif save_location == "custom":
            if not custom_path or not os.path.exists(custom_path):
                raise ValueError(
                    f"❌ save_location=custom requires valid custom_path\n"
                    f"Provided: {custom_path}"
                )
            base_dir = custom_path
            location_name = "custom"
        else:
            raise ValueError(f"Invalid save_location: {save_location}")
        
        # サブフォルダを追加
        if subfolder:
            save_dir = os.path.join(base_dir, subfolder)
        else:
            save_dir = base_dir
        
        # ディレクトリ作成
        os.makedirs(save_dir, exist_ok=True)
        
        return save_dir, location_name, base_dir
    
    def _get_filename(self, video_path, filename_mode, custom_filename, output_format):
        """
        ファイル名を決定
        """
        if filename_mode == "auto":
            # ランダムUUID
            filename = f"{uuid.uuid4()}.{output_format}"
            
        elif filename_mode == "video_name":
            # 元動画のファイル名を使用
            video_basename = os.path.basename(video_path)
            video_name_no_ext = os.path.splitext(video_basename)[0]
            filename = f"{video_name_no_ext}.{output_format}"
            
        elif filename_mode == "custom":
            if not custom_filename:
                raise ValueError(
                    "❌ filename_mode=custom requires custom_filename"
                )
            # 拡張子がついていたら除去
            custom_name_no_ext = os.path.splitext(custom_filename)[0]
            filename = f"{custom_name_no_ext}.{output_format}"
            
        else:
            raise ValueError(f"Invalid filename_mode: {filename_mode}")
        
        return filename
    
    def extract_audio(self, video_path, output_format, sample_rate, save_location, 
                     filename_mode, custom_path="", custom_filename="", subfolder="audio"):
        """
        動画から音声を抽出
        """
        print("\n" + "="*80)
        print("🎵 RogoAI Extract Audio v2")
        print("="*80)
        
        # 入力チェック
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"❌ Video file not found: {video_path}")
        
        print(f"📹 Input video: {video_path}")
        
        # ffmpeg検索
        ffmpeg_path = self._find_ffmpeg()
        print(f"✅ ffmpeg found: {ffmpeg_path}")
        
        # 保存先ディレクトリ決定
        save_dir, location_name, base_dir = self._get_save_directory(
            save_location, custom_path, subfolder
        )
        
        # ファイル名決定
        filename = self._get_filename(
            video_path, filename_mode, custom_filename, output_format
        )
        
        # 完全なファイルパス
        audio_file_path = os.path.join(save_dir, filename)
        
        # 既に同名ファイルが存在する場合の処理
        if os.path.exists(audio_file_path):
            print(f"⚠️  File already exists: {filename}")
            # ファイル名に連番を追加
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(audio_file_path):
                filename = f"{base}_{counter:03d}{ext}"
                audio_file_path = os.path.join(save_dir, filename)
                counter += 1
            print(f"📝 Renamed to: {filename}")
        
        # 保存情報を構築
        save_info = (
            f"📁 Location: {location_name}\n"
            f"📂 Base dir: {base_dir}\n"
        )
        if subfolder:
            save_info += f"📁 Subfolder: {subfolder}\n"
        save_info += (
            f"📄 Filename: {filename}\n"
            f"💾 Full path: {audio_file_path}\n"
            f"🎵 Format: {output_format} @ {sample_rate}Hz"
        )
        
        print("\n" + save_info)
        
        # ffmpegコマンド構築
        cmd = [
            ffmpeg_path,
            "-i", video_path,
            "-vn",  # 映像を無視
            "-acodec", "pcm_s16le" if output_format == "wav" else "libmp3lame",
            "-ar", str(sample_rate),
            "-ac", "1",  # モノラル
            "-y",  # 上書き確認なし
            audio_file_path
        ]
        
        # 実行
        print("\n🔧 Running ffmpeg...")
        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )
            
            # ファイルサイズ確認
            file_size = os.path.getsize(audio_file_path)
            file_size_mb = file_size / (1024 * 1024)
            
            print(f"✅ Extraction completed")
            print(f"📦 File size: {file_size_mb:.2f} MB")
            print("="*80 + "\n")
            
            return (audio_file_path, save_info, filename)
            
        except subprocess.CalledProcessError as e:
            error_msg = (
                f"❌ FFmpeg error:\n"
                f"Command: {' '.join(cmd)}\n"
                f"Error: {e.stderr}"
            )
            print(error_msg)
            raise RuntimeError(error_msg)


# ノード登録
NODE_CLASS_MAPPINGS = {
    "RogoAI_ExtractAudioFromVideo_v2": RogoAI_ExtractAudioFromVideo_v2,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RogoAI_ExtractAudioFromVideo_v2": "RogoAI Extract Audio v2 📁",
}
