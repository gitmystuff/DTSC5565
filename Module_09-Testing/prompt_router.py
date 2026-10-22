"""
prompt_router.py -- turns every structured prompt in prompts/ into a named
Agent and runs them under a Router that decides what happens next.

Design rule: AGENTS DON'T KNOW OTHER AGENTS EXIST. A prompt only has to
follow the class template (the 8 sections: Role, Context, Task/Objective,
Requirements, Constraints, Process, Output Format, Verification). It does
not need a handoff block, a phase id, a status field, or any mention of
what comes before or after it. All of that is the Router's job:

  classify  -- the Router reads the roster (each agent's Role + Task) and
               the project description, and picks the first agent
  select    -- looks that agent up
  execute   -- runs it, giving it the project description plus whatever
               earlier agents produced (the Router passes artifacts
               forward; the agent just sees "prior work")
  verify    -- the Router reads the agent's output and judges whether the
               work is done, needs another pass, or needs an earlier agent
  route     -- the Router names the next agent, or DONE

Adding a prompt = drop a .md file in prompts/. Nothing else changes. The
filename is just a label; the Router chooses by what the prompt DOES.
"""

import json
import os
import re
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MODEL = "openai/gpt-oss-120b"
PROMPTS_DIR = Path(__file__).parent / "prompts"
OUTPUT_DIR = Path(__file__).parent / "output"   # each run saves here

# Hard cap on total agent executions per run. An agent may legitimately run
# more than once (the Router can send work back to an earlier agent), so
# this -- not "each agent once" -- is what prevents endless loops.
MAX_STEPS = 8

# Size budget for ONE request. Groq's free tier rejects any single request
# over 8,000 tokens per minute (HTTP 413), so the router fits each request
# under INPUT_TOKEN_BUDGET (a little below the limit, for estimate error).
# Tokens are estimated as characters / CHARS_PER_TOKEN -- close enough for
# English prose and markdown (calibrated against a real run). On a paid tier
# with a higher limit, raise INPUT_TOKEN_BUDGET and more earlier work fits.
INPUT_TOKEN_BUDGET = 7000
CHARS_PER_TOKEN = 3

# If the model says "slow down" (HTTP 429), wait and try again this many times.
RETRY_LIMIT = 3

# Free-tier pacing. Groq's free plan allows about 8,000 tokens per minute across
# ALL requests, so before each call the router checks what it has already used in
# the last 60 seconds and waits if this call would go over. Set the environment
# variable TPM_LIMIT to your own limit (or 0 to turn pacing off).
TPM_LIMIT = int(os.environ.get("TPM_LIMIT", "8000"))
_usage = []   # [(time.monotonic() when used, tokens)] for the last minute

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

ANY_HEADING_RE = re.compile(r"^#{1,6}\s+.+$", re.MULTILINE)

_SECTION_NAME_PATTERN = "|".join(
    name.replace("/", r"\s*/\s*") for name in CANONICAL_SECTIONS
)
SECTION_NAME_RE = re.compile(
    rf"^#{{1,6}}\s*(?:\d+\.\s*)?({_SECTION_NAME_PATTERN})\s*$",
    re.IGNORECASE | re.MULTILINE,
)

# Placeholders may be written [NAME] (the class template style) or {{NAME}}.
PLACEHOLDER_RE = re.compile(r"\{\{([A-Z0-9_]+)\}\}|\[([A-Z][A-Z0-9_]{2,})\]")


# ---------------------------------------------------------------------------
# Prompt parsing
# ---------------------------------------------------------------------------

def _canonical_name(matched_text):
    key = matched_text.lower().replace(" ", "").replace("/", "")
    return next(
        (c for c in CANONICAL_SECTIONS
         if c.lower().replace(" ", "").replace("/", "") == key),
        None,
    )


