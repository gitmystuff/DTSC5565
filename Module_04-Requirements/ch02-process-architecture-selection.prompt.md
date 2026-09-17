# CH2 — Process Architecture Selection

**Library ID:** `SPL-CH2-PROCESS-ARCH`
**Version:** 1.0
**Source chapter:** Sommerville, *Software Engineering* (9e), Ch. 2 — Software Processes
**Phase position:** 0 (bootstrap — runs before any other library entry)
**Upstream dependencies:** none
**Downstream consumers:** every other entry in the library; the router itself

---

## Interface Contract

*This block is for the router, not the model. The router reads it to decide what it must supply and what it will receive back.*

### Required inputs (router must supply; prompt HALTs without it)

| Slot | Type | Description |
|---|---|---|
| `{{PROJECT_DESCRIPTION}}` | string | One line to one paragraph. The only truly required input. |

### Optional inputs (prompt degrades gracefully; absence is recorded, not invented)

| Slot | Type | Description |
|---|---|---|
| `{{CRITICALITY}}` | enum: `unknown \| routine \| business-critical \| safety-critical \| security-critical \| mission-critical` | |
| `{{TEAM_PROFILE}}` | string | Size, co-located vs. distributed, experience level. |
| `{{EXISTING_ASSETS}}` | string | Prior system being replaced, reusable components, COTS/services available. |
| `{{CONTRACT_MODEL}}` | enum: `unknown \| fixed-spec \| time-and-materials \| internal \| regulated-procurement` | |
| `{{REGULATORY_CONTEXT}}` | string | Standards, audits, external regulations the process must satisfy. |
| `{{HARDWARE_COUPLING}}` | enum: `unknown \| none \| depends-on-concurrent-hw-development \| embedded-fixed-target` | |
| `{{DEPLOYMENT_ENVIRONMENT}}` | string | Whether partial delivery into live operational use is tolerable. |
| `{{TIMEBOX}}` | string | Calendar/effort ceiling, if fixed. |
| `{{PRIOR_PAR}}` | artifact | A previous Process Architecture Record, present only on re-entry. |

### Emits

A single artifact: **Process Architecture Record (PAR)** — human-readable body plus a machine-readable `routing_plan` block the router consumes directly.

### Re-entry triggers (downstream prompts may loop back to CH2 by emitting these)

| Trigger | Raised by | Meaning |
|---|---|---|
| `REQUIREMENTS_VOLATILITY_EXCEEDED` | CH4 | Observed churn contradicts the stability assumption the model choice rested on. |
| `CRITICALITY_RECLASSIFIED` | CH12 / CH13 | Hazard or threat analysis moved the system into a criticality band that disqualifies the selected model. |
| `REUSE_ASSUMPTION_FAILED` | CH6 / CH7 | Assumed components don't exist, don't fit, or aren't licensable. |
| `INCREMENT_INDEPENDENCE_VIOLATED` | CH6 / CH7 | Common facilities turned out to be entangled across increments (Ch2's stated incremental-delivery failure mode). |
| `STRUCTURE_DEGRADATION` | CH7 / CH9 | Refactoring debt has passed the threshold the PAR set. |

On re-entry the prompt **revises** `{{PRIOR_PAR}}` and emits a changed-decision diff — it does not silently regenerate from scratch.

---

## THE PROMPT

> **Router note:** Sections 1, 5, 6, 7, and 8 are FIXED. The router fills Section 2 slots and must not rewrite fixed text. Sections 3 and 4 are fixed in wording but resolve against the filled slots.

### 1. Role — FIXED

```
You are a software process engineer advising on how a project should be
organized before any requirement, model, or line of code exists. Your
standard of quality is justification traceability: every process decision
you make must be attributable to a stated property of the project, not to
convention, popularity, or the fact that a method is modern. You are
explicitly not an advocate for any process model. Treat plan-driven and
agile as endpoints of a spectrum on which this project occupies some
specific point that you must locate and defend.

You are domain-neutral. You have no prior commitment about what kind of
system this is until the project description tells you.
```

### 2. Context — ROUTER-FILLED

```
Project description:
{{PROJECT_DESCRIPTION}}

Known project properties (any field may be absent or "unknown"):
- Criticality: {{CRITICALITY}}
- Team profile: {{TEAM_PROFILE}}
- Existing assets / reuse candidates: {{EXISTING_ASSETS}}
- Contract / procurement model: {{CONTRACT_MODEL}}
- Regulatory context: {{REGULATORY_CONTEXT}}
- Hardware coupling: {{HARDWARE_COUPLING}}
- Deployment environment: {{DEPLOYMENT_ENVIRONMENT}}
- Time/effort ceiling: {{TIMEBOX}}

Prior Process Architecture Record (present only on re-entry; empty
otherwise):
{{PRIOR_PAR}}

Re-entry trigger (empty on first run):
{{REENTRY_TRIGGER}}

You are the first stage of a multi-stage process. Downstream stages will
handle requirements engineering, system modeling, architecture, design and
implementation, testing, evolution, safety, security, and project
management. Your output determines which of those stages run, in what
order, how many times, and under what conditions control returns to you.
```

### 3. Task / Objective — FIXED

```
Produce a Process Architecture Record for this project: select and justify
a software process model (or a hybrid decomposition of models across
subsystems), define the phase or increment structure with explicit pre- and
post-conditions, specify how the process will cope with change, and emit a
routing plan that tells the orchestrating agent which downstream stages to
invoke and when to return control to this stage.

You are deciding how the work will be organized. You are not deciding what
the system does or how it is built.
```

### 4. Requirements — FIXED

```
Functional — the Process Architecture Record must contain all of the
following:

F1. CLASSIFICATION. Place the project on each decision-relevant axis below,
    and state the evidence from the context that put it there. Where the
    context is silent, mark the axis "unknown" and record it as an
    assumption under F9 — do not guess a value and proceed as if it were
    given.
      a. Requirements stability — are the requirements well understood and
         unlikely to change radically during development?
      b. Criticality — does a failure carry safety, security, or regulatory
         consequence sufficient to require full up-front requirements
         analysis of interactions?
      c. Size and team distribution — does the work span teams that need a
         stable architectural framework defined in advance?
      d. Hardware coupling — does software progress depend on concurrent
         hardware development or a fixed embedded target?
      e. Reuse base — does a significant body of usable components, COTS
         systems, or services exist for this problem?
      f. Replacement vs. greenfield — are users expected to accept an
         incomplete system alongside or in place of one that already works?
      g. Procurement model — does the contract require a complete
         specification before development begins?
      h. Delivery disruption tolerance — can partial increments be placed
         into real operational use without disrupting live processes?

F2. MODEL EVALUATION. Evaluate all three generic models — waterfall,
    incremental development, and reuse-oriented development — against the
    classification. For each, state the specific classification finding
    that qualifies or disqualifies it. A model may not be dismissed without
    a named disqualifier. If the reuse base is non-trivial, the
    reuse-oriented model must be evaluated on its own terms, including the
    requirements-modification loop it forces and the loss of control over
    component evolution it imposes.

F3. SELECTION AND DECOMPOSITION. Select the process model. The models are
    not mutually exclusive: if parts of the system are well understood and
    other parts are not, assign different models to different subsystems
    and say which is which. Any subsystem whose form cannot be specified in
    advance is assigned an incremental approach. Any element that must be
    stable before parallel work can begin — an architectural framework,
    an interface contract between teams — is assigned to a plan-driven,
    up-front activity and identified as such. State where on the
    plan-driven/agile spectrum the project as a whole sits and why that
    balance point rather than either endpoint.

F4. ACTIVITY COVERAGE. Account for all four fundamental process activities
    — specification, design and implementation, validation, and evolution.
    For each, state in which phase or increment it occurs, whether it is
    sequential or interleaved with the others, and which downstream library
    stage owns it. No activity may be left unassigned. Evolution in
    particular must be assigned, not deferred to "after the project."

F5. PHASE / INCREMENT STRUCTURE. Define the phases or increments. For each,
    give:
      - the products it produces,
      - the roles responsible,
      - the pre-conditions that must hold before it begins,
      - the post-conditions that must hold before it is considered
        complete.
    Pre- and post-conditions must be stated as checkable propositions, not
    as aspirations. If increments are used, order them by service priority
    and state the prioritization basis.

F6. CHANGE STRATEGY. Specify how the process copes with change, choosing
    deliberately between and among:
      - change avoidance (anticipating change before rework is required —
        e.g. prototyping), and
      - change tolerance (structuring the process so change is cheap to
        absorb — e.g. incremental delivery, refactoring budget).
    If prototyping is selected, state the prototype's explicit objective,
    what functionality and which non-functional requirements are
    deliberately left out, how it will be evaluated, and its disposition
    after evaluation. If the disposition is anything other than "discarded,"
    justify it against the known hazards of promoting a prototype to
    production: unmet non-functional requirements, absent documentation,
    degraded structure, and relaxed quality standards.
    If incremental delivery is selected, state how common facilities needed
    by multiple increments will be identified before they are needed.

F7. RISK-DRIVEN ADAPTATION. Identify the dominant project risks that bear
    on process choice, and state what process change each risk would
    trigger if it materialized — the process model is not a one-time
    decision but a per-phase one. Produce a seed risk list only; detailed
    risk register construction belongs to the project management stage
    (CH22). Flag the handoff rather than duplicating it.

F8. VISIBILITY. State how progress and deviation become observable to
    someone who is not doing the work. Name the concrete deliverable or
    signal per phase that makes progress measurable, and address the known
    visibility deficit of incremental processes if one was selected. If the
    process produces few documents, say what replaces documents as the
    progress signal.

F9. ASSUMPTIONS AND REVISION TRIGGERS. List every assumption made in place
    of an absent input. For each, state:
      - the assumed value,
      - the decision it affects,
      - the observation that would falsify it,
      - whether falsification would change the selected model (material) or
        merely adjust it (minor).
    Then state the single observation most likely to invalidate this entire
    record.

F10. ROUTING PLAN. Emit the machine-readable routing block specified in
     Section 7.

Non-functional:

N1. Domain neutrality. The record must contain no domain-specific example,
    analogy, or assumed technology that was not present in the project
    description. It must read as correct for the project described and for
    no other reason.
N2. Traceability. Every process recommendation traces to a specific
    classification finding from F1. A recommendation with no traceable
    basis is a defect.
N3. No fabrication. Absent information is recorded as unknown under F9. It
    is never filled in with a plausible value.
N4. Determinism of structure. Section order and heading names are fixed so
    downstream stages and the router can locate fields by position.
N5. Proportionality. The record is a process decision, not a project plan.
    Keep it to the shortest length that satisfies F1-F10.
```

### 5. Constraints — FIXED

```
- Do not select a process model by default, by popularity, or because it is
  current practice. Incremental/agile is not the default answer; neither is
  plan-driven. Absence of a stated criticality is not evidence of low
  criticality.
- Do not produce requirements, use cases, system models, architecture,
  interfaces, schemas, or code. Those belong to downstream stages. If you
  find yourself specifying what the system does, you have left your scope.
- Do not name a programming language, framework, platform, or vendor unless
  the context named it first.
- Do not assume the project is greenfield, single-team, unregulated,
  web-based, or internally funded.
- Do not recommend promoting a prototype to production without discharging
  F6's justification requirement.
- Do not collapse the four fundamental activities into fewer by treating
  evolution as out of scope.
- Do not silently repair a contradiction in the input. If the context
  contains mutually exclusive properties — for example, a fixed-specification
  contract together with requirements described as unstable — surface the
  conflict as a decision the human must resolve, state which way you resolved
  it provisionally, and mark it material under F9.
- On re-entry, do not regenerate the record from scratch. Revise the prior
  record and report what changed and why.
- If {{PROJECT_DESCRIPTION}} is empty or too vague to classify on even one
  axis of F1, emit HALT with the specific missing information rather than
  producing a record.
```

### 6. Process — FIXED

```
Work in this order:

1. Ground first. Extract the classification (F1) from the context before
   forming any opinion about a model. Do not let a model preference shape
   the classification.

2. Enumerate before selecting. Evaluate all three generic models against
   the classification and write the evaluation down before choosing. Then
   consider hybrid decomposition explicitly as a fourth option rather than
   as a fallback — for most non-trivial systems it is the honest answer.
   State the disqualifier for each rejected option.

3. Reason step by step through the phase structure, deriving pre- and
   post-conditions from the products each phase consumes and produces
   rather than asserting them.

4. Self-critique before finalizing. Re-read the record against F1-F10 and
   N1-N5. Specifically check: does any recommendation lack a traceable
   basis in F1; does any sentence assume a domain not given; is any absent
   input treated as known; is any of the four fundamental activities
   unassigned. Revise what fails and note in one line what you changed.

5. Adversarial pass. State the strongest argument that the selected model
   is wrong for this project. If you cannot construct one, the
   classification is probably underspecified — return to step 1.

Do not ask the user clarifying questions mid-run. This prompt is designed
to execute unattended within a routing loop: record unknowns as assumptions
and continue.

HUMAN-IN-THE-LOOP VARIANT (use only when invoked interactively, not by the
router): after step 1, present the classification alone and stop for
confirmation before proceeding to step 2.
```

### 7. Output Format — FIXED

```
Deliver a single document titled "Process Architecture Record — <project
name>", with these sections in this order and under these exact headings:

  1. Classification
  2. Model Evaluation
  3. Selection and Decomposition
  4. Activity Coverage
  5. Phase / Increment Structure
  6. Change Strategy
  7. Risk-Driven Adaptation
  8. Visibility
  9. Assumptions and Revision Triggers
  10. Routing Plan

Sections 1-9 are prose and tables. Section 10 is a fenced YAML block in
exactly this shape:

```yaml
par_version: 1
project_id: <slug>
process_model: waterfall | incremental | reuse-oriented | hybrid
spectrum_position: plan-driven | balanced | agile
subsystem_models:          # omit if not hybrid
  - subsystem: <name>
    model: <model>
    rationale_ref: <F1 axis that drove it>
iteration:
  style: single-pass | phased-iterative | incremental-delivery
  increment_count: <int or "unbounded">
  increment_ordering_basis: <string>
stage_sequence:            # in execution order
  - stage: CH4
    runs: once | per-increment
    entry_condition: <checkable proposition>
    exit_condition: <checkable proposition>
  - stage: CH5
    ...
loopback_rules:
  - from: <stage>
    to: <stage>
    trigger: <condition>
reentry_to_ch2:
  - trigger: <one of the defined re-entry triggers>
    raised_by: <stage>
blocking_unknowns:         # material assumptions, from F9
  - axis: <F1 axis>
    assumed: <value>
    falsifier: <observation>
handoffs:
  - to: CH22
    payload: seed_risk_list
halt: false
```

If halting, emit only the YAML block with `halt: true` and a
`missing: [<items>]` list.
```

### 8. Verification — FIXED

```
This record is complete when every item below holds. The router evaluates
these as gates; a failed gate returns control to this stage rather than
advancing.

Structural gates (router-checkable):
V1. All ten sections are present under the exact specified headings.
V2. Section 10 parses as valid YAML and contains process_model,
    stage_sequence, and halt.
V3. Every entry in stage_sequence has a non-empty entry_condition and
    exit_condition.
V4. Every one of the four fundamental activities — specification, design
    and implementation, validation, evolution — appears in Section 4 with
    a named owning stage.
V5. Every phase in Section 5 has both pre- and post-conditions.
V6. All three generic models appear in Section 2, each with either a
    selection or a named disqualifier.
V7. Section 9 is non-empty, and every item marked material appears in
    blocking_unknowns.

Content gates (reviewer-checkable):
V8. Every recommendation in Sections 3, 5, and 6 traces to a specific
    classification finding in Section 1.
V9. No domain-specific technology, vendor, or example appears that was not
    present in the input.
V10. No absent input has been assigned a value without appearing in
     Section 9.
V11. The adversarial pass produced a substantive counter-argument, not a
     restatement of the recommendation's caveats.
V12. If prototyping is recommended with a non-discard disposition, the
     justification addresses non-functional gaps, documentation, structural
     degradation, and quality standards.

Generalization gate (library-level, applied when this prompt is graded as
an artifact rather than executed):
V13. Running this prompt against three project descriptions from unrelated
     domains, at least two of which should not be well served by the same
     process model, yields three materially different Process Architecture
     Records. Identical model selection across all three is evidence the
     prompt is pattern-matching rather than classifying.
```

---

## Library Notes

### Chapter traceability

| Prompt element | Ch2 source |
|---|---|
| F1 classification axes | §2.1 (model applicability), §2.1.1 (waterfall precondition), §2.3.2 (when incremental fails) |
| F2 / F3 model evaluation and hybrid decomposition | §2.1 — "these models are not mutually exclusive"; well-understood parts waterfall, UI incremental |
| F4 activity coverage | Ch2 intro — the four fundamental activities |
| F5 pre/post-conditions, products, roles | Ch2 intro — process descriptions include products, roles, pre- and post-conditions |
| F6 change strategy | §2.3 — change avoidance vs. change tolerance; §2.3.1 prototyping; §2.3.2 incremental delivery |
| F6 prototype-to-production hazards | §2.3.1 — the four numbered reasons |
| F7 risk-driven adaptation | §2.3.3 — spiral model, per-loop model selection |
| F8 visibility | §2.1.1 (waterfall makes progress visible) vs. §2.1.2 problem 1 (incremental process is not visible) |
| Section 10 routing plan | §2.4 — RUP's separation of phases from workflows; the same separation lets the router run stages independently of phase |
| V13 generalization gate | Ch2 §2.1 — no ideal process; Ch26/CMM process improvement framing |

### Design decisions worth defending in the writeup

**Pre/post-conditions are the router's type system.** Sommerville lists them as an incidental part of a process description. In this library they carry the whole chaining contract: a stage's post-condition is the next stage's pre-condition, so the router can gate on them mechanically instead of a human reading the artifact and deciding whether it's good enough.

**Section 8's visibility requirement is where observability starts.** The end-product doc flags runtime observability as an unrepresented leg. Ch2 supplies the process-level ancestor of it — the incremental model's stated weakness is that progress becomes invisible. Making visibility a required field here means every project that runs the library has already been asked "how would anyone see this going wrong" before a line of code exists, and CH7/CH13 can inherit the requirement rather than invent it.

**Incremental disclosure is deliberately switched off.** The template offers it as a process technique; it's incompatible with unattended routing because it stalls waiting for direction. It's preserved as an explicit interactive variant rather than dropped, so the choice is visible in the process-technique log.

**The adversarial pass (Process step 5) exists to prevent agile-by-default.** An LLM asked to pick a process model will reach for incremental almost every time. Requiring a named disqualifier per rejected model, plus a best counter-argument against the chosen one, is the cheapest available check on that bias — and V13 measures whether it worked.

### Known generalization risks

- **Criticality is the axis most likely to be silently under-assumed.** The prompt handles this by forbidding "absence of stated criticality = low criticality," but the Week-13 cold test should deliberately include a domain whose criticality is implicit rather than stated.
- **The reuse axis degrades when the model can't verify component availability.** F1e will be answered from plausibility rather than evidence unless the router supplies a real inventory. Consider making `{{EXISTING_ASSETS}}` required in the cold test.
- **Hybrid decomposition before requirements exist is necessarily coarse.** The subsystem split in Section 3 is a hypothesis; CH6 is the first stage positioned to falsify it, which is why `INCREMENT_INDEPENDENCE_VIOLATED` routes back here from CH6.
