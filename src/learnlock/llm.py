"""LLM interface for learn-lock. Uses Groq for extraction, Gemini for evaluation."""

import os
import json

from . import config


def _get_groq_response(prompt: str, system: str = None) -> str:
    """Get response from Groq."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not set")
    
    import litellm
    litellm.suppress_debug_info = True
    
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    
    response = litellm.completion(
        model=f"groq/{config.GROQ_MODEL}",
        messages=messages,
        max_tokens=config.LLM_MAX_TOKENS,
        temperature=config.LLM_TEMPERATURE,
    )
    return response.choices[0].message.content


def _get_gemini_response(prompt: str, system: str = None) -> str:
    """Get response from Gemini."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")
    
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    
    full_prompt = prompt
    if system:
        full_prompt = f"{system}\n\n{prompt}"
    
    model = genai.GenerativeModel(config.GEMINI_MODEL)
    response = model.generate_content(full_prompt)
    return response.text


def _parse_json_response(response: str) -> dict | list:
    """Parse JSON from LLM response, handling markdown code blocks."""
    response = response.strip()
    
    # Handle markdown code blocks
    if response.startswith("```"):
        lines = response.split("\n")
        # Find start and end of code block
        start_idx = 0
        end_idx = len(lines)
        for i, line in enumerate(lines):
            if line.startswith("```") and i == 0:
                start_idx = 1
            elif line.startswith("```") and i > 0:
                end_idx = i
                break
        response = "\n".join(lines[start_idx:end_idx])
        
        # Remove language identifier if present
        if response.startswith("json"):
            response = response[4:].strip()
    
    return json.loads(response)


def extract_concepts(content: str, title: str) -> list[dict]:
    """Extract concepts from content using Groq.
    
    Returns list of {"name": str, "source_quote": str}
    """
    system = """You are a learning assistant that extracts key concepts from educational content.
For each concept, provide the exact quote from the source that explains it."""

    # Truncate content to configured max
    truncated_content = content[:config.CONTENT_MAX_CHARS]
    
    prompt = f"""Extract {config.MIN_CONCEPTS}-{config.MAX_CONCEPTS} key concepts from this content.

TITLE: {title}

CONTENT:
{truncated_content}

Return ONLY valid JSON array:
[
  {{"name": "Concept Name", "source_quote": "Exact quote from content explaining this concept (1-3 sentences)"}},
  ...
]

Rules:
- source_quote MUST be exact text from the content, not paraphrased
- Focus on the most important concepts
- Each quote should be self-contained and understandable"""

    response = _get_groq_response(prompt, system)
    concepts = _parse_json_response(response)
    
    # Validate structure
    valid = []
    for c in concepts:
        if isinstance(c, dict) and "name" in c and "source_quote" in c:
            name = str(c["name"]).strip()
            quote = str(c["source_quote"]).strip()
            if name and quote:
                valid.append({"name": name, "source_quote": quote})
    
    if not valid:
        raise RuntimeError("No valid concepts extracted")
    
    return valid


def evaluate_explanation(concept_name: str, source_quote: str, user_explanation: str) -> dict:
    """Evaluate user's explanation against source.
    
    Tries Gemini first, falls back to Groq if rate limited.
    Returns {"score": 1-5, "covered": [...], "missed": [...], "feedback": str}
    """
    prompt = f"""You are evaluating a student's explanation of a concept.

CONCEPT: {concept_name}

SOURCE (ground truth):
"{source_quote}"

STUDENT'S EXPLANATION:
"{user_explanation}"

Compare the student's explanation to the source.

Return ONLY valid JSON:
{{
  "score": <{config.SCORE_MIN}-{config.SCORE_MAX}>,
  "covered": ["key point 1 they got right", "key point 2 they got right"],
  "missed": ["key point 1 they missed", "key point 2 they missed"],
  "feedback": "One sentence summary of their understanding"
}}

Scoring guide:
{config.SCORE_MIN} = Completely wrong or empty
2 = Missed most key points
3 = Got the gist, missed important details
4 = Good understanding, minor gaps
{config.SCORE_MAX} = Fully captured the concept

Be strict but fair. Vague language instead of precise terms counts as partial miss."""

    # Try Gemini first, fallback to Groq
    response = None
    last_error = None
    
    for get_response in [_get_gemini_response, _get_groq_response]:
        try:
            response = get_response(prompt)
            break
        except Exception as e:
            last_error = e
            continue
    
    if not response:
        return {
            "score": config.DEFAULT_FALLBACK_SCORE,
            "covered": [],
            "missed": [],
            "feedback": f"Evaluation unavailable: {last_error}"
        }
    
    try:
        result = _parse_json_response(response)
        
        # Validate and normalize score to configured range
        score = int(result.get("score", config.DEFAULT_FALLBACK_SCORE))
        score = max(config.SCORE_MIN, min(config.SCORE_MAX, score))
        
        return {
            "score": score,
            "covered": result.get("covered", []),
            "missed": result.get("missed", []),
            "feedback": str(result.get("feedback", ""))
        }
        
    except Exception as e:
        return {
            "score": config.DEFAULT_FALLBACK_SCORE,
            "covered": [],
            "missed": [],
            "feedback": f"Parse error: {e}"
        }
