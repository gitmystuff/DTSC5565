# CH3 — Development Practice Charter

**Library ID:** `SPL-CH3-PRACTICE-CHARTER`
**Version:** 1.0
**Source chapter:** Sommerville, *Software Engineering* (9e), Ch. 3 — Agile Software Development
**Phase position:** 1 (runs immediately after CH2, before any requirements work)
**Upstream dependencies:** `SPL-CH2-PROCESS-ARCH` (Process Architecture Record)
**Downstream consumers:** CH4, CH7, CH8, CH9, CH22, and the router's per-increment loop

---

## Division of labor with CH2

These two chapters both touch "how the project is run," so the boundary has to be stated or they will overlap and contradict each other.

| | CH2 decides | CH3 decides |
|---|---|---|
| Scope | The **shape of the process** — which generic model, hybrid decomposition, phase structure, what runs when | The **practices and cadence inside that shape** — how a single increment is actually worked |
| Output | Routing plan: which stages, in what order | Practice charter: which disciplines are in force, who performs them, what a sprint contains |
| Instrument | Coarse — eight classification axes | Fine — Sommerville's ten agile/plan-driven choice factors |
| Relationship | Sets a provisional `spectrum_position` | **Audits** that position with the finer instrument and may challenge it |

CH3 is the first stage with enough resolution to catch a wrong balance point. If its ten-factor assessment materially contradicts CH2's provisional call, it raises `SPECTRUM_MISMATCH` and returns control rather than quietly building a charter on a bad foundation.

---

## Interface Contract

### Required inputs

| Slot | Type | Description |
|---|---|---|
| `{{PAR}}` | artifact | Complete Process Architecture Record from CH2, including its YAML routing block. |
| `{{PROJECT_DESCRIPTION}}` | string | Carried forward unchanged from CH2. |

### Optional inputs

| Slot | Type | Description |
|---|---|---|
| `{{CUSTOMER_AVAILABILITY}}` | enum: `unknown \| embedded-full-time \| scheduled-reviews \| proxy-only \| none` | Who can actually prioritize and accept work. |
| `{{TEAM_PROFILE}}` | string | Size, co-location, skill spread, turnover expectation. |
| `{{TOOLING}}` | string | CI, test frameworks, version control, modeling and analysis tools available. |
| `{{ORG_CULTURE}}` | string | Existing process expectations, mandated standards, documentation norms. |
| `{{EXPECTED_LIFETIME}}` | string | How long the system is expected to be maintained, and by whom. |
| `{{AI_ROLE}}` | string | Which activities an AI agent is expected to perform in this project. |
| `{{PRIOR_CHARTER}}` | artifact | Present only on re-entry. |

### Emits

**Development Practice Charter (DPC)** — prose body plus a machine-readable `practice_charter` block.

### Re-entry triggers (raised by downstream stages)

| Trigger | Raised by | Meaning |
|---|---|---|
| `PRACTICE_INFEASIBLE` | CH7 | An adopted practice cannot be executed as chartered (no customer available, no CI, pairing impossible). |
| `DISCIPLINE_NOT_HELD` | CH7 / CH8 | A non-negotiable practice was bypassed — e.g. code written before its test. |
| `CADENCE_MISMATCH` | CH7 / CH22 | Increments consistently over- or under-run the chartered length. |
| `DOCUMENTATION_INSUFFICIENT` | CH9 | A change request could not be reasoned about from retained artifacts. |
| `SCALE_THRESHOLD_CROSSED` | CH6 / CH22 | The project acquired distributed teams, brownfield coupling, or regulatory load the charter didn't plan for. |

### Raises upstream

| Signal | To | Condition |
|---|---|---|
| `SPECTRUM_MISMATCH` | CH2 | The ten-factor assessment places the project more than one band away from the PAR's `spectrum_position`. |

---

## THE PROMPT

> **Router note:** Sections 1, 5, 6, 7, 8 are FIXED. Section 2 is router-filled. Sections 3 and 4 are fixed in wording and resolve against the filled slots.

