# Course End Product: A Domain-Agnostic Structured Prompt Library + Router Agent

## Vision

The deliverable for this course is not an application. It is a **reusable, generalizable software engineering process, encoded as prompts**, that can be pointed at *any* software project and reliably produce a well-specified, tested, safe, and secure result — the "Vibe Coding the Sommerville Way" process, operationalized as something an AI agent can execute.

We will build this over the semester and prove it works in the final weeks by handing it an unfamiliar project domain and watching it perform cold.

> **The product is the process.** The application built in Week 13 is evidence, not the deliverable.

---

## What gets built

### 1. A Structured Prompt Library

One prompt per chapter/phase of the Sommerville process, each written as a **generic, parameterized template** — never tied to a specific project domain. Each entry follows the 8-part structured prompt framework (Role, Context, Task, Requirements, Constraints, Process, Output, Verification).

| Chapter | Prompt Purpose | Core Artifact It Produces |
|---|---|---|
| Ch3 — Agile SW Development | Scope a project and select a process model (plan-driven / agile / hybrid) from any one-line project description | Process-model justification |
| Ch4 — Requirements Engineering | Elicit functional + non-functional requirements from a project description | Requirements document |
| Ch5 — System Modeling | Generate appropriate models (use case, class, sequence, activity) from requirements | System models |
| Ch6 — Architectural Design | Propose and justify a system architecture from requirements + models | Architecture design doc |
| Ch7 — Design & Implementation | Implement components using test-first, incremental, and reasoning-transparent techniques | Working code + prompt/reasoning log |
| Ch8 — Software Testing | Generate a test plan and automated test suite from requirements | Test plan + test suite |
| Ch9 — Software Evolution | Handle a change request against an existing system without breaking prior guarantees | Change log + updated artifacts |
| Ch12 — Safety Engineering | Identify hazards, classify risk, derive safety requirements, and generate defensive tests | Hazard log + safety requirements |
| Ch13 — Security Engineering | Identify assets/trust boundaries, enumerate threats (STRIDE-style), propose mitigations with tradeoffs, generate adversarial tests | Threat model + mitigations |
| Ch22 — Project Management | Produce a schedule, risk register, and status reporting structure from project scope | Project plan + risk register |

Each prompt is validated on a **shared, neutral case study** (for example, the iris-classifier repo) throughout the semester — used only as a sanity check, never as "the project." The graded artifact each week is the **prompt itself**: does it generalize, does it follow the framework, does it hold up without silently assuming a domain?

### 2. A Router Agent

A single orchestrating prompt/agent that:

- Determines what phase of development a project is currently in (or is told explicitly)
- Selects the correct prompt from the library for that phase
- Passes forward the relevant context/artifacts from prior phases (e.g., requirements feed into architecture; architecture feeds into implementation)
- Knows when to loop back 

This is where "agents, to get specific" becomes concrete: classify → select → execute → verify → route to next phase or loop back — the same control-flow pattern underlying real agent frameworks and tools like Claude Code's slash-command system.

---

## How it's proven: the cold test (Weeks 13-15)

| Week | Activity |
|---|---|
| 13 | Each team receives (or draws) a **project domain they did not design for** — assigned or swapped between teams. They run their router + full prompt library cold: scope, spec, design, implement, test, secure, and document the project live, using only what they built weeks 3-12. |
| 14-15 | Team presentations: the resulting application, **and** an honest report on where the library/router held up vs. where it broke or needed patching against an unfamiliar domain. |

The Week 13 "break points" are a feature, not a failure — they are direct evidence of the Ch2/CMM idea of process improvement, applied to the our own artifact instead of a hypothetical case study.

---

## The endgame reasoning

