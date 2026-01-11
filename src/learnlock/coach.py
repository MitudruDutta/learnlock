"""Adversarial Learning Coach - Socratic dialogue that finds holes in understanding."""

import re
import warnings
import os

# Suppress all warnings before any imports
warnings.filterwarnings("ignore")

from . import config


def _get_llm_response(prompt: str, system: str = None) -> str:
    """Get LLM response, trying Gemini first then Groq."""
    import os
    
    # Try Gemini first (better at dialogue)
    if os.environ.get("GEMINI_API_KEY"):
        try:
            import google.generativeai as genai
            genai.configure(api_key=os.environ["GEMINI_API_KEY"])
            full_prompt = f"{system}\n\n{prompt}" if system else prompt
            model = genai.GenerativeModel(config.GEMINI_MODEL)
            return model.generate_content(full_prompt).text
        except:
            pass
    
    # Fallback to Groq
    if os.environ.get("GROQ_API_KEY"):
        import litellm
        litellm.suppress_debug_info = True
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        response = litellm.completion(
            model=f"groq/{config.GROQ_MODEL}",
            messages=messages,
            max_tokens=500,
            temperature=0.7,
        )
        return response.choices[0].message.content
    
    raise ValueError("No API key set")


class SocraticCoach:
    """Multi-turn adversarial dialogue that probes understanding."""
    
    def __init__(self, concept_name: str, source_quote: str, question: str):
        self.concept_name = concept_name
        self.source_quote = source_quote
        self.question = question
        self.history = []  # [(role, text), ...]
        self.turn = 0
        self.max_turns = 3
        self.confidence_score = 5  # Starts high, drops when holes found
        self.holes_found = []
        self.strengths_found = []
        self.finished = False
    
    def get_initial_challenge(self) -> str:
        """Return the initial challenge question."""
        return self.question
    
    def respond(self, user_input: str) -> dict:
        """Process user response and generate Socratic follow-up.
        
        Returns: {
            "type": "followup" | "final",
            "message": str,
            "score": int (1-5, only on final),
            "holes": list (only on final),
            "strengths": list (only on final),
        }
        """
        self.turn += 1
        self.history.append(("user", user_input))
        
        # Analyze the response
        analysis = self._analyze_response(user_input)
        
        # If we found a hole and have turns left, probe deeper
        if analysis["has_hole"] and self.turn < self.max_turns:
            self.holes_found.append(analysis["hole_description"])
            self.confidence_score = max(1, self.confidence_score - 1)
            
            followup = self._generate_followup(analysis)
            self.history.append(("coach", followup))
            
            return {
                "type": "followup",
                "message": followup,
            }
        
        # Otherwise, wrap up
        if analysis["strength"]:
            self.strengths_found.append(analysis["strength"])
        if analysis["has_hole"]:
            self.holes_found.append(analysis["hole_description"])
            self.confidence_score = max(1, self.confidence_score - 1)
        
        self.finished = True
        final = self._generate_final_verdict()
        
        return {
            "type": "final",
            "message": final["feedback"],
            "score": self.confidence_score,
            "holes": self.holes_found,
            "strengths": self.strengths_found,
        }
    
    def _analyze_response(self, user_input: str) -> dict:
        """Analyze user response for holes and strengths."""
        history_text = "\n".join([f"{r}: {t}" for r, t in self.history])
        
        prompt = f"""You are a Socratic teacher analyzing a student's explanation.

CONCEPT: {self.concept_name}
SOURCE TRUTH: "{self.source_quote}"
ORIGINAL QUESTION: {self.question}

CONVERSATION SO FAR:
{history_text}

Analyze the student's LATEST response. Look for:
1. HOLES: Misconceptions, oversimplifications, missing key points, confident-but-wrong statements
2. STRENGTHS: Correct understanding, good analogies, accurate details

Reply in this EXACT format (no other text):
HAS_HOLE: yes/no
HOLE: [brief description of the gap or misconception, or "none"]
STRENGTH: [what they got right, or "none"]
PROBE: [a pointed follow-up question that exposes the hole, or "none"]"""

        try:
            response = _get_llm_response(prompt)
            
            has_hole = "has_hole: yes" in response.lower()
            
            # Parse HOLE (between HOLE: and STRENGTH:)
            hole_match = re.search(r'\nHOLE:\s*(.+?)(?=\nSTRENGTH:)', response, re.IGNORECASE | re.DOTALL)
            hole = hole_match.group(1).strip() if hole_match else None
            if hole and hole.lower() == "none":
                hole = None
            
            # Parse STRENGTH (between STRENGTH: and PROBE:)
            strength_match = re.search(r'\nSTRENGTH:\s*(.+?)(?=\nPROBE:)', response, re.IGNORECASE | re.DOTALL)
            strength = strength_match.group(1).strip() if strength_match else None
            if strength and strength.lower() == "none":
                strength = None
            
            # Parse PROBE (after PROBE:)
            probe_match = re.search(r'\nPROBE:\s*(.+)', response, re.IGNORECASE | re.DOTALL)
            probe = probe_match.group(1).strip() if probe_match else None
            if probe and probe.lower() == "none":
                probe = None
            
            return {
                "has_hole": has_hole and hole,
                "hole_description": hole,
                "strength": strength,
                "probe_question": probe,
            }
        except Exception as e:
            return {
                "has_hole": False,
                "hole_description": None,
                "strength": "Explanation recorded",
                "probe_question": None,
            }
    
    def _generate_followup(self, analysis: dict) -> str:
        """Generate a Socratic follow-up that probes the hole."""
        if analysis.get("probe_question"):
            return analysis["probe_question"]
        
        # Generate a new probe
        prompt = f"""You are a Socratic teacher who found a gap in understanding.

CONCEPT: {self.concept_name}
GAP FOUND: {analysis['hole_description']}

Generate ONE pointed follow-up question that:
- Directly targets this gap
- Cannot be answered with a vague response
- Forces the student to confront what they don't know

Reply with ONLY the question, nothing else. Be direct and challenging."""

        try:
            return _get_llm_response(prompt).strip().strip('"')
        except:
            return f"Can you explain more specifically how {self.concept_name} handles {analysis['hole_description']}?"
    
    def _generate_final_verdict(self) -> dict:
        """Generate final feedback."""
        if not self.holes_found and not self.strengths_found:
            return {"feedback": "Explanation recorded."}
        
        history_text = "\n".join([f"{r}: {t}" for r, t in self.history])
        
        prompt = f"""You are a Socratic teacher giving final feedback.

CONCEPT: {self.concept_name}
CONVERSATION:
{history_text}

HOLES FOUND: {self.holes_found if self.holes_found else "None"}
STRENGTHS: {self.strengths_found if self.strengths_found else "None"}

Write ONE sentence of direct, honest feedback. No fluff. Tell them exactly what they need to review."""

        try:
            feedback = _get_llm_response(prompt).strip()
            return {"feedback": feedback[:200]}
        except:
            if self.holes_found:
                return {"feedback": f"Review: {self.holes_found[0]}"}
            return {"feedback": "Good understanding demonstrated."}


def create_coach(concept_name: str, source_quote: str, question: str = None) -> SocraticCoach:
    """Factory function to create a Socratic coach for a concept."""
    if not question:
        question = f"Explain {concept_name} in your own words."
    return SocraticCoach(concept_name, source_quote, question)
