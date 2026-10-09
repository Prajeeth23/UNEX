import pytest
import asyncio
from tests.stability_runner import run_stability_test
from scripts.unex_daemon import get_daemon_pid, is_running

@pytest.mark.asyncio
async def test_stability_runner_cycles():
    # Run 2 quick cycles of the stability test
    success = await run_stability_test(duration_hours=0.01, max_cycles=2)
    assert success is True

def test_daemon_process_helpers():
    # Verify helper does not raise on invalid or non-existent PID
    assert is_running(999999) is False
    pid = get_daemon_pid()
    assert pid is None or isinstance(pid, int)
