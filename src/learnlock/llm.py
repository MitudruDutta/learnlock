"""LLM interface for learn-lock. Uses Groq for extraction, Gemini for evaluation."""

import os
import json
import re

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


def _extract_json_from_response(response: str) -> str:
    """Extract JSON from LLM response, handling various formats."""
    response = response.strip()
    
    # Try to find JSON in markdown code blocks
    code_block_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', response)
    if code_block_match:
        return code_block_match.group(1).strip()
    
    # Try to find JSON array or object directly
    array_match = re.search(r'(\[[\s\S]*\])', response)
    if array_match:
        return array_match.group(1)
    
    obj_match = re.search(r'(\{[\s\S]*\})', response)
    if obj_match:
        return obj_match.group(1)
    
    return response


def _parse_json_response(response: str) -> dict | list:
    """Parse JSON from LLM response with robust error handling."""
    json_str = _extract_json_from_response(response)
    
    # Try direct parse
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        pass
    
    # Try fixing common issues - remove trailing commas
    json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        pass
    
    # Last resort: try to extract individual objects
    try:
        objects = re.findall(r'\{[^{}]*\}', json_str)
        if objects:
            parsed = []
            for obj in objects:
                try:
                    parsed.append(json.loads(obj))
                except:
                    continue
            if parsed:
                return parsed
    except:
        pass
    
    raise ValueError("Could not parse JSON from response")


def extract_concepts(content: str, title: str) -> list[dict]:
    """Extract concepts from content using Groq.
    
    Returns list of {"name": str, "source_quote": str}
    """
    system = """You are a learning assistant. Extract key concepts and return valid JSON only.
Never include special characters or newlines inside JSON strings."""

    # Truncate and clean content
    truncated_content = content[:config.CONTENT_MAX_CHARS]
    truncated_content = truncated_content.replace('"', "'").replace('\n', ' ').replace('\r', ' ')
    truncated_content = re.sub(r'\s+', ' ', truncated_content)

    prompt = f"""Extract {config.MIN_CONCEPTS}-{config.MAX_CONCEPTS} key concepts from this content.

TITLE: {title}

CONTENT:
{truncated_content[:config.CONTENT_TRUNCATE_FOR_PROMPT]}

Return ONLY a valid JSON array with this exact format:
[
  {{"name": "Short Concept Name", "source_quote": "Brief quote from content"}},
  {{"name": "Another Concept", "source_quote": "Another brief quote"}}
]

IMPORTANT: 
- Keep quotes SHORT (under {config.MAX_QUOTE_LENGTH} characters)
- No special characters or newlines in strings
- Return ONLY the JSON array, nothing else"""

    last_error = None
    for attempt in range(config.EXTRACTION_MAX_RETRIES + 1):
        try:
            response = _get_groq_response(prompt, system)
            concepts = _parse_json_response(response)
            
            # Validate structure
            valid = []
            for c in concepts:
                if isinstance(c, dict) and "name" in c and "source_quote" in c:
                    name = str(c["name"]).strip()[:config.MAX_CONCEPT_NAME_LENGTH]
                    quote = str(c["source_quote"]).strip()[:config.MAX_QUOTE_LENGTH]
                    if name and quote:
                        valid.append({"name": name, "source_quote": quote})
            
            if valid:
                return valid
            
            last_error = "No valid concepts in response"
        except Exception as e:
            last_error = str(e)
            continue
    
    raise RuntimeError(f"Concept extraction failed after {config.EXTRACTION_MAX_RETRIES + 1} attempts: {last_error}")


def evaluate_explanation(concept_name: str, source_quote: str, user_explanation: str) -> dict:
    """Evaluate user's explanation against source.
    
    Tries Gemini first, falls back to Groq if rate limited.
    Returns {"score": 1-5, "covered": [...], "missed": [...], "feedback": str}
    """
    # Clean and truncate inputs
    concept_name = concept_name[:config.MAX_CONCEPT_NAME_LENGTH]
    source_quote = source_quote[:config.MAX_QUOTE_LENGTH]
    user_explanation = user_explanation[:config.MAX_EXPLANATION_LENGTH]
    
    prompt = f"""Evaluate this student explanation.

CONCEPT: {concept_name}

SOURCE (ground truth):
"{source_quote}"

STUDENT'S EXPLANATION:
"{user_explanation}"

Return ONLY valid JSON:
{{"score": <{config.SCORE_MIN}-{config.SCORE_MAX}>, "covered": ["point1", "point2"], "missed": ["point1"], "feedback": "One sentence"}}

Scoring: {config.SCORE_MIN}=wrong, {config.SCORE_MAX}=excellent"""

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
        
        # Validate and normalize score
        score = int(result.get("score", config.DEFAULT_FALLBACK_SCORE))
        score = max(config.SCORE_MIN, min(config.SCORE_MAX, score))
        
        covered = result.get("covered", [])
        if not isinstance(covered, list):
            covered = [str(covered)] if covered else []
        
        missed = result.get("missed", [])
        if not isinstance(missed, list):
            missed = [str(missed)] if missed else []
        
        return {
            "score": score,
            "covered": [str(c)[:config.MAX_COVERED_MISSED_LENGTH] for c in covered[:config.MAX_COVERED_MISSED_ITEMS]],
            "missed": [str(m)[:config.MAX_COVERED_MISSED_LENGTH] for m in missed[:config.MAX_COVERED_MISSED_ITEMS]],
            "feedback": str(result.get("feedback", ""))[:config.MAX_FEEDBACK_LENGTH]
        }
        
    except Exception as e:
        return {
            "score": config.DEFAULT_FALLBACK_SCORE,
            "covered": [],
            "missed": [],
            "feedback": f"Parse error: {e}"
        }