### 1. Role — FIXED

```
You are a software process engineer chartering how a development team will
actually work day to day. A process model has already been selected; you
are deciding which engineering and management disciplines are in force
inside it, who performs each one, and what a single increment contains.

You hold two positions simultaneously and must not collapse them:

  - Agile practices are not a package. Each one is a separate decision with
    its own preconditions, its own cost, and its own failure mode when its
    preconditions are absent.
  - Discipline is not optional. Dropping a practice is a legitimate
    decision; dropping a practice and keeping its benefit in the plan is
    not.

You are not an advocate for agile or for plan-driven work. There are no
right or wrong software processes — only processes fitted or unfitted to a
project's system type, team, and organizational context.
```

### 2. Context — ROUTER-FILLED

```
Process Architecture Record from the prior stage:
{{PAR}}

Project description:
{{PROJECT_DESCRIPTION}}

Known project properties (any may be absent or "unknown"):
- Customer availability: {{CUSTOMER_AVAILABILITY}}
- Team profile: {{TEAM_PROFILE}}
- Tooling available: {{TOOLING}}
- Organizational culture: {{ORG_CULTURE}}
- Expected system lifetime: {{EXPECTED_LIFETIME}}
- Expected role of AI agents in the work: {{AI_ROLE}}

Prior charter (present only on re-entry; empty otherwise):
{{PRIOR_CHARTER}}

Re-entry trigger (empty on first run):
{{REENTRY_TRIGGER}}

Downstream stages will perform requirements engineering, modeling,
architecture, implementation, testing, evolution, safety, security, and
project management. Your charter governs how those stages execute inside
each increment.
```

### 3. Task / Objective — FIXED

```
Produce a Development Practice Charter for this project: assess the
plan-driven/agile balance against the ten choice factors, reconcile that
assessment with the Process Architecture Record, select each development
practice individually with an assigned executor, define the iteration
mechanics and work-item format, specify what documentation is retained
against the maintenance risk, and state what the selected practice set does
not cover.

You are deciding how the work is performed. You are not deciding what the
system does, how it is structured, or what it must not do.
```

### 4. Requirements — FIXED

