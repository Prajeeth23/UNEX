# UNEX OS (Universal Neural Executive)

<p align="center">
  <strong>A 100% Local, Offline-First Autonomous AI Operating System & Personal Executive</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Production%20v1.0.0-06b6d4?style=for-the-badge" alt="Status">
  <img src="https://img.shields.io/badge/Hardware-NVIDIA%20RTX%203050%20(CUDA%2013.3)-8b5cf6?style=for-the-badge" alt="Hardware">
  <img src="https://img.shields.io/badge/Tests-53%2F53%20Passing-10b981?style=for-the-badge" alt="Tests">
  <img src="https://img.shields.io/badge/License-MIT-blue?style=for-the-badge" alt="License">
</p>

---

## 🌟 Overview

**UNEX** is a privacy-first, locally-hosted personal AI operating system engineered to execute entirely on consumer hardware without sending private data to cloud servers. Built with **LangGraph**, **FastAPI**, **Ollama**, and **Win32 API**, UNEX combines real-time continuous voice interaction, multimodal desktop vision, autonomous OS automation, and semantic memory indexing into a unified Mission Control experience.

---

## ⚡ Core Capabilities

- **🎙️ Real-Time Voice Loop & Wake-Word Daemon:**
  - 100% offline wake-word detection using **OpenWakeWord ONNX** (`Hey Jarvis`, `Alexa`).
  - Real-time barge-in acoustic interruption: UNEX halts neural TTS speech immediately when user begins speaking.
  - Sub-50ms acoustic response with **Faster-Whisper** (`base.en`) and **Kokoro-82M** 24kHz neural TTS.
- **👁️ Multimodal Desktop Vision & OCR:**
  - Real-time screen perception with **Moondream** multimodal vision model (`moondream:latest`).
  - High-speed offline text extraction via **RapidOCR** (PP-OCRv4 on ONNX Runtime).
  - Active foreground window inspector tracking title, PID, process name, bounds, and screen quadrant.
- **🖱️ Autonomous OS Automation & Computer Control:**
  - Safe Windows OS input automation: keystrokes, Unicode string typing (`SendInput`), and mouse actions.
  - Safety constraints: multi-monitor coordinate clamping, click rate limits, and restricted hotkeys (`ctrl+alt+del` blocked).
  - Window state management: list open windows, focus by keyword, minimize, maximize, and restore.
  - Safe clipboard reading and writing with automatic lock retry backoff.
- **🧠 Long-Term Memory, RAG & Decay Pruning:**
  - Multi-tier memory architecture: Short-Term interaction window, Structured SQLite persistence, and 768-dim semantic search via **Nomic-Embed-Text**.
  - Automatic memory decay and pruning: preserves user preferences while expiring ephemeral low-importance notes to maintain a flat memory footprint.
- **🛡️ Security & Multi-Tier Risk Matrix:**
  - Every tool execution routes through `ActionValidator`.
  - Read-only tools (`LOW` risk) run instantly; system modifications (`MEDIUM`/`HIGH`) require explicit confirmation.
- **🖥️ Mission Control Web Dashboard:**
  - Built with **Modern Deep Glassmorphism**: translucent obsidian/indigo plates (`backdrop-filter: blur(24px)`), electric cyan and violet highlights.
  - Live hardware telemetry gauges (GPU VRAM, CPU load, RAM), central rotating neural voice orb with canvas waveform visualizer, conversation stream, live screen preview, and audit log drawer.

---

## 🤖 Local Model Inventory

All models run offline on local hardware with hardware acceleration:

| Role | Model / Engine | Footprint | Acceleration |
|---|---|---|---|
| **Primary LLM** | `qwen2.5:3b` (Ollama) | 1.9 GB | CUDA 13.3 (RTX 3050 Laptop GPU) |
| **Multimodal Vision** | `moondream:latest` (Ollama) | 1.7 GB | CUDA 13.3 |
| **Semantic Embeddings** | `nomic-embed-text:latest` (Ollama) | 274 MB | CUDA 13.3 (768-dim) |
| **Offline Screen OCR** | `rapidocr-onnxruntime` | ~15 MB | ONNX Runtime CPU/DirectML |
| **Speech-To-Text (STT)** | `faster-whisper` (`base.en`) | ~140 MB | CTranslate2 CPU INT8 |
| **Neural TTS** | `Kokoro-82M` (24kHz) | ~320 MB | PyTorch CPU with pyttsx3 fallback |
| **Wake-Word Engine** | `openwakeword` ONNX | ~10 MB | ONNX Runtime |

---

## 🚀 Quick Start

### 1. Requirements
- Windows 10/11 (64-bit)
- Python 3.12 (in a virtual environment)
- Ollama CLI installed and running
- NVIDIA GPU with 4GB+ VRAM recommended

### 2. Setup Environment
```powershell
# Clone repository
git clone https://github.com/prajeeth-07/UNEX.git
cd UNEX

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 3. Launch UNEX Mission Control
```powershell
# Interactive Launcher
python start_unex.py
```
Open your browser to:
- **Cockpit Dashboard:** [http://localhost:8000/dashboard/](http://localhost:8000/dashboard/)
- **Swagger API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Background Service / Silent Launch
```powershell
# Start daemon in background
python scripts/unex_daemon.py start

# Check daemon status
python scripts/unex_daemon.py status

# Stop daemon
python scripts/unex_daemon.py stop

# Or double-click start_unex_background.vbs for silent startup
```

---

## 🧪 Testing & Verification

Run the full test suite across all subsystems:

```powershell
.\.venv\Scripts\python -m pytest -v
```

**Results:** **53/53 tests passed** (including unit tests, live hardware inference, stability stress tests, and API endpoints).

---

## 🗺️ Completed Roadmap

- [x] **Phase 1: Environment Stabilization & Core Fixes** — Dependency resolution, clean test baseline (commit `26a5b67`).
- [x] **Phase 2: Live Local AI Engine Connection** — Live Ollama connection, CUDA acceleration, 6 verified local models.
- [x] **Phase 3: Real-Time Voice Loop & Wake-Word Daemon** — OpenWakeWord, Faster-Whisper, Kokoro TTS, acoustic barge-in.
- [x] **Phase 4: Autonomous OS Automation & Computer Control** — Win32 input injection, bounds clamping, active window inspection, RapidOCR.
- [x] **Phase 5: Futuristic Web UI Dashboard & Real-Time Cockpit** — Modern Deep Glassmorphism cockpit, live telemetry, audio visualizer.
- [x] **Phase 6: Long-Term Stress Testing, Memory Pruning & Hardening** — Scalability benchmarks, age-based memory decay, zero-leak verification, Windows daemon.

---

## 📄 License
MIT License. Created by Prajeeth.