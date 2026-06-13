import asyncio
from enum import Enum
import time

class VoiceState(Enum):
    IDLE = "IDLE"           # Listening for wake word only
    LISTENING = "LISTENING" # Active listening for command
    THINKING = "THINKING"   # Processing via LLM
    SPEAKING = "SPEAKING"   # TTS playback
    EXECUTING = "EXECUTING" # Tool execution in progress
    AWAITING_APPROVAL = "AWAITING_APPROVAL" # Waiting for Yes/No confirmation

class VoiceSession:
    def __init__(self):
        self.current_state = VoiceState.IDLE
        self.is_muted = False
        self.is_sleeping = False
        self.last_speech = ""
        self.current_action = ""
        self.state_changed_at = time.time()
        
    def transition_to(self, new_state: VoiceState):
        if self.is_sleeping and new_state != VoiceState.IDLE:
            return # Block transitions if sleeping (unless waking up which is handled explicitly)
            
        print(f"[VoiceSession] Transition: {self.current_state.value} -> {new_state.value}")
        self.current_state = new_state
        self.state_changed_at = time.time()
        
    def handle_builtin_command(self, text: str) -> bool:
        """Returns True if the command was an offline builtin, handled instantly."""
        text_lower = text.lower().strip()
        
        # Strip punctuation for cleaner matching
        import string
        text_lower = text_lower.translate(str.maketrans('', '', string.punctuation))
        
        if text_lower in ["stop", "cancel", "shut up"]:
            self.transition_to(VoiceState.IDLE)
            return True
            
        elif text_lower == "mute":
            self.is_muted = True
            self.transition_to(VoiceState.IDLE)
            return True
            
        elif text_lower == "unmute":
            self.is_muted = False
            self.transition_to(VoiceState.IDLE)
            return True
            
        elif text_lower in ["sleep", "go to sleep"]:
            self.is_sleeping = True
            self.transition_to(VoiceState.IDLE)
            return True
            
        elif text_lower == "wake up":
            self.is_sleeping = False
            self.transition_to(VoiceState.LISTENING)
            return True
            
        elif text_lower == "repeat that":
            # Action logic should handle re-triggering TTS for self.last_speech
            return True
            
        elif text_lower == "what are you doing":
            # Action logic should handle TTS for self.current_action
            return True
            
        return False
        
    def check_barge_in(self) -> bool:
        """Determines if the user's voice should interrupt the current state."""
        return self.current_state == VoiceState.SPEAKING
