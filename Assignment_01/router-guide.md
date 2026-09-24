# Building Your First Router

Your agent from Part 2 has exactly one tool — it either uses it or it
doesn't. A **router** is an agent with more than one tool available,
whose job is to figure out *which one* (if any) fits the task in front of
it. This is the same reason → act → observe idea, generalized twice:

1. More than one tool is registered, so the model has to choose
2. Instead of a single if-check, the loop keeps going — act, look at the
   result, decide what to do next — until the model is ready to answer

This is the actual mechanism behind the orchestrator we've been building
toward all semester. Today's version has two bare Python functions as its
"tools." Later, some of those tools will be full structured prompts from
our library instead of simple functions — but the routing logic barely
changes.

**Prerequisites:** Complete Part 2 (`groq-agent-guide.md`) first. This
guide reuses `calculate_average` and adds a second tool.

---

## Step 0: Set up `router.py`

Copy the setup from `agent.py` into a new file so `router.py` is
self-contained:

```python
import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MODEL = "openai/gpt-oss-120b"
```

Also copy over your `calculate_average` function and its tool
description from `agent.py` — you'll register it alongside the new tool
below.

---

## Step 1: A second tool

Add this to a new file, `router.py` (don't just edit `agent.py` — keep
both, since we'll compare them):

```python
def check_password_strength(password):
    """Assess a password's strength and return a rating plus any issues found."""
    issues = []
    if len(password) < 8:
        issues.append("shorter than 8 characters")
    if not any(c.isupper() for c in password):
        issues.append("no uppercase letter")
    if not any(c.islower() for c in password):
        issues.append("no lowercase letter")
    if not any(c.isdigit() for c in password):
        issues.append("no digit")
    if not any(not c.isalnum() for c in password):
        issues.append("no special character")

    if not issues:
        rating = "strong"
    elif len(issues) <= 2:
        rating = "moderate"
    else:
        rating = "weak"

    return {"rating": rating, "issues": issues}
```

Notice this function has nothing to do with `calculate_average` — that's
deliberate. A router with two similar tools makes it hard to tell whether
routing actually worked; two clearly different tools make a wrong choice
obvious immediately.

## Step 2: Register both tools

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "calculate_average",
            "description": "Calculate the average of a list of numeric scores.",
            "parameters": {
                "type": "object",
                "properties": {
                    "scores": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "The list of numeric scores to average.",
                    }
                },
                "required": ["scores"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_password_strength",
            "description": "Assess the strength of a password and list any issues found (length, missing character types).",
            "parameters": {
                "type": "object",
                "properties": {
                    "password": {
                        "type": "string",
                        "description": "The password to assess.",
                    }
                },
                "required": ["password"],
            },
        },
    },
]

available_functions = {
    "calculate_average": calculate_average,
    "check_password_strength": check_password_strength,
}
```

The model only ever sees the `description` fields — it has no idea what
your code actually does beyond what you write here. If two tools have
vague or overlapping descriptions, expect the router to guess wrong.

## Step 3: Generalize the loop

This is the same shape as `agent.py`'s loop, with one real change: a
`for` loop that keeps going (up to a safety limit) instead of stopping
after one round.

```python
MAX_STEPS = 5  # safety cap so a confused loop can't run forever

def run_router(user_prompt):
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Use tools when they help you answer accurately. Only use a tool when it's actually relevant."},
        {"role": "user", "content": user_prompt},
    ]

    for _ in range(MAX_STEPS):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if not tool_calls:
            return response_message.content

        messages.append({
            "role": "assistant",
            "content": response_message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                }
                for tc in tool_calls
            ],
        })

        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            function_to_call = available_functions[function_name]
            result = function_to_call(**function_args)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": json.dumps(result),
            })

        # Loop continues: the model sees the tool result and decides what's next.

    return "Reached the step limit without a final answer -- something may be looping."
```

**Why the safety cap matters:** without `MAX_STEPS`, a model that gets
confused (or a tool that returns something the model keeps trying to "fix"
by calling more tools) could loop indefinitely, burning API calls the
whole time. This is a small taste of the "design for failure" idea from
earlier in the semester, applied to your own code.

## Step 4: Test all three cases

```python
if __name__ == "__main__":
    print("--- Should route to calculate_average ---")
    print(run_router("What's the average of these exam scores: 80, 90, 70, 100?"))

    print("\n--- Should route to check_password_strength ---")
    print(run_router("Is 'hunter2' a strong password?"))

    print("\n--- Should need no tool at all ---")
    print(run_router("What is the capital of France?"))
```

Run it:

```bash
uv run router.py
```

You should see the model correctly pick `calculate_average` for the
first prompt, `check_password_strength` for the second, and answer the
third directly with no tool call at all.

---

## What you just built

This is genuinely the same pattern behind every "agent" and "router" idea
discussed all semester:

- **Reason** — the model looks at the prompt and the available tools
- **Act** — it requests a specific tool with specific arguments
- **Observe** — your code runs the tool and reports the result back
- **Repeat or respond** — the model either asks for another tool, or
  gives a final answer

The only thing that changes as this project grows is the **size of the
`tools` list and `available_functions` dictionary** — the loop itself
barely needs to change. That's worth sitting with: the same 40 lines of
control flow you just wrote will still be doing the routing work when
there are ten tools instead of two.

---

## Troubleshooting

| Problem | Likely fix |
|---|---|
| Router always picks the same tool, even when it shouldn't | Check both tool `description` fields — vague or overlapping descriptions are the most common cause |
| `KeyError` in `available_functions` | The model returned a tool name that doesn't exactly match a key in your dictionary — print `function_name` to check for typos or mismatched casing |
| Loop hits `MAX_STEPS` every time | Print `tool_calls` and `response_message.content` inside the loop to see what the model is actually doing at each step |
| Works for one prompt but not others in the same run | Make sure you're starting a **fresh** `messages` list for each call to `run_router` — reusing one across prompts will confuse the model with leftover history |

---

## Recommended next step: test your tools with pytest

Your tool functions (`calculate_average`, `check_password_strength`) are
just plain Python functions — test them the same way you tested
`calculate_average` back in the pytest lecture, no API or mocking needed:

```python
# tests/test_tools.py
from router import calculate_average, check_password_strength

def test_average_of_scores():
    assert calculate_average([80, 90, 70, 100]) == 85.0

def test_weak_password_flagged():
    result = check_password_strength("hunter2")
    assert result["rating"] == "weak"

def test_strong_password_passes():
    result = check_password_strength("Tr0ub4dor!X9")
    assert result["rating"] == "strong"
```

This is deliberately separate from testing the *router's* choice of tool
— testing "does the model pick the right tool" is a different, harder
problem (the model's behavior isn't fully deterministic) than testing
"does this tool function compute the right answer." Keep those two
concerns separate as this project grows.
