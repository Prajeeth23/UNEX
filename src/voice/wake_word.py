import numpy as np

class WakeWordDetector:
    def __init__(self, sensitivity: float = 0.5):
        self.sensitivity = sensitivity
        self.last_detected_wakeword = None
        try:
            import openwakeword
            from openwakeword.model import Model
            print("[WakeWord] Initializing OpenWakeWord 100% offline engine...")
            openwakeword.utils.download_models()
            # Support both hey_jarvis and alexa wakewords
            self.model = Model(wakeword_models=["hey_jarvis", "alexa"], inference_framework="onnx")
            self.frame_length = 1280  # OpenWakeWord prefers chunks of 1280 for 16kHz
        except Exception as e:
            print(f"[WakeWord] Error initializing OpenWakeWord: {e}")
            self.model = None
            self.frame_length = 1280

        self.buffer = np.array([], dtype=np.int16)
        
    def process_chunk(self, audio_chunk_float32: np.ndarray) -> bool:
        """Returns True if a registered wake word is detected."""
        if not self.model:
            return False
            
        # Convert float32 [-1.0, 1.0] to int16
        audio_int16 = (audio_chunk_float32 * 32767).astype(np.int16)
        self.buffer = np.append(self.buffer, audio_int16)
        
        while len(self.buffer) >= self.frame_length:
            frame = self.buffer[:self.frame_length]
            self.buffer = self.buffer[self.frame_length:]
            
            # Predict
            predictions = self.model.predict(frame)
            
            # Check if any model score exceeds the sensitivity
            for wakeword, score in predictions.items():
                if score >= self.sensitivity:
                    self.last_detected_wakeword = wakeword
                    # Reset internal state after trigger
                    self.model.reset()
                    self.buffer = np.array([], dtype=np.int16)
                    return True
                    
        return False
        
    def clear_buffer(self):
        self.buffer = np.array([], dtype=np.int16)
        if self.model:
            self.model.reset()

    def cleanup(self):
        self.clear_buffer()

