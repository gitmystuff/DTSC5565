# Assignment 1
## Setting Up Your AI Engineering Environment & Building Your First Agent + Router

## Overview

This assignment moves you from prompting inside a chat window to writing
code that calls a language model programmatically and lets it take
action. By the end of today's three-hour class, you will have a working
local development environment, a small agent with one tool, and a router
that chooses between two tools and loops until it's ready to answer.

**This is not a one-off assignment.** The code you write today is the
starting point for the project we build for the rest of the semester —
each future assignment adds more tools (and eventually, full structured
prompts from our library) into this same router. Structure it cleanly
now; you'll thank yourself in Week 10.

**Format:** Individual. Everyone implements the same two tools
(`calculate_average` and `check_password_strength`), described below —
this keeps grading consistent and means we can debug together as a class
when something breaks, since everyone's code does the same thing at each
stage.

**Due:** Next week (see course calendar). Today is for getting the core
working in class, with support available; Part 5 (reflection) and any
polish can be finished as homework.

## Learning Objectives

By completing this assignment, you will be able to:

- Set up a reproducible Python development environment using `uv`
- Call an LLM API (Groq) from a Python script
- Define a tool the model can call, using function-calling / tool-use
- Implement a reason → act → observe loop (the mechanism behind
  ReAct-style agents)
- Extend that loop to choose between multiple tools — your first router
- Explain, using your own working code, the difference between a prompt
  and an agent

## Prerequisites

