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
        self.audio_manager = AudioManager()
        self.wake_word = WakeWordDetector()
        self.stt = SpeechToText()
        self.tts = TextToSpeech(self.audio_manager)
        self.session = VoiceSession()
        
        self._running = False
        self._thread = None
        self._loop = asyncio.new_event_loop()
        
    def start(self):
        if self._running:
            return
        self._running = True
        self.audio_manager.start_recording()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        print("[VoiceController] Voice system started.")
        
    def stop(self):
        self._running = False
        self.audio_manager.stop_recording()
        self.tts.stop()
        self.stt.clear_buffer()
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
                continue
                
            state = self.session.current_state
            
            # --- IDLE STATE ---
            if state == VoiceState.IDLE:
                if self.wake_word.process_chunk(chunk):
                    print("\n[VoiceController] Wake word detected!")
                    self.session.transition_to(VoiceState.LISTENING)
                    self.tts.speak("Hello Prajeeth, I'm listening.")
                    self.stt.clear_buffer()
                    
            # --- LISTENING STATE ---
            elif state == VoiceState.LISTENING:
                # Barge-in check: if we are speaking, and STT detects loud energy, we might want to stop TTS.
                # Currently, Barge-in is requested as: User speaks during TTS -> stop TTS -> listening mode.
                # However, if we are in LISTENING mode, we are just accumulating audio.
                text = self.stt.add_audio(chunk, self.audio_manager.sample_rate)
                if text:
                    print(f"\n[User] {text}")
                    # Check offline built-in commands first
                    if self.session.handle_builtin_command(text):
                        pass # Handled internally
                    else:
                        self.session.transition_to(VoiceState.THINKING)
                        # Dispatch to agent
                        self._loop.run_until_complete(self._handle_agent_request(text))
                        
            # --- SPEAKING STATE ---
            elif state == VoiceState.SPEAKING:
                # Barge-in logic: Check if user is speaking loudly to interrupt
                # rms = np.sqrt(np.mean(chunk**2))
                # if rms > some_threshold:
                #    self.tts.stop()
                #    self.session.transition_to(VoiceState.LISTENING)
                #    self.stt.clear_buffer()
                # Simplified for MVP: rely on 'Stop' command handled below
                
                # We can also run STT continuously to catch the "Stop" command during speaking
                text = self.stt.add_audio(chunk, self.audio_manager.sample_rate)
                if text:
                    print(f"\n[User Interruption] {text}")
                    self.tts.stop()
                    if self.session.handle_builtin_command(text):
                        pass
                    else:
                        self.session.transition_to(VoiceState.THINKING)
                        self._loop.run_until_complete(self._handle_agent_request(text))

            # --- AWAITING_APPROVAL STATE ---
            elif state == VoiceState.AWAITING_APPROVAL:
                text = self.stt.add_audio(chunk, self.audio_manager.sample_rate)
                if text:
                    print(f"\n[User (Approval)] {text}")
                    text_lower = text.lower()
                    if "yes" in text_lower or "confirm" in text_lower or "do it" in text_lower:
                        validator.approval_manager.provide_confirmation(True)
                    elif "no" in text_lower or "cancel" in text_lower or "stop" in text_lower:
                        validator.approval_manager.provide_confirmation(False)
                        
                    self.session.transition_to(VoiceState.THINKING)
                    self._loop.run_until_complete(self._handle_agent_request(text))

            # Auto-revert from Speaking back to IDLE or AWAITING_APPROVAL
            if state == VoiceState.SPEAKING and not self.tts._is_playing:
                if validator.approval_manager.pending_action:
                    self.session.transition_to(VoiceState.AWAITING_APPROVAL)
                else:
                    self.session.transition_to(VoiceState.IDLE)
                
    async def _handle_agent_request(self, text: str):
        # We need a new state object for LangGraph to maintain conversation history.
        # For this MVP, we create a basic state.
        state = {"messages": [{"role": "user", "content": text}]}
        
        try:
            # We don't want to call _call_agent directly as it is an internal method,
            # but LangGraph exposes ainvokve/invoke.
            result = await self.agent.graph.ainvoke(state)
            messages = result["messages"]
            final_response = messages[-1]["content"]
            
            print(f"[UNEX] {final_response}")
            self.session.transition_to(VoiceState.SPEAKING)
            self.tts.speak(final_response)
        except Exception as e:
            print(f"[VoiceController] Agent execution error: {e}")
            self.session.transition_to(VoiceState.IDLE)
