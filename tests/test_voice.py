import pytest
import time
from src.voice.voice_session import VoiceSession, VoiceState

def test_initial_state():
    session = VoiceSession()
    assert session.current_state == VoiceState.IDLE
    assert not session.is_muted
    assert not session.is_sleeping

def test_builtin_sleep_wake():
    session = VoiceSession()
    
    # Send sleep command
    handled = session.handle_builtin_command("go to sleep")
    assert handled is True
    assert session.is_sleeping is True
    assert session.current_state == VoiceState.IDLE
    
    # Try to transition while sleeping - should be blocked
    session.transition_to(VoiceState.LISTENING)
    assert session.current_state == VoiceState.IDLE
    
    # Wake up
    handled = session.handle_builtin_command("wake up")
    assert handled is True
    assert session.is_sleeping is False
    assert session.current_state == VoiceState.LISTENING

def test_builtin_stop_barge_in():
    session = VoiceSession()
    
    session.transition_to(VoiceState.SPEAKING)
    assert session.check_barge_in() is True
    
    # User interrupts with "Stop"
    handled = session.handle_builtin_command("stop")
    assert handled is True
    assert session.current_state == VoiceState.IDLE
    
def test_mute_unmute():
    session = VoiceSession()
    
    session.handle_builtin_command("mute")
    assert session.is_muted is True
    
    session.handle_builtin_command("unmute")
    assert session.is_muted is False

def test_state_transitions():
    session = VoiceSession()
    
    # Detect wake word
    session.transition_to(VoiceState.LISTENING)
    assert session.current_state == VoiceState.LISTENING
    
    # Command received
    session.transition_to(VoiceState.THINKING)
    assert session.current_state == VoiceState.THINKING
    
    # Executing Tool
    session.transition_to(VoiceState.EXECUTING)
    assert session.current_state == VoiceState.EXECUTING
    
    # Agent responding
    session.transition_to(VoiceState.SPEAKING)
    assert session.current_state == VoiceState.SPEAKING
    
    # Finished speaking
    session.transition_to(VoiceState.IDLE)
    assert session.current_state == VoiceState.IDLE

def test_session_trigger_barge_in():
    session = VoiceSession()
    session.transition_to(VoiceState.SPEAKING)
    assert session.trigger_barge_in() is True
    assert session.current_state == VoiceState.LISTENING

def test_audio_manager_push_and_clear():
    import numpy as np
    from src.voice.audio_manager import AudioManager
    mgr = AudioManager()
    chunk = np.ones(1280, dtype=np.float32) * 0.1
    mgr.push_audio_chunk(chunk)
    retrieved = mgr.get_audio_chunk(block=False)
    assert retrieved is not None
    assert len(retrieved) == 1280
    mgr.push_audio_chunk(chunk)
    mgr.clear_input_queue()
    assert mgr.get_audio_chunk(block=False) is None

def test_voice_controller_barge_in_interruption():
    import numpy as np
    from unittest.mock import MagicMock
    from src.voice.voice_controller import VoiceController
    
    mock_agent = MagicMock()
    vc = VoiceController(mock_agent)
    vc._init_audio()
    vc.session.transition_to(VoiceState.SPEAKING)
    vc.tts._is_playing = True
    
    # Send loud chunk 1
    loud_chunk = np.ones(1280, dtype=np.float32) * 0.2
    vc.process_audio_chunk(loud_chunk)
    assert vc.session.current_state == VoiceState.SPEAKING
    assert vc._barge_in_consecutive_loud_frames == 1
    
    # Send loud chunk 2 (triggers barge-in threshold)
    vc.process_audio_chunk(loud_chunk)
    assert vc.session.current_state == VoiceState.LISTENING
    assert vc.tts._is_playing is False
    assert vc._barge_in_consecutive_loud_frames == 0