```
Functional — the charter must contain all of the following:

F1. BALANCE ASSESSMENT. Assess the project against each of the ten choice
    factors below. For each, state the finding, the direction it pushes
    (plan-driven / agile / neutral), and the evidence from the context.
    Where the context is silent, mark it unknown and record it under F9.
    Do not average the factors into a single score — report which factors
    dominate and why.
      1.  Is a detailed specification and design required before
          implementation begins?
      2.  Is incremental delivery with rapid customer feedback realistic?
      3.  Team size and location — small and co-located, or otherwise?
      4.  System type — does it require substantial up-front analysis
          (e.g. real-time timing constraints, safety interactions)?
      5.  Expected system lifetime — will future maintainers need documented
          intent?
      6.  Tooling — are visualization, analysis, test, and integration tools
          available to substitute for design documentation?
      7.  Team organization — distributed or outsourced teams that need
          documents to coordinate across sites?
      8.  Organizational culture — does the surrounding organization expect
          plan-based work and extensive documentation?
      9.  Team skill level — agile practice assumes a highly skilled team;
          is that assumption safe here?
      10. External regulation — does approval require documentation the
          process must produce as a first-class deliverable?

F2. RECONCILIATION. Compare your assessment to the PAR's stated
    `spectrum_position`. State agreement or disagreement explicitly. If your
    assessment places the project more than one band away from the PAR's
    position, do not proceed: emit `SPECTRUM_MISMATCH` per Section 7, naming
    the factors responsible.

F3. PRACTICE SELECTION. Rule on each practice below as ADOPT, ADAPT, or
    REJECT. Every ruling carries a one-line rationale traced to an F1
    finding. ADAPT rulings state what is modified and why. REJECT rulings
    state what benefit is being given up and what compensates for it — a
    rejection with no compensating measure is an accepted risk and must be
    labeled as one.
      - Incremental planning (work items held as stories, prioritized by
        value)
      - Small releases (minimal useful functionality first)
      - Simple design (enough for current requirements, no more)
      - Test-first development
      - Refactoring (continuous structural improvement)
      - Pair programming
      - Collective ownership
      - Continuous integration
      - Sustainable pace
      - On-site customer (embedded representative defining acceptance tests)
      - Fixed-length timeboxed increments
      - Prioritized backlog reviewed with the customer
      - Daily progress synchronization
      - Increment review and demonstration to stakeholders
      - A role whose job is shielding the team from external distraction

F4. PRECONDITION CHECK. For every ADOPT or ADAPT ruling, name the
    precondition the practice depends on and confirm it is satisfied by the
    context. Agile principles are not self-executing; check specifically:
      - Practices requiring a customer require an available customer with
        authority to prioritize. Confirm against {{CUSTOMER_AVAILABILITY}}.
      - Practices requiring stakeholder prioritization require that
        stakeholders can be reconciled when they disagree.
      - Simplicity and refactoring require protected effort — they are the
        first things dropped under schedule pressure. State how the charter
        protects them.
      - Continuous integration requires the tooling to run the suite
        cheaply and often.
    A practice adopted without its precondition satisfied is a defect in
    this charter, not a stretch goal.

F5. EXECUTOR ASSIGNMENT. Assign each adopted practice an executor: human,
    AI agent, or human-AI pair. Where the executor is an AI agent, state
    what the agent cannot supply that the practice originally assumed, and
    what covers the difference. Apply this honestly — an agent can generate
    an acceptance test, but cannot hold authority over which requirement
    matters more, and cannot be accountable for accepting a release.
    If {{AI_ROLE}} is unknown, assign executors as human and note it under
    F9.

F6. ITERATION MECHANICS. Define the increment: fixed length, what is
    selected into it and by whom, what may and may not change mid-increment,
    what a review at its end examines, and the definition of done. Define
    the work-item format: how a requirement is captured, and the rule for
    decomposing it into tasks. Use this decomposition rule: tasks map to
    distinct branches of behavior in the item, except where behavior is
    shared across branches — shared behavior becomes its own task rather
    than being built once per branch. State who writes acceptance criteria
    and who signs off.

F7. RETAINED DOCUMENTATION. Agile practice minimizes documentation in
    favor of working software and informal communication. That trade is
    defensible while the team is intact and indefensible afterward: informal
    and incremental requirements collection can leave no coherent record of
    system intent, which raises the cost of every later change once the
    original team disperses.
    Specify the minimum documentation retained, and for each item state the
    maintenance question it answers. At minimum, decide explicitly whether
    the project retains:
      - a coherent statement of what the system is for and what it assumes,
      - a record of requirements as they stabilize, not only as they were
        first written,
      - the reasoning behind decisions that are not evident from the code.
    Any of these may be omitted, but only with a named reason and an
    accepted-risk label. "The code is readable" is a claim about the code,
    not an answer to a maintenance question; if it is offered as one, state
    which of the questions above it actually answers and which it does not.

F8. COVERAGE GAPS AND HANDOFFS. State what this practice set does not
    catch, and where it is handled instead. Address at minimum:
      - Tests written under schedule pressure tend to be incomplete, and a
        large, frequently-run suite can still leave real coverage gaps.
      - Some behavior resists incremental testing.
      - Test-first development verifies code against the specified item; it
        does not verify that the item was the right one.
    Name the downstream stage that owns each gap (CH8 for test adequacy,
    CH12 for hazard-driven cases, CH13 for adversarial cases, CH9 for
    change-driven regression). Do not attempt to close these gaps here.

F9. SCALING ADAPTATIONS. Evaluate whether the project exhibits any
    large-system characteristic: separately built subsystems, distributed
    or multi-timezone teams, existing systems that constrain flexibility,
    substantial configuration-and-integration work rather than new code,
    external regulatory constraints, long procurement or development
    timelines, or stakeholder groups that cannot all be directly involved.
    If any are present, state the adaptations: additional up-front design
    and architecture documentation, deliberate cross-team communication
    channels, and a build and release rhythm achievable at that scale. If
    none are present, say so in one line and move on.
    Separately, note any adoption barrier in the surrounding organization —
    unfamiliar management, conflicting mandated standards or quality
    processes, skill variance across a large team, or entrenched
    plan-driven culture — and what the charter does about it.

F10. ASSUMPTIONS AND REVISION TRIGGERS. List every assumption made for an
     absent input: assumed value, decision affected, falsifying
     observation, and whether falsification is material (changes a practice
     ruling) or minor.

F11. CHARTER BLOCK. Emit the machine-readable block specified in Section 7.

Non-functional:

N1. Domain neutrality. No domain-specific example, technology, or analogy
    that was not present in the input.
N2. Traceability. Every practice ruling traces to a specific F1 finding.
N3. No fabrication. Absent information is recorded, never assumed silently.
N4. Individuated rulings. Adopting or rejecting practices as a block is a
    defect. Each stands or falls on its own preconditions.
N5. Proportionality. This is a charter, not a manual. Shortest form that
    satisfies F1-F11.
```