def split_sections(raw_text):
    """Return {canonical section name: body}. Sections are matched by NAME,
    not number or position; anything else in the file is ignored."""
    all_headings = list(ANY_HEADING_RE.finditer(raw_text))
    sections = {}
    for i, heading_match in enumerate(all_headings):
        name_match = SECTION_NAME_RE.match(heading_match.group(0))
        if not name_match:
            continue
        canonical = _canonical_name(name_match.group(1))
        if canonical is None:
            continue
        start = heading_match.end()
        end = all_headings[i + 1].start() if i + 1 < len(all_headings) else len(raw_text)
        body = raw_text[start:end].strip()
        if body.startswith("```"):
            closing_idx = body.find("```", 3)
            inner = body[3:closing_idx] if closing_idx != -1 else body[3:]
            inner = re.sub(r"^[a-zA-Z]*\n", "", inner, count=1)
            body = inner.strip()
        sections.setdefault(canonical, body)
    return sections


def extract_core_sections(raw_text, source_filename="this prompt"):
    """The 8 required sections only, in canonical order."""
    sections = split_sections(raw_text)
    missing = [n for n in CANONICAL_SECTIONS if n not in sections]
    if missing:
        raise ValueError(
            f"\n{source_filename} is missing required section(s): "
            f"{', '.join(missing)}.\nEvery prompt needs a heading for each of: "
            f"{', '.join(CANONICAL_SECTIONS)}."
        )
    return "\n\n".join(sections[n] for n in CANONICAL_SECTIONS)


DIAGRAM_LANGS = {"plantuml", "uml", "mermaid", "dot", "graphviz", "puml"}


def compact_for_handoff(text):
    """Shrink an earlier agent's output before passing it on: diagram source
    (PlantUML, Mermaid, ...) costs many tokens and a later agent gains little
    from it, so each diagram block becomes a one-line note. The full output is
    still saved to disk untouched."""
    def swap(m):
        lang = m.group(1).lower()
        if lang in DIAGRAM_LANGS:
            return f"[{lang} diagram omitted to save space]"
        return m.group(0)
    return FENCE_RE.sub(swap, text or "")


class ModelCallError(RuntimeError):
    """The model call failed in a way the router can explain and stop on.
    too_large is True when the provider said the request itself was too big
    (HTTP 413), which a smaller request can fix."""
    def __init__(self, message, too_large=False):
        super().__init__(message)
        self.too_large = too_large


def trim_middle(text, limit):
    """Shrink text to about `limit` characters by cutting out the MIDDLE,
    keeping the start (summary, purpose) and the end (verification,
    open questions), which are the most useful parts of these documents."""
    if limit <= 0:
        return ""
    if len(text) <= limit:
        return text
    marker = "\n[...middle omitted to fit the model's size limit...]\n"
    keep = max(limit - len(marker), 0)
    head = int(keep * 0.6)
    tail = keep - head
    return text[:head] + marker + (text[-tail:] if tail else "")


def _first_sentence(text, limit=220):
    text = re.sub(r"\s+", " ", text).strip()
    match = re.match(r"(.+?[.!?])(\s|$)", text)
    return (match.group(1) if match else text)[:limit]


# ---------------------------------------------------------------------------
# Agent: one prompt file, runnable. Knows nothing about any other agent.
# ---------------------------------------------------------------------------

