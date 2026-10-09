import numpy as np
from faster_whisper import WhisperModel
import time

class SpeechToText:
    def __init__(self, model_size="base.en", device="cpu", compute_type="int8"):
        print(f"[STT] Loading faster-whisper model '{model_size}' on {device}...")
        try:
            self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        except Exception as e:
            print(f"[STT] Failed to load on {device}, falling back: {e}")
            self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
            
        self.audio_buffer = []
        self.silence_threshold = 0.01  # Energy threshold
        self.silence_duration = 0.0
        self.max_silence = 1.2         # Seconds of silence to trigger transcription
        self.last_rms = 0.0
        
    def add_audio(self, chunk_float32: np.ndarray, sample_rate: int = 16000) -> str:
        """
        Adds audio to buffer. If silence is detected after speech, runs transcription and returns text.
        Otherwise returns empty string.
        """
        chunk = np.asarray(chunk_float32, dtype=np.float32)
        self.audio_buffer.append(chunk)
        
        # Calculate energy (RMS)
        rms = float(np.sqrt(np.mean(chunk**2))) if len(chunk) > 0 else 0.0
        self.last_rms = rms
        chunk_duration = len(chunk) / float(sample_rate)
        
        if rms < self.silence_threshold:
            self.silence_duration += chunk_duration
        else:
            self.silence_duration = 0.0
            
        total_samples = sum(len(c) for c in self.audio_buffer)
        min_required_samples = int(sample_rate * 0.4)
        
        if self.silence_duration >= self.max_silence and total_samples >= min_required_samples:
            # User finished speaking, transcribe!
            return self._transcribe_buffer(sample_rate)
            
        return ""
        
    def _transcribe_buffer(self, sample_rate: int = 16000) -> str:
        if not self.audio_buffer:
            return ""
            
        audio_data = np.concatenate(self.audio_buffer)
        self.audio_buffer = [] # Reset buffer
        self.silence_duration = 0.0
        
        try:
            segments, info = self.model.transcribe(audio_data, beam_size=1, vad_filter=True)
            text = " ".join([segment.text for segment in segments]).strip()
            return text
        except Exception as e:
            print(f"[STT] Transcription error: {e}")
            return ""

    def force_transcribe(self, sample_rate: int = 16000) -> str:
        """Forces immediate transcription of whatever is currently accumulated in the buffer."""
        return self._transcribe_buffer(sample_rate)

    def clear_buffer(self):
        self.audio_buffer = []
        self.silence_duration = 0.0
