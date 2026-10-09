import threading
import time
import asyncio
from src.voice.audio_manager import AudioManager
from src.voice.wake_word import WakeWordDetector
from src.voice.speech_to_text import SpeechToText
from src.voice.text_to_speech import TextToSpeech
from src.voice.voice_session import VoiceSession, VoiceState
from src.agent.agent_manager import UNEXAgent
from src.security.action_validator import validator

class VoiceController:
    def __init__(self, agent: UNEXAgent):
        self.agent = agent
        self.audio_manager = None
        self.wake_word = None
        self.stt = None
        self.tts = None
        self.session = VoiceSession()
        
        self._running = False
        self._thread = None
        self._loop = asyncio.new_event_loop()
        self._next_state_after_speaking = None
        self._barge_in_consecutive_loud_frames = 0
        self._listening_started_at = 0.0
        self.barge_in_rms_threshold = 0.05
        
    def _init_audio(self):
        if self.audio_manager is None:
            self.audio_manager = AudioManager()
        if self.wake_word is None:
            self.wake_word = WakeWordDetector()
        if self.stt is None:
            self.stt = SpeechToText()
        if self.tts is None:
            self.tts = TextToSpeech(self.audio_manager)

    def start(self):
        if self._running:
            return
        self._init_audio()
        self._running = True
        self.audio_manager.start_recording()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        print("[VoiceController] Voice system started.")
        
    def stop(self):
        self._running = False
        if self.audio_manager:
            self.audio_manager.stop_recording()
        if self.tts:
            self.tts.stop()
        if self.stt:
            self.stt.clear_buffer()
        if self.wake_word:
            self.wake_word.cleanup()
        if self._thread:
            self._thread.join(timeout=2.0)
            
    def get_diagnostics(self) -> dict:
        return {
            "current_state": self.session.current_state.value,
            "is_muted": self.session.is_muted,
            "is_sleeping": self.session.is_sleeping,
            "stt_active": self.session.current_state == VoiceState.LISTENING,
            "tts_active": self.session.current_state == VoiceState.SPEAKING
        }
            
    def _run_loop(self):
        asyncio.set_event_loop(self._loop)
        while self._running:
            chunk = self.audio_manager.get_audio_chunk(block=True, timeout=0.1)
            if chunk is None:
                # If idle or speaking, perform idle cleanup checks
                self._check_state_transitions()
                continue
                
            self.process_audio_chunk(chunk)

    def process_audio_chunk(self, chunk):
        """Processes a single audio chunk through the voice state machine."""
        import numpy as np
        state = self.session.current_state
        rms = float(np.sqrt(np.mean(chunk**2))) if len(chunk) > 0 else 0.0
        
        # --- 1. IDLE STATE ---
        if state == VoiceState.IDLE:
            if not self.session.is_sleeping and self.wake_word.process_chunk(chunk):
                print("\n[VoiceController] Wake word detected!")
                self.session.transition_to(VoiceState.SPEAKING)
                self._next_state_after_speaking = VoiceState.LISTENING
                self._listening_started_at = time.time()
                if not self.session.is_muted:
                    self.tts.speak("Hello Prajeeth, I'm listening.")
                else:
                    self.session.transition_to(VoiceState.LISTENING)
                self.stt.clear_buffer()
                self.wake_word.clear_buffer()
                return
                
        # --- 2. LISTENING STATE ---
        elif state == VoiceState.LISTENING:
            # Timeout safeguard: return to IDLE if no user voice after 12 seconds
            if time.time() - self._listening_started_at > 12.0 and not self.stt.audio_buffer:
                print("[VoiceController] Listening timeout, reverting to IDLE.")
                self.session.transition_to(VoiceState.IDLE)
                return
                
            text = self.stt.add_audio(chunk, self.audio_manager.sample_rate)
            if text:
                print(f"\n[User] {text}")
                self.stt.clear_buffer()
                # Check offline built-in commands first
                if self.session.handle_builtin_command(text):
                    pass # Handled internally
                else:
                    self.session.transition_to(VoiceState.THINKING)
                    self._loop.run_until_complete(self._handle_agent_request(text))
                    
        # --- 3. SPEAKING STATE ---
        elif state == VoiceState.SPEAKING:
            # Energy-based Barge-In: if user speaks over TTS playback, stop speech immediately
            if self.tts._is_playing and rms > self.barge_in_rms_threshold:
                self._barge_in_consecutive_loud_frames += 1
            else:
                self._barge_in_consecutive_loud_frames = 0
                
            if self._barge_in_consecutive_loud_frames >= 2:
                print("\n[VoiceController] Barge-in detected! Stopping TTS playback.")
                self.tts.stop()
                self._barge_in_consecutive_loud_frames = 0
                self._next_state_after_speaking = None
                self.session.trigger_barge_in()
                self.stt.clear_buffer()
                self._listening_started_at = time.time()
                self.stt.add_audio(chunk, self.audio_manager.sample_rate)
                return

        # --- 4. AWAITING_APPROVAL STATE ---
        elif state == VoiceState.AWAITING_APPROVAL:
            text = self.stt.add_audio(chunk, self.audio_manager.sample_rate)
            if text:
                print(f"\n[User (Approval)] {text}")
                self.stt.clear_buffer()
                text_lower = text.lower()
                if any(w in text_lower for w in ["yes", "confirm", "do it", "approved", "proceed"]):
                    validator.approval_manager.provide_confirmation(True)
                elif any(w in text_lower for w in ["no", "cancel", "stop", "abort", "reject"]):
                    validator.approval_manager.provide_confirmation(False)
                    
                self.session.transition_to(VoiceState.THINKING)
                self._loop.run_until_complete(self._handle_agent_request(text))

        self._check_state_transitions()

    def _check_state_transitions(self):
        state = self.session.current_state
        if state == VoiceState.SPEAKING and not self.tts._is_playing:
            next_s = self._next_state_after_speaking
            if next_s:
                self._next_state_after_speaking = None
                self.session.transition_to(next_s)
                if next_s == VoiceState.LISTENING:
                    self._listening_started_at = time.time()
                    self.stt.clear_buffer()
                    self.wake_word.clear_buffer()
            elif validator.approval_manager.pending_action:
                self.session.transition_to(VoiceState.AWAITING_APPROVAL)
            else:
                self.session.transition_to(VoiceState.IDLE)
                
    async def _handle_agent_request(self, text: str):
        try:
            final_response = await self.agent.chat(user_input=text)
            print(f"[UNEX] {final_response}")
            self.session.transition_to(VoiceState.SPEAKING)
            self._next_state_after_speaking = None
            if not self.session.is_muted:
                self.tts.speak(final_response)
        except Exception as e:
            print(f"[VoiceController] Agent execution error: {e}")
            self.session.transition_to(VoiceState.IDLE)