class Agent:
    def __init__(self, agent_id, path, raw):
        self.id = agent_id          # the filename stem -- just a label
        self.path = path
        self.raw = raw
        sections = split_sections(raw)
        role = _first_sentence(sections.get("Role", ""))
        task = _first_sentence(sections.get("Task/Objective", ""), limit=300)
        self.role = role
        self.task = task

    def run(self, project_description, prior_work=None, max_tokens=4096):
        """
        Fill the prompt and call the model. prior_work is a list of
        (agent_id, output) the Router chose to pass along; the agent just
        sees it as earlier material to build on. If the provider says the
        request is too large, retry with less earlier work (60%, then 30%)
        before giving up.
        """
        core = extract_core_sections(self.raw, source_filename=self.path.name)
        filled = fill_placeholders(core, project_description)
        compacted = [(aid, compact_for_handoff(out)) for aid, out in (prior_work or [])]
        scales = (1.0, 0.6, 0.3) if compacted else (1.0,)
        for attempt, scale in enumerate(scales, start=1):
            user_msg = self._build_user_message(filled, compacted, scale)
            try:
                return call_model(filled, user_msg, max_tokens=max_tokens)
            except ModelCallError as e:
                if not e.too_large or attempt == len(scales):
                    raise
                print(f"  [size] the provider said the request was too large; "
                      f"retrying with less earlier work ({int(scales[attempt] * 100)}%).")

    def _build_user_message(self, filled, prior_work, scale):
        user_msg = "Proceed with the task as specified above."
        if not prior_work:
            return user_msg
        intro = (
            "\n\nThe following work was already produced earlier in this "
            "project. Treat it as input where it is relevant.\n\n"
        )
        # Whatever room is left after this agent's own prompt is shared
        # equally among the earlier outputs. 300 chars of slack covers
        # the "### Earlier work" labels.
        room = (INPUT_TOKEN_BUDGET * CHARS_PER_TOKEN
                - len(filled) - len(user_msg) - len(intro) - 300)
        per_output = int(room * scale) // len(prior_work)
        if per_output < 1500:
            print(f"  [size] {self.id}'s own prompt leaves almost no room "
                  f"for earlier work under the {INPUT_TOKEN_BUDGET}-token "
                  f"budget, so none is passed in this time.")
            return user_msg
        blocks = []
        for agent_id, output in prior_work:
            if len(output) > per_output:
                print(f"  [size] trimmed {agent_id}'s earlier output from "
                      f"{len(output)} to ~{per_output} characters to "
                      f"fit the model's size limit.")
                output = trim_middle(output, per_output)
            blocks.append(f"### Earlier work: {agent_id}\n{output}")
        return user_msg + intro + "\n\n".join(blocks)


def discover_agents(prompts_dir=None):
    """One Agent per prompts/*.md that follows the 8-section template.
    A file that doesn't is reported and skipped, not fatal."""
    prompts_dir = Path(prompts_dir) if prompts_dir else PROMPTS_DIR
    md_files = sorted(prompts_dir.glob("*.md"))
    if not md_files:
        raise FileNotFoundError(
            f"\nNo .md files found in {prompts_dir}/. Add your structured "
            f"prompts there first."
        )
    agents = {}
    for path in md_files:
        raw = path.read_text()
        try:
            extract_core_sections(raw, source_filename=path.name)
        except ValueError as e:
            print(f"  [skip] {path.name}: not usable as an agent.{e}")
            continue
        agents[path.stem] = Agent(path.stem, path, raw)
    if not agents:
        raise ValueError("No prompt in prompts/ follows the 8-section template.")
    return agents


def list_agents(agents=None):
    agents = agents if agents is not None else discover_agents()
    print(f"{len(agents)} agent(s) in {PROMPTS_DIR}/:\n")
    for agent_id in sorted(agents):
        a = agents[agent_id]
        print(f"  {agent_id}")
        print(f"    role: {a.role}")
        print(f"    task: {a.task}")
    return agents


def fill_placeholders(text, project_description):
    """
    Generic placeholder rules (no per-prompt knowledge needed):
      INTERACTION_MODE      -> "autonomous" (a script can't pause mid-run)
      names with DESCRIPTION -> the project description
      (both [NAME] and {{NAME}} spellings are recognized)
      everything else        -> "UNKNOWN" (the library's honest 'not given')
    Earlier agents' work reaches an agent through run(prior_work=...),
    not through placeholders.
    """
    def replace(match):
        name = match.group(1) or match.group(2)
        if name == "INTERACTION_MODE":
            return "autonomous"
        if "DESCRIPTION" in name:
            return project_description
        return "UNKNOWN"
    return PLACEHOLDER_RE.sub(replace, text)


