# Structured Prompting as a Software Process Model

## The core idea

In Chapter 2, Sommerville draws a distinction between a **software process** (the actual set of activities a team performs) and a **software process model** (an abstract representation — waterfall, incremental, reuse-oriented — that describes how those activities are organized).

The same distinction applies to prompting an AI coding assistant.

- **Prompting techniques** (chain-of-thought, ReAct, Tree of Thoughts, Reflexion, etc.) are **process activities** — individual moves you make to get better reasoning, better iteration, or better self-checking out of the model.
- The **8-part structured prompt template** is the **process model** — the overall scaffold that organizes *when* and *how* those activities get invoked, and *in what order*, for a given task.

No single prompting technique is universally "best," in the same way no single software process model (waterfall, incremental, reuse-oriented) is universally best. The skill is **selecting and combining techniques to fit the task** — exactly the judgment call Sommerville describes for process models.

> **Key framing:** You are not choosing *a* prompting technique. You are designing a *process* for how the AI should approach the work, and techniques like CoT or ReAct are activities you select and place inside that process — most often inside the **Process** section of your structured prompt.

---

## Prompt content techniques (what to say)

These shape the *content and reasoning style* of a single prompt response.

| Technique | What it does | When to use it |
|---|---|---|
| **Zero-shot** | No examples, no scaffolding — a direct ask. | Quick exploration, throwaway scripts. The prompting equivalent of skipping process entirely. |
| **Few-shot** | Provide input/output examples before the real task, so the model generalizes the pattern. | Enforcing a consistent format, style, or output shape. |
| **Chain-of-thought (CoT)** | Ask the model to reason step-by-step before answering. | Any task with a non-obvious logic path — debugging, algorithm design. |
| **Tree of Thoughts (ToT)** | Explore multiple reasoning branches in parallel, evaluate, and prune before committing. | Comparing design alternatives before picking one. |
| **Role-based** | Frame the model as a specific persona ("senior engineer," "security reviewer") to set a standard of output. | Setting quality expectations, review-style tasks. |

## Prompt process techniques (how to proceed across steps)

These shape *iteration, action, and self-correction* — closer to a real software process than a single response.

| Technique | What it does | Sommerville parallel |
|---|---|---|
| **ReAct** (Reason + Act) | Interleave reasoning with real actions (read a file, run a test, call a tool), observing results and adjusting. | Incremental development — plan, build a bit, check, adjust. |
| **Reflexion / self-critique** | Generate an answer, critique it against requirements, then revise. | Validation and verification (V&V). |
| **Least-to-most prompting** | Break a complex problem into an ordered sequence of simpler subproblems, solved in order. | Incremental delivery — highest-priority pieces first. |
| **Retrieval-augmented prompting (RAG-style)** | Ground the prompt in retrieved context — existing code, docs, data — rather than the model's unaided memory. | Requirements elicitation grounded in the real, existing system. |
| **Multi-agent / role-decomposition** | Split responsibilities across multiple prompts or agents (planner, coder, reviewer) that pass work to each other. | "Roles" in process descriptions — different responsibilities, different people (or agents). |
| **Incremental disclosure** | Present one core idea or output at a time; flag related concepts in a single line without expanding them; wait for explicit direction before continuing to a flagged tangent. | Incremental delivery — one increment delivered, evaluated by the user, before the next proceeds; requirements for later increments stay open until asked for. |

---

## Full comparison table

| Technique | Category | Solves | Sommerville parallel |
|---|---|---|---|
| Zero-shot | Content | Baseline — nothing | No process |
| Few-shot | Content | Output consistency | Product/format specification |
| Chain-of-thought | Content | Reasoning transparency | — |
| Tree of Thoughts | Content | Exploring design alternatives | Design activities |
| Role-based | Content | Standard of output | Roles |
| ReAct | Process | Iterative execution with real feedback | Incremental development |
| Reflexion | Process | Self-checking against spec | Validation / V&V |
| Least-to-most | Process | Breaking scope into stages | Incremental delivery |
| RAG-style | Process | Grounding in real context | Requirements elicitation |
| Multi-agent / roles | Process | Dividing responsibilities | Roles (process descriptions) |
| Incremental disclosure | Process | Preventing conversational scope creep / sidetracking | Incremental delivery |

---

## Where the structured prompt template fits

https://www.isophist.com/p/is-structured-prompting-dead 

The **8-part structured prompt** (Role, Context, Task, Requirements, Constraints, Process, Output, Verification) is the process model that organizes all of the above. Specifically:

- **Role** and **Context** set up the frame the model operates in — comparable to defining project scope and stakeholders before process activities begin.
- **Task** and **Requirements** are direct analogs of Sommerville's **specification** activity.
- **Constraints** narrows the design space — comparable to non-functional requirements shaping **design** activities.
- **Process** is where you actively select techniques: "reason step-by-step" (CoT), "work incrementally and verify after each step" (ReAct/least-to-most), "check your work against the requirements before finishing" (Reflexion), "review the existing codebase first" (RAG-style), "deliver one idea at a time and wait before expanding on related ones" (incremental disclosure).
- **Output** defines the deliverable shape — the **product** of the process.
- **Verification** is explicit **validation** — how we'll know the result actually meets the requirements.

Just as a real project might blend waterfall's discipline with incremental development's adaptability, a single structured prompt often blends techniques: CoT reasoning inside a ReAct loop, with a Reflexion pass before final output. The template doesn't lock you into one technique — it gives you a place to deliberately choose.

---

## Discussion

> Sommerville says: *"There are no right or wrong software processes."* Is the same true of prompting techniques? What determines the right technique (or combination) for a given task — and how is that decision similar to (or different from) a real engineering team choosing between waterfall, incremental, and reuse-oriented development?
