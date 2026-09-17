# Why We're Doing This

*A plain-language refresher on what we're building this semester and why. Re-read it any week you're not sure what the point is. That's what it's for.*

---

## The one-sentence version

We are building a **reusable process for engineering software with AI** — written as a set of prompts — and then proving it works by pointing it at a project nobody on the team designed for.

The app we build in Week 13 is not the deliverable. It's the proof.

---

## The problem we're actually working on

You can already get an AI to write code. That part is solved well enough to be boring.

What isn't solved is everything around it. Ask an AI for a feature and you'll get working code fast. Ask it for a *system* — one that someone else can pick up in six months, that doesn't fall over when the input is weird, that you can explain to a regulator, that survives a change request without quietly breaking three other things — and the speed stops helping. That's the gap people mean when they say "vibe coding doesn't scale."

Software engineering already has answers for that gap. They're in Sommerville: figure out what you're building before you build it, model it, design an architecture, test it, think about what could go wrong, plan for change. Those answers are older than any of us and they work.

**Our bet for the semester:** those answers can be written down as instructions precise enough that an AI can execute them. Not "be careful" — actual, structured, repeatable instructions. If that's true, we get the speed of AI-assisted development without giving up the discipline that makes software last.

That's the whole course. Everything else is detail.

---

## What we're building, concretely

### 1. A prompt library

One prompt per chapter of the Sommerville process. Requirements engineering gets a prompt. Architecture gets a prompt. Testing, safety, security, evolution — each gets one.

Each prompt is a **template, not a message**. It has blanks in it. You don't write "elicit requirements for a plant-watering app." You write a prompt that can elicit requirements for *any* project, with the project description dropped into a slot.

That distinction is the single most common thing to lose track of. If your prompt only works for the project you had in mind when you wrote it, it isn't finished.

### 2. A router

One agent whose entire job is deciding which prompt to run next.

It figures out (or is told) what phase the project is in, picks the right prompt from the library, hands it the artifacts from earlier phases, reads the result, and decides: move forward, or go back and redo something.

That loop — classify, select, execute, verify, route — is what people mean when they say "agent." Not magic. A decision loop with a library attached. Building one is how you stop taking anybody's word for what an agent is.

---

## Why the prompt is the graded artifact, not the output

This is the part that feels backwards at first.

If you write a prompt and it produces a great requirements document, you might reasonably think the requirements document is the work. It isn't. The requirements document is *evidence about* the work.

Here's why. A great requirements document proves you can get one good result once. A prompt that reliably produces good requirements documents across projects you haven't seen proves you built something reusable. Only the second thing is worth carrying out of this class.

So when you're stuck on an assignment, the question isn't "is this output good?" It's:

- Would this still work on a completely different kind of project?
- Did I accidentally bake in an assumption about the domain?
- Does it say what to do when the information it needs is missing?
- Can someone tell from the output whether it worked, without reading the whole thing carefully?

---

## Why we test it cold in Week 13

Every team will have been polishing their library against familiar projects for ten weeks. That's a rigged test. You can't tell the difference between a process that generalizes and one you've unconsciously tuned to your own project.

So in Week 13 you get a domain you didn't design for. You run your library on it from scratch — scope, spec, design, build, test, secure, document — using only what you built in Weeks 3 through 12.

**Things will break. That's the point.**

Where it breaks is the most valuable data the course produces. "Our architecture prompt assumed there'd be a database" is a real finding. It's the Chapter 2 idea of process improvement applied to something you actually made instead of a case study in a textbook. A team that reports three honest break points learned more than a team that reports none.

---

## Why "we'll just write good tests" isn't enough

There's a reasonable-sounding position: define what you want carefully, write tests for it, and you've solved reliability.

It doesn't hold, and understanding why is close to the center of this course.

Tests check that your **code** matches your **spec**. They say nothing about whether your spec matched reality. Five ways that bites:

1. **You built the wrong thing.** The requirement was subtly wrong. Every test passes. You have correctly built a mistake.
2. **The world moved.** A dependency updated, an API changed shape, a certificate expired. Your tests were right when written. They test your code, not the world it runs in.
3. **Two correct things, combined.** Component A is fine. Component B is fine. Together, under specific timing, they deadlock. Nobody skipped a test — the interaction was never in scope.
4. **Scale you never tried.** Passes every functional test, dies at 10x traffic or on a slow network.
5. **Adversarial input.** Tests cover input you expected. An attacker's entire job is finding input nobody expected.

Testing shrinks the space of surprises. It can't eliminate it, because it can only test against failures somebody was able to imagine, and reality is bigger than anyone's imagination.

A team that believes good tests mean no surprises is *more* exposed when the surprise comes, because they built nothing to see it with.

### So the target is three things, not one

| | What it does | Where it comes from |
|---|---|---|
| **Tests** | Catch the failures you anticipated | Ch8, plus the adversarial and safety tests in Ch12/13 |
| **Intent documentation** | Explains *why* something works the way it does and what it assumes, so a stranger can reason toward a fix for a problem nobody predicted | Ch7 — and it's an acceptance criterion, not a formatting nicety |
| **Observability** | Logging, clear errors, traceability, so an unanticipated failure is *visible and diagnosable at all* | The gap we're closing — Ch7 or Ch13 |

A system is fixable by a stranger only when all three are present. Vibe coding as usually practiced has none of them at production quality.

### The drill that tests this for real

Team B gets Team A's working codebase with a deliberately introduced failure — one that Team A's own test suite does not catch. Team B must find and fix it using only Team A's documentation, logs, and prompts. No asking Team A.

That measures the thing we actually claim: that a stranger can diagnose and repair an unplanned failure from what we left behind. Anything less is measuring whether a team can navigate its own work, which everyone can.

---

## How each chapter earns its place

Nothing in the sequence is decorative. Each chapter produces one required, reusable piece.

| Chapter | What its prompt does | What it hands forward |
|---|---|---|
| Ch2/Ch3 | Decide how the project should be organized and which phases run | The routing plan |
| Ch4 | Elicit functional and non-functional requirements | Requirements document |
| Ch5 | Model the system from those requirements | Use case, class, sequence, activity models |
| Ch6 | Propose and justify an architecture | Architecture design doc |
| Ch7 | Implement test-first, incrementally, with reasoning visible | Working code + reasoning log |
| Ch8 | Turn requirements into a test plan and suite | Test plan + tests |
| Ch9 | Absorb a change request without breaking prior guarantees | Change log + updated artifacts |
| Ch12 | Find hazards, classify risk, derive safety requirements | Hazard log + safety requirements |
| Ch13 | Find assets and threats, propose mitigations, test adversarially | Threat model + mitigations |
| Ch22 | Schedule, risks, status reporting | Project plan + risk register |

Notice the third column. Each prompt's output is the next prompt's input. That's the chain the router walks, and it's why a prompt that produces a beautiful document in the wrong *shape* is still broken.

---

## Five things to hold onto

1. **The product is the process.** The app is evidence.
2. **If it only works on your project, it isn't done.**
3. **Output shape matters as much as output quality** — something downstream has to consume it.
4. **Breaking in Week 13 is data, not failure.** Hiding that it broke is the only real failure.
5. **Tests, intent docs, and observability.** All three, or a stranger can't fix it.

---

## Questions people keep asking

**Am I supposed to be writing code or writing prompts?**
Mostly prompts. You'll write and run code to check that the prompts work. The code is the experiment; the prompt is the finding.

**Isn't this all going to be obsolete in a year?**
Some of the specifics, yes. The structure won't be. "Break work into phases, define what each phase needs and produces, check the output before moving on" predates AI by decades and will outlast whatever model we're using in May. Chapter 2 makes the same point about process models: there's no ideal one, and the useful skill is choosing and adapting rather than memorizing.

**My prompt works. Why does the feedback say it's incomplete?**
Usually one of: it assumes a domain, it has no defined behavior when an input is missing, or its output can't be checked without a human reading it end to end.

**Why so much structure? Can't I just ask the AI nicely?**
You can, and for a one-off it's often fine. Structure is what makes it *repeatable by someone else* — which is the entire claim we're testing. The comparison is worth doing yourself: run a task zero-shot, then run it through the full template, and look at what changed.

**What do I actually take away from this class?**
A structured prompt library and a router pattern you can point at real work, plus the judgment to know when the AI's confident answer is missing something. Both transfer. Neither depends on this semester's tools.
