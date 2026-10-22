"""Staying inside the free tier's tokens-per-minute limit, and saving run.log."""
import time
import pytest
import prompt_router as pr


@pytest.fixture
def sleeps(monkeypatch):
    waited = []
    monkeypatch.setattr(pr.time, "sleep", lambda s: waited.append(s))
    return waited


def test_no_wait_when_under_the_limit(sleeps):
    pr._pace(2000)
    assert sleeps == []

def test_waits_when_the_minute_is_nearly_used_up(sleeps):
    pr._usage.append((time.monotonic(), 7000))
    pr._pace(2000)                                  # 7000 + 2000 > 8000
    assert sleeps and sleeps[0] >= 1

def test_old_usage_does_not_count(sleeps):
    pr._usage.append((time.monotonic() - 61, 8000))   # over a minute ago
    pr._pace(5000)
    assert sleeps == []

def test_zero_limit_turns_pacing_off(sleeps, monkeypatch):
    monkeypatch.setattr(pr, "TPM_LIMIT", 0)
    pr._usage.append((time.monotonic(), 9999))
    pr._pace(9999)
    assert sleeps == []

def test_a_single_oversized_request_is_not_stuck_waiting(sleeps):
    pr._pace(20000)                                  # nothing to wait for; the provider decides
    assert sleeps == []

def test_provider_reported_usage_is_remembered():
    resp = type("R", (), {"usage": type("U", (), {"total_tokens": 4321})})
    pr._record_usage(resp, "s", "u", "out")
    assert pr._usage[-1][1] == 4321

def test_usage_is_estimated_when_provider_gives_none():
    pr._record_usage(object(), "a" * 300, "b" * 300, "c" * 300)
    assert pr._usage[-1][1] == 900 // pr.CHARS_PER_TOKEN

def test_second_big_call_in_a_minute_waits(model, prompts_dir, sleeps, monkeypatch):
    monkeypatch.setattr(pr.time, "sleep", lambda s: sleeps.append(s))   # `model` fixture silences sleep; record it instead
    model.agent_reply = lambda n: "x" * 9000                            # ~3000 tokens out
    model.script("ch05_process_model", "ch06_architecture", "DONE")
    pr.run_router("Water tracker app.")
    assert any(s >= 1 for s in sleeps)


# ---- run.log --------------------------------------------------------------------------------
def test_run_log_contains_what_was_shown_on_screen(model, prompts_dir):
    model.script("ch05_process_model", "DONE")
    r = pr.run_router("Water tracker app.")
    log = (r["run_dir"] / "run.log").read_text()
    assert "STEP 1" in log and "GUARDRAILS SUMMARY" in log

def test_no_log_when_saving_is_off(model, prompts_dir, output_dir):
    model.script("ch05_process_model", "DONE")
    pr.run_router("Water tracker app.", save_outputs=False)
    assert not output_dir.exists()

def test_screen_output_still_appears(model, prompts_dir, capsys):
    model.script("ch05_process_model", "DONE")
    pr.run_router("Water tracker app.")
    assert "STEP 1" in capsys.readouterr().out
