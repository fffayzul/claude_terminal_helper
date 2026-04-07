import json
import anthropic

client = anthropic.Anthropic()

SYSTEM = """You are an expert terminal assistant. The user will describe what they want to do in plain English.
Your job is to translate their request into an exact shell command for their OS.

You MUST respond with a valid JSON object and nothing else:
{{
  "command": "<the exact shell command to run>",
  "explanation": "<one sentence explaining what the command does>",
  "dangerous": <true if the command could delete, overwrite, or cause irreversible changes, otherwise false>
}}

OS context:
{context}
"""


def interpret(user_request: str, context_summary: str) -> dict:
    """Ask Claude to turn a plain-English request into a shell command."""
    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=512,
        system=SYSTEM.format(context=context_summary),
        messages=[{"role": "user", "content": user_request}],
    )

    raw = response.content[0].text.strip()

    # Strip markdown code fences if Claude wraps the JSON
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "command": None,
            "explanation": raw,
            "dangerous": False,
        }