- A Groq API key (see `getting-api-keys-guide.md` from earlier in the
  semester if you haven't set this up yet)
- Git and a GitHub account
- A laptop where you can install software (VS Code, uv)

---

## In-Class Schedule (3 hours)

| Time | Activity |
|---|---|
| 0:00 – 0:20 | Environment setup: VS Code, uv, project init, `.env` |
| 0:20 – 1:10 | Build the single-tool agent (`agent.py`) — live-coded, tested against two prompts |
| 1:10 – 1:20 | Break |
| 1:20 – 2:25 | Build the router (`router.py`) — two tools, looping logic, tested against three prompts |
| 2:25 – 2:45 | Recommended project structure + intro to writing pytest tests for your tools |
| 2:45 – 3:00 | Wrap-up: what's due next week, questions, start on reflection if time allows |

This is a target, not a contract — skill levels vary, so expect to flex
time between the two build sections depending on how the room is doing.

---

## Part 1 — Environment Setup

Follow `vscode-uv-setup-guide.md`. By the end of this part you should have:

- [ ] VS Code installed, with the Python extension
- [ ] `uv` installed and verified (`uv --version` runs)
- [ ] A new project folder initialized with `uv init`
- [ ] Your Groq API key stored in a `.env` file, with `.env` in `.gitignore`

## Part 2 — Your First Agent

Follow `groq-agent-guide.md`. Everyone implements the same tool:

- **Tool:** `calculate_average(scores)` — returns the average of a list
  of numeric scores, rounded to one decimal place

You will:

1. Write a script that sends a basic prompt to Groq and prints the response
2. Define the tool and wire it into the model call
3. Implement the loop that checks whether the model requested a tool
   call, runs it, and sends the result back for a final answer
4. Test with **two prompts**: one that should NOT trigger the tool, and
   one that SHOULD — confirm the model chooses correctly

## Part 3 — Your First Router

Follow `router-guide.md`. Everyone adds the same second tool:

- **Tool:** `check_password_strength(password)` — rates a password
  (weak/moderate/strong) and lists specific issues found

You will:

1. Register **both** tools with the model at once
2. Generalize your single if-check into a loop, so the agent can keep
   acting on multiple tool calls before giving a final answer
3. Test with **three prompts** — one that should route to each tool, and
   one that needs neither

## Part 4 — Project Structure (recommended, start today if time allows)

Since this project continues all semester, organize it now rather than
later:

```
your-agent-project/
├── .env                  # never committed
├── .gitignore
├── pyproject.toml
├── agent.py               # Part 2: single-tool agent
├── router.py               # Part 3: multi-tool router
└── tests/
    └── test_tools.py        # pytest tests for your tool functions
```

Write at least one pytest test for each tool function (not the API call
itself — just `calculate_average` and `check_password_strength` as plain
functions). This is the same test-first discipline from earlier in the
semester, applied to code that now happens to be called by a model
instead of by you directly.

## Part 5 — Reflection (homework, due with the rest of the assignment)

In a short written response (roughly half a page), answer:

- What's the difference between what you built today and a structured
  prompt from earlier in the semester? Where does the line between
  "prompt" and "agent" actually fall in your own code?
- Walk through what happened, step by step, the first time your router
  correctly chose `check_password_strength` over `calculate_average`.
  What did the model actually receive, and what did it send back?
- Your router currently chooses from 2 tools using a plain Python
  dictionary lookup (`available_functions`). What do you expect will get
  harder as more tools are added — and what's one idea for how you'd
  handle that?

## Deliverables

- Your working `agent.py` and `router.py`, pushed to a GitHub repo
  (**do not commit your `.env` file or API key**)
- Your `tests/` folder with at least one test per tool
- A short README explaining how to run your agent and router
- Your written reflection (Part 5)

## Suggested Grading Breakdown

| Component | Weight |
|---|---|
| Environment set up correctly, repo structured cleanly | 15% |
| Agent (Part 2) working correctly | 20% |
| Router (Part 3) correctly routes all three test cases | 30% |
| Tests for both tool functions | 15% |
| Reflection | 20% |

---

## How This Project Grows

This is one repo, reused for the rest of the semester — not a new repo
per assignment. A few things worth deciding now, while the codebase is
still small, rather than discovering them later as a forced rewrite:

- **Keep working in the same project.** Future assignments add to
  `agent.py` and `router.py` (or files that grow out of them) — they
  don't start over. Commit your work at the end of each assignment so
  there's a clean history to look back on.

- **Consider renaming `router.py` sooner rather than later.** Today it's
  a two-tool demo; by the end of the semester it's meant to become the
  actual orchestrator from our course endgame document. Renaming a file
  after ten other files import it is annoying — renaming it now, while
  nothing depends on it yet, is free. `orchestrator.py` is a reasonable
  name if you want to commit to that now; `router.py` is also fine if
  you'd rather decide later. Either way, decide on purpose, not by
  accident.

- **The `tools` list will outgrow living in `router.py` itself.** At two
  tools, keeping the tool descriptions and functions in one file is
  fine. Once you're at five or six, that file gets hard to read. A
  natural next step is splitting tools into their own module (e.g. a
  `tools/` folder, one file per tool, with a small registry that
  collects them into the `tools` list and `available_functions` dict
  your loop already expects). You don't need to do this yet — just
  expect it, so it's a planned refactor and not an emergency one.

- **Not every future "tool" will be a Python function.** The chapter-
  mapped structured prompts from our prompt library (requirements,
  architecture, testing, etc.) are meant to eventually plug into this
  same router — but a structured prompt isn't a function you call, it's
  text you send to the model in a particular way. When that happens,
  `available_functions` as a simple name-to-function dictionary won't be
  enough on its own — the router will need to handle two different kinds
  of "things it can do": call a function, or run a structured prompt.
  That's a real design decision for a later assignment, not something to
  solve today, but it's why the loop in `router.py` was written to be
  generalized rather than hard-coded around exactly two functions.

- **Testing grows alongside the tools.** Every new tool function gets its
  own entry in `tests/test_tools.py`, the same way `calculate_average`
  and `check_password_strength` did today. If a tool stops having a
  test, that's a sign it was added in a hurry — worth going back and
  fixing before it becomes someone else's confusing bug.



1. Is the 3-hour schedule realistic given room size / TA support, or
   should Part 3 (router) start as a live demo I walk through, with
   individual build time only for whatever's left?
2. Should the pytest tests in Part 4 be required for full credit today,
   or explicitly OK to finish as homework given the time crunch?