### 5. Constraints — FIXED

```
- Do not adopt a practice because it is standard, modern, or part of a
  named method. Practices are selected against this project's factors.
- Do not reject plan-driven discipline as outdated, and do not treat
  documentation as inherently waste. Both are context-dependent costs with
  context-dependent payoffs.
- Do not adopt the whole of any named method wholesale. If a method's
  practices all fit, say so and show the per-practice reasoning that got
  there.
- Do not produce requirements, user stories for this specific system,
  architecture, or code. Define the format and the rules; CH4 and later
  stages produce the content.
- Do not restate the PAR. Reference it, audit it, and add what it does not
  contain.
- Do not resolve the coverage gaps in F8. Naming and routing them is the
  deliverable; closing them belongs downstream.
- Do not assume a customer exists, is available, or has authority. Do not
  assume CI, test tooling, or version control exists.
- Do not assume the team is small, co-located, skilled, or stable.
- Do not describe an undisciplined process as agile. A process with no
  specification, no retained intent, and no protected refactoring effort is
  not an agile process with some practices omitted; it is the absence of a
  process, and must be labeled as such if the inputs describe one.
- On re-entry, revise the prior charter and report the diff. Do not
  regenerate from scratch.
- If {{PAR}} is absent, malformed, or contains `halt: true`, emit HALT
  naming the missing upstream artifact. Do not reconstruct the PAR
  yourself.
```

### 6. Process — FIXED

```
Work in this order:

1. Read the PAR first and extract its `process_model`, `spectrum_position`,
   and `iteration` block. Everything you decide operates inside those.

2. Assess the ten factors before forming any view about which practices you
   like. Record findings, then look at what they add up to.

3. Reconcile against the PAR immediately after step 2, before any practice
   selection. If the mismatch condition in F2 holds, stop and emit the
   mismatch signal. Building a charter on a contradicted foundation wastes
   the whole downstream run.

4. Rule on practices one at a time. For each, state the precondition before
   the ruling. If you find yourself adopting a run of practices without
   examining preconditions, you have started reciting a method instead of
   selecting for this project — restart the run.

5. Self-critique before finalizing. Check specifically: is any practice
   adopted whose precondition is unmet; is any rejection missing its
   compensating measure or accepted-risk label; does any ruling lack a
   traceable F1 basis; has any coverage gap been closed here instead of
   routed; does any sentence assume a domain not given.

6. Adversarial pass. State the strongest case that this charter will be
   abandoned under pressure in week three — which practice goes first, and
   what in the charter makes it survivable or not. If nothing in the
   charter protects the vulnerable practice, that is a finding to report,
   not a flaw to hide.

Do not ask clarifying questions mid-run. Record unknowns and continue.

HUMAN-IN-THE-LOOP VARIANT (interactive invocation only): after step 3,
present the balance assessment and reconciliation alone and stop for
confirmation before ruling on practices.
```

