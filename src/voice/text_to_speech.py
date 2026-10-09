import numpy as np
import threading
import pyttsx3

class TextToSpeech:
    def __init__(self, audio_manager, speed=1.0, volume=1.0, voice="af_heart"):
        self.audio_manager = audio_manager
        self.speed = speed
        self.volume = volume
        self.voice = voice
        self._playback_thread = None
        self._is_playing = False
        
        # Initialize Kokoro Neural TTS pipeline
        self._kokoro_pipeline = None
        try:
            from kokoro import KPipeline
            self._kokoro_pipeline = KPipeline(lang_code='a')
            print("[TTS] Kokoro Neural TTS pipeline loaded.")
        except Exception as e:
            print(f"[TTS] Kokoro unavailable ({e}). Using pyttsx3 fallback.")

        # Fallback TTS engine
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', int(150 * speed))
            self.engine.setProperty('volume', volume)
        except Exception as e:
            self.engine = None
            print(f"[TTS] pyttsx3 init warning: {e}")

    def speak(self, text: str):
        """Synthesizes text and plays it asynchronously. Interrupts current playback."""
        self.stop()
        self._is_playing = True
        self._playback_thread = threading.Thread(target=self._synthesize_and_play, args=(text,))
        self._playback_thread.start()

    def _synthesize_and_play(self, text: str):
        print(f"[TTS] Synthesizing: {text}")
        try:
            # 1. Try Kokoro Neural TTS
            if self._kokoro_pipeline is not None:
                audio_chunks = []
                generator = self._kokoro_pipeline(text, voice=self.voice, speed=self.speed)
                for gs, ps, audio in generator:
                    if not self._is_playing:
                        return
                    if hasattr(audio, 'detach'):
                        audio = audio.detach().cpu().numpy()
                    elif hasattr(audio, 'numpy'):
                        audio = audio.numpy()
                    audio_chunks.append(audio.astype(np.float32))
                    
                if audio_chunks and self._is_playing:
                    combined = np.concatenate(audio_chunks)
                    if self.volume != 1.0:
                        combined = combined * float(self.volume)
                    self.audio_manager.play_audio(combined, 24000)
                    return

            # 2. Fallback to pyttsx3
            if self.engine and self._is_playing:
                self.engine.say(text)
                self.engine.runAndWait()
        except Exception as e:
            print(f"[TTS] Error: {e}")
            if self.engine and self._is_playing:
                try:
                    self.engine.say(text)
                    self.engine.runAndWait()
                except Exception:
                    pass
        finally:
            self._is_playing = False

    def stop(self):
        """Immediately stops playback."""
        self._is_playing = False
        if self.audio_manager:
            self.audio_manager.stop_playback()
        if self.engine:
            try:
                self.engine.stop()
            except:
                pass
