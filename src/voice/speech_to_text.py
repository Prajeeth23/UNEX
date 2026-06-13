import numpy as np
from faster_whisper import WhisperModel
import time

class SpeechToText:
    def __init__(self, model_size="small.en", device="cpu", compute_type="int8"):
        print(f"[STT] Loading faster-whisper model '{model_size}' on {device}...")
        try:
            self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        except Exception as e:
            print(f"[STT] Failed to load on {device}, falling back: {e}")
            self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
            
        self.audio_buffer = []
        self.silence_threshold = 0.01  # Energy threshold
        self.silence_duration = 0.0
        self.max_silence = 1.5         # Seconds of silence to trigger transcription
        
    def add_audio(self, chunk_float32: np.ndarray, sample_rate: int = 16000) -> str:
        """
        Adds audio to buffer. If silence is detected, runs transcription and returns text.
        Otherwise returns empty string.
        """
        self.audio_buffer.append(chunk_float32)
        
        # Calculate energy (RMS)
        rms = np.sqrt(np.mean(chunk_float32**2))
        
        chunk_duration = len(chunk_float32) / sample_rate
        
        if rms < self.silence_threshold:
            self.silence_duration += chunk_duration
        else:
            self.silence_duration = 0.0
            
        if self.silence_duration >= self.max_silence and len(self.audio_buffer) > int(sample_rate * 0.5) / len(chunk_float32):
            # User stopped speaking, transcribe!
            return self._transcribe_buffer(sample_rate)
            
        return ""
        
    def _transcribe_buffer(self, sample_rate: int) -> str:
        if not self.audio_buffer:
            return ""
            
        audio_data = np.concatenate(self.audio_buffer)
        self.audio_buffer = [] # Reset buffer
        self.silence_duration = 0.0
        
        segments, info = self.model.transcribe(audio_data, beam_size=1, vad_filter=True)
        text = " ".join([segment.text for segment in segments]).strip()
        
        return text

    def clear_buffer(self):
        self.audio_buffer = []
        self.silence_duration = 0.0
