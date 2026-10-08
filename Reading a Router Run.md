# Reading a Router Run

Oct 8, 2026 · @Clifford K Whitworth

## The setup lines

The first nine lines of the log are `uv` preparing the project, and none of them is an error.

- **"Ignoring existing virtual environment... non-existent Python interpreter."** The `.venv` folder was made on another machine or Python install, so `uv` threw it away and built a new one. That is the right behavior.
- **"Failed to hardlink files; falling back to full copy."** A harmless warning, shown because the project lives on Google Drive (`G:`). Installing is a little slower, nothing else.
- **"Installed 15 packages."** `uv` installed `groq`, `python-dotenv` and their dependencies, so nobody had to run `pip install`.

## What the router did

The router chose its own agents, passed work between them without the agents knowing, and sent one agent back to redo its work. These are the steps, in log order.

1. **Discovery (log lines 10-18).** The router scanned `prompts/` and found two agents. For each it read only the Role and Task sentences, which is all the router knows about them.
2. **First agent (line 20).** It picked `ch05_process_model` and gave a reason: models come before architecture. Nobody told it that order. It read the two job descriptions and the project and decided.
3. **Step 1 ran (lines 22-340).** The Ch5 agent wrote UML models and a traceability matrix. It noted that no requirements document existed, invented placeholder IDs (R-01 to R-05), and flagged that itself in Requirement Feedback (FB-01). That is the prompt's "record it, don't silently guess" rule working.
4. **Handoff (line 342).** The router judged the models complete and chose the architect next.
5. **Earlier work passed in (lines 345-347).** The log says "Earlier work passed in from: ch05\_process\_model". The architect never knew Ch5 existed. The router put Ch5's output in front of it.
6. **Loop back (line 625).** The architect's output was cut off partway. The router noticed it was incomplete and sent `ch06` to run a second time. A fixed A-then-B script cannot do that.

## What went wrong

The crash at step 3 was a size limit, not a logic bug: Groq's free tier allows 8,000 tokens per minute, and the request asked for 10,495 (log lines 632-652).

The request was too big because it carried both earlier outputs, which were already long, plus the prompt itself. Truncation made things worse. Each reply is capped at `max_tokens=4096`, and these prompts ask for very long documents. That is why the Ch5 verification table stops mid-sentence ("State diagrams have start state") and Ch6 ends at section 12.5.

Two lessons for beginners:

- **A model can only see and write so much at once.** Chaining agents makes each handoff bigger, so the more you pass forward, the sooner you hit a limit.
- **The error message states the problem.** "Limit 8000, Requested 10495" says exactly what happened and by how much.

## A discussion point: self-checks are not verification

The Ch5 agent reported its own checks as passing, including "all Mermaid blocks render." But some of its diagrams use `end` as a node name (`P --> end([End])`), and `end` is a reserved word in Mermaid that is likely to break rendering. This has not been rendered to confirm, so test it in class.

The point for students: a model grading its own work is not real verification. A real check would render the diagrams, or a separate step would look at the result.

## Fixing the crash

Two changes to `prompt_router.py` would stop the crash and keep the loop-back behavior.

- **Send less to each agent.** Pass a shortened summary of earlier work instead of the full document, so a request stays under the 8,000-token limit.
- **Wait and retry on rate limits.** When Groq returns a 413 or 429 error, pause briefly and try again instead of stopping the run.

These changes are not made yet; they are the proposed next step.
