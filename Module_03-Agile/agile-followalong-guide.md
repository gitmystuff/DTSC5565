# XP in Practice: Story → Task → Test → AI
### A Follow-Along Guide for Pairs

**Time budget:** ~60–90 minutes total. Suggested pacing is noted at each step — don't linger past it. It's fine to be imperfect; the point is to practice the *thinking*, not to produce a polished product.

**Roles:** Pick a Driver (types/talks to the AI) and a Navigator (reads, questions, catches mistakes). **Swap roles at the halfway point** — after Step 2, before Step 3.

Throughout this guide, we'll show a **worked example** in shaded callouts, based on this story:

> *"As a user, I want to calculate the total runtime of a road trip playlist from a collection of song durations, and be warned if any single track takes up more than half of the total listening time."*

Your story will be different. Use the worked example to see the *pattern*, not to copy the specifics.

---

## Step 0 — Read your story out loud (2 minutes)

Before doing anything else, both partners should read the generated story together and answer out loud:

- Who is the "user" in this story, and what do they actually want?
- What's the **normal case** — the thing that happens most of the time?
- What's the **one edge case or warning condition** built into the story? (Every generated story has exactly one — find it before moving on.)

> **Worked example:**
> - User: someone building a road trip playlist
> - Normal case: add up song durations to get a total time
> - Edge case: warn if one track is "too big" relative to the rest (over half the total)

If you can't answer all three, re-read the story before continuing — don't move to Step 1 until you can.

---

## Step 1 — Break the story into task cards (10–15 minutes)

### What a "task" actually is

A task is **one distinct, independently-testable piece of behavior**. A useful test: *"Could I write a single, focused test for this on its own, without needing the rest of the story to make sense?"* If yes, it's probably a task. If you find yourself needing three sentences to describe it, it's probably two tasks.

### How to find your tasks

Go sentence by sentence (or clause by clause) through your story and ask, for each piece:

1. Is this describing the **main/expected behavior**? → That's usually Task 1.
2. Is this describing a **calculation or lookup** the main behavior depends on? → That's often its own task, especially if it could be reused elsewhere.
3. Is this a **check, warning, or validation rule**? → This is almost always its own task, separate from the behavior it's checking. (This is the "dose-checking" pattern from the medication example — validation logic gets pulled out on its own.)

A good target for this activity is **2–4 tasks**. Fewer than 2 and you probably haven't separated the edge case out; more than 4 and you're likely overcomplicating a low-stakes exercise.

### Write your tasks down

For each task, write:
- A short title (a few words)
- One sentence describing what it does
- One sentence describing what "correct" looks like for it

> **Worked example — task breakdown:**
>
> **Task 1: Calculate total runtime**
> What it does: Add up all song durations to get the playlist's total time.
> Correct looks like: Given a list of durations, returns their sum.
>
> **Task 2: Find the longest track's share**
> What it does: Determine what fraction of the total one track represents.
> Correct looks like: Given a list of durations, returns the largest single duration divided by the total.
>
> **Task 3: Warn if imbalanced**
> What it does: Flags whether the longest track exceeds half the total listening time.
> Correct looks like: Returns True/False based on whether Task 2's result is greater than 0.5.
>
> Notice Task 3 depends on Task 2, and Task 2 depends on Task 1 — that's normal. Tasks can build on each other; they just need to be **separately testable**.

**Checkpoint before moving on:** Does one of your tasks correspond to the warning/edge case you identified in Step 0? If not, go back — you likely folded it into another task instead of giving it its own.

---

## Step 2 — Write a pytest test for each task, BEFORE any code exists (15–20 minutes)

This is the step students find hardest to trust, because it feels backwards — you're testing something that doesn't exist yet. That's the point. Writing the test **forces you to decide exactly what "correct" means** before you let an AI (or anyone) start guessing.

### The pattern for every test

