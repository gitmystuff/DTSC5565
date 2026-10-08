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
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MODEL = "openai/gpt-oss-120b"
PROMPTS_DIR = Path(__file__).parent / "prompts"

# Hard cap on total agent executions per run. An agent may legitimately run
# more than once (the Router can send work back to an earlier agent), so
# this -- not "each agent once" -- is what prevents endless loops.
MAX_STEPS = 8

# Prior outputs are passed forward whole, but capped so a long chain can't
# blow the model's context window. Raise if outputs are getting cut off.
PRIOR_OUTPUT_CHAR_LIMIT = 12000

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

PLACEHOLDER_RE = re.compile(r"\{\{([A-Z0-9_]+)\}\}")


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
        sees it as earlier material to build on.
        """
        core = extract_core_sections(self.raw, source_filename=self.path.name)
        filled = fill_placeholders(core, project_description)
        user_msg = "Proceed with the task as specified above."
        if prior_work:
            blocks = []
            for agent_id, output in prior_work:
                if len(output) > PRIOR_OUTPUT_CHAR_LIMIT:
                    output = output[:PRIOR_OUTPUT_CHAR_LIMIT] + "\n[...truncated...]"
                blocks.append(f"### Earlier work: {agent_id}\n{output}")
            user_msg += (
                "\n\nThe following work was already produced earlier in this "
                "project. Treat it as input where it is relevant.\n\n"
                + "\n\n".join(blocks)
            )
        return call_model(filled, user_msg, max_tokens=max_tokens)


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
      everything else        -> "UNKNOWN" (the library's honest 'not given')
    Earlier agents' work reaches an agent through run(prior_work=...),
    not through placeholders.
    """
    def replace(match):
        name = match.group(1)
        if name == "INTERACTION_MODE":
            return "autonomous"
        if "DESCRIPTION" in name:
            return project_description
        return "UNKNOWN"
    return PLACEHOLDER_RE.sub(replace, text)


def call_model(system_prompt, user_message, max_tokens=4096):
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content


# ---------------------------------------------------------------------------
# The Router: the only thing that knows about more than one agent.
# ---------------------------------------------------------------------------

ROUTER_SYSTEM = """You are the Router for a multi-agent software engineering workflow. \
You do not do the work yourself. You decide which specialist agent should run next, \
or whether the work is finished.

You will be given the project description, the roster of available agents (id, role, \
task), and the steps completed so far with their outputs. Choose the single best next \
agent. You may choose an agent that already ran if its earlier output needs to be \
redone in light of later work. Only choose DONE if nothing in the roster would \
meaningfully improve the result. Only choose ids that appear in the roster.

Reply with ONLY a JSON object, no other text:
{"next": "<agent id or DONE>", "reason": "<one or two sentences>"}"""


def route(project_description, agents, steps):
    """
    One Router decision. steps is [(agent_id, output), ...] so far.
    Returns (next_agent_id_or_None, reason). None means stop.
    """
    roster = "\n".join(
        f"- {a.id}: role = {a.role} | task = {a.task}"
        for a in sorted(agents.values(), key=lambda a: a.id)
    )
    if steps:
        done = "\n\n".join(
            f"[step {i}] {agent_id} output:\n{out[:3000]}"
            + ("\n[...truncated for routing...]" if len(out) > 3000 else "")
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
    if choice not in agents:
        return None, (f"Router chose \"{choice}\", which isn't in the roster, "
                      f"so stopping. Reason given: {reason}")
    return choice, reason


def run_router(project_description, starting_agent=None, max_steps=MAX_STEPS):
    """
    Conductor loop. starting_agent (an id) skips the first Router decision;
    otherwise the Router picks the first agent too.
    """
    print("Scanning prompts/ ...")
    agents = discover_agents()
    list_agents(agents)

    steps = []   # [(agent_id, output)] in execution order, repeats allowed
    latest = {}  # agent_id -> most recent output (what gets passed forward)

    if starting_agent:
        if starting_agent not in agents:
            raise ValueError(f"starting_agent \"{starting_agent}\" isn't in prompts/.")
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
    return {"steps": steps, "latest": latest, "summary": summary}


if __name__ == "__main__":
    project_description = (
        "A small team is building a mobile app that lets users log daily "
        "water intake and get reminders. They expect a few thousand users, "
        "want to iterate quickly based on user feedback, and have no "
        "strict security or safety requirements."
    )
    run_router(project_description)
