"""
RogoAI Load Text File
自動エンコーディング検出機能付きテキストファイル読み込みノード

対応エンコーディング:
- UTF-8
- UTF-8 with BOM
- Shift-JIS (日本語Windows)
- CP932 (日本語Windows拡張)
- ISO-2022-JP
- EUC-JP
"""

import os

class RogoAI_LoadTextFile:
    """
    テキストファイルを自動エンコーディング検出で読み込む
    
    【特徴】
    ・複数のエンコーディングを自動試行
    ・日本語ファイルに完全対応
    ・WAS Node Suiteのエラーを解決
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_path": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
            },
            "optional": {
                "encoding_hint": (["auto", "utf-8", "shift-jis", "cp932", "iso-2022-jp", "euc-jp"], {
                    "default": "auto"
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING", "INT")
    RETURN_NAMES = ("text", "detected_encoding", "char_count")
    FUNCTION = "load_text"
    CATEGORY = "RogoAI/IO"
    
    DESCRIPTION = """
自動エンコーディング検出テキストファイル読み込み

【対応エンコーディング】
・UTF-8
・UTF-8 with BOM
・Shift-JIS（日本語Windows）
・CP932（日本語Windows拡張）
・ISO-2022-JP
・EUC-JP

【使用例】
Qwen3-ASR/Whisperの出力ファイル（Shift-JIS）を
自動的に正しく読み込みます
    """
    
    def _detect_encoding(self, file_path, encoding_hint="auto"):
        """
        ファイルのエンコーディングを検出
        """
        if encoding_hint != "auto":
            # ヒントが指定されている場合は優先
            encodings = [encoding_hint, 'utf-8', 'shift-jis', 'cp932']
        else:
            # 日本語環境で一般的な順序で試行
            encodings = [
                'utf-8',
                'utf-8-sig',  # UTF-8 with BOM
                'shift-jis',
                'cp932',
                'iso-2022-jp',
                'euc-jp',
            ]
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                return content, encoding
            except (UnicodeDecodeError, LookupError):
                continue
        
        # 全て失敗した場合、エラーを無視して読み込み
        print(f"⚠️  [RogoAI LoadTextFile] Could not detect encoding, using UTF-8 with error ignore")
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        return content, "utf-8 (with errors ignored)"
    
    def load_text(self, file_path, encoding_hint="auto"):
        """
        テキストファイルを読み込み
        """
        # ファイル存在確認
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # エンコーディング検出して読み込み
        text, detected_encoding = self._detect_encoding(file_path, encoding_hint)
        
        char_count = len(text)
        
        print(f"📄 [RogoAI LoadTextFile] File loaded successfully")
        print(f"   Path: {file_path}")
        print(f"   Encoding: {detected_encoding}")
        print(f"   Characters: {char_count:,}")
        
        return (text, detected_encoding, char_count)


# ノード登録
NODE_CLASS_MAPPINGS = {
    "RogoAI_LoadTextFile": RogoAI_LoadTextFile,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RogoAI_LoadTextFile": "RogoAI Load Text File 📄",
}
