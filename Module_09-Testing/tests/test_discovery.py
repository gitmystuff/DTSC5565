"""Finding agents in the prompts folder."""
import pytest
import prompt_router as pr


def test_discovers_valid_prompts(prompts_dir):
    assert sorted(pr.discover_agents()) == ["ch05_process_model", "ch06_architecture"]

def test_non_template_file_is_skipped(prompts_dir, capsys):
    (prompts_dir / "notes.md").write_text("# just notes\nno template here")
    assert "notes" not in pr.discover_agents()
    assert "[skip] notes.md" in capsys.readouterr().out

def test_filename_is_only_a_label(prompts_dir):
    (prompts_dir / "Ch7 — Design and Implementation Structured Prompt.md").write_text(
        (prompts_dir / "ch05_process_model.md").read_text())
    assert "Ch7 — Design and Implementation Structured Prompt" in pr.discover_agents()

def test_empty_folder_gives_clear_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        pr.discover_agents(tmp_path)

def test_folder_with_no_valid_prompt_gives_clear_error(tmp_path):
    (tmp_path / "a.md").write_text("nothing useful")
    with pytest.raises(ValueError):
        pr.discover_agents(tmp_path)
