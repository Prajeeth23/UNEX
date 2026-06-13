import sounddevice as sd
import numpy as np
import queue
import threading

class AudioManager:
    """Manages raw audio input/output streams."""
    def __init__(self, sample_rate=16000, channels=1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.input_queue = queue.Queue()
        self.stream = None
        self.is_recording = False
        
    def _audio_callback(self, indata, frames, time, status):
        if status:
            print(f"[AudioManager] Error: {status}")
        if self.is_recording:
            # Flatten to 1D array of float32
            self.input_queue.put(indata.copy().flatten())
            
    def start_recording(self):
        if self.stream is not None:
            return
        self.is_recording = True
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype='float32',
            callback=self._audio_callback
        )
        self.stream.start()
        
    def stop_recording(self):
        self.is_recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
            
    def get_audio_chunk(self, block=True, timeout=None):
        try:
            return self.input_queue.get(block=block, timeout=timeout)
        except queue.Empty:
            return None
            
    def play_audio(self, audio_data: np.ndarray, samplerate: int):
        """Blocking playback. Can be interrupted by stopping the thread."""
        try:
            sd.play(audio_data, samplerate)
            sd.wait()
        except sd.PortAudioError as e:
            print(f"[AudioManager] Playback Error: {e}")
            
    def stop_playback(self):
        sd.stop()
