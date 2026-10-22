"""The project brief file: what we want built, kept outside the code."""
import pytest
import prompt_router as pr


def test_reads_brief_from_a_file(tmp_path):
    f = tmp_path / "my_brief.md"; f.write_text("  A water tracker web page.  \n")
    assert pr.load_project_brief(str(f)) == "A water tracker web page."

def test_plain_text_argument_is_used_as_the_brief(tmp_path):
    assert pr.load_project_brief("Build a todo list", base_dir=tmp_path) == "Build a todo list"

def test_no_argument_uses_project_md(tmp_path):
    (tmp_path / "project.md").write_text("From the default file")
    assert pr.load_project_brief(base_dir=tmp_path) == "From the default file"

def test_relative_file_name_is_found_in_project_folder(tmp_path):
    (tmp_path / "brief2.md").write_text("Relative brief")
    assert pr.load_project_brief("brief2.md", base_dir=tmp_path) == "Relative brief"

def test_missing_default_brief_gives_clear_error(tmp_path):
    with pytest.raises(ValueError, match="project.md"):
        pr.load_project_brief(base_dir=tmp_path)

def test_empty_brief_file_gives_clear_error(tmp_path):
    f = tmp_path / "empty.md"; f.write_text("  \n")
    with pytest.raises(ValueError, match="empty"):
        pr.load_project_brief(str(f))

def test_long_brief_warns_but_still_works(tmp_path, capsys):
    f = tmp_path / "long.md"; f.write_text("x" * (pr.BRIEF_WARN_CHARS + 1))
    assert len(pr.load_project_brief(str(f))) == pr.BRIEF_WARN_CHARS + 1
    assert "[warn]" in capsys.readouterr().out
