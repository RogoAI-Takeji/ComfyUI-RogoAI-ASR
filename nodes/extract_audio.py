"""
RogoAI Extract Audio From Video
動画ファイルから音声を抽出するノード（外部プロセスで実行）
"""

import os
import subprocess
import folder_paths
from pathlib import Path

class RogoAI_ExtractAudioFromVideo:
    """
    動画から音声を抽出（外部プロセスで実行、ComfyUIに負担をかけない）
    抽出した音声ファイルのパスを返すので、VHS_LoadAudioで読み込んでください
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video_path": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "動画ファイルのフルパスを入力"
                }),
                "output_format": (["wav", "mp3"], {
                    "default": "wav"
                }),
                "sample_rate": (["16000", "22050", "44100", "48000"], {
                    "default": "16000"
                }),
            },
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("audio_file_path",)
    FUNCTION = "extract_audio"
    CATEGORY = "RogoAI/ASR"
    OUTPUT_NODE = False
    
    def extract_audio(self, video_path, output_format="wav", sample_rate="16000"):
        """
        動画から音声を抽出
        """
        # パスの正規化
        video_path = video_path.strip().strip('"').strip("'").strip()
        video_path = video_path.replace('\\', '/')
        
        print(f"[RogoAI ExtractAudio] 入力動画: {video_path}")
        
        # ファイル存在確認
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"動画ファイルが見つかりません: {video_path}")
        
        # 出力先を決定
        temp_dir = folder_paths.get_temp_directory()
        os.makedirs(temp_dir, exist_ok=True)
        
        video_name = Path(video_path).stem
        # ファイル名にハッシュを追加して一意性を確保
        import hashlib
        path_hash = hashlib.md5(video_path.encode()).hexdigest()[:8]
        audio_filename = f"{video_name}_{path_hash}.{output_format}"
        audio_path = os.path.join(temp_dir, audio_filename)
        
        # 既存ファイルがあればスキップ
        if os.path.exists(audio_path):
            file_size = os.path.getsize(audio_path) / (1024 * 1024)
            print(f"[RogoAI ExtractAudio] 既存の音声ファイルを使用: {audio_path} ({file_size:.2f} MB)")
            return (audio_path,)
        
        # ffmpegパスを取得
        ffmpeg_cmd = self._find_ffmpeg()
        print(f"[RogoAI ExtractAudio] ffmpeg: {ffmpeg_cmd}")
        
        # コーデックパラメータ
        if output_format == "wav":
            codec_params = ['-acodec', 'pcm_s16le']
        elif output_format == "mp3":
            codec_params = ['-acodec', 'libmp3lame', '-b:a', '128k']
        else:
            codec_params = ['-acodec', 'pcm_s16le']
        
        # ffmpegコマンド構築
        cmd = [
            ffmpeg_cmd,
            '-i', video_path,
            '-vn',  # 動画ストリームを無効化
            *codec_params,
            '-ar', sample_rate,  # サンプルレート
            '-ac', '1',  # モノラル
            '-loglevel', 'error',
            '-y',  # 上書き
            audio_path
        ]
        
        print(f"[RogoAI ExtractAudio] 音声抽出中...")
        print(f"[RogoAI ExtractAudio] 出力: {audio_path}")
        
        try:
            # 外部プロセスで実行
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10分タイムアウト
            )
            
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else "不明なエラー"
                raise RuntimeError(f"ffmpegエラー:\n{error_msg}")
            
            # 出力ファイルの確認
            if not os.path.exists(audio_path):
                raise FileNotFoundError("音声ファイルが生成されませんでした")
            
            file_size = os.path.getsize(audio_path) / (1024 * 1024)
            print(f"[RogoAI ExtractAudio] 抽出完了: {file_size:.2f} MB")
            
            return (audio_path,)
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("音声抽出がタイムアウトしました（10分以上）")
        except Exception as e:
            print(f"[RogoAI ExtractAudio] エラー: {str(e)}")
            raise
    
    def _find_ffmpeg(self):
        """
        ffmpegの実行ファイルを探す
        """
        import shutil
        
        # まずシステムPATHから探す
        ffmpeg = shutil.which('ffmpeg')
        if ffmpeg:
            return ffmpeg
        
        # 既知の場所を直接チェック
        known_paths = [
            r'C:\Users\fareg\AppData\Local\FFmpeg\bin\ffmpeg.exe',
            r'C:\ffmpeg\bin\ffmpeg.exe',
            r'C:\Program Files\ffmpeg\bin\ffmpeg.exe',
            r'D:\ffmpeg\bin\ffmpeg.exe',
            '/usr/bin/ffmpeg',  # Linux
            '/usr/local/bin/ffmpeg',  # macOS
        ]
        
        for path in known_paths:
            if os.path.exists(path):
                return path
        
        raise FileNotFoundError(
            "ffmpegが見つかりません。\n\n"
            "解決方法:\n"
            "1. ffmpegをダウンロード: https://ffmpeg.org/download.html\n"
            "2. 解凍してC:\\ffmpeg\\ に配置\n"
            "3. システム環境変数PATHに C:\\ffmpeg\\bin を追加\n"
            "4. ComfyUIを再起動"
        )
    
    @classmethod
    def IS_CHANGED(cls, video_path, output_format, sample_rate):
        """
        入力変更チェック
        """
        video_path = video_path.strip().strip('"').strip("'").strip()
        
        if not video_path or not os.path.exists(video_path):
            return float("nan")
        
        # ファイルの更新日時を返す
        return f"{os.path.getmtime(video_path)}_{output_format}_{sample_rate}"


# ノード登録
NODE_CLASS_MAPPINGS = {
    "RogoAI_ExtractAudioFromVideo": RogoAI_ExtractAudioFromVideo
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RogoAI_ExtractAudioFromVideo": "RogoAI Extract Audio from Video"
}