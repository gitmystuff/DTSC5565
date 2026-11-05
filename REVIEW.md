# Talking Points: Where We Are and Where We're Going
**CSCE 5565 · Thursday Nov 5 · Review of Modules 1–9 as teams begin the final project app**

> How to use this: each section has (1) the idea in one breath, (2) what to say, (3) a question for the room, and (4) what it means for the team project. Items marked **[added]** are my suggestions, not on your slides. Chapters 8 and 9 are one section because your deck blends them.
>
> Suggested pacing if you want a ~35-minute review: Big picture 5 · Mod 1–2 5 · Mod 3 4 · Mod 4 6 · Mod 5–6 6 · Mod 7 4 · Mod 8–9 6 · Close 3. Cut the "question for the room" lines to shorten.

---

## 0. The big picture (open with this)

**One breath:** We've spent the semester learning a process, one chapter at a time, and encoding each piece as a structured prompt. Now we use that process on a real app.

**Say:**
- Each chapter is one **phase**: process → agile practice → requirements → models → architecture → design/implementation → testing → evolution.
- Each phase has an **input** (what it needs from earlier phases) and an **output** (what it hands to the next). A phase's post-condition is the next phase's pre-condition. That's what lets a router chain prompts together.
- The router (`se-agent`) is an **assistant**. It drafts; people decide and are accountable.
- Our recurring lesson: *a strong prompt reduces the chance of a bad outcome; it does not replace checking the output.* Prompting is risk reduction, not risk elimination.

