"""
se-agent lite -- the whole idea in one small file.

  1. Read the brief (what we want built).
  2. Read the prompts in lite_prompts/ in order: design, build, verify.
  3. Run each prompt. Each one sees the brief and the work done so far.
  4. Save every result, and save the web page the build step wrote.

Usage:   uv run python lite.py water-tracker.md
Needs:   a .env file containing GROQ_API_KEY=...
"""
import re
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

MODEL = "openai/gpt-oss-120b"
PROMPTS = Path(__file__).parent / "lite_prompts"
OUTPUT = Path(__file__).parent / "output_lite"
PAUSE = 40          # seconds between steps; the free tier allows ~8,000 tokens a minute
MAX_EARLIER = 6000  # characters of earlier work we pass along (keeps requests small)


def describe_usage(reply):
    """A one-line token report for a model reply, or '' if it gave none."""
    usage = getattr(reply, "usage", None)
    if usage is None:
        return ""
    return (f"  Tokens: {usage.prompt_tokens:,} in (what we sent) + "
            f"{usage.completion_tokens:,} out (what came back) = {usage.total_tokens:,}")


def ask(client, system_prompt, user_message, max_tokens=3000):
    """One call to the model. Returns the text of its reply.
    If the free tier says "slow down" (error 429), wait and try again."""
    for attempt in range(3):
        try:
            reply = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "system", "content": system_prompt},
                          {"role": "user", "content": user_message}],
                max_tokens=max_tokens,
            )
            report = describe_usage(reply)
            if report:
                print(report)
            return reply.choices[0].message.content
        except Exception as error:
            if getattr(error, "status_code", None) == 429 and attempt < 2:
                print("  Rate limit reached; waiting 30 seconds...")
                time.sleep(30)
                continue
            raise


def extract_html(text):
    """The first ```html code block in a reply, or None."""
    match = re.search(r"```html\s*\n(.*?)```", text, re.DOTALL)
    return match.group(1).strip() + "\n" if match else None


def run(brief, client, pause=PAUSE):
    prompt_files = sorted(PROMPTS.glob("*.md"))
    steps = []                                       # [(name, reply)]
    for i, path in enumerate(prompt_files, start=1):
        print(f"Step {i} of {len(prompt_files)}: {path.stem}")
        system_prompt = path.read_text(encoding="utf-8").replace("[PROJECT_DESCRIPTION]", brief)
        earlier = "\n\n".join(f"### {name}\n{text}" for name, text in steps)
        user_message = "Do the task above."
        if earlier:
            user_message += "\n\nEarlier work:\n" + earlier[-MAX_EARLIER:]
        steps.append((path.stem, ask(client, system_prompt, user_message)))
        if i < len(prompt_files):
            time.sleep(pause)                        # stay under the free tier's limit
    return steps


def save(steps, out_root=OUTPUT):
    folder = Path(out_root) / time.strftime("%Y%m%d-%H%M%S")
    folder.mkdir(parents=True, exist_ok=True)
    for name, text in steps:
        (folder / f"{name}.md").write_text(text, encoding="utf-8")
    for name, text in steps:
        html = extract_html(text)
        if html:
            (folder / "index.html").write_text(html, encoding="utf-8")
    return folder


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: uv run python lite.py <brief-file>")
    load_dotenv()
    brief = Path(sys.argv[1]).read_text(encoding="utf-8").strip()
    steps = run(brief, Groq())
    folder = save(steps)
    print(f"\nSaved to {folder}")
    if (folder / "index.html").exists():
        print(f"Open in your browser: {folder / 'index.html'}")
