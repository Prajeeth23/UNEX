import pytest
import asyncio
import base64
import io
import numpy as np
from PIL import Image, ImageDraw

from src.llm.ollama_client import OllamaProvider
from src.rag.document_indexer import DocumentIndexer
from src.vision.vision_models import VisionModelProvider
from src.vision.ocr_engine import OCREngine
from src.voice.speech_to_text import SpeechToText
from src.voice.text_to_speech import TextToSpeech
from src.voice.audio_manager import AudioManager
from src.agent.agent_manager import UNEXAgent

@pytest.mark.asyncio
async def test_live_ollama_llm():
    """Verify live Qwen2.5:3b text generation on local Ollama server."""
    provider = OllamaProvider(default_model="qwen2.5:3b")
    response = await provider.agenerate("Respond with the exact word 'PONG' and nothing else.")
    assert len(response.strip()) > 0
    assert "PONG" in response.upper()

@pytest.mark.asyncio
async def test_live_nomic_embeddings():
    """Verify live nomic-embed-text 768-dim embeddings via Ollama."""
    provider = OllamaProvider()
    indexer = DocumentIndexer(provider)
    embedding = await indexer._get_embedding("UNEX Phase 2 Vector Embedding Test")
    assert isinstance(embedding, list)
    assert len(embedding) == 768

@pytest.mark.asyncio
async def test_live_moondream_vision():
    """Verify live Moondream multimodal vision analysis."""
    img = Image.new('RGB', (120, 120), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.rectangle((20, 20, 100, 100), fill=(0, 128, 255))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    vp = VisionModelProvider()
    vp.model = "moondream"
    analysis = await vp.analyze_image(b64, "Describe the primary object in this image.")
    assert len(analysis.strip()) > 0

def test_live_ocr_engine():
    """Verify live OCR text extraction."""
    img = Image.new('RGB', (300, 80), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((20, 25), "UNEX VERIFIED 2026", fill=(0, 0, 0))
    
    ocr = OCREngine()
    extracted = ocr.extract_text(img)
    assert len(extracted.strip()) > 0
    assert "UNEX" in extracted

def test_live_whisper_stt():
    """Verify live Whisper model loading and audio buffer handling."""
    stt = SpeechToText(model_size="base.en", device="cpu")
    assert stt.model is not None
    dummy = np.zeros(16000, dtype=np.float32)
    result = stt.add_audio(dummy)
    assert isinstance(result, str)

def test_live_kokoro_tts():
    """Verify Kokoro Neural TTS pipeline initialization and audio generation."""
    audio_mgr = AudioManager()
    tts = TextToSpeech(audio_mgr, voice="af_heart")
    assert tts._kokoro_pipeline is not None
    generator = tts._kokoro_pipeline("Hello UNEX", voice="af_heart")
    chunks = list(generator)
    assert len(chunks) > 0
    gs, ps, audio = chunks[0]
    assert audio is not None

@pytest.mark.asyncio
async def test_live_agent_chat_e2e():
    """Verify full end-to-end UNEXAgent loop with live LLM and memory context."""
    agent = UNEXAgent()
    reply = await agent.chat("Introduce yourself in one concise sentence.")
    assert len(reply.strip()) > 0