def _pace(estimated_tokens):
    """Wait, if needed, so this call stays inside the per-minute token limit."""
    if TPM_LIMIT <= 0:
        return
    now = time.monotonic()
    _usage[:] = [(t, n) for t, n in _usage if now - t < 60]
    while _usage and sum(n for _, n in _usage) + estimated_tokens > TPM_LIMIT:
        oldest_time, _ = _usage[0]
        wait = max(1, int(oldest_time + 60 - time.monotonic()) + 1)
        print(f"  [pace] waiting {wait}s to stay inside the free tier's "
              f"{TPM_LIMIT}-token-per-minute limit...")
        time.sleep(wait)
        _usage.pop(0)            # that usage has now aged out of the minute


def _record_usage(response, system_prompt, user_message, output):
    """Remember what this call cost (the provider's number if it gave one)."""
    used = getattr(getattr(response, "usage", None), "total_tokens", None)
    if not isinstance(used, int):
        used = (len(system_prompt) + len(user_message) + len(output or "")) // CHARS_PER_TOKEN
    _usage.append((time.monotonic(), used))


def call_model(system_prompt, user_message, max_tokens=4096):
    """
    One model call. 429 ("slow down") is retried after a short wait; 413
    ("request too big") can't be fixed by waiting, so it is turned into a
    plain-English ModelCallError the router can stop on cleanly.
    """
    for attempt in range(1, RETRY_LIMIT + 1):
        try:
            _pace((len(system_prompt) + len(user_message)) // CHARS_PER_TOKEN)
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                max_tokens=max_tokens,
            )
            output = response.choices[0].message.content
            _record_usage(response, system_prompt, user_message, output)
            return output
        except Exception as e:
            status = getattr(e, "status_code", None)
            if status == 429 and attempt < RETRY_LIMIT:
                wait = 15 * attempt
                print(f"  [rate limit] model asked us to slow down; waiting "
                      f"{wait}s (try {attempt} of {RETRY_LIMIT})...")
                time.sleep(wait)
                continue
            if status == 413:
                raise ModelCallError(
                    f"The request was too large for the model's per-minute "
                    f"limit (we estimated about "
                    f"{(len(system_prompt) + len(user_message)) // CHARS_PER_TOKEN} "
                    f"tokens). Provider said: {str(e)[:300]}",
                    too_large=True,
                ) from e
            if status == 429:
                raise ModelCallError(
                    "Still rate limited after several waits. Try again in a "
                    "minute, or use a tier with a higher limit."
                ) from e
            raise


# ---------------------------------------------------------------------------
# The Router: the only thing that knows about more than one agent.
# ---------------------------------------------------------------------------

ROUTER_SYSTEM = """You are the Router for a multi-agent software engineering workflow. \
You do not do the work yourself. You decide which specialist agent should run next, \
or whether the work is finished.

You will be given the project description, the roster of available agents (number, \
name, role, task), and the steps completed so far with their outputs. Choose the single best next \
agent. You may choose an agent that already ran if its earlier output needs to be \
redone in light of later work. Only choose DONE if nothing in the roster would \
meaningfully improve the result. Each agent in the roster has a number. Choose by that number; file names do not \
matter.

Reply with ONLY a JSON object, no other text:
{"next": <roster number, or "DONE">, "reason": "<one or two sentences>"}"""


def resolve_agent_choice(choice, agents):
    """Match what the Router named to a real agent id, forgivingly.
    The roster is numbered in sorted order, and a number is the normal answer.
    Models often shorten a long file name ("Ch5" for "Ch5 \u2014 System Modeling
    Structured Prompt"). Tried in order: exact; same ignoring case and
    quotes; the one id that starts with it (whole-word, so "Ch1" never
    matches "Ch10"); the one id that contains it. Returns None if there is no
    match or more than one."""
    choice = choice.strip().strip("\"'`")
    number = re.fullmatch(r"\[?#?(\d+)\]?\.?", choice)
    if number:                                   # "3", "[3]", "#3" -> roster position
        ordered = sorted(agents)
        n = int(number.group(1))
        return ordered[n - 1] if 1 <= n <= len(ordered) else None
    if choice in agents:
        return choice
    low = choice.lower()
    for tier in (
        lambda i: i.lower() == low,
        lambda i: i.lower().startswith(low) and (len(i) == len(low) or not i[len(low)].isalnum()),
        lambda i: low in i.lower(),
    ):
        hits = [i for i in agents if tier(i)]
        if len(hits) == 1:
            return hits[0]
        if len(hits) > 1:
            return None
    return None


