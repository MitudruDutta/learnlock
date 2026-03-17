"""Duel Engine - The cognitive core of LearnLock.

Not a tutor. Not a quiz. Not a chatbot.
An engine that infers what you believe and uses it against you.
"""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime

from . import llm, storage
from .security import sanitize_filename


@dataclass
class Claim:
    """A testable factual claim about a concept."""

    statement: str
    claim_type: str  # mechanism, requirement, boundary, definition
    index: int = 0


@dataclass
class BeliefError:
    """Typed error with severity. Must reference a claim."""

    type: str
    description: str
    severity: int
    violated_claim: str
    claim_index: int
    confidence: float = 1.0


@dataclass
class BeliefSnapshot:
    """A moment in belief evolution with causal trigger."""

    belief: str
    trigger: str
    errors_at_time: list[BeliefError] = field(default_factory=list)


@dataclass
class BeliefState:
    """The product. The conversation is just visualization."""

    belief: str = ""
    history: list[BeliefSnapshot] = field(default_factory=list)
    errors: list[BeliefError] = field(default_factory=list)
    confidence: float = 0.0
    evidence: list[str] = field(default_factory=list)
    attack_history: list[str] = field(default_factory=list)
    ground_truth: str = ""
    claims: list[Claim] = field(default_factory=list)


# ============ DUEL LLM PARAMETERS ============
# Duel uses higher temperature for more probing questions
_DUEL_TEMPERATURE = 0.7
_DUEL_MAX_TOKENS = 500
LOW_CONFIDENCE_THRESHOLD = 0.7
MIN_ACTIONABLE_CONFIDENCE = 0.4


def _duel_llm(prompt: str) -> str:
    """LLM call with duel-specific parameters. Prefers Gemini for evaluation quality."""
    return llm.call(
        prompt,
        temperature=_DUEL_TEMPERATURE,
        max_tokens=_DUEL_MAX_TOKENS,
        prefer="gemini",
    )


