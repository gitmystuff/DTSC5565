# Building Your First Agent with Groq

This walks you through writing a small agent: a script that sends a
prompt to a model, and lets the model decide on its own whether it needs
to call a tool (a Python function) to answer accurately.

This is the mechanism behind everything we've called "agents" all
semester — reason, act, observe, respond. Today you're building the
simplest possible version of that loop, by hand, so you understand
exactly what's happening before we build something that chooses between
multiple tools.

**Prerequisites:** Complete `vscode-uv-setup-guide.md` first — you need a
working project with `groq` and `python-dotenv` installed, and your
`GROQ_API_KEY` in a `.env` file.

---

## Step 1: The simplest possible call

Before adding any tools, confirm you can talk to the model at all.

> **Note on the model name:** Groq's available models change over time —
> models get deprecated, moved to enterprise-only tiers, or replaced.
> `openai/gpt-oss-120b` is Groq's current flagship production model on
> the free/developer tier as of this writing. If you get an
> authorization or "model not found" error, check
> **console.groq.com/docs/models** for what's currently available, or
> run this to list models your key actually has access to:
> ```bash
> curl -X GET "https://api.groq.com/openai/v1/models" \
>      -H "Authorization: Bearer $GROQ_API_KEY"
> ```

Create `hello_agent.py`:

```python
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {"role": "user", "content": "In one sentence, what is an AI agent?"}
    ],
)

print(response.choices[0].message.content)
```

Run it:

```bash
uv run hello_agent.py
```

If you see a sentence printed back, your key and environment are working.
If not, check the Troubleshooting section at the bottom.

---

## Step 2: Give the model a tool it can choose to use

A "tool" is just a Python function, described to the model in a specific
format so it knows the tool exists, what it does, and what arguments it
takes. The model never runs your code directly — it tells you *which*
tool it wants and with *what arguments*, and your code is responsible for
actually running it.

Create `agent.py`:

```python
import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

MODEL = "openai/gpt-oss-120b"


# --- The tool our agent can call ---
def calculate_average(scores):
    """Return the average of a list of numeric scores, rounded to one decimal."""
    return round(sum(scores) / len(scores), 1)


# --- Describe that tool to the model, in the format it expects ---
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
    }
]

# So we can map a tool name back to the real Python function that runs it
available_functions = {
    "calculate_average": calculate_average,
}
```

Notice the `description` fields — this is the *only* information the
model has about what your tool does and when to use it. A vague
description leads to a model that either never uses the tool or uses it
at the wrong times. This is the same discipline as writing a good
docstring, just read by a model instead of a person.

---

## Step 3: The reason → act → observe loop

Now the actual agent logic. Append this to `agent.py`:

```python
def run_agent(user_prompt):
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Use tools when they help you answer accurately."},
        {"role": "user", "content": user_prompt},
    ]

    # Step 1: send the prompt, telling the model which tools are available
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # Step 2: did the model decide it needs a tool?
    if not tool_calls:
        # No tool needed -- just return its direct answer
        return response_message.content

    # Step 3: the model wants to call a tool. Add its request to the
    # conversation as a plain dict (not the raw SDK object), then actually
    # run the corresponding Python function.
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

        # Feed the tool's result back into the conversation
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": function_name,
            "content": json.dumps(result),
        })

    # Step 4: send the conversation (now including the tool's result) back
    # to the model so it can produce a final, natural-language answer.
    second_response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
    )
    return second_response.choices[0].message.content


if __name__ == "__main__":
    print("--- Prompt that should NOT need the tool ---")
    print(run_agent("What is the capital of France?"))

    print("\n--- Prompt that SHOULD trigger the tool ---")
    print(run_agent("What's the average of these exam scores: 80, 90, 70, 100?"))
```

**A detail worth pausing on:** in Step 3, the assistant's tool-call
request gets appended as a plain dictionary, not the raw object the SDK
returned. This matters — the *second* call to the model needs the full
conversation history in a consistent format, and mixing SDK objects into
that list will break the follow-up call. This is a real, easy mistake to
make when building this for the first time.

Run it:

```bash
uv run agent.py
```

## Step 4: What you should see

For the France question, the model should answer directly — no tool
involved, since it doesn't need one. For the exam scores question, three
things happen behind the scenes:

1. The model receives your question plus the tool description, and
   responds with "please call `calculate_average` with these arguments"
   instead of an answer
2. Your code actually runs `calculate_average([80, 90, 70, 100])`,
   getting `85.0`
3. That result is sent back to the model, which now writes a final,
   natural-language answer referencing the real, correctly computed number

That three-step shape — reason, act, observe — is the same loop behind
every agent we've discussed this semester, including where we're headed
next: a router that chooses between *several* tools instead of just one.

---

## Troubleshooting

| Problem | Likely fix |
|---|---|
| `groq.AuthenticationError` | Double-check your `.env` file has the exact key from console.groq.com, with no extra quotes or spaces |
| `KeyError` on `GROQ_API_KEY` | Confirm `load_dotenv()` runs before you read the environment variable, and that `.env` is in the same folder you're running the script from |
| The model never calls the tool, even for the average question | Try rephrasing the prompt more explicitly, or check that `tools=tools` and `tool_choice="auto"` are actually being passed in the first API call |
| `json.JSONDecodeError` when parsing arguments | Print `tool_call.function.arguments` before parsing it to see the raw string — this usually reveals a malformed tool description |
| Second API call fails or behaves oddly | Check that you appended a plain dict for the assistant's tool-call message, not the raw SDK object (see the callout above) |

---

## What's next

This agent has exactly one tool and no way to choose between options —
it either uses `calculate_average` or it doesn't. Next, in `router-guide.md`,
we'll add a second tool and generalize this same loop so the model can
choose between them — your first router.
