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

if __name__ == "__main__":
    print("--- Should route to calculate_average ---")
    print(run_router("What's the average of these exam scores: 80, 90, 70, 100?"))

    print("\n--- Should route to check_password_strength ---")
    print(run_router("Is 'hunter2' a strong password?"))

    print("\n--- Should need no tool at all ---")
    print(run_router("What is the capital of France?"))