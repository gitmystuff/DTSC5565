# Lab 1: GitHub Fundamentals — Fork It, Run It, Trust It

**DTSC 4565/5565 — Software Engineering for Data Scientists**
**Companion to:** Chapter 1, Introduction

---

## Why this lab

Chapter 1 makes a case for software engineering as a *discipline* — not just writing code, but building it in a way that's maintainable, dependable, and trustworthy. It's easy to nod along with that in the abstract. This lab makes it concrete before we've written a single line of data science code.

You're going to fork a small, already-finished project — a classifier for the classic Iris dataset — and get it running in two different states:

1. **`exploration.ipynb`** — the notebook phase. Data loading, model building, and evaluation, all mixed together. This is how most of us learned to do data science, and it's genuinely useful for figuring things out.
2. **`iris_classifier/` + `tests/`** — the *same logic*, refactored into separate, independently testable modules with a passing test suite.

Nothing in the notebook is "wrong." But notice which one you'd trust handing off to a teammate, deploying to production, or maintaining six months from now. That gap — notebook-you versus production-you — is the gap this course closes.

**Ties to Ch1:** this lab is your first hands-on look at two of the "Essential attributes of good software" from the slides — **maintainability** and **dependability** — and a preview of the "Software process activities" (specification → development → validation → evolution) you'll cycle through all semester.

---

## Before you start

- A free [GitHub account](https://github.com/join). If you already have one, use it.
- A modern browser. That's it — no local Python install needed for this lab.

---

## Step 1: Fork the repo

1. Go to **[github.com/gitmystuff/iris-classifier](https://github.com/gitmystuff/iris-classifier)**.
2. Click **Fork** (top right).
3. Fork it into your own account. You now own a full copy — changes here never touch the original.

**Why this matters:** forking is how you get a personal, isolated copy of someone else's work without asking permission. It's the foundation of nearly every collaborative workflow you'll use this semester — team projects, pull requests, code review all build on this.

---

## Step 2: Turn on the in-browser runner

Your fork includes a small page (`docs/index.html`) that can run `main.py` and your `pytest` suite *directly in your browser* — no local Python install. It's off by default per-fork; you switch it on once.

1. On **your forked repo's** GitHub page, click **Settings**.
2. In the left sidebar, click **Pages**.
3. Under **Build and deployment → Source**, choose **Deploy from a branch**.
4. Set **Branch** to `main`, folder to **`/docs`**.
5. Click **Save**.

Wait about a minute — GitHub will show you a green box with your page's address:

```
https://<your-username>.github.io/iris-classifier/
```

---

## Step 3: Point the page at your fork

The page defaults to looking at the original `gitmystuff` repo, not yours. Two options:

- **Quick (do it every time):** open your page, type your GitHub username into the box next to the GitHub logo, click **Load repo**.
- **Permanent (recommended):** edit `docs/index.html` in your fork (via [vscode.dev](https://vscode.dev/github/YOUR-USERNAME/iris-classifier) — no install needed) so it opens already pointed at you. Find the line containing `value="gitmystuff"` and replace `gitmystuff` with your own username. Commit and push using the Source Control panel.

---

## Step 4: Run it

Open your page's address from Step 2.

1. Wait for the green **"Python runtime ready"** status (first load is slow — it's downloading a Python environment into your browser).
2. Click **Load repo**.
3. Click **▶ Run main.py** — this runs the refactored, modular version of the classifier.
4. Click **▶ Run pytest** — this runs the test suite against it.

If you get a red error, read it — it usually names the exact file. Most common first-run issues: your fork isn't public, or your username was typo'd.

---

## Step 5: Compare the two versions

Open both files in [vscode.dev](https://vscode.dev/github/YOUR-USERNAME/iris-classifier) (browser-based VS Code — the same editor you'll use locally later in the course):

- `exploration.ipynb`
- `iris_classifier/` (four files: `data.py`, `model.py`, `evaluate.py`, `predict.py`) + `tests/` (one test file per module)

**Reflection — answer these in a few sentences each, and bring them to class:**

1. In the notebook, if you changed how the data is split, how many places would you have to check to make sure nothing else broke? In the modular version?
2. `tests/test_model.py` exists specifically to check `model.py` in isolation. What does that buy you that manually re-running the notebook top-to-bottom doesn't?
3. Chapter 1 draws a line between **generic products** (owned by the developer) and **customized products** (owned by the customer). Which category does *this repo* fall into, and which category will your team's semester project fall into? What does that change about who decides when something's "done"?

---

## What's next

This fork-and-run workflow — notebook → tests → modules — is the shape of every project you'll build this semester. As the tool stack grows (Git branching, Docker, GitHub Actions, Postman), we'll build out a more capable version of this "browser IDE" together, chapter by chapter, rather than dropping it on you all at once.

For now: keep your fork. You'll be extending it.