- **Generality over polish.** A single finished app can't prove the process is reusable — a cold, unfamiliar test can.
- **The artifact has career value beyond this class.** A structured prompt library + router pattern is directly transferable to real AI-assisted engineering work, "at least for now, considering how things change" — exactly the AI literacy goal for the course.
- **Every chapter earns its place.** Nothing in the 12-chapter sequence is decorative — each one produces a specific, required, reusable piece of the final system.
- **It demonstrates agentic behavior concretely**, rather than describing it abstractly — we will build and watch a routing/selection loop operate on our own work.
- **Orchestration with a router/conductor** maps to an established pattern: this is a multi-agent orchestrator, where the router is the "conductor" agent whose whole job is deciding which specialist agent to invoke next, passing it context, and interpreting its output well enough to route to the next step (or loop back on failure).

---

## Why "Tests Will Catch Everything" Is a Trap

A natural assumption is: if we carefully define what we want (TDD) and write tests for it, failure is solved. It isn't a nd this is the actual crux of the vibe-coding sustainability debate.

An application can't do something outside the behavior you built into it. But failures don't require the app to do something you didn't design — they happen in the gap between what you specified and what actually occurs:

1. **You Built The Wrong Thing.** TDD verifies your code matches your spec. It says nothing about whether your spec matched reality. If a requirement was subtly wrong or incomplete, every test passes and the failure is still there — the tests just confirm you built the mistake correctly.

2. **The environment changes, the code doesn't.** A dependency updates, an API changes its response shape, a certificate expires, a rate limit appears. The tests were correct *at the time they were written* — they test your code, not the world your code depends on.

3. **Combinatorial explosion.** Each component can be individually correct and fully tested, and the *combination* of two correct components under specific timing or ordering still fails (race conditions, deadlocks, cascading retries). Nobody skipped testing A or B — the interaction between them was never in scope.

4. **Load and scale you didn't test at.** Code that passes every functional test can still fail under conditions never simulated — 10x traffic, a slow network, a full disk. Not a logic bug — a resource/environment bug.

5. **Adversarial input.** Tests cover expected input. An attacker's entire job is finding input nobody expected. This is structurally different from "define what you want and test it" — it's defining what you *don't* want, against someone actively searching for the gaps in that definition.

**An honest framing:** TDD shrinks the space of unanticipated failure; it does not eliminate it, because it can only ever test against requirements someone was able to imagine, and reality is larger than anyone's imagination. A team that believes "good tests = no surprises" is *more* exposed when the surprise arrives, because they built no way to see it coming or diagnose it afterward.

### What this means for the end product

Tests alone do not satisfy the "will this fix vibe coding's sustainability problem" bar. The end product needs to demonstrably provide three things, not one:

| Leg | What it does | Where it lives in the course |
|---|---|---|
| **Tests** | Catch known/anticipated failure classes before shipping | Ch8 (testing), plus Ch12/13 adversarial and safety tests |
| **Intent documentation** | Explains *why* a component works the way it does and what it assumes — not just "if X breaks, do Y" (which only covers the anticipated) — so a stranger can reason toward a fix for something nobody predicted | Ch7 (implementation), strengthened as an explicit acceptance criterion, not a formatting nicety |
| **Observability** | Logging, clear error messages, and traceability so an *unanticipated* failure is even visible and diagnosable in the first place — the fallback for residual risk that testing structurally cannot cover | Currently missing — candidate addition to Ch7 or Ch13 |

A system is only fixable by a stranger when all three are present. Vibe coding, as typically practiced, has none of them at production quality. This course's current design gets tests solidly and documentation partially — observability is not yet represented and is a design gap to close before calling the process "solved."

### Proposed validation: the handoff/fix drill

To actually test — not just claim — that the end product solves this, we will add a drill where teams swap not just a project domain but a **working codebase**: Team B receives Team A's app with a deliberately introduced, *unanticipated* failure (not one covered by Team A's own test suite) and must find and fix it using only Team A's documentation, logs, and prompt library — no access to Team A. This directly measures whether the documentation and process let a stranger diagnose and repair a real, unplanned failure, rather than measuring whether the team can navigate its own work.

