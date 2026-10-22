"""The Router decides; agents just do their job (fake model, scripted decisions)."""
import pytest
import prompt_router as pr


def run(model, *names, max_steps=8):
    model.script(*names)
    return pr.run_router("Water tracker app.", max_steps=max_steps)


def test_runs_agents_in_the_order_the_router_picks(model, prompts_dir):
    r = run(model, "ch05_process_model", "ch06_architecture", "DONE")
    assert [s[0] for s in r["steps"]] == ["ch05_process_model", "ch06_architecture"]

def test_first_agent_gets_no_prior_work(model, prompts_dir):
    run(model, "ch05_process_model", "DONE")
    assert "Earlier work" not in model.agent_calls()[0][2]

def test_later_agent_receives_earlier_output(model, prompts_dir):
    run(model, "ch05_process_model", "ch06_architecture", "DONE")
    assert "AGENT-OUTPUT-1" in model.agent_calls()[1][2]

def test_loop_back_passes_freshest_output(model, prompts_dir):
    run(model, "ch05_process_model", "ch06_architecture", "ch05_process_model",
        "ch06_architecture", "DONE")
    fourth = model.agent_calls()[3][2]
    assert "AGENT-OUTPUT-3" in fourth and "AGENT-OUTPUT-1" not in fourth

def test_step_limit_stops_runaway(model, prompts_dir):
    model.router_script = ['{"next": "ch05_process_model", "reason": "again"}'] * 20
    r = pr.run_router("Water tracker app.", max_steps=3)
    assert len(r["steps"]) == 3

def test_unknown_agent_name_stops_cleanly(model, prompts_dir):
    r = run(model, "ch05_process_model", "ch99_nonexistent")
    assert len(r["steps"]) == 1

def test_garbage_router_reply_stops_cleanly(model, prompts_dir):
    model.router_script = ["I think maybe ch05?"]
    assert pr.run_router("Water tracker app.")["steps"] == []

def test_explicit_starting_agent_skips_first_decision(model, prompts_dir):
    model.script("DONE")
    r = pr.run_router("Water tracker app.", starting_agent="ch06_architecture")
    assert r["steps"][0][0] == "ch06_architecture"

def test_summary_labels_each_step(model, prompts_dir):
    r = run(model, "ch05_process_model", "ch06_architecture", "DONE")
    assert r["summary"].index("CH05_PROCESS_MODEL (step 1)") < r["summary"].index("CH06_ARCHITECTURE (step 2)")

def test_prompts_sent_to_agents_have_no_unfilled_placeholders(model, prompts_dir):
    run(model, "ch05_process_model", "DONE")
    assert all("{{" not in c[1] for c in model.agent_calls())


# ---- forgiving agent names (real file names are long: "Ch5 — System Modeling ...") ----
LONG = ["Ch5 — System Modeling Structured Prompt", "Ch6 — Architectural Design Structured Prompt",
        "Ch10 — Something Else", "Ch8 — Software Testing Structured Prompt"]

def test_short_name_resolves_to_long_agent_id():
    agents = dict.fromkeys(LONG)
    assert pr.resolve_agent_choice("Ch5", agents) == LONG[0]

def test_exact_name_still_works():
    assert pr.resolve_agent_choice(LONG[1], dict.fromkeys(LONG)) == LONG[1]

def test_case_and_quotes_are_ignored():
    assert pr.resolve_agent_choice('"ch8"', dict.fromkeys(LONG)) == LONG[3]

def test_short_name_matches_whole_word_only():
    agents = {"Ch1 — A": 0, "Ch10 — B": 0}
    assert pr.resolve_agent_choice("Ch1", agents) == "Ch1 — A"

def test_ambiguous_name_is_rejected():
    assert pr.resolve_agent_choice("Ch", dict.fromkeys(LONG)) is None

def test_nonsense_name_is_rejected():
    assert pr.resolve_agent_choice("Ch99", dict.fromkeys(LONG)) is None

def test_router_short_name_runs_the_right_long_named_agent(model, tmp_path, monkeypatch):
    from conftest import make_prompt
    d = tmp_path / "p"; d.mkdir()
    (d / "Ch5 — System Modeling Structured Prompt.md").write_text(make_prompt("a"))
    (d / "Ch6 — Architectural Design Structured Prompt.md").write_text(make_prompt("b"))
    monkeypatch.setattr(pr, "PROMPTS_DIR", d)
    model.script("Ch5", "ch6", "DONE")
    r = pr.run_router("Water tracker app.")
    assert [s[0] for s in r["steps"]] == ["Ch5 — System Modeling Structured Prompt",
                                          "Ch6 — Architectural Design Structured Prompt"]


# ---- the Router answers with a roster NUMBER; file names are only labels --------------
@pytest.mark.parametrize("answer,expected", [("1", "a first"), ("[2]", "b second"), ("#3", "c third"), (" 2 ", "b second")])
def test_roster_numbers_resolve(answer, expected):
    agents = dict.fromkeys(["b second", "a first", "c third"])
    assert pr.resolve_agent_choice(answer, agents) == expected

@pytest.mark.parametrize("answer", ["0", "4", "99"])
def test_out_of_range_number_is_rejected(answer):
    assert pr.resolve_agent_choice(answer, dict.fromkeys(["a", "b", "c"])) is None

def test_roster_is_numbered_and_asks_for_numbers(model, prompts_dir):
    model.script("1", "DONE")
    pr.run_router("Water tracker app.")
    router_msgs = [c for c in model.calls if c[0] == "router"]
    assert "[1] ch05_process_model" in router_msgs[0][2] and "[2] ch06_architecture" in router_msgs[0][2]
    assert "roster number" in router_msgs[0][1]

def test_any_file_names_work_when_router_answers_with_numbers(model, tmp_path, monkeypatch):
    from conftest import make_prompt
    d = tmp_path / "p"; d.mkdir()
    for name in ["zzz weird name!!.md", "Final_v2 (copy).md", "01.md"]:
        (d / name).write_text(make_prompt(name))
    monkeypatch.setattr(pr, "PROMPTS_DIR", d)
    model.script("1", "2", "3", "DONE")
    r = pr.run_router("Water tracker app.")
    assert [s[0] for s in r["steps"]] == ["01", "Final_v2 (copy)", "zzz weird name!!"]

def test_numeric_answer_given_as_json_number_works(model, prompts_dir):
    model.router_script = ['{"next": 1, "reason": "x"}', '{"next": "DONE", "reason": "y"}']
    r = pr.run_router("Water tracker app.")
    assert len(r["steps"]) == 1