**Ask:** "Which step do people most often skip when an AI hands them something that looks finished?" (Answer you've modeled: Verification.)

**For the project:** the repo's `docs/TEAM_PROJECT_GUIDE.md` walks the same phases; the workbook is the fill-in version.

---

## 1. Module 1: Introduction (Ch 1)

**One breath:** Software engineering is a discipline, not just coding: it's about building software that is maintainable, dependable and trustworthy.

**Say:**
- Notebook-you vs production-you (Lab 1, the Iris classifier): same logic, but one version is something you'd hand to a teammate or deploy.
- The Sommerville attributes of good software: acceptability, dependability and security, efficiency, maintainability. The lab ties the exercise to **maintainability** and **dependability**.
- The core software process activities appear here first: specification → development → validation → evolution. Everything after this module zooms into one of them.
- Vibe coding: where it works, where it doesn't (see the "Grounding Vibe Coding in Software Engineering for Data Scientists" paper in Module 1).

**Ask:** "What did you trust more in Lab 1, the notebook or the tested modules, and why?"

**For the project:** the team must be able to hand its app to a stranger. That's the whole definition of "maintainable."

---

## 2. Module 2: Software processes (Ch 2)

**One breath:** A *process model* (waterfall, incremental, reuse-oriented) is an abstract scaffold; the *process* is what the team actually does. Prompting works the same way.

**Say:**
- Sommerville: "There are no right or wrong software processes." The skill is choosing and combining, using named factors (requirements stability, criticality, team distribution, reuse base, delivery tolerance).
- **Prompting techniques are activities; the 8-part template is the process model.**
  - Content techniques: zero-shot, few-shot, chain-of-thought, tree of thoughts, role-based.
  - Process techniques: ReAct (≈ incremental development), Reflexion (≈ V&V), least-to-most (≈ incremental delivery), RAG-style grounding (≈ requirements from the real system), multi-agent roles, incremental disclosure.
- The 8 sections and what they correspond to: Role/Context (scope and stakeholders), Task/Requirements (specification), Constraints (design limits), Process (where you pick techniques), Output Format (the product), Verification (validation).
- **Pre- and post-conditions are the router's type system:** each stage's post-condition becomes the next stage's pre-condition, stated as *checkable* propositions ("all requirements have a verification method," not "requirements are good").
- Design rule: *agents don't know other agents exist.* A prompt needs only the 8 sections; the router handles ordering.

**Ask:** "Is there a 'right' prompting technique, or does it depend on the task? How is that like choosing waterfall vs incremental?"

**For the project:** teams write down their chosen process and *why*, in their charter (Phase 0).

---

## 3. Module 3: Agile (Ch 3)

**One breath:** Agile exists because requirements change and customers only know what they want after they've seen working software.

**Say:**
- The manifesto: individuals/interactions, working software, customer collaboration, responding to change (over the items on the right).
- Five principles: customer involvement, incremental delivery, people not process, embrace change, maintain simplicity.
- **Plan-driven vs agile** is decided by factors, not ideology: need for a detailed spec up front, feedback speed, team size/location, system type, lifetime, tooling, team organization, culture, skill, regulation. Agile struggles with safety-critical and heavily regulated systems (a preview of Ch 12–13).
- **XP:** user stories → tasks, small releases, simple design, **test-first**, refactoring, pair programming, collective ownership, continuous integration, sustainable pace, on-site customer.
- **Scrum:** product backlog, sprints (2–4 weeks), daily stand-up, Scrum Master (shields the team, not a traditional manager), review and demo.
- **Agile and maintenance:** the risk of informal requirements is that nobody can reconstruct intent later.
- **From your library:** "Who performs each practice?" XP assumes humans. An agent can write the failing test first or draft acceptance criteria, but it **cannot hold authority over priority or be accountable for accepting a release.** Ch 3 is allowed to tell Ch 2 it was wrong (`SPECTRUM_MISMATCH`).
- Vibe coding: agile without discipline, or no process at all? (Your prompt is required to say the second.)

**Testing & ownership (your Module 3 deck) — tell the story:**
- You asked for one test per task, got far more, accepted it anyway, and it became over everyone's head. The failure wasn't the AI; it was **skipping Verification**.
- How to own a failure: state it plainly, name the exact skipped step, connect it to real practice, show the artifact, say a *checkable* change.
- A test is **verification, specification, and documentation.**
- FIRST: Fast, Independent, Repeatable, Self-validating, Timely (+ Proportionate in your deck). Arrange–Act–Assert. Files named `test_*.py` or pytest finds nothing and says nothing.

**Ask:** "Which XP practice can a four-person student team realistically do, and which can't it? Who plays the customer?"

**For the project:** stories, a sprint plan, a definition of done, and a named person accountable for accepting each AI-drafted artifact. Decide now who plays the customer.

---

## 4. Module 4: Requirements engineering (Ch 4)

**One breath:** Requirements say what the system must do and the constraints it must satisfy. Getting them wrong is the most expensive mistake, because every later phase builds faithfully on them.

**Say:**
- **User vs system requirements**; **functional vs non-functional**. NFRs apply to the whole system and are often more critical. Write them **quantitatively** ("fewer than 2 errors per hour after 4 hours of training," not "easy to use").
- NFR types: product (performance, reliability, security, usability), organizational, external (regulatory, ethical, privacy).
- The **SRS**: IEEE-style structure (preface, introduction, glossary, user requirements, architecture, system requirements, models, evolution, appendices). In agile, user stories may replace a heavy SRS, but a short record of business and dependability requirements is still valuable.
- Writing: standard format, **"shall"** for mandatory, **"should"** for desirable, avoid jargon, give each a **rationale**; structured specifications (function, inputs, outputs, pre/post-conditions).
- The RE process is iterative: feasibility → elicitation & analysis → specification → validation.
- Elicitation techniques and their limits: interviews (miss obvious/political knowledge), scenarios (only cover imagined paths), use cases (weak on NFRs), ethnography (finds how people *actually* work).
- Validation: validity, consistency, completeness, realism, **verifiability**. Fixing a requirements error is far more expensive than fixing a coding error.
- Management: unique IDs, change control, **traceability**.
- **From your library, the key honesty point:** an agent cannot interview, observe, or hear the unsaid. It doesn't refuse; it answers beautifully *from nothing.* Every test passes and the wrong system ships (failure mode #1: "you built the wrong thing").
- The mechanism: label every requirement **GIVEN / DERIVED / PROPOSED / DOMAIN-ASSUMED** and report a `confirmed_fraction` up front. A mostly-PROPOSED spec must say so. The agent also produces **interview questions and scenario drafts** for a human to go ask.
- Expect: labels drift optimistic; NFR sweeps skip organizational and ethical needs; domain assumptions are confidently wrong.

**Ask:** "If an AI can't interview or observe, is 'requirements engineering' even the right name for what it does? What should we call it?"

**For the project:** the Product Owner must actually talk to the "customer" (you). Teams keep provenance labels on their requirements and say how many are confirmed. Every NFR names a measurable threshold **[added: and a runtime signal; see observability below]**.

---

## 5. Module 5: System modeling (Ch 5)

**One breath:** A model is a deliberately simplified view of a system. Different models answer different questions.

**Say:**
- Four perspectives: **context** (what's outside), **interaction**, **structural**, **behavioral**.
- UML's five key diagrams: activity, use case, sequence, class, state.
- Three uses of models: to discuss (can be incomplete, the norm in agile), to document (needn't be complete but must be correct), to specify for code generation (must be complete and correct).
- **Context models** decide the system boundary, which is a design choice with social and organizational causes, not a neutral fact. Pair with activity diagrams for business processes.
- **Interaction:** use cases (actors + system) and sequence diagrams (read top to bottom, lifelines, `alt` boxes). They complement each other: a use case's detail often lives in a sequence diagram.
- **Structural:** class diagrams (classes, attributes, operations, associations, multiplicity), generalization (inheritance), aggregation.
- **Behavioral:** data-driven (activity diagrams, formerly DFDs) vs event-driven (state diagrams; e.g. the microwave oven).
- **Model-driven engineering:** models as the main output, CIM → PIM → PSM → code; executable UML. Real successes at large firms, but an uneasy fit with agile.

**Ask:** "What would be the system boundary of a water tracker? Is the phone's clock inside or outside?"

**For the project:** a context model, a use case with a sequence diagram for the main flow, a class model, and a state diagram if the app has modes. Models must agree with the requirements and each other **[added: have teams list one inconsistency they found]**.

---

## 6. Module 6: Architectural design (Ch 6)

**One breath:** Architecture is how the system is organized into components. It's the dominant influence on non-functional requirements, and it's the link between requirements and design.

**Say:**
- Why it matters (Bass et al.): stakeholder communication, system analysis (can the critical requirements even be met?), and large-scale reuse.
- Architecture "in the small" (one program) vs "in the large" (systems of systems).
- **Nine decisions** (a set of choices, not a sequence): generic architecture? distribution? patterns? fundamental structure? decomposition? control strategy? NFR fit? evaluation? documentation?
- **NFRs shape structure and they conflict:**
  - performance → fewer, larger, co-located components;
  - security → layered with critical assets innermost;
  - safety → isolate safety-related operations;
  - availability → redundancy;
  - maintainability → small, self-contained components, producers separate from consumers.
- **Views:** Kruchten's 4+1 (logical, process, development, physical, plus scenarios) and the conceptual view. No single diagram shows everything. Notation is a live debate: block diagrams are informal; UML can be too close to implementation.
- **Patterns** (each with name, description, example, when to use, advantages/disadvantages): **MVC, Layered, Repository, Client-Server, Pipe-and-Filter.**
- **Application architectures:** transaction processing, information systems, language processing.

**Ask:** "A water tracker with an AI-generated summary: which NFRs pull in different directions, and what pattern does each push you toward?"

**For the project:** pick a pattern *because of* named NFRs, write a short decisions log, and say what each rejected alternative would have cost. If the app calls an AI service, show where, what happens when it fails, and cost per use.

---

## 7. Module 7: Design and implementation (Ch 7)

**One breath:** Design and implementation are interleaved. Design identifies components and their relationships; implementation realizes them. Ch 7 also covers the practical issues programming books skip.

**Say:**
- The OO design process: understand context → design architecture → identify objects → develop models → specify interfaces. Not a clean sequence: propose, refine, revisit.
- Finding objects: grammatical analysis (nouns/verbs), tangible domain entities, scenario-based analysis. In practice, combine them.
- **Interface specification** lets teams work in parallel; no data representation details, so the representation can change. One object can offer several interfaces.
- **Design patterns:** Name, Problem, Solution, Consequences. Example: **Observer** (separates display from state; minimal coupling, but may cause unnecessary updates). Others: Façade, Iterator, Decorator. Benefit: shared vocabulary. Challenge: you often recognize the pattern *after* hitting the problem, and experience matters.
- **Reuse levels:** abstraction (patterns), object, component, system (COTS). Benefits vs costs (searching, assessing, adapting, integrating, conflicting assumptions).
- **Configuration management:** version management, system integration, problem tracking. For us: Git, pull requests, issues.
- **Host-target development** (develop on one machine, run on another).
- **Open source and licensing:** GPL (reciprocal), LGPL, BSD (non-reciprocal). "Free to read" ≠ "free to do anything."
- From your Reading a Router Run notes: the router picked its own agents, passed work without agents knowing, and sent one back to redo its work. Reading the run log critically is part of the skill.

**Ask:** "You fork a repo with no license. What are you allowed to do?" (Nice tie-in to our repo's MIT license.)

**For the project:** separate logic from display, use branches and reviewed PRs, check the license of anything reused, and design the interfaces first so teammates can work in parallel.

---

## 8. Modules 8–9: Testing and evolution as one loop (Ch 8–9)

**One breath:** Testing produces the regression suite; evolution consumes it as the safety net for every change. They are one loop, not two chapters.

### Testing (Ch 8)
- **Two goals:** validation testing (show it meets requirements) and defect testing (find where it doesn't). Dijkstra: tests show the presence of defects, never their absence.
- **Verification** = "are we building the product right?" **Validation** = "are we building the right product?" (This is exactly the Ch 4 trap.)
- **Inspections vs testing:** inspections find different defects (errors can't mask each other, work on incomplete code, check standards); informal inspections can find over 60% of defects. Testing finds interactions, timing and performance problems. Neither replaces the other.
- **Three stages:** development testing (the team: unit, component, system), release testing (a separate team, black-box), user testing (alpha, beta, acceptance).
- **Unit tests:** setup → call → assertion; use a framework (pytest) and mocks. **Partitions and boundaries:** group inputs the code treats alike; test boundaries and the midpoint, because failures cluster at boundaries. (Slide example: 4–10 inputs, values 10000–99999.)
- **Component/interface testing:** misuse, misunderstanding, timing errors. **System testing:** integrate incrementally; test emergent behavior, including what the system must *not* do.
- **TDD and regression:** write the test, watch it fail, implement, refactor, all tests pass. Benefits: every segment has a test, the regression suite grows, tests document intent. Limits: you can't test what you don't understand; it's weak for legacy code and multi-threading; it doesn't replace system testing.
- **Release testing:** requirements-based (several tests per requirement, with traceability), scenario testing, performance testing (stress past the limit to check it fails soft).
- **Acceptance:** define criteria early, run, then *negotiate*; few tests pass cleanly.

### Evolution (Ch 9)
- Systems change after delivery and live 10–30+ years. Life cycle: development → **evolution** (significant change) → **servicing** (small, essential changes) → phase-out.
- **Evolution process:** change request → impact analysis → release planning → implementation → release. Ideally spec, design and code change together. **Urgent repairs** skip analysis and leave requirements, design and code inconsistent; flag them for follow-up.
- **Lehman's laws:** continuing change, increasing complexity, declining quality, continuing growth, and others. The theme: structure decays unless you spend effort on it.
- **Maintenance types and cost:** functionality changes (~65%), environmental adaptation (~18%), fault repair (~17%). About two-thirds of IT budgets go to maintenance. It costs more than development because teams disperse, there's no incentive for maintainable code, and structure degrades.
- **Refactoring vs reengineering:** refactoring is continuous, adds no new function, and is safe only with regression tests; reengineering is after-the-fact, same function, better structure, cheaper than replacement.
- **Legacy systems:** quality × business value grid → scrap, maintain, reengineer, or replace; decisions are often political.

### The loop and the prompt view
- Every accepted change needs a test that **fails without it and passes with it.** A change that can't be tested safely loops back to earlier phases.
- Reusable verification checklists: every requirement has a test and a trace; boundaries covered; new tests fail before code exists; expected results stated, not assumed; release tested by someone other than the author.
- **From your end-product document, "why tests aren't enough":** you can build the wrong thing; the environment changes and the code doesn't; combinations of correct components fail; load you didn't test; adversarial input. TDD shrinks the space of surprise. It doesn't eliminate it. A system needs **tests + intent documentation + observability.**
- **The handoff/fix drill:** Team B gets Team A's app with an *unanticipated* defect and must fix it using only A's docs, logs and prompts. That measures whether the process works for a stranger.

**Ask:** "Your AI-written test suite is all green. What three questions do you ask before you believe it?" (Do the tests fail when you break the code? Is each requirement traced to a test? Did anyone outside the team try the app?)

**For the project:** a requirements-to-test map; at least one test you've proved can fail; user testing by someone outside the team; and **one real change request carried out**, with impact analysis, as the evolution exercise.

---

## 9. Where we're going: the team app

**Say (be explicit about this, because it's a shift):**
- Your endgame document says *the product is the process* and the app is evidence. The cold test, an unfamiliar domain run only with what the class built, is what proves the process generalizes.
- A team building an app from the **water-tracker brief** is a *known* domain. It proves the pipeline runs; it doesn't prove generality. **[added]** Decide with students whether there will also be a swapped or cold brief later, and say so now so nobody is surprised.
- Teams run through the **instructor's OpenAI account**: one run per team per sprint, cheap model first, a $2 / 1,000,000-token spending guard per run, requests via the GitHub issue template.
- The router's output is a **first draft.** Teams review it, test it, and own every decision.

**Four things for teams to do this week:**
1. Form teams and assign roles (Product Owner, process lead, architect, quality lead, prompt engineer).
2. Fork the repo, run `uv run pytest` (passes with no key), and read the Team Project Guide.
3. Write the charter: process model and why, definition of done, AI-use rules.
4. Draft the brief (`docs/BRIEF_TEMPLATE.md`), with measurable acceptance criteria.

**Optional (Hugging Face), only after requirements and architecture exist:** a small `transformers` pipeline, speech-to-text, or text-to-speech can be an AI feature, if the team can state its cost, failure behavior, and non-AI fallback. Diffusion models are a stretch goal (GPU, slow, hard to test).

---

## 10. Gaps worth saying out loud **[added]**
- **Safety, security, project management (Ch 12, 13, 22)** are planned in your library but not yet taught. Ch 3 and Ch 6 already say they shape process and architecture, so either give 10 minutes of threat-thinking (assets, trust boundaries, "what could a hostile user type?") before architecture, or tell teams security is deferred.
- **Observability** was a gap in your end-product document, and Ch 4 now requires every NFR to name a runtime signal. Ask teams: "How would you know it failed if nobody told you?"
- **Customer role:** roughly a third of Ch 3 depends on someone available to prioritize and accept. In a student team, that's you, or the Product Owner standing in. Name who it is.

---

## Closing line
> A strong prompt reduces the chance of a bad outcome. It does not replace checking. The product is the process, and the process only counts if a stranger can follow it.
