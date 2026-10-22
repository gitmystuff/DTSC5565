# se-agent lite: Talking Points for Class

CSCE 5565 Software Engineering · Thursday, Oct 22, 2026 · about 40 minutes

**The idea in one sentence:** we give an AI a one-page description of an app and three prompts (design, build, verify). Each prompt does one job. The result is a web app we can open and click.

---

## Before class (5 minutes)

1. Open a terminal in the `se-agent` folder.
2. Run `uv run pytest`. Expect all tests to pass.
3. Keep a good saved run ready as a backup. Tonight's run is `output_lite\20261021-234135\`. Its `index.html` opens and works.
4. Have these tabs open: `lite.py`, `lite_prompts\2_build.md`, `water-tracker.md`, and the terminal.
5. Start the live run **early in class** (see section 4). It takes a few minutes because of the pauses.

**If the live run fails:** say "this is a real run from earlier" and walk through the saved files. A failed run is a legitimate lesson, so ask the class why it failed (rate limit, bad reply, network).

---

## 1. Open with the problem (3 min)

- Show `water-tracker.md`. Say: "Here's a one-page description of an app. What would it take to turn this into working software?"
- Let them answer. Then say: "Design it, build it, check it. Today we make an AI do each job, with one prompt per job."
- Link to Sommerville: this is the same pipeline from Chapters 5–8 (model, design, implement, test), shrunk to three steps.

## 2. Walk through `lite.py` (10 min)

Scroll slowly and say one sentence per block.

| Block | What to say |
|---|---|
| Docstring at the top | "This is the whole plan: read the brief, run the prompts in order, save the results." |
| `MODEL`, `PAUSE`, `MAX_EARLIER` | "Three settings: which model, how long to wait between steps, and how much earlier work we pass along. The last two exist because of limits. We'll see why." |
| `ask()` | "The only place we talk to the model. We send a system prompt and a message, and we get text back. If the free tier says slow down (error 429), it waits and tries again. Everything else is plain Python." |
| `describe_usage()` | "Prints how many tokens each call used. Hold that thought, because we'll come back to it." |
| `run()` | "A loop. For each prompt file: put the brief in, add the earlier work, ask, remember the answer. This one loop is the pipeline." |
| `save()` | "Writes each result to a file and pulls the web page out of the build step's reply." |

## 3. Show one prompt (5 min)

- Open `lite_prompts\2_build.md`: "These are the eight sections you've used all semester."
- Point at **Constraints** (one file, no libraries, small): "If we don't say this, the model chooses for us."
- Point at **Verification**: "This is how we'll know if it did the job."
- Point out the `[PROJECT_DESCRIPTION]` placeholder: "`lite.py` swaps the brief in here. The prompt never changes. The brief does."
- Ask: "If I change the brief to a to-do list, what changes? What stays the same?"

## 4. Run it live (10 min)

Start `uv run python lite.py water-tracker.md` and narrate while it runs:

- **After step 1 (design):** "The design took about N tokens in and M out."
- **During the pause:** "Why are we waiting? The free tier lets us use about 8,000 tokens a minute, so the program spaces its requests out."
- **After step 2 (build):** "Look at the input count. It's bigger than step 1. Why?" (Because we sent the design along with the brief.)
- **After step 3 (verify):** "Bigger again: brief plus design plus code."

## 5. Teach tokens (5 min)

Do this on the board while the run is going.

- A token is a piece of a word. In plain English, about 4 characters.
- **Both directions count:** what we send (input) and what the model writes back (output).
- Code, tables and diagrams use more tokens per character than plain prose.
- Free tier: about 8,000 tokens per minute and about 200,000 per day. Paid plans bill per token, and output usually costs more than input.
- **The lesson:** every step passes forward what came before, so input grows with each step. That is why long pipelines get expensive, and why we trim what we pass along (`MAX_EARLIER`). Real systems have a token budget.

## 6. Open the result (5 min)

- Open `output_lite\<timestamp>\index.html` and try it:
  - Click +250, then +500.
  - Type 0, then -5, then 5000. Each should show an error.
  - Reload the page. The total should still be there (localStorage).
- Open `3_verify.md`: "The tester agent says PASS or FAIL for each requirement. Did it get it right? Does the page agree?"

**Real example from tonight's run (use it if yours matches):**

- The verifier marked every requirement PASS, then listed one bug of its own: typing `150.5` is silently turned into `150` by `parseInt`.
- Ask the class: "Is a verifier that says PASS good enough?" The answer is no, because the same kind of model wrote the code and checked it.
- There may be more bugs the verifier missed. For example, the page builds "today" from a UTC timestamp (`toISOString`), so in the evening in Chicago it can already show tomorrow's date. And the streak shows 0 until today's goal is met, even if yesterday's was. Let students find these by testing.

## 7. Close with the engineering questions (5 min)

- "What can go wrong when an AI writes the code?" (Wrong output, a missed rule, invented requirements, quiet bugs.)
- "What catches it, or what should have?" (Verification, real unit tests, a human reading the code.)
- "What would you change in the prompts to prevent today's bug?" (Add a test case for decimals, or ask for tests to be run, not just described.)
- **Preview of next week:** the same idea with a router, an AI that decides which prompt goes next. Two versions:
  - **Free:** keep it small and slow to stay within the limits.
  - **Paid (a few dollars):** more room per request, so fewer retries and better results.

---

## Quick reference

| Thing | Value |
|---|---|
| Run it | `uv run python lite.py water-tracker.md` |
| Output | `output_lite\<timestamp>\` (`1_design.md`, `2_build.md`, `3_verify.md`, `index.html`) |
| Model | `openai/gpt-oss-120b` on Groq (free tier) |
| Wait between steps | 40 seconds |
| Tests | `uv run pytest` |
| If rate-limited | wait a minute and run again; the program retries on its own |