### 7. Output Format — FIXED

```
Deliver a single document titled "Development Practice Charter — <project
name>", with these sections in this order and under these exact headings:

  1. Balance Assessment
  2. Reconciliation with the Process Architecture Record
  3. Practice Selection
  4. Precondition Check
  5. Executor Assignment
  6. Iteration Mechanics
  7. Retained Documentation
  8. Coverage Gaps and Handoffs
  9. Scaling Adaptations
  10. Assumptions and Revision Triggers
  11. Charter Block

Sections 3, 4, and 5 may be combined into a single table with columns:
Practice | Ruling | Rationale (F1 ref) | Precondition | Precondition met? |
Executor | Substitution limit.

Section 11 is a fenced YAML block in exactly this shape:

```yaml
charter_version: 1
project_id: <slug>            # must match the PAR
par_ref: <par_version>
spectrum_position: plan-driven | balanced | agile
reconciliation: agrees | adjusted-within-band | mismatch
increment:
  length: <duration or "not timeboxed">
  scope_locked_mid_increment: true | false
  selected_by: <role>
  definition_of_done: <checkable proposition>
work_items:
  format: <string>
  decomposition_rule: branch-based-with-shared-extraction
  acceptance_criteria_author: <role>
  signoff_authority: <role>
practices:
  - name: <practice>
    ruling: adopt | adapt | reject
    executor: human | ai | pair
    precondition_met: true | false | unknown
    substitution_limit: <string or null>
    accepted_risk: <string or null>
non_negotiable:                # practices the router must verify are held
  - <practice>
retained_documentation:
  - artifact: <name>
    answers: <maintenance question>
    owner_stage: <CHn>
coverage_gaps:
  - gap: <string>
    routed_to: <CHn>
scaling_adaptations: [<string>, ...]   # empty list if none
blocking_unknowns:
  - field: <slot>
    assumed: <value>
    falsifier: <observation>
raises_upstream:               # empty unless mismatch
  - signal: SPECTRUM_MISMATCH
    to: CH2
    factors: [<factor numbers>]
halt: false
```

If halting or raising a mismatch, emit only the YAML block with the
relevant fields populated and a one-paragraph explanation above it.
```

### 8. Verification — FIXED

```
Structural gates (router-checkable):
V1.  All eleven sections present under the exact specified headings.
V2.  Section 11 parses as valid YAML; `project_id` matches the PAR.
V3.  All fifteen practices from F3 appear with a ruling. None omitted.
V4.  Every adopt/adapt ruling has a precondition and a precondition_met
     value.
V5.  Every reject ruling has either a compensating measure or a populated
     accepted_risk field.
V6.  Every adopted practice has an executor; every AI executor has a
     non-null substitution_limit.
V7.  `non_negotiable` is non-empty.
V8.  `coverage_gaps` is non-empty and every entry routes to a named stage.
V9.  `retained_documentation` is non-empty, or its emptiness appears in
     Section 7 with an explicit accepted-risk label.
V10. If reconciliation is `mismatch`, no practice selection is present and
     raises_upstream is populated.

Content gates (reviewer-checkable):
V11. Every ruling in Section 3 traces to a numbered finding in Section 1.
V12. No practice is adopted whose precondition is marked unmet.
V13. No domain-specific technology, vendor, or example appears that was not
     in the input.
V14. The adversarial pass names a specific practice at risk and a specific
     charter mechanism that does or does not protect it.
V15. Section 7 answers maintenance questions rather than listing document
     types.

Generalization gate (applied when this prompt is graded as an artifact):
V16. Run against three projects whose ten-factor profiles differ sharply —
     at minimum one small co-located product build, one regulated or
     safety-relevant system, and one distributed brownfield integration.
     The three charters must differ in their practice rulings, not only in
     their prose. Identical practice sets across all three is evidence the
     prompt is reciting a method rather than selecting one.
V17. At least one run must produce a reject ruling on a practice the model
     would otherwise reach for by default. A charter that adopts everything
     has not been selecting.
```

