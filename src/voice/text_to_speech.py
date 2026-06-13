import numpy as np
import threading
import pyttsx3
# import kokoro # Placeholder for actual kokoro import

class TextToSpeech:
    def __init__(self, audio_manager, speed=1.0, volume=1.0):
        self.audio_manager = audio_manager
        self.speed = speed
        self.volume = volume
        self._playback_thread = None
        self._is_playing = False
        
        # Initialize fallback TTS
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', int(150 * speed))
        self.engine.setProperty('volume', volume)

    def speak(self, text: str):
        """Synthesizes text and plays it asynchronously. Interrupts current playback."""
        self.stop()
        self._is_playing = True
        self._playback_thread = threading.Thread(target=self._synthesize_and_play, args=(text,))
        self._playback_thread.start()

    def _synthesize_and_play(self, text: str):
        print(f"[TTS] Synthesizing: {text}")
        try:
            # Kokoro implementation would generate audio array here
            # audio_data, sample_rate = kokoro.generate(text, speed=self.speed)
            # if self._is_playing:
            #     self.audio_manager.play_audio(audio_data, sample_rate)
            
            # Using pyttsx3 fallback for MVP
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"[TTS] Error: {e}")
        finally:
            self._is_playing = False

    def stop(self):
        """Immediately stops playback."""
        self._is_playing = False
        self.audio_manager.stop_playback()
        # pyttsx3 engine.stop() is tricky across threads, but audio_manager.stop_playback() handles sd.stop()
        try:
            self.engine.stop()
        except:
            pass
