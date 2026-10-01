import os
import re
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MODEL = "openai/gpt-oss-120b"
PROMPTS_DIR = Path(__file__).parent / "prompts"

# Point these at YOUR actual filenames in prompts/ -- naming conventions
# vary (ch3_process_model.md, ch03_process_model.md, etc.) depending on
# how you generated them. Nothing else below needs to change.
CH3_PROMPT_FILE = "ch03_process_model.md"
CH6_PROMPT_FILE = "ch06_architecture.md"

# The 8 required section names, in canonical order. Every prompt must have
# a heading containing each of these -- numbering, heading level ("##" vs
# "###"), and order don't matter; the NAME is the contract.
CANONICAL_SECTIONS = [
    "Role",
    "Context",
    "Task/Objective",
    "Requirements",
    "Constraints",
    "Process",
    "Output Format",
    "Verification",
]

# Matches ANY markdown heading, used to find section boundaries.
ANY_HEADING_RE = re.compile(r"^#{1,6}\s+.+$", re.MULTILINE)

# Matches a heading containing one of the 8 canonical section names, with an
# optional leading number ("1.", "2.", etc.) and tolerant of "Task/Objective"
# being written as "Task / Objective" or "Task and Objective".
_SECTION_NAME_PATTERN = "|".join(
    name.replace("/", r"\s*/\s*") for name in CANONICAL_SECTIONS
)
SECTION_NAME_RE = re.compile(
    rf"^#{{1,6}}\s*(?:\d+\.\s*)?({_SECTION_NAME_PATTERN})\s*$",
    re.IGNORECASE | re.MULTILINE,
)

# Matches {{SOME_PLACEHOLDER}} tokens.
PLACEHOLDER_RE = re.compile(r"\{\{([A-Z0-9_]+)\}\}")


def load_prompt(filename):
    """Load a structured prompt from the prompts/ folder as plain text."""
    path = PROMPTS_DIR / filename
    if not path.exists():
        if filename == CH3_PROMPT_FILE:
            hint = (
                "That's the prompt you built a few weeks ago using "
                "ch3-prompt-generator.md. Run that again (with the Chapter 3 "
                "slides attached) if you don't already have a saved copy."
            )
        else:
            hint = (
                "Check that the filename above exactly matches what's "
                "actually in your prompts/ folder -- naming conventions "
                "vary (e.g. ch6_ vs ch06_), and CH3_PROMPT_FILE / "
                "CH6_PROMPT_FILE at the top of this script need to match."
            )
        raise FileNotFoundError(f"\nMissing prompts/{filename}.\n{hint}")
    return path.read_text()


def extract_core_sections(raw_text, source_filename="this prompt"):
    """
    Pull out ONLY the 8 required sections (Role, Context, Task/Objective,
    Requirements, Constraints, Process, Output Format, Verification) from
    a prompt file, in canonical order, ignoring everything else: library-
    entry headers, Input Parameters tables, "Notes for the library"
    sections, etc.

    Sections are matched by NAME, not by number or position. That's the
    actual class-wide contract: every prompt must have a heading for each
    of these 8 names -- numbering, heading level, and order don't matter.

    Handles both fenced (```) and unfenced section bodies, since not
    everyone wraps sections in code fences the same way. A section's body
    ends at the next heading of ANY kind, not just the next recognized
    one -- an unrelated heading like "## Notes for the library" still has
    to end whatever section precedes it.
    """
    all_headings = list(ANY_HEADING_RE.finditer(raw_text))
    sections = {}

    for i, heading_match in enumerate(all_headings):
        line = heading_match.group(0)
        name_match = SECTION_NAME_RE.match(line)
        if not name_match:
            continue

        # Normalize to the canonical name (case/spacing may vary).
        matched_text = name_match.group(1).lower().replace(" ", "").replace("/", "")
        canonical = next(
            (c for c in CANONICAL_SECTIONS if c.lower().replace(" ", "").replace("/", "") == matched_text),
            None,
        )
        if canonical is None:
            continue

        start = heading_match.end()
        end = all_headings[i + 1].start() if i + 1 < len(all_headings) else len(raw_text)
        body = raw_text[start:end].strip()

        # Strip one wrapping code fence, if the section body has one. Find
        # the matching closing fence explicitly rather than assuming the
        # body ends with it -- there's often trailing content after it
        # (like a "---" horizontal rule before the next heading).
        if body.startswith("```"):
            closing_idx = body.find("```", 3)
            inner = body[3:closing_idx] if closing_idx != -1 else body[3:]
            inner = re.sub(r"^[a-zA-Z]*\n", "", inner, count=1)
            body = inner.strip()

        # If the same section name appears more than once, keep the first.
        sections.setdefault(canonical, body)

    missing = [name for name in CANONICAL_SECTIONS if name not in sections]
    if missing:
        raise ValueError(
            f"\n{source_filename} is missing required section(s): {', '.join(missing)}.\n"
            f"Every prompt needs a heading for each of: {', '.join(CANONICAL_SECTIONS)}."
        )

    return "\n\n".join(sections[name] for name in CANONICAL_SECTIONS)


