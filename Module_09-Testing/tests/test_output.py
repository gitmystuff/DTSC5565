"""Saving a run and turning code blocks into real files (the web-app demo)."""
import prompt_router as pr

HTML = "<!DOCTYPE html>\n<html><body><h1>Water</h1></body></html>"


def block(lang, code):
    return f"```{lang}\n{code}\n```"


# ---- extract_code_files -------------------------------------------------------------
def test_html_block_becomes_index_html():
    files = pr.extract_code_files("Here you go:\n" + block("html", HTML))
    assert list(files) == ["index.html"] and "<h1>Water</h1>" in files["index.html"]

def test_language_picks_default_names():
    text = "\n".join([block("html", HTML), block("css", "body{}"), block("javascript", "let a=1;")])
    assert set(pr.extract_code_files(text)) == {"index.html", "style.css", "app.js"}

def test_filename_above_the_block_is_used():
    text = "### `tracker.html`\n" + block("html", HTML)
    assert list(pr.extract_code_files(text)) == ["tracker.html"]

def test_filename_in_first_comment_line_is_used():
    text = block("js", "// water.js\nlet a = 1;")
    assert list(pr.extract_code_files(text)) == ["water.js"]

def test_two_blocks_of_same_language_do_not_overwrite_each_other():
    text = block("html", "<p>1</p>") + "\n" + block("html", "<p>2</p>")
    assert list(pr.extract_code_files(text)) == ["index.html", "index_2.html"]

def test_non_code_blocks_are_ignored():
    text = "\n".join([block("mermaid", "graph TD; A-->B"), block("bash", "ls"), block("", "plain")])
    assert pr.extract_code_files(text) == {}

def test_filename_cannot_escape_the_folder():
    text = "### ../../evil.py\n" + block("python", "print(1)")
    names = list(pr.extract_code_files(text))
    assert names and all("/" not in n and ".." not in n for n in names)

def test_text_without_code_gives_no_files():
    assert pr.extract_code_files("just prose, no code") == {}


# ---- save_run ------------------------------------------------------------------------
def test_save_run_writes_each_step_and_the_app(tmp_path):
    steps = [("ch05 models", "## Models\ntext"), ("ch07_code", "Code:\n" + block("html", HTML))]
    run_dir, code = pr.save_run(steps, tmp_path)
    assert (run_dir / "01_ch05_models.md").read_text() == "## Models\ntext"
    assert (run_dir / "02_ch07_code.md").exists()
    assert [p.name for p in code] == ["index.html"] and code[0].parent == run_dir / "app"

def test_later_step_overwrites_earlier_code_file(tmp_path):
    steps = [("a", block("html", "<p>old</p>")), ("b", block("html", "<p>new</p>"))]
    _, code = pr.save_run(steps, tmp_path)
    assert "new" in code[0].read_text()

def test_no_code_means_no_app_folder(tmp_path):
    run_dir, code = pr.save_run([("a", "only prose")], tmp_path)
    assert code == [] and not (run_dir / "app").exists()


# ---- end to end with the fake model -----------------------------------------------------
def test_run_router_saves_outputs_and_app(model, prompts_dir, output_dir):
    model.agent_reply = lambda n: "Result:\n" + block("html", HTML)
    model.script("ch05_process_model", "DONE")
    r = pr.run_router("Water tracker web app.")
    assert (r["run_dir"] / "01_ch05_process_model.md").exists()
    assert r["code_files"][0].name == "index.html"
    assert r["run_dir"].parent == output_dir

def test_save_outputs_false_writes_nothing(model, prompts_dir, output_dir):
    model.script("ch05_process_model", "DONE")
    r = pr.run_router("Water tracker web app.", save_outputs=False)
    assert r["run_dir"] is None and not output_dir.exists()

def test_unwritable_output_folder_does_not_lose_the_run(model, prompts_dir, monkeypatch):
    def boom(*a, **k): raise OSError("disk full")
    monkeypatch.setattr(pr, "save_run", boom)
    model.script("ch05_process_model", "DONE")
    r = pr.run_router("Water tracker web app.")
    assert len(r["steps"]) == 1 and r["run_dir"] is None


# ---- file names from the top comment of the code (seen in the first real run) --------------
def test_at_file_comment_names_the_file():
    code = "/**\n * @file   validator.js\n * @module x\n */\nexport const a = 1;"
    assert list(pr.extract_code_files(block("javascript", code))) == ["validator.js"]

def test_separate_modules_get_their_own_names():
    text = (block("js", "/**\n * @file storage.js\n */\nlet a;") + "\n" +
            block("js", "/**\n * @file tracker.js\n */\nlet b;"))
    assert sorted(pr.extract_code_files(text)) == ["storage.js", "tracker.js"]

def test_import_line_does_not_name_the_file():
    code = "import { x } from './other.js';\nexport const y = 1;"
    assert list(pr.extract_code_files(block("js", code))) == ["app.js"]