---

## Library Notes

### Chapter traceability

| Prompt element | Ch3 source |
|---|---|
| F1 ten choice factors | §3.2, "Choosing an Approach" 1 and 2 — the full ten, unmerged |
| F3 practice list | §3.3 XP practices (ten) plus §3.4 Scrum structure (timebox, backlog, sync, review, shielding role) |
| F4 precondition check | §3.1 "Agile Principles Are Hard to Realize" — willing customer, personality fit, stakeholder disagreement, simplicity under deadline pressure, organizational culture |
| F6 decomposition rule | §3.3 story/task card example — tasks map to behavior branches; behavior shared across branches becomes its own task |
| F7 retained documentation | §3.1 "Agile Methods and Software Maintenance" — the counter-argument that informal requirements collection leaves no coherent record and raises maintenance cost once the team disperses |
| F8 coverage gaps | §3.3 "Testing in XP" caveats — incomplete tests under pressure, behavior resistant to incremental testing, large suites with real gaps |
| F9 scaling | §3.5 — large-system characteristics, scaling up vs. out, critical adaptations, adoption barriers |
| Role section's "no right or wrong processes" | §3.5 Key Points and the chapter's closing discussion |

### Design decisions worth defending in the writeup

**Practices are ruled on individually, and the prompt is built to make block-adoption hard.** Sommerville's factors are independent and often point in opposite directions, so the honest output for most projects is a mixed charter. An LLM asked about agile will recite XP and Scrum as packages; N4, Process step 4, and V17 all exist to fight that specific failure. V17 is the sharpest of the three — if no run ever rejects anything, the prompt is reciting.

**F7 is where the intent-documentation leg gets forced.** The end-product doc identifies intent documentation as only partially covered. Ch3 is the right place to close it, because agile is precisely the process that drops documentation by design and Sommerville himself raises the objection: when the original team disperses, there may be no coherent record of what the system was for. Requiring that each retained artifact name the *maintenance question it answers* — rather than listing document types — is what connects this to the handoff/fix drill. A team whose Ch3 charter retained nothing will fail that drill, and will be able to trace the failure back to a decision they made in week three.

**F8 refuses to let the charter claim more than it delivers.** Ch3's own testing caveats are the in-chapter version of the "tests will catch everything is a trap" argument. Making the prompt state its coverage gaps and route them is what keeps the library honest at the seams instead of each stage assuming another one handled it.

**F5 (executor assignment) is the AI-specific addition and the one genuinely not in Sommerville.** XP's practices assume humans: an on-site customer with authority, a pair who catches your mistakes, a team with a sustainable pace. Building an AI-assisted process means saying which of those an agent can stand in for and which it cannot. The substitution-limit field is where that gets recorded rather than glossed. Expect this to be the most-argued field in review, which is the point.

**The `SPECTRUM_MISMATCH` signal is the library's first real loop-back.** Everything before this point flows forward. Ch3 is the first stage with a finer instrument than the one that made the upstream decision, which makes it the first stage that can legitimately contradict its predecessor. Worth watching closely in the cold test — if it never fires across any team's Week 13 run, either the Ch2 classification is doing more work than expected or Ch3 is deferring to it rather than auditing it.

### Known generalization risks

- **The ten factors are not equally weighted, and the prompt deliberately refuses to weight them.** Factors 4 and 10 (system type, external regulation) can override the other eight on their own. F1's instruction to report dominance rather than average is a partial fix; watch whether runs actually honor it or quietly produce a middling "balanced" result from a profile that should have been decisively plan-driven.
- **`{{CUSTOMER_AVAILABILITY}}` is the highest-leverage optional input.** Roughly a third of the practice list depends on it. In the cold test, consider making it required — a charter built on an assumed customer is the most likely single source of Week 13 breakage.
- **F5 will drift as model capability changes.** The substitution limits written this semester are a snapshot. That's a feature for the process-improvement discussion: the field is designed to be revisited, and the diff over time is itself evidence.
