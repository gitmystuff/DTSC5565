"""Tests for lite.py using a fake model, so no key, no network, no waiting."""
import lite


class FakeClient:
    """Stands in for Groq(): records every request and returns scripted replies."""
    def __init__(self, replies):
        self.replies, self.requests = list(replies), []
        self.chat = type("Chat", (), {"completions": self})()

    def create(self, model, messages, max_tokens):
        self.requests.append((messages[0]["content"], messages[1]["content"]))
        text = self.replies.pop(0)
        msg = type("M", (), {"content": text})
        reply = type("R", (), {"choices": [type("C", (), {"message": msg})]})()
        if getattr(self, "usage", None):
            reply.usage = self.usage
        return reply


HTML_REPLY = "Here it is:\n```html\n<html><body>Water</body></html>\n```\nOpen it."


def make_client():
    return FakeClient(["DESIGN TEXT", HTML_REPLY, "VERIFY TEXT"])


def test_runs_every_prompt_in_order():
    steps = lite.run("A water app", make_client(), pause=0)
    assert [name for name, _ in steps] == ["1_design", "2_build", "3_verify"]

def test_the_brief_is_put_into_each_prompt():
    client = make_client()
    lite.run("A WATER APP BRIEF", client, pause=0)
    assert all("A WATER APP BRIEF" in system for system, _ in client.requests)
    assert all("[PROJECT_DESCRIPTION]" not in system for system, _ in client.requests)

def test_first_step_gets_no_earlier_work_later_steps_do():
    client = make_client()
    lite.run("brief", client, pause=0)
    assert "Earlier work" not in client.requests[0][1]
    assert "DESIGN TEXT" in client.requests[1][1]
    assert "DESIGN TEXT" in client.requests[2][1] and "<html>" in client.requests[2][1]

def test_earlier_work_is_capped(monkeypatch):
    monkeypatch.setattr(lite, "MAX_EARLIER", 50)
    client = FakeClient(["x" * 5000, HTML_REPLY, "v"])
    lite.run("brief", client, pause=0)
    assert len(client.requests[1][1]) < 200

def test_pauses_between_steps_but_not_after_the_last(monkeypatch):
    waits = []
    monkeypatch.setattr(lite.time, "sleep", lambda s: waits.append(s))
    lite.run("brief", make_client(), pause=7)
    assert waits == [7, 7]

def test_extract_html_finds_the_page():
    assert lite.extract_html(HTML_REPLY) == "<html><body>Water</body></html>\n"

def test_extract_html_returns_none_without_a_code_block():
    assert lite.extract_html("no code here") is None

def test_save_writes_each_step_and_the_web_page(tmp_path):
    steps = [("1_design", "D"), ("2_build", HTML_REPLY), ("3_verify", "V")]
    folder = lite.save(steps, tmp_path)
    assert (folder / "1_design.md").read_text() == "D"
    assert "<body>Water</body>" in (folder / "index.html").read_text()

def test_save_without_html_makes_no_web_page(tmp_path):
    folder = lite.save([("1_design", "D")], tmp_path)
    assert not (folder / "index.html").exists()


class SlowDownThenWork(FakeClient):
    """Raises a 429 on the first call, then behaves normally."""
    def create(self, model, messages, max_tokens):
        if not self.requests:
            self.requests.append(("429", ""))
            error = RuntimeError("slow down"); error.status_code = 429
            raise error
        return super().create(model, messages, max_tokens)


def test_a_rate_limit_error_is_retried(monkeypatch):
    waits = []
    monkeypatch.setattr(lite.time, "sleep", lambda s: waits.append(s))
    client = SlowDownThenWork(["ok"])
    assert lite.ask(client, "sys", "user") == "ok" and waits == [30]

def test_other_errors_are_not_hidden():
    import pytest
    class Broken(FakeClient):
        def create(self, model, messages, max_tokens):
            raise ValueError("bad request")
    with pytest.raises(ValueError):
        lite.ask(Broken([]), "sys", "user")


def usage(prompt, completion):
    return type("U", (), {"prompt_tokens": prompt, "completion_tokens": completion,
                          "total_tokens": prompt + completion})


def test_token_counts_are_reported_for_each_call(capsys):
    client = FakeClient(["ok"])
    client.usage = usage(1150, 2340)
    lite.ask(client, "sys", "user")
    out = capsys.readouterr().out
    assert "1,150 in" in out and "2,340 out" in out and "3,490" in out

def test_missing_usage_does_not_break_anything(capsys):
    assert lite.ask(FakeClient(["ok"]), "sys", "user") == "ok"
    assert "Tokens" not in capsys.readouterr().out

def test_describe_usage_is_empty_without_usage():
    assert lite.describe_usage(object()) == ""
