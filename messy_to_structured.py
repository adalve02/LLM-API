"""
A minimal example: calling the Claude API to turn messy, unstructured
text into structured JSON output.

This mirrors what Gertex's "Reporting Agent" and "AI Prototyping" work
actually need: take unreliable/free-text input, produce consistent,
structured output that another system (or person) can rely on.

To run this yourself:
1. Get an API key from https://console.anthropic.com/ (free tier available)
2. Set it as an environment variable: export ANTHROPIC_API_KEY="your-key-here"
3. Run: python messy_to_structured.py
"""

import os
import json
import anthropic

client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY")
)

# Example: messy sales call notes -> structured Salesforce-style record
# This is the exact shape of problem the job posting describes:
# "sales call recordings and meeting notes are transcribed, summarized,
# and converted into structured Salesforce records"

messy_input = """
Had a call with Sarah from Northwind Logistics today. They're looking
at about 500 units/month of the corrugated boxes, similar to what we
quoted Meridian last quarter. Budget seems flexible, she mentioned Q4
timeline. Wants a follow up call next week with their ops lead. Seemed
pretty serious, not just browsing - already compared us to two other
vendors and liked our turnaround time best.
"""

# The key technique: constrain the output with an explicit schema in
# the prompt, and ask for ONLY JSON back — nothing else — so the
# response is reliably parseable.
system_prompt = """You are a data extraction assistant. Given free-text
sales call notes, extract structured information and respond with
ONLY a JSON object, no other text, matching this exact schema:

{
  "company_name": string,
  "contact_name": string,
  "estimated_volume": string,
  "timeline": string,
  "lead_quality_signal": "low" | "medium" | "high",
  "next_step": string
}

If a field isn't mentioned, use null. Do not include any text outside
the JSON object."""

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=500,
    system=system_prompt,
    messages=[
        {"role": "user", "content": messy_input}
    ]
)

raw_text = response.content[0].text

# Validation step: don't trust the output blindly, confirm it's
# actually valid JSON matching what we expect before using it downstream.
try:
    structured = json.loads(raw_text)
    print("Successfully parsed structured output:")
    print(json.dumps(structured, indent=2))

    # A real pipeline would validate required fields here too, e.g.:
    required_fields = ["company_name", "lead_quality_signal", "next_step"]
    missing = [f for f in required_fields if structured.get(f) is None]
    if missing:
        print(f"\nWarning: missing required fields {missing} — would flag for human review")
    else:
        print("\nAll required fields present — safe to write downstream")

except json.JSONDecodeError:
    print("Model did not return valid JSON — would flag for retry or human review")
    print("Raw output:", raw_text)
