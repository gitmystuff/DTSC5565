# Structured Prompt Template

A reusable scaffold for AI-assisted software engineering tasks. Fill in each section for the task at hand — not every section needs to be long, but don't skip one without deciding to skip it on purpose.

This template will be reused and adapted throughout the semester. Different assignments will lean harder on different sections (e.g., a testing-focused exercise will have a heavier **Verification** section; a design exercise will lean on **Constraints** and **Process**).

---

## [Prompt Name / Assignment Reference]
*e.g., "Week 3 — Add confidence-threshold rejection to iris-classifier predict.py"*

### 1. Role
*Who/what standard should the AI operate as? This sets the quality bar and mindset.*

```
You are a [senior software engineer / test engineer / code reviewer / etc.]
working on [type of system]. Prioritize [correctness / readability /
maintainability / performance — pick what matters most for this task].
```

### 2. Context
*Relevant background: existing code, architecture, data, constraints already in place. This is your pre-condition — what's true before the AI starts.*

```
The existing codebase is structured as follows: [describe or paste relevant
files/structure]. The current behavior is: [...]. Relevant prior decisions:
[...].
```

### 3. Task / Objective
*One clear, scoped statement of what is being built or changed. If you can't say it in 1-2 sentences, the scope is probably too big — break it up.*

```
Build/modify [specific thing] so that [specific outcome].
```

### 4. Requirements
*Functional and non-functional requirements, listed explicitly. Don't rely on the AI to infer these.*

```
Functional:
- [The system must do X]
- [The system must do Y]

Non-functional:
- [Performance / security / maintainability expectations]
```

### 5. Constraints
*What NOT to do. Boundaries, tech stack, style rules, things that are off-limits.*

```
- Do not modify [file/module] unless necessary.
- Use [language/library/version].
- Follow [style guide / existing pattern in the codebase].
- Do not introduce new dependencies without flagging them.
```

### 6. Process
*How should the AI approach the work? This is where you select and combine prompting techniques based on the task. Choose deliberately — see the companion comparison doc for options.*

```
[Pick and combine as appropriate:]
- Reason step-by-step before writing code (chain-of-thought).
- Write the test(s) first, then implement to satisfy them (test-first).
- Work incrementally: implement the smallest working version first, verify,
  then extend (least-to-most / incremental).
- If there are multiple viable approaches, briefly list them and justify the
  one you choose before implementing (Tree of Thoughts).
- After producing a solution, check it against the Requirements above and
  revise if anything is missed (Reflexion / self-critique).
- Reference the existing code/context above rather than assuming unstated
  behavior (RAG-style grounding).
- Present one core idea, answer, or output at a time. If something related
  comes up, flag it in a single line without expanding on it. Wait for
  explicit direction before continuing to a flagged item (incremental
  disclosure).
```

### 7. Output Format
*Exact deliverable shape — what files, what structure, what level of documentation.*

```
Deliver:
- [File(s) to create/modify, with paths]
- [Docstrings / comments expected]
- [Any explanation or summary expected alongside the code]
```

### 8. Verification
*How will we know the result is correct? Acceptance criteria, test cases, what "done" looks like.*

```
This is complete when:
- [Specific test(s) pass]
- [Specific behavior is observable/demonstrable]
- [Edge cases handled: ...]
```

---

## Quick-reference: minimal version

For lower-stakes or early-semester exercises, the essential five sections are usually enough:

**Role → Context → Task → Requirements → Verification**

Constraints, Process, and Output Format can be added once students are comfortable with the basics, or included by default once you're working against a real codebase (like the iris-classifier repo) where conventions already exist.

---

## Notes for reuse across the semester

- Keep a running log of which **Process** techniques were selected for each assignment and why — this becomes its own dataset for the "process improvement" discussion (Ch2, CMM) later in the course.
- Encourage students to compare a zero-shot version of a task against the structured version, using this template, to make the value of structure tangible rather than assumed.
- This template is deliberately generic — expect to adapt Requirements/Constraints/Verification most heavily per-assignment, while Role and Process stay relatively stable within a given unit of the course.
