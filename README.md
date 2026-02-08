# ComfyUI-RogoAI-ASR

**Custom ComfyUI nodes for long-duration audio transcription and Japanese segment SRT output using Qwen3-ASR**

[![YouTube](https://img.shields.io/badge/YouTube-老後AI-red?logo=youtube)](https://youtu.be/-XDKu5yBPlY)
[![GitHub](https://img.shields.io/github/stars/RogoAI-Takeji/ComfyUI-RogoAI-ASR?style=social)](https://github.com/RogoAI-Takeji/ComfyUI-RogoAI-ASR)

---

## Overview

This custom node extends **Qwen3-ASR** (released by Alibaba Cloud on Jan 29, 2026) for practical use in ComfyUI, addressing critical limitations in the official implementation.

### Problems Solved
- ❌ **Official sample**: 256 token limit → Only ~1 minute audio
- ❌ **Standard nodes**: Memory overflow with Load Video → Crashes at 5 minutes
- ❌ **SRT output**: Word-level only → Not optimized for YouTube Japanese subtitles

### RogoAI Features
- ✅ **Long-duration support**: Process 11+ minute videos
- ✅ **Auto audio extraction**: No manual ffmpeg operations required
- ✅ **Japanese segment SRT**: YouTube-optimized subtitle formatting
- ✅ **Accuracy evaluation**: Objective comparison with reference text

---

## Requirements

- **ComfyUI**: Latest version
- **Python**: 3.10+
- **VRAM**: 12GB+ recommended (8GB for Qwen3-ASR only)
- **OS**: Windows/Linux

---

## Installation

### 1. Clone Repository

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/RogoAI-Takeji/ComfyUI-RogoAI-ASR.git
cd ComfyUI-RogoAI-ASR
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Restart ComfyUI

---

## Quick Start

### Basic Workflow
1. **Load Video** → `RogoAI Extract Audio` node
2. **Extract Audio** → Auto-saved to TEMP folder
3. **Load Audio** → Set transcription time range
4. **RogoAI Qwen3 ASR Loader** → Load model
5. **RogoAI Qwen3 ASR Transcribe** → Execute transcription
6. **Words to Segments** → Generate Japanese segment SRT

### Example Workflows

Download sample workflows from the [workflows/](workflows/) folder:

- **[Original_ASR.json](workflows/Original_ASR.json)**: Standard Qwen3-ASR, Whisper, and Faster Whisper comparison workflow
- **[RogoAI_Qwen3_ASR.json](workflows/RogoAI_Qwen3_ASR.json)**: Full RogoAI nodes workflow with long-duration support and Japanese SRT output

**Note**: Update file paths in the workflows to match your local ComfyUI setup.

---

## Node List

| Node Name | Function |
|-----------|----------|
| **RogoAI Extract Audio** | Auto-extract audio from video (TEMP) |
| **RogoAI Extract Audio v2** | Audio extraction + save option |
| **RogoAI Qwen3 ASR Loader** | Load Qwen3-ASR model |
| **RogoAI Qwen3 ASR Transcribe** | Long-duration transcription |
| **RogoAI Words to Segments** | Japanese segment SRT generation |
| **RogoAI Load Text File** | Load text files |
| **RogoAI Compare Three Texts** | Accuracy evaluation (3-file comparison) |

---

## Performance Benchmark

**Test Conditions**: 11min 27sec video (3786 characters)

| Model | Processing Time | Accuracy | Character Count |
|-------|----------------|----------|-----------------|
| **Qwen3-ASR** | 2m 30s | 73.6% | High deletion rate |
| **Whisper** | 4m 52s | 80.6% | High insertion rate |
| **Faster Whisper** | 4m 56s | High | High deletion rate |

### Use Case Recommendations
- **Speed priority** → Qwen3-ASR
- **Accuracy priority** → Whisper/Faster Whisper
- **With existing transcript** → Qwen3-ASR (timestamp-only)

---

## Configuration Tips

### VRAM Management
- Simultaneous Qwen3-ASR + Whisper execution is difficult
- Use **Group Bypasser** to switch models
- Restart ComfyUI if memory overflow occurs

### Japanese Segment Tuning
- Default: Max 8 seconds, 50 characters
- Adjust to **6 seconds, 40 characters** if segments feel unnatural

### Audio Format
- Sample Rate: **16000Hz** recommended
- Format: WAV/MP3 supported

---

## Troubleshooting

### Q: Model loading is slow
**A**: Normal on first run (auto-downloads from Hugging Face)

### Q: Memory overflow error
**A**: 
1. Bypass one model using Group Bypasser
2. Restart ComfyUI
3. Check VRAM (use 0.6B model if <12GB)

### Q: SRT not generated
**A**: Set `forced_aligner` to **0.6B**

---

## About the Developer

**RogoAI (老後AI) / Take-jii**

Developed by a Japanese senior citizen (70s) exploring local AI on a pension budget. Philosophy: *"Elderly people don't have time to redo things - they need perfect results from the start."*

- YouTube: [老後AI Channel](https://youtube.com/@RogoAI) (Japanese)
- Concept: Senior-friendly AI tools with complete functionality

---

## License

MIT License

---

## Changelog

- **2026/02/08**: Initial release
  - Long-duration audio support
  - Japanese segment SRT output
  - Accuracy evaluation feature

---

**日本語ドキュメント / Japanese Documentation**: [README_ja.md](README_ja.md)