def _calc_claim_count(content_len: int) -> tuple[int, int]:
    """Calculate min/max claims based on ground truth length.

    Short content gets fewer claims, longer content gets more.
    Clamped to 2-6 range.
    """
    # ~1 claim per 100 chars of ground truth
    base = max(2, min(6, content_len // 100))
    return max(2, base - 1), min(6, base + 1)


_CLAIM_PROMPT_TEMPLATE = """Extract {min_claims}-{max_claims} conceptual claims about this topic.

SOURCE: {source}

RULES:
- Claims must be CONCEPTUAL TRUTHS, not runtime facts
- Claims must be FALSIFIABLE by a wrong explanation
- Claims must capture WHY or HOW, not just WHAT
- NO tautologies ("server serves", "runs when running")
- NO operational state ("is active", "must remain")

GOOD: "A backend server mediates between clients and data stores"
GOOD: "It enforces business logic like auth and validation"
BAD: "The server processes requests" (too obvious)
BAD: "It must be running to work" (tautology)

Types: definition, mechanism, requirement, boundary

Reply ONLY as:
TYPE|CLAIM"""

_STOP_WORDS = frozenset({
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "to", "of", "in", "for", "on", "with", "at", "by", "from", "as",
    "it", "its", "that", "this", "and", "or", "but", "not", "no",
    "can", "do", "does", "did", "has", "have", "had", "will", "would",
    "should", "may", "might", "must", "shall",
})


def _generate_raw_claims(
    safe_truth: str, temperature: float, max_claims: int
) -> list[Claim]:
    """Generate claims at a specific temperature. Returns parsed but unfiltered claims."""
    min_c, max_c = _calc_claim_count(len(safe_truth))
    prompt = _CLAIM_PROMPT_TEMPLATE.format(
        source=safe_truth, min_claims=min_c, max_claims=max_c
    )
    try:
        resp = llm.call(
            prompt,
            temperature=temperature,
            max_tokens=_DUEL_MAX_TOKENS,
            prefer="gemini",
        ).strip()

        claims = []
        seen: set[str] = set()

        for line in resp.split("\n"):
            if "|" not in line:
                continue
            parts = line.split("|", 1)
            if len(parts) != 2:
                continue

            ctype = parts[0].strip().lower()
            stmt = parts[1].strip()[:150]

            if ctype not in ("definition", "mechanism", "requirement", "boundary"):
                continue
            if len(stmt) < 10:
                continue
            if stmt in seen:
                continue

            seen.add(stmt)
            claims.append(Claim(statement=stmt, claim_type=ctype, index=len(claims)))

        return claims[:max_claims]
    except Exception:
        return []


def _claims_similar(a: str, b: str) -> bool:
    """Check if two claims overlap enough to be considered the same idea."""
    words_a = set(a.lower().split()) - _STOP_WORDS
    words_b = set(b.lower().split()) - _STOP_WORDS
    if not words_a or not words_b:
        return False
    overlap = len(words_a & words_b)
    smaller = min(len(words_a), len(words_b))
    return overlap / smaller >= 0.5


def _intersect_claims(primary: list[Claim], secondary: list[Claim]) -> list[Claim]:
    """Keep claims from primary that have a matching idea in secondary."""
    verified = []
    for claim in primary:
        for other in secondary:
            if _claims_similar(claim.statement, other.statement):
                verified.append(claim)
                break
    return verified


def _parse_claims(ground_truth: str) -> list[Claim]:
    """Parse ground truth into 2-4 testable claims, then verify.

    Uses dual-temperature generation: runs claim extraction twice at different
    temperatures and keeps only claims that appear in both runs. This eliminates
    hallucinated claims before the garbage and sharpness filters.
    """
    safe_truth = llm.sanitize_for_prompt(ground_truth, max_length=500)

    try:
        # Pass 1: Dual-temperature generation for variance check
        _, max_claims = _calc_claim_count(len(safe_truth))
        claims_low = _generate_raw_claims(safe_truth, temperature=0.4, max_claims=max_claims)
        claims_high = _generate_raw_claims(safe_truth, temperature=0.9, max_claims=max_claims)

        # Intersect: keep only claims that appear in both runs
        if claims_low and claims_high:
            claims = _intersect_claims(claims_low, claims_high)
            if len(claims) < 2:
                # Not enough overlap — trust the lower-temp run
                claims = claims_low
        elif claims_low:
            claims = claims_low
        elif claims_high:
            claims = claims_high
        else:
            return [Claim(safe_truth[:150], "definition", 0)]

        if len(claims) < 2:
            return [Claim(safe_truth[:150], "definition", 0)]

        # Pass 2: Verify claims - prune garbage
        claims = _verify_claims(claims)

        if not claims:
            return [Claim(safe_truth[:150], "definition", 0)]

        # Pass 3: Sharpen claims - reject blurry truths
        claims = _sharpen_claims(claims)

        if not claims:
            return [Claim(safe_truth[:150], "definition", 0)]

        # Re-index after pruning
        for i, c in enumerate(claims):
            c.index = i

        return claims
    except Exception:
        return [Claim(safe_truth[:150], "definition", 0)]


def _verify_claims(claims: list[Claim]) -> list[Claim]:
    """Prune claims that are stateful, vague, or not conceptual truths."""

    if not claims:
        return claims

    # Fast pattern rejection (no LLM needed)
    garbage_patterns = [
        # Stateful
        "currently",
        "is now",
        "has been",
        "is running",
        "is listening",
        "must remain",
        "must be active",
        "needs to be running",
        "running server",
        # Vague
        "is useful",
        "is important",
        "is helpful",
        "helps with",
        "is required",
        "is needed",
        "must be",
        "should be",
        "requires the",
        "needs the",
        "to function",
        # Tautological
        "processes requests",
        "serves requests",
        "handles requests",
        "processes and responds",
        "receives and processes",
        "responds to",
        "receives and",
        "sends and receives",
        "when running",
        "while running",
        "if running",
        "incoming requests",
        "client requests",
    ]

    def is_garbage(stmt: str) -> bool:
        lower = stmt.lower()
        return any(p in lower for p in garbage_patterns)

    # Pre-filter obvious garbage
    candidates = [c for c in claims if not is_garbage(c.statement)]

    # If we pruned everything, keep the first claim as fallback
    if not candidates:
        return claims[:1]

    # If only 1-2 left, skip LLM verification
    if len(candidates) <= 2:
        return candidates

    # Pass 2: LLM verification for remaining claims
    claims_str = "\n".join(
        f"{i + 1}. [{c.claim_type}] {c.statement}" for i, c in enumerate(candidates)
    )

    prompt = f"""Review these claims. Keep ONLY conceptual truths.

CLAIMS:
{claims_str}

REJECT claims that are:
- Tautological (obvious, unfalsifiable)
- Runtime state (not conceptual)
- Too vague to violate

Reply with ONLY the numbers to KEEP, comma-separated.
Example: 1,3

If all are bad, reply: NONE"""

    try:
        resp = _duel_llm(prompt).strip().upper()

        if resp == "NONE" or not resp:
            return candidates[:1]

        kept = []
        for part in resp.replace(" ", "").split(","):
            try:
                idx = int(part) - 1
                if 0 <= idx < len(candidates):
                    kept.append(candidates[idx])
            except (ValueError, IndexError):
                continue

        return kept if kept else candidates[:2]
    except Exception:
        return candidates


def _sharpen_claims(claims: list[Claim]) -> list[Claim]:
    """Reject blurry truths. Keep only claims sharp enough to violate."""

    if len(claims) <= 1:
        return claims

    # Blurry patterns - technically true but unfalsifiable
    blurry_patterns = [
        "handle ",
        "handles ",
        "manage ",
        "manages ",
        "deal with",
        "deals with",
        "work with",
        "works with",
        "is responsible",
        "takes care",
        "involved in",
        "related to",
        "associated with",
        "connected to",
        "plays a role",
        "is part of",
        "contributes to",
        "helps ensure",
        "helps provide",
        "helps manage",
        "various",
        "different types",
        "multiple",
        "many kinds",
        "and more",
        "and other",
        "etc",
        "such as",
        "in some way",
        "in general",
        "typically",
        "usually",
        "can be used",
        "may be used",
        "might be",
    ]

    def is_blurry(stmt: str) -> bool:
        lower = stmt.lower()
        return any(p in lower for p in blurry_patterns)

    sharp = [c for c in claims if not is_blurry(c.statement)]

    # Keep at least one claim
    return sharp if sharp else claims[:1]


def _is_non_answer(text: str) -> bool:
    """Detect dodging or ignorance."""
    text = text.lower().strip()
    dodges = [
        "i don't know",
        "i dont know",
        "idk",
        "no idea",
        "not sure",
        "i'm not sure",
        "im not sure",
        "no clue",
        "beats me",
        "i have no idea",
        "haven't learned",
        "havent learned",
        "don't understand",
        "dont understand",
        "confused",
        "i don't remember",
        "i dont remember",
        "forgot",
        "forget",
        "i forgot",
        "i forget",
        "forgotten",
        "pass",
        "can't answer",
        "cant answer",
        "don't know anything",
        "dont know anything",
        "no answer",
        "don't recall",
        "dont recall",
    ]
    for d in dodges:
        if d in text:
            return True
    return len(text.split()) < 3


def _run_belief_model(concept: str, user_msg: str, state: BeliefState) -> dict:
    """Extract what the student believes."""

    if _is_non_answer(user_msg):
        return {"belief": state.belief or "", "is_non_answer": True}

    safe_concept = llm.sanitize_for_prompt(concept, max_length=200)
    safe_msg = llm.sanitize_for_prompt(user_msg, max_length=2000)

    conv = []
    for i, ev in enumerate(state.evidence):
        conv.append(f"Student: {ev}")
        if i < len(state.attack_history):
            conv.append(f"Challenge: {state.attack_history[i]}")
    conv.append(f"Student: {safe_msg}")

    prompt = f"""Model what this student believes about {safe_concept}.

PREVIOUS BELIEF: {state.belief or "None"}

CONVERSATION:
{chr(10).join(conv)}

Reply EXACTLY as:
BELIEF: [one sentence - their mental model]"""

    resp = _duel_llm(prompt)
    belief = ""
    for line in resp.strip().split("\n"):
        if line.upper().startswith("BELIEF:"):
            belief = line[7:].strip()
            break

    if len(belief) < 10:
        belief = state.belief or ""

    return {"belief": belief, "is_non_answer": False}


def _run_contradiction_detector(belief: str, claims: list[Claim], turn: int) -> list[BeliefError]:
    """Check belief against claims. Errors MUST reference claims."""

    if not claims:
        return []

    # No belief extracted = student gave nothing useful
    if not belief:
        return [
            BeliefError(
                "missing_mechanism",
                "No substantive answer provided",
                2,
                claims[0].statement,
                0,
                confidence=1.0,
            )
        ]

    claims_str = "\n".join(f"{c.index + 1}. [{c.claim_type}] {c.statement}" for c in claims)

    prompt = f"""You are a strict examiner. Check if the student's belief covers ALL claims.

BELIEF: {belief}

CLAIMS:
{claims_str}

RULES:
- A claim is ONLY satisfied if the belief EXPLICITLY addresses it with correct detail.
- Vague, generic, or surface-level answers count as missing_mechanism.
- If the belief does not mention a claim AT ALL, that is missing_mechanism (severity 2).
- If the belief contradicts a claim, that is wrong_mechanism (severity 3).
- Be strict: "it does stuff" does NOT satisfy "X uses algorithm Y to achieve Z".

For EACH violation, output one line:
CLAIM_NUM|ERROR_TYPE|DESCRIPTION|SEVERITY|CONFIDENCE

Types: wrong_mechanism, missing_mechanism, boundary_error, conflation, superficial
Severity: 1=minor, 2=significant, 3=critical
Confidence: 0.0 to 1.0

If EVERY claim is explicitly and correctly addressed: NONE"""

    resp = _duel_llm(prompt).strip()
    if resp.upper() in ("NONE", "N/A", ""):
        return []

    errors = []
    for line in resp.split("\n"):
        if "|" not in line:
            continue
        parts = [part.strip() for part in line.split("|")]
        if len(parts) < 4:
            continue
        try:
            idx = int(parts[0]) - 1
            if idx < 0 or idx >= len(claims):
                continue  # Discard errors without valid claim

            # Last part might be confidence (float), second-to-last is severity
            # Format: CLAIM|TYPE|DESC...|SEVERITY or CLAIM|TYPE|DESC...|SEVERITY|CONF
            conf = 1.0
            try:
                maybe_conf = float(parts[-1])
                if 0.0 <= maybe_conf <= 1.0 and len(parts) >= 5:
                    conf = maybe_conf
                    severity = int(parts[-2])
                    description = "|".join(parts[2:-2]).strip()
                else:
                    severity = int(parts[-1])
                    description = "|".join(parts[2:-1]).strip()
            except ValueError:
                severity = int(parts[-1])
                description = "|".join(parts[2:-1]).strip()

            if not description:
                continue

            errors.append(
                BeliefError(
                    type=parts[1].lower(),
                    description=description,
                    severity=min(3, max(1, severity)),
                    violated_claim=claims[idx].statement,
                    claim_index=idx,
                    confidence=conf,
                )
            )
        except (ValueError, IndexError):
            continue  # Discard malformed errors

    return errors


def _generate_non_answer_attack(concept: str, claims: list[Claim], history: list[str]) -> str:
    """Guide ignorant student toward a claim."""

    claim = claims[0] if claims else None
    history_str = "\n".join(f"- {q}" for q in history) if history else "None"
    safe_concept = llm.sanitize_for_prompt(concept, max_length=200)

    prompt = f"""Student doesn't know about: {safe_concept}

TARGET CLAIM: {claim.statement if claim else safe_concept}

ALREADY ASKED:
{history_str}

Generate ONE question that helps them reason toward this claim.
Reply with ONLY the question."""

    q = _duel_llm(prompt).strip().strip("\"'")
    q = re.sub(r"^(Q:|Question:)\s*", "", q, flags=re.I)
    return q or f"What do you think {concept} might involve?"


def _run_interrogator(
    belief: str, errors: list[BeliefError], claims: list[Claim], history: list[str]
) -> str | None:
    """Attack highest severity error. Must reference violated claim."""

    if not errors:
        return None

    target = primary_error(errors)
    if target is None:
        return None
    history_str = "\n".join(f"- {q}" for q in history) if history else "None"

    prompt = f"""Corner this student.

THEY BELIEVE: {belief}

ERROR: {target.type} (severity {target.severity})
VIOLATES CLAIM: "{target.violated_claim}"
BECAUSE: {target.description}

ALREADY ASKED:
{history_str}

Generate ONE question that exposes why their belief violates this specific claim.
The question must force them to confront: "{target.violated_claim}"

Reply with ONLY the question."""

    q = _duel_llm(prompt).strip().strip("\"'")
    q = re.sub(r"^(Q:|Question:)\s*", "", q, flags=re.I)
    return q or None


def effective_error_severity(error: BeliefError) -> int:
    """Down-weight low-confidence findings before they affect product behavior."""
    if error.confidence < MIN_ACTIONABLE_CONFIDENCE:
        return 0
    if error.confidence < LOW_CONFIDENCE_THRESHOLD:
        return max(1, error.severity - 1)
    return error.severity


def actionable_errors(errors: list[BeliefError]) -> list[BeliefError]:
    """Errors strong enough to drive interrogation and scoring."""
    return [error for error in errors if effective_error_severity(error) > 0]


def primary_error(errors: list[BeliefError]) -> BeliefError | None:
    """Select the strongest actionable error, preferring higher confidence on ties."""
    if not errors:
        return None
    candidates = actionable_errors(errors)
    if not candidates:
        return None
    return max(
        candidates,
        key=lambda error: (
            effective_error_severity(error),
            error.confidence,
            error.severity,
        ),
    )


def get_or_create_claims(ground_truth: str, concept_id: int | None = None) -> list[Claim]:
    """Load cached claims when possible, otherwise parse and persist them."""
    cached = storage.get_cached_claims(concept_id) if concept_id is not None else None
    if cached:
        return [
            Claim(claim["statement"], claim["claim_type"], claim["claim_index"])
            for claim in cached
        ]

    claims = _parse_claims(ground_truth)
    if concept_id is not None and claims:
        storage.save_cached_claims(
            concept_id,
            [
                {
                    "statement": claim.statement,
                    "claim_type": claim.claim_type,
                    "claim_index": claim.index,
                }
                for claim in claims
            ],
        )
    return claims


class DuelEngine:
    """Adversarial Socratic interrogation engine."""

    def __init__(
        self,
        concept: str,
        ground_truth: str,
        question: str | None = None,
        concept_id: int | None = None,
    ):
        self.concept = concept
        self.concept_id = concept_id
        self.state = BeliefState(ground_truth=ground_truth)
        self.state.claims = get_or_create_claims(ground_truth, concept_id)

        self.turn = 0
        self.max_turns = 3
        self.finished = False
        self._initial_q = question or f"Explain {concept} in your own words."

    def get_challenge(self) -> str:
        if self.state.attack_history:
            return self.state.attack_history[-1]
        return self._initial_q

    def get_claims(self) -> list[Claim]:
        return self.state.claims

    def process(self, user_input: str) -> dict:
        self.turn += 1
        trigger = self.state.attack_history[-1] if self.state.attack_history else "initial"

        try:
            belief_result = _run_belief_model(self.concept, user_input, self.state)
        except Exception:
            # If belief extraction fails, use raw input as belief
            belief_result = {"belief": user_input, "is_non_answer": False}

        if belief_result["belief"] and belief_result["belief"] != self.state.belief:
            self.state.belief = belief_result["belief"]
        self.state.evidence.append(user_input)

        # Non-answer handling
        if belief_result.get("is_non_answer"):
            if self.turn >= self.max_turns:
                self.state.errors = [
                    BeliefError(
                        "no_response",
                        "Unable to explain",
                        3,
                        self.state.claims[0].statement if self.state.claims else "",
                        0,
                    )
                ]
                self.finished = True
                return {"type": "reveal", "message": ""}

            attack = _generate_non_answer_attack(
                self.concept, self.state.claims, self.state.attack_history
            )
            self.state.attack_history.append(attack)
            return {"type": "attack", "message": attack}

        # Check against claims — if detector fails, assume errors exist
        try:
            errors = _run_contradiction_detector(
                self.state.belief, self.state.claims, self.turn
            )
        except Exception:
            errors = [
                BeliefError(
                    "evaluation_failed",
                    "Could not verify answer",
                    2,
                    self.state.claims[0].statement if self.state.claims else "",
                    0,
                    confidence=1.0,
                )
            ]
        self.state.errors = errors
        actionable = actionable_errors(errors)

        # Record snapshot (only if belief exists)
        if self.state.belief:
            self.state.history.append(
                BeliefSnapshot(
                    belief=self.state.belief,
                    trigger=trigger,
                    errors_at_time=list(errors),
                )
            )

        if not actionable:
            self.finished = True
            return {"type": "reveal", "message": ""}

        if self.turn >= self.max_turns:
            self.finished = True
            return {"type": "reveal", "message": ""}

        attack = _run_interrogator(
            self.state.belief, self.state.errors, self.state.claims, self.state.attack_history
        )
        if attack:
            self.state.attack_history.append(attack)
            return {"type": "attack", "message": attack}

        self.finished = True
        return {"type": "reveal", "message": ""}

    def get_reveal(self) -> dict:
        return {
            "belief": self.state.belief,
            "claims": self.state.claims,
            "history": self.state.history,
            "errors": self.state.errors,
            "ground_truth": self.state.ground_truth,
            "turns": self.turn,
            "evidence": self.state.evidence,
            "attacks": self.state.attack_history,
        }


def create_duel(
    concept: str,
    ground_truth: str,
    question: str | None = None,
    concept_id: int | None = None,
) -> DuelEngine:
    return DuelEngine(concept, ground_truth, question, concept_id)


def belief_to_score(state: BeliefState) -> int:
    """Convert final belief state to a 1-5 score.

    Mapping: no errors=5, minor(1)=4, significant(2)=3, critical(3)=1
    """
    effective_errors = actionable_errors(state.errors)
    if not effective_errors:
        return 5
    max_sev = max(effective_error_severity(error) for error in effective_errors)
    return {3: 1, 2: 3, 1: 4}.get(max_sev, 2)


def export_duel_data(state: BeliefState, concept: str) -> dict:
    """Export duel data for research/training."""
    return {
        "concept": concept,
        "timestamp": datetime.now().isoformat(),
        "ground_truth": state.ground_truth,
        "claims": [
            {"type": c.claim_type, "statement": c.statement, "index": c.index} for c in state.claims
        ],
        "final_belief": state.belief,
        "trajectory": [
            {
                "belief": s.belief,
                "trigger": s.trigger,
                "errors": [
                    {
                        "type": e.type,
                        "desc": e.description,
                        "severity": e.severity,
                        "claim": e.violated_claim,
                        "claim_idx": e.claim_index,
                        "confidence": e.confidence,
                    }
                    for e in s.errors_at_time
                ],
            }
            for s in state.history
        ],
        "final_errors": [
            {
                "type": e.type,
                "desc": e.description,
                "severity": e.severity,
                "claim": e.violated_claim,
                "claim_idx": e.claim_index,
                "confidence": e.confidence,
            }
            for e in state.errors
        ],
        "evidence": state.evidence,
        "attacks": state.attack_history,
    }


def save_duel_data(state: BeliefState, concept: str) -> str:
    """Save duel data to /data/duels/YYYY-MM-DD/"""
    from . import config

    data = export_duel_data(state, concept)
    date_str = datetime.now().strftime("%Y-%m-%d")
    duel_dir = config.DATA_DIR / "duels" / date_str
    duel_dir.mkdir(parents=True, exist_ok=True)

    safe_concept = sanitize_filename(concept, default="concept")
    filename = f"{safe_concept}_{datetime.now().strftime('%H%M%S')}.json"
    filepath = duel_dir / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return str(filepath)
