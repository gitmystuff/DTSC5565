"""Unit tests for the small pure functions (no model, no files needed)."""
import pytest
import prompt_router as pr
from conftest import make_prompt


# ---- trim_middle: partition + boundary testing ----------------------------------
def test_trim_keeps_start_and_end():
    out = pr.trim_middle("START" + "x" * 5000 + "END", 1000)
    assert out.startswith("START") and out.endswith("END") and len(out) <= 1000

def test_trim_leaves_short_text_alone():
    assert pr.trim_middle("short", 1000) == "short"

@pytest.mark.parametrize("extra", [-1, 0])                     # at / just under the limit
def test_trim_boundary_not_trimmed(extra):
    text = "a" * (100 + extra)
    assert pr.trim_middle(text, 100) == text

def test_trim_one_over_limit_is_trimmed():
    assert len(pr.trim_middle("a" * 101, 100)) <= 100

def test_trim_zero_or_negative_limit_gives_empty():
    assert pr.trim_middle("anything", 0) == ""
    assert pr.trim_middle("anything", -5) == ""


# ---- section handling --------------------------------------------------------------
def test_all_eight_sections_found():
    assert list(pr.split_sections(make_prompt("x"))) == pr.CANONICAL_SECTIONS

def test_sections_match_by_name_not_number():
    text = "\n".join(f"### {s}\nbody {s}" for s in reversed(pr.CANONICAL_SECTIONS))
    assert set(pr.split_sections(text)) == set(pr.CANONICAL_SECTIONS)

def test_missing_section_raises_clear_error():
    text = make_prompt("x").replace("## 8. Verification", "## 8. Something else")
    with pytest.raises(ValueError, match="Verification"):
        pr.extract_core_sections(text, "demo.md")

def test_extra_sections_are_ignored():
    text = make_prompt("x") + "\n\n## 9. Handoff\nphase: next"
    core = pr.extract_core_sections(text)
    assert "phase: next" not in core

def test_core_sections_come_out_in_canonical_order():
    core = pr.extract_core_sections(make_prompt("x", "Boss"))
    assert core.index("Boss") < core.index("Text for Context") < core.index("Text for Verification")


# ---- placeholders: both [NAME] and {{NAME}} spellings -----------------------------
def test_square_bracket_placeholders_are_filled():
    out = pr.fill_placeholders("Project: [PROJECT_DESCRIPTION]. Mode: [INTERACTION_MODE].", "Water app")
    assert out == "Project: Water app. Mode: autonomous."

def test_double_brace_placeholders_still_work():
    assert pr.fill_placeholders("{{PROJECT_DESCRIPTION}}", "Water app") == "Water app"

def test_unknown_placeholder_becomes_UNKNOWN():
    assert pr.fill_placeholders("Stack: [TECH_STACK]", "x") == "Stack: UNKNOWN"

def test_ordinary_brackets_are_left_alone():
    text = "See [1] and [Q-01] and [x] and [ab]"
    assert pr.fill_placeholders(text, "x") == text
