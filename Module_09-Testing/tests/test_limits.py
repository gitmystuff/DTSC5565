"""Stress and failure behavior: size limit (413) and rate limit (429)."""
import pytest
import prompt_router as pr
from conftest import LIMIT_TOKENS, FakeAPIError


def test_big_outputs_never_exceed_the_size_limit(model, prompts_dir):
    model.agent_reply = lambda n: "Section text with tables. " * 2500     # ~15,000 chars each
    model.script("ch05_process_model", "ch06_architecture", "ch06_architecture", "DONE")
    r = pr.run_router("Water tracker app.")
    assert len(r["steps"]) == 3
    assert max(model.sent) <= LIMIT_TOKENS

def test_long_loop_back_chain_stays_under_limit(model, prompts_dir):
    model.agent_reply = lambda n: "Section text with tables. " * 2500
    model.script("ch05_process_model", "ch06_architecture", "ch05_process_model",
                 "ch06_architecture", "ch05_process_model", "DONE")
    pr.run_router("Water tracker app.", max_steps=8)
    assert max(model.sent) <= LIMIT_TOKENS

def test_429_is_retried_then_succeeds(model, prompts_dir):
    model.fail_with = [FakeAPIError(429)]
    model.script("ch05_process_model", "DONE")
    assert len(pr.run_router("Water tracker app.")["steps"]) == 1

def test_repeated_429_becomes_clear_error():
    class Always429:
        def create(self, **kw): raise FakeAPIError(429)
    pr.client.chat.completions = Always429()
    pr.time.sleep = lambda s: None
    with pytest.raises(pr.ModelCallError, match="rate limited"):
        pr.call_model("sys", "user")

def test_413_becomes_clear_error_not_traceback(model):
    model.fail_with = [FakeAPIError(413)]
    with pytest.raises(pr.ModelCallError, match="too large"):
        pr.call_model("sys", "user")

def test_413_midrun_keeps_finished_steps(model, prompts_dir):
    model.script("ch05_process_model", "ch06_architecture", "DONE")
    original = model.create
    state = {"n": 0}
    def create(**kw):
        state["n"] += 1
        if state["n"] >= 3:                 # 1 = router, 2 = ch05, 3 = router decision
            raise FakeAPIError(413)
        return original(**kw)
    model.create = create
    r = pr.run_router("Water tracker app.")
    assert len(r["steps"]) == 1 and "CH05_PROCESS_MODEL" in r["summary"]


# ---- diagram compaction and retry-on-too-large (found in the first real run) ---------------
PLANT = "```plantuml\n@startuml\nA -> B\n@enduml\n```"
HTML = "```html\n<p>keep me</p>\n```"


def test_diagram_blocks_are_replaced_but_code_blocks_are_kept():
    out = pr.compact_for_handoff(f"Intro\n{PLANT}\nMid\n{HTML}\nEnd")
    assert "@startuml" not in out and "plantuml diagram omitted" in out
    assert "<p>keep me</p>" in out and "Intro" in out and "End" in out

def test_mermaid_is_compacted_too():
    assert "mermaid diagram omitted" in pr.compact_for_handoff("```mermaid\ngraph TD; A-->B\n```")

def test_agent_receives_compacted_earlier_work_not_diagram_source(model, prompts_dir):
    model.agent_reply = lambda n: "Models:\n" + PLANT
    model.script("ch05_process_model", "ch06_architecture", "DONE")
    pr.run_router("Water tracker app.")
    second_agent_msg = model.agent_calls()[1][2]
    assert "@startuml" not in second_agent_msg and "diagram omitted" in second_agent_msg

def test_saved_file_keeps_the_full_diagram(model, prompts_dir, output_dir):
    model.agent_reply = lambda n: "Models:\n" + PLANT
    model.script("ch05_process_model", "DONE")
    r = pr.run_router("Water tracker app.")
    assert "@startuml" in next(r["run_dir"].glob("01_*.md")).read_text()

def test_too_large_request_is_retried_with_less_earlier_work(model, prompts_dir):
    model.agent_reply = lambda n: "x" * 12000
    model.script("ch05_process_model", "ch06_architecture", "DONE")
    original = model.create
    state = {"agent_calls": 0}
    def create(**kw):
        if not kw["messages"][0]["content"].startswith("You are the Router"):
            state["agent_calls"] += 1
            if state["agent_calls"] == 2:            # the 2nd agent's first try is "too big"
                raise FakeAPIError(413, "Request too large: limit 8000, requested 9100")
        return original(**kw)
    model.create = create
    r = pr.run_router("Water tracker app.")
    assert len(r["steps"]) == 2                                   # it still finished
    assert state["agent_calls"] == 3                              # try, retry, (agent 1 was call 1)

def test_gives_up_cleanly_after_all_retries(model, prompts_dir):
    model.agent_reply = lambda n: "x" * 12000
    model.script("ch05_process_model", "ch06_architecture", "DONE")
    original = model.create
    state = {"n": 0}
    def create(**kw):
        if not kw["messages"][0]["content"].startswith("You are the Router"):
            state["n"] += 1
            if state["n"] >= 2:
                raise FakeAPIError(413, "too big")
        return original(**kw)
    model.create = create
    r = pr.run_router("Water tracker app.")
    assert len(r["steps"]) == 1 and "CH05_PROCESS_MODEL" in r["summary"]

def test_413_error_message_includes_the_providers_words():
    pr.client.chat.completions = type("C", (), {"create": lambda self, **kw: (_ for _ in ()).throw(FakeAPIError(413, "limit 8000, requested 9123"))})()
    with pytest.raises(pr.ModelCallError, match="requested 9123") as info:
        pr.call_model("sys", "user")
    assert info.value.too_large is True