def extract_handoff_block(raw_response):
    """
    Pull out just the YAML handoff block from a prompt's response, instead
    of forwarding the entire multi-section document to the next step.

    Our ch03_process_model.md explicitly designs for this: its Output
    Format section defines a "Handoff Block" specifically described as
    "consumed by the router and by downstream prompts" -- a compact
    summary, not the full prose document. Forwarding the whole document
    both ignores that design and is the main reason Step 2's request blew
    past Groq's token limit.

    Looks for a ```yaml fenced block first; falls back to the full
    response (with a warning) if no fenced YAML block is found, so this
    doesn't silently break for a prompt that doesn't follow this
    convention.
    """
    match = re.search(r"```yaml\s*(.*?)```", raw_response, re.DOTALL)
    if match:
        return match.group(1).strip()
    print(
        "  [warning] No ```yaml handoff block found in the previous step's "
        "output -- forwarding the full response instead. This will use a "
        "lot more tokens."
    )
    return raw_response


def fill_placeholders(text, project_description, overrides=None):
    """
    Placeholder substitution with EXPLICIT overrides for specific tokens,
    rather than a blanket rule applied to every token that merely contains
    a given word.

    Why explicit: a prompt like ch06_architecture.md has BOTH
    {{CH02_HANDOFF}} and {{CH03_HANDOFF}}. A blanket "any token with
    HANDOFF in its name gets the prior output" rule fills both with the
    SAME text -- duplicating it in the request and wasting a large number
    of tokens for no benefit. `overrides` lets the caller say exactly
    which token gets which value; anything not named in `overrides` falls
    through to the generic rules below.

    Generic rules for anything not explicitly overridden:
      - a token with "DESCRIPTION" in its name -> the real project description
      - everything else -> "UNKNOWN" (both of our example prompts document
        this as a valid, honest value for a genuinely unfilled input)
    """
    overrides = overrides or {}

    def replace(match):
        name = match.group(1)
        if name in overrides:
            return overrides[name]
        if "DESCRIPTION" in name:
            return project_description
        return "UNKNOWN"

    return PLACEHOLDER_RE.sub(replace, text)


def call_model(assembled_prompt, max_tokens=4096):
    """
    Send one fully-assembled, placeholder-filled prompt to the model.

    The whole thing (Role through Verification, with the real project
    description already substituted into Context) goes in as the system
    message, since the Role section defines the persona the way a system
    message normally would. The user turn is just a minimal trigger.

    max_tokens is set explicitly and generously (4096) because these
    structured prompts ask for long, multi-section outputs (including a
    Handoff Block at the end). Without this, the API's default output
    limit can silently truncate the response before it's complete --
    which breaks any later step that depends on reading that Handoff
    Block. If a response still gets cut off, raise this further.
    """
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": assembled_prompt},
            {"role": "user", "content": "Proceed with the task as specified above."},
        ],
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


def run_prompt_chain(project_description):
    """
    A deterministic two-step chain (NOT model-decided routing):
      Step 1 always runs the process-model prompt.
      Step 2 always runs the architecture prompt, using Step 1's raw
      output as the prior-phase handoff input.

    This is simpler than last week's router, which let the model choose
    which tool to call. Here, WE decide the order in advance, because the
    architecture decision assumes a process model is already known.
    """
    print("=" * 70)
    print("STEP 1 of 2")
    print(f"Using prompt: prompts/{CH3_PROMPT_FILE}")
    print("Why: a process-model decision needs to exist before an")
    print("architecture can be chosen.")
    print("=" * 70)

    ch3_raw = load_prompt(CH3_PROMPT_FILE)
    ch3_core = extract_core_sections(ch3_raw, source_filename=CH3_PROMPT_FILE)
    ch3_filled = fill_placeholders(ch3_core, project_description)
    process_model_decision = call_model(ch3_filled)
    print(f"\n--- Result from {CH3_PROMPT_FILE} ---")
    print(process_model_decision)

    # Forward only the compact handoff block to Step 2, not the entire
    # multi-section document -- this is what keeps the chain's token cost
    # manageable, and it's what ch03_process_model.md's own Output Format
    # section says the handoff block is FOR.
    handoff = extract_handoff_block(process_model_decision)

    print("\n" + "=" * 70)
    print("STEP 2 of 2")
    print(f"Using prompt: prompts/{CH6_PROMPT_FILE}")
    print("Why: with the process model now decided, we can match an")
    print("architecture to the project, using Step 1's handoff block as")
    print("the prior-phase input this prompt expects.")
    print("=" * 70)

    ch6_raw = load_prompt(CH6_PROMPT_FILE)
    ch6_core = extract_core_sections(ch6_raw, source_filename=CH6_PROMPT_FILE)
    # Only {{CH02_HANDOFF}} gets real data -- ch03_process_model.md's own
    # handoff block identifies ITSELF as phase "ch02-process-model-selection".
    # {{CH03_HANDOFF}} (a separate agile-practice-configuration phase we
    # haven't run today) explicitly gets "NONE" rather than a duplicate copy.
    ch6_filled = fill_placeholders(
        ch6_core,
        project_description,
        overrides={"CH02_HANDOFF": handoff, "CH03_HANDOFF": "NONE"},
    )
    architecture_decision = call_model(ch6_filled)
    print(f"\n--- Result from {CH6_PROMPT_FILE} ---")
    print(architecture_decision)

    print("\n" + "=" * 70)
    print("GUARDRAILS SUMMARY")
    print("=" * 70)
    summary = (
        f"PROCESS MODEL:\n{process_model_decision}\n\n"
        f"ARCHITECTURE:\n{architecture_decision}"
    )
    print(summary)
    return summary


if __name__ == "__main__":
    project_description = (
        "A small team is building a mobile app that lets users log daily "
        "water intake and get reminders. They expect a few thousand users, "
        "want to iterate quickly based on user feedback, and have no "
        "strict security or safety requirements."
    )
    run_prompt_chain(project_description)