def route(project_description, agents, steps):
    """
    One Router decision. steps is [(agent_id, output), ...] so far.
    Returns (next_agent_id_or_None, reason). None means stop.
    """
    ordered = sorted(agents.values(), key=lambda a: a.id)
    roster = "\n".join(
        f"[{n}] {a.id} -- role: {a.role} | task: {a.task}"
        for n, a in enumerate(ordered, start=1)
    )
    if steps:
        # The Router only needs enough of each output to judge it, so it
        # gets a trimmed view, sized to share the request budget.
        room = (INPUT_TOKEN_BUDGET * CHARS_PER_TOKEN
                - len(ROUTER_SYSTEM) - len(roster) - len(project_description) - 600)
        per_step = max(min(2500, room // len(steps)), 400)
        done = "\n\n".join(
            f"[step {i}] {agent_id} output:\n{trim_middle(compact_for_handoff(out), per_step)}"
            for i, (agent_id, out) in enumerate(steps, start=1)
        )
    else:
        done = "(none yet -- choose the first agent)"

    user_msg = (
        f"PROJECT DESCRIPTION:\n{project_description}\n\n"
        f"ROSTER:\n{roster}\n\n"
        f"COMPLETED STEPS:\n{done}\n\n"
        f"Which agent runs next?"
    )
    reply = call_model(ROUTER_SYSTEM, user_msg, max_tokens=1000)

    match = re.search(r"\{.*\}", reply or "", re.DOTALL)
    if not match:
        return None, f"Router reply wasn't JSON, stopping. Reply was: {reply!r}"
    try:
        decision = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None, f"Router reply wasn't valid JSON, stopping. Reply was: {reply!r}"

    choice = str(decision.get("next", "")).strip()
    reason = str(decision.get("reason", "")).strip()
    if choice.upper() == "DONE":
        return None, reason or "Router judged the work complete."
    resolved = resolve_agent_choice(choice, agents) if choice else None
    if resolved is None:
        return None, (f"Router chose \"{choice}\", which isn't in the roster "
                      f"(or matches more than one agent), so stopping. "
                      f"Reason given: {reason}")
    return resolved, reason


# ---------------------------------------------------------------------------
# Saving a run: every agent's output as a file, plus any code as real files
# ---------------------------------------------------------------------------

FENCE_RE = re.compile(r"^```([\w+-]*)[ \t]*\n(.*?)^```[ \t]*$", re.MULTILINE | re.DOTALL)
FILENAME_HINT_RE = re.compile(r"(?<![\w./-])([\w-]+(?:\.[\w-]+)*\.(?:html|css|js|py))\b", re.IGNORECASE)
# Only these code languages become files; diagrams, tables, shell, etc. do not.
LANG_DEFAULT_FILE = {
    "html": "index.html", "css": "style.css",
    "javascript": "app.js", "js": "app.js", "python": "app.py", "py": "app.py",
}


def _safe_filename(name):
    """Bare file name only: no folders, no '..', nothing odd."""
    name = Path(name).name
    return name if re.fullmatch(r"[\w][\w.-]*", name) else None


def extract_code_files(text):
    """{filename: code} for html/css/js/python code blocks in an agent's output.
    A file name is taken from the line just above the block or the first line
    inside it (for example '### index.html' or '<!-- index.html -->'); if
    there is none, the language picks a default (index.html, style.css, ...)."""
    files = {}
    lines_before = text
    for m in FENCE_RE.finditer(text):
        lang = m.group(1).lower()
        if lang not in LANG_DEFAULT_FILE:
            continue
        code = m.group(2).rstrip("\n") + "\n"
        above = lines_before[:m.start()].rstrip().splitlines()[-1:] or [""]
        # Comment lines at the top of the block often name the file, e.g.
        # "// water.js" or " * @file validator.js". Only comment lines count, so
        # an import line that mentions another file is never mistaken for a name.
        top_comments = [ln[:120] for ln in code.splitlines()[:6]
                        if re.match(r"\s*(?:/\*+|\*|//|#|<!--)", ln)]
        name = None
        for candidate in [above[0][-120:]] + top_comments:
            hint = FILENAME_HINT_RE.search(candidate)
            if hint and _safe_filename(hint.group(1)):
                name = _safe_filename(hint.group(1))
                break
        if name is None:
            name = LANG_DEFAULT_FILE[lang]
            stem, dot, ext = name.partition(".")
            n = 2
            while name in files:
                name = f"{stem}_{n}.{ext}"
                n += 1
        files[name] = code
    return files


def save_run(steps, out_root=None):
    """Write every step's output as markdown and any code as real files.
    Returns (run_dir, [code file paths]). Later steps overwrite earlier code
    files of the same name, so the freshest version wins."""
    out_root = Path(out_root) if out_root else OUTPUT_DIR
    run_dir = out_root / time.strftime("%Y%m%d-%H%M%S")
    app_dir = run_dir / "app"
    run_dir.mkdir(parents=True, exist_ok=True)
    code_paths = {}
    for i, (agent_id, output) in enumerate(steps, start=1):
        label = re.sub(r"[^\w.-]+", "_", agent_id).strip("_") or "agent"
        (run_dir / f"{i:02d}_{label}.md").write_text(output or "", encoding="utf-8")
        for name, code in extract_code_files(output or "").items():
            app_dir.mkdir(exist_ok=True)
            (app_dir / name).write_text(code, encoding="utf-8")
            code_paths[name] = app_dir / name
    return run_dir, sorted(code_paths.values())


def _run_router(project_description, starting_agent=None, max_steps=MAX_STEPS,
                save_outputs=True):
    """
    Conductor loop. starting_agent (an id) skips the first Router decision;
    otherwise the Router picks the first agent too.
    """
    print("Scanning prompts/ ...")
    agents = discover_agents()
    list_agents(agents)

    steps = []   # [(agent_id, output)] in execution order, repeats allowed
    latest = {}  # agent_id -> most recent output (what gets passed forward)

    if starting_agent and starting_agent not in agents:
        raise ValueError(f"starting_agent \"{starting_agent}\" isn't in prompts/.")

    current = None
    try:
        if starting_agent:
            current, reason = starting_agent, "explicit starting agent"
        else:
            current, reason = route(project_description, agents, steps)
        print(f"\n[route] first agent: {current}  -- {reason}\n")

        while current and len(steps) < max_steps:
            n = len(steps) + 1
            agent = agents[current]
            prior = list(latest.items())

            print("=" * 70)
            print(f"STEP {n} (max {max_steps})  --  {current}")
            print(f"Prompt: prompts/{agent.path.name}")
            if prior:
                print(f"Earlier work passed in from: {', '.join(k for k, _ in prior)}")
            print("=" * 70)

            output = agent.run(project_description, prior_work=prior)
            steps.append((current, output))
            latest[current] = output

            print(f"\n--- Result from {current} ---")
            print(output)

            if len(steps) >= max_steps:
                break
            current, reason = route(project_description, agents, steps)
            print(f"\n[route] next: {current or 'DONE'}  -- {reason}\n")
    except ModelCallError as e:
        # Stop here, but keep and show everything that already finished.
        print(f"\n[stop] The run ended early: {e}")
        print(f"       {len(steps)} step(s) completed before this; they are "
              f"shown in the summary below.")
        current = None

    if current and len(steps) >= max_steps:
        print(f"[stop] Reached the {max_steps}-step limit. Raise max_steps if "
              f"a longer back-and-forth is expected.")

    print("\n" + "=" * 70)
    print("GUARDRAILS SUMMARY")
    print("=" * 70)
    summary = "\n\n".join(
        f"{agent_id.upper()} (step {i}):\n{out}"
        for i, (agent_id, out) in enumerate(steps, start=1)
    )
    print(summary)

    run_dir, code_files = None, []
    if save_outputs and steps:
        try:
            run_dir, code_files = save_run(steps)
            print("\n" + "=" * 70)
            print(f"SAVED to {run_dir}")
            for i, (agent_id, _) in enumerate(steps, start=1):
                print(f"  step {i}: {agent_id}")
            if code_files:
                print("Code files written to " + str(code_files[0].parent) + ":")
                for p in code_files:
                    print(f"  {p.name}")
                index = next((p for p in code_files if p.name == "index.html"), None)
                if index:
                    print(f"\nOpen this in your browser:  {index}")
            else:
                print("(No html/css/js/python code blocks found in the outputs.)")
        except OSError as e:
            print(f"\n[warn] Could not save the run to disk: {e}")
    return {"steps": steps, "latest": latest, "summary": summary,
            "run_dir": run_dir, "code_files": code_files}


class _Tee:
    """Copies everything printed to the screen so it can also be saved."""
    def __init__(self, real):
        self.real, self.parts = real, []
    def write(self, text):
        self.parts.append(text)
        return self.real.write(text)
    def flush(self):
        self.real.flush()
    def __getattr__(self, name):
        return getattr(self.real, name)


def run_router(project_description, starting_agent=None, max_steps=MAX_STEPS,
               save_outputs=True):
    """Run the whole workflow (see _run_router) and also save everything shown
    on screen to run.log inside the run's output folder."""
    real = sys.stdout
    tee = _Tee(real)
    sys.stdout = tee
    try:
        result = _run_router(project_description, starting_agent, max_steps, save_outputs)
    finally:
        sys.stdout = real
    if result.get("run_dir"):
        try:
            (result["run_dir"] / "run.log").write_text("".join(tee.parts), encoding="utf-8")
        except OSError as e:
            print(f"[warn] Could not save run.log: {e}")
    return result


DEFAULT_BRIEF_FILE = "project.md"
BRIEF_WARN_CHARS = 4000   # the brief goes into every model call, so keep it short


def load_project_brief(arg=None, base_dir=None):
    """The project description comes from a brief file, not from the code.
      arg is a path to a file  -> that file's text is the brief
      arg is any other text    -> that text is the brief
      arg is None              -> project.md in the project folder
    Raises ValueError with a plain-English message if there is no usable brief."""
    base = Path(base_dir) if base_dir else Path(__file__).parent
    if arg:
        candidate = Path(arg)
        if not candidate.is_absolute() and not candidate.exists():
            candidate = base / arg
        if candidate.is_file():
            text = candidate.read_text(encoding="utf-8").strip()
            source = str(candidate)
        else:
            text, source = arg.strip(), "command line"
    else:
        candidate = base / DEFAULT_BRIEF_FILE
        if not candidate.is_file():
            raise ValueError(
                f"No project brief found. Create {DEFAULT_BRIEF_FILE} describing "
                f"the app you want, or run: python prompt_router.py <brief-file>")
        text, source = candidate.read_text(encoding="utf-8").strip(), str(candidate)
    if not text:
        raise ValueError(f"The project brief ({source}) is empty.")
    if len(text) > BRIEF_WARN_CHARS:
        print(f"[warn] The brief is {len(text)} characters. It is sent with every "
              f"model call, so a long brief leaves less room for earlier work.")
    print(f"Project brief: {source}")
    return text


if __name__ == "__main__":
    # Usage:
    #   python prompt_router.py                 uses project.md in this folder
    #   python prompt_router.py my_brief.md     uses that file
    #   python prompt_router.py "short text"    uses the text itself
    try:
        brief = load_project_brief(sys.argv[1] if len(sys.argv) > 1 else None)
    except ValueError as e:
        sys.exit(str(e))
    run_router(brief)
