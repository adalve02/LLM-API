# Messy-to-Structured: Sales Notes → JSON

A small hands-on project exploring how to reliably turn unstructured 
text into structured data using an LLM API.

## What it does
Takes free-text sales call notes (the kind a rep might jot down after 
a call) and uses the Claude API to extract a consistent JSON record:
company name, contact name, estimated volume, timeline, lead quality 
signal, and next step.

## Why
Raw LLM output can't always be trusted blindly — models can miss 
fields, misformat output, or occasionally hallucinate. This project 
focuses as much on **validating** the output as generating it:
- The prompt constrains the model to return *only* JSON matching a 
  defined schema (no free text)
- A validation step confirms the response actually parses as valid 
  JSON
- Required fields are checked before the record would be considered 
  safe to use downstream — anything incomplete gets flagged for 
  human review instead of silently passed along

## Setup
1. Get an API key from [console.anthropic.com](https://console.anthropic.com/)
2. `pip install anthropic`
3. `export ANTHROPIC_API_KEY="your-key-here"`
4. `python messy_to_structured.py`

## Example
Input: a paragraph of loose sales call notes  
Output: a clean, validated JSON record — or a flag if something's missing
