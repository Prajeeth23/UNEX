import time
import numpy as np
import sys
import os

# Add project root to sys path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.voice.wake_word import WakeWordDetector
from src.voice.speech_to_text import SpeechToText

def generate_dummy_audio(seconds: float, sample_rate: int = 16000) -> np.ndarray:
    """Generates random noise audio."""
    num_samples = int(seconds * sample_rate)
    return np.random.uniform(-0.5, 0.5, num_samples).astype(np.float32)

def generate_silence(seconds: float, sample_rate: int = 16000) -> np.ndarray:
    num_samples = int(seconds * sample_rate)
    return np.zeros(num_samples, dtype=np.float32)

def run_benchmark():
    print("Initializing Voice Models for Benchmark...")
    
    # 1. Wake Word Benchmarking
    start_init = time.time()
    wake_word = WakeWordDetector()
    print(f"Wake Word init time: {time.time() - start_init:.2f}s")
    
    # Process 1 second of audio in small chunks
    audio_1s = generate_dummy_audio(1.0)
    chunk_size = 512
    
    start_ww = time.time()
    for i in range(0, len(audio_1s), chunk_size):
        chunk = audio_1s[i:i+chunk_size]
        wake_word.process_chunk(chunk)
    end_ww = time.time()
    print(f"Wake Word Latency (Processing 1s of audio): {(end_ww - start_ww) * 1000:.2f} ms")
    
    # 2. STT Benchmarking
    start_init = time.time()
    stt = SpeechToText(model_size="tiny.en", compute_type="int8") # Use tiny for fast bench
    print(f"\nSTT init time: {time.time() - start_init:.2f}s")
    
    audio_3s = generate_dummy_audio(3.0)
    start_stt = time.time()
    text = stt.add_audio(audio_3s)
    
    # Force silence to trigger transcription
    silence = generate_silence(2.0)
    text = stt.add_audio(silence)
    end_stt = time.time()
    print(f"STT Latency (Transcribing 3s of audio): {(end_stt - start_stt) * 1000:.2f} ms")
    print(f"STT Output (Expected random/empty due to noise): '{text}'")

if __name__ == "__main__":
    run_benchmark()
