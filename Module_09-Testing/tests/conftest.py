"""Shared test setup: a fake model so tests never call Groq, and tiny fake prompts."""
import json
import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("GROQ_API_KEY", "test-key")           # Groq() needs some key to import
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import prompt_router as pr                                   # noqa: E402

LIMIT_TOKENS = 8000        # what Groq's free tier enforces per request


class FakeAPIError(Exception):
    """Looks like an HTTP error from the model provider."""
    def __init__(self, status_code, msg="error"):
        super().__init__(msg)
        self.status_code = status_code


class FakeModel:
    """Stands in for client.chat.completions. Records every request."""
    def __init__(self):
        self.router_script = []     # replies the Router will give, in order
        self.sent = []              # estimated tokens of each request
        self.calls = []             # (kind, system, user)
        self.fail_with = []         # exceptions to raise on the next calls
        self.agent_reply = lambda n: f"AGENT-OUTPUT-{n}"
        self._agents_run = 0

    def create(self, model, messages, max_tokens=None):
        system, user = messages[0]["content"], messages[1]["content"]
        self.sent.append((len(system) + len(user)) // 4)
        if self.fail_with:
            raise self.fail_with.pop(0)
        if self.sent[-1] > LIMIT_TOKENS:
            raise FakeAPIError(413, "request too large")
        if system.startswith("You are the Router"):
            self.calls.append(("router", system, user))
            return _resp(self.router_script.pop(0))
        self._agents_run += 1
        self.calls.append(("agent", system, user))
        return _resp(self.agent_reply(self._agents_run))

    # helpers for tests
    def script(self, *names):
        self.router_script = [json.dumps({"next": n, "reason": "test"}) for n in names]

    def agent_calls(self):
        return [c for c in self.calls if c[0] == "agent"]


def _resp(text):
    msg = type("Msg", (), {"content": text})
    choice = type("Choice", (), {"message": msg})
    return type("Resp", (), {"choices": [choice]})


def make_prompt(name, role="Test role"):
    sections = ["Role", "Context", "Task/Objective", "Requirements",
                "Constraints", "Process", "Output Format", "Verification"]
    body = "\n\n".join(
        f"## {i}. {s}\n\n{role if s == 'Role' else 'Text for ' + s}." for i, s in enumerate(sections, 1))
    return body


@pytest.fixture
def model(monkeypatch):
    fake = FakeModel()
    monkeypatch.setattr(pr.client.chat, "completions", fake)
    monkeypatch.setattr(pr.time, "sleep", lambda s: None)     # never really wait
    return fake


@pytest.fixture(autouse=True)
def fresh_usage():
    """Each test starts with no remembered token usage (pacing is per-minute state)."""
    pr._usage.clear()
    yield
    pr._usage.clear()


@pytest.fixture(autouse=True)
def output_dir(tmp_path, monkeypatch):
    """Runs save files; send them to a temp folder so tests never write into the project."""
    d = tmp_path / "output"
    monkeypatch.setattr(pr, "OUTPUT_DIR", d)
    return d


@pytest.fixture
def prompts_dir(tmp_path, monkeypatch):
    """Two valid agents, so tests do not depend on your real prompts folder."""
    d = tmp_path / "prompts"; d.mkdir()
    (d / "ch05_process_model.md").write_text(make_prompt("a", "Modeler"))
    (d / "ch06_architecture.md").write_text(make_prompt("b", "Architect"))
    monkeypatch.setattr(pr, "PROMPTS_DIR", d)
    return d