```python
def test_<what_you_are_checking>():
    # 1. Set up some sample input
    sample_input = ...

    # 2. Call the function you WISH already existed (pick a name now)
    result = your_function_name(sample_input)

    # 3. Assert what the correct output should be
    assert result == expected_value
```

You are naming functions that don't exist yet — that's normal and intentional. The AI will implement functions matching the names and behavior your tests expect.

### Write at least ONE test per task. For your validation/warning task, write at least TWO:
- One test where the warning should **not** trigger (the normal case)
- One test where the warning **should** trigger (the edge case)

> **Worked example — tests:**
> ```python
> def test_total_runtime():
>     durations = [180, 200, 210, 195]
>     assert calculate_total_runtime(durations) == 785
>
> def test_longest_track_share():
>     durations = [600, 60, 45]
>     assert longest_track_share(durations) == 600 / 705
>
> def test_no_warning_when_balanced():
>     durations = [180, 200, 210, 195]
>     assert check_imbalance(durations) == False
>
> def test_warning_when_one_track_dominates():
>     durations = [600, 60, 45]
>     assert check_imbalance(durations) == True
> ```

### Before moving on, ask each other:

- Did we write at least one test per task?
- Did we test BOTH the "no warning" case and the "warning" case?
- **What about weird inputs we haven't thought about yet?** (An empty playlist? Only one song? A duration of zero or negative?) Jot these down even if you don't write a test for all of them — this list matters later.

**This is your moment to think like the "adversary" from the lecture** — nobody else is going to imagine these edge cases for you. If you skip this, don't be surprised if the AI's implementation has a blind spot exactly where you didn't look.

**★ Swap roles now — Navigator becomes Driver for the rest of the activity.**

---

## Step 3 — Hand the story, tasks, and tests to an AI assistant (10 minutes)

Do **not** ask the AI to design the solution from scratch. Give it everything you've already decided, and ask it only to satisfy what you've specified. Use a prompt shaped like this:

```
Here is a user story, a task breakdown, and a set of pytest tests my
partner and I wrote. Please implement the functions needed so that all
of these tests pass. Do not change the tests. Do not add functionality
beyond what the tests require.

STORY:
[paste your story]

TASKS:
[paste your task list]

TESTS:
[paste your pytest code]
```

This keeps the AI in the implementer role, not the designer role — the design decisions (what counts as correct) were already made by you in Steps 1–2.

---

## Step 4 — Run the tests and evaluate (10 minutes)

Run your pytest file against the AI's implementation.

**If everything passes:** Don't just move on — ask each other *why*. Was it because your tests were thorough? Or could the AI have technically passed your tests while still doing something subtly wrong? (Hint: check this by trying one of the "weird inputs" you jotted down in Step 2 but didn't write a formal test for. Does it still behave sensibly?)

**If something fails:** This is the most valuable outcome of the whole exercise, not a setback. Look at *why* it failed:
- Did the AI misunderstand the story?
- Did your test have a mistake?
- Did the AI satisfy the letter of your test but not what you actually meant?

Write down, in one sentence, what the mismatch reveals about the gap between "what we specified" and "what we actually meant."

---

## Step 5 — Debrief (5 minutes, whole class)

Be ready to discuss as a class:

> *"What we just did — story, task, test-first — is Extreme Programming. If your team were running this same story under pure Scrum instead, what would be missing, and what would you have to decide for yourselves?"*

---

## Quick Reference: The Whole Flow at a Glance

| Step | What you produce | Time |
|---|---|---|
| 0. Read the story | Answers to 3 questions | 2 min |
| 1. Break into tasks | 2–4 task cards | 10–15 min |
| 2. Write tests first | 1+ pytest test per task | 15–20 min |
| 3. Hand off to AI | A prompt with story + tasks + tests | 10 min |
| 4. Run & evaluate | Pass/fail + one sentence on any gap | 10 min |
| 5. Debrief | Class discussion | 5 min |
