"""Tests for the Duel Engine."""

from pathlib import Path

from learnlock import config
from learnlock.duel import (
    BeliefError,
    BeliefState,
    Claim,
    DuelEngine,
    _calc_claim_count,
    _claims_similar,
    _intersect_claims,
    _is_non_answer,
    _run_contradiction_detector,
    _sharpen_claims,
    _verify_claims,
    belief_to_score,
    save_duel_data,
)


class TestBeliefToScore:
    def test_no_errors_gives_5(self):
        state = BeliefState()
        assert belief_to_score(state) == 5

    def test_minor_severity_gives_4(self):
        state = BeliefState(errors=[BeliefError("superficial", "desc", 1, "claim", 0)])
        assert belief_to_score(state) == 4

    def test_significant_severity_gives_3(self):
        state = BeliefState(errors=[BeliefError("missing_mechanism", "desc", 2, "claim", 0)])
        assert belief_to_score(state) == 3

    def test_critical_severity_gives_1(self):
        state = BeliefState(errors=[BeliefError("wrong_mechanism", "desc", 3, "claim", 0)])
        assert belief_to_score(state) == 1

    def test_mixed_severities_uses_max(self):
        state = BeliefState(
            errors=[
                BeliefError("superficial", "desc", 1, "claim", 0),
                BeliefError("wrong_mechanism", "desc", 3, "claim", 1),
            ]
        )
        assert belief_to_score(state) == 1

    def test_all_scores_reachable(self):
        """Verify scores 1, 3, 4, 5 are all reachable."""
        reachable = set()

        reachable.add(belief_to_score(BeliefState()))  # 5
        reachable.add(belief_to_score(BeliefState(errors=[BeliefError("x", "d", 1, "c", 0)])))  # 4
        reachable.add(belief_to_score(BeliefState(errors=[BeliefError("x", "d", 2, "c", 0)])))  # 3
        reachable.add(belief_to_score(BeliefState(errors=[BeliefError("x", "d", 3, "c", 0)])))  # 1

        assert reachable == {1, 3, 4, 5}

    def test_low_confidence_critical_error_is_downgraded(self):
        state = BeliefState(
            errors=[BeliefError("wrong_mechanism", "desc", 3, "claim", 0, confidence=0.5)]
        )
        assert belief_to_score(state) == 3

    def test_very_low_confidence_error_is_ignored(self):
        state = BeliefState(
            errors=[BeliefError("wrong_mechanism", "desc", 3, "claim", 0, confidence=0.2)]
        )
        assert belief_to_score(state) == 5


class TestIsNonAnswer:
    def test_idk(self):
        assert _is_non_answer("idk")

    def test_i_dont_know(self):
        assert _is_non_answer("I don't know")

    def test_pass(self):
        assert _is_non_answer("pass")

    def test_short_answer(self):
        assert _is_non_answer("um")

    def test_real_answer(self):
        assert not _is_non_answer("It works by using a hash table for O(1) lookups")

    def test_confused(self):
        assert _is_non_answer("I'm confused about this")

    def test_empty(self):
        assert _is_non_answer("")

    def test_two_words(self):
        assert _is_non_answer("no clue")


class TestVerifyClaims:
    def test_empty_list(self):
        assert _verify_claims([]) == []

    def test_filters_garbage(self):
        claims = [
            Claim("The server processes requests", "mechanism", 0),
            Claim("JWT tokens use HMAC-SHA256 for signature verification", "mechanism", 1),
        ]
        result = _verify_claims(claims)
        # Garbage pattern "processes requests" should be filtered
        assert len(result) <= len(claims)
        statements = [c.statement for c in result]
        assert "The server processes requests" not in statements

    def test_keeps_at_least_one(self):
        claims = [
            Claim("The server processes requests", "mechanism", 0),
            Claim("It handles requests", "mechanism", 1),
        ]
        result = _verify_claims(claims)
        assert len(result) >= 1  # Fallback keeps at least one


class TestSharpenClaims:
    def test_filters_blurry(self):
        claims = [
            Claim("It handles various security concerns", "mechanism", 0),
            Claim("JWT tokens expire after a configurable TTL", "boundary", 1),
        ]
        result = _sharpen_claims(claims)
        statements = [c.statement for c in result]
        assert "JWT tokens expire after a configurable TTL" in statements

    def test_single_claim_kept(self):
        claims = [Claim("something blurry that handles things", "definition", 0)]
        result = _sharpen_claims(claims)
        assert len(result) == 1  # Single claim always kept

    def test_empty_list(self):
        assert _sharpen_claims([]) == []


class TestContradictionDetector:
    def test_keeps_description_with_pipes(self, monkeypatch):
        """Pipe characters in the description should be preserved."""
        monkeypatch.setattr(
            "learnlock.duel._duel_llm",
            lambda prompt: "1|wrong_mechanism|Explains the wrong step|skips the real mechanism|3",
        )

        errors = _run_contradiction_detector(
            belief="It works because of the wrong step.",
            claims=[Claim("It relies on the real mechanism", "mechanism", index=0)],
            turn=2,
        )

        assert len(errors) == 1
        assert errors[0].severity == 3
        assert errors[0].description == "Explains the wrong step|skips the real mechanism"

    def test_empty_belief_returns_empty(self):
        assert _run_contradiction_detector("", [Claim("x", "y", 0)], 1) == []

    def test_empty_claims_returns_empty(self):
        assert _run_contradiction_detector("some belief", [], 1) == []

    def test_invalid_claim_index_discarded(self, monkeypatch):
        monkeypatch.setattr(
            "learnlock.duel._duel_llm",
            lambda prompt: "99|wrong_mechanism|bad index|2",
        )
        errors = _run_contradiction_detector("belief", [Claim("claim", "mechanism", 0)], 1)
        assert len(errors) == 0

    def test_parses_confidence_value(self, monkeypatch):
        """Confidence should be parsed from the 5th pipe-separated field."""
        monkeypatch.setattr(
            "learnlock.duel._duel_llm",
            lambda prompt: "1|wrong_mechanism|Wrong explanation|2|0.6",
        )
        errors = _run_contradiction_detector(
            "wrong", [Claim("correct claim", "mechanism", 0)], 2,
        )
        assert len(errors) == 1
        assert errors[0].confidence == 0.6

    def test_missing_confidence_defaults_to_1(self, monkeypatch):
        """Without a confidence field, default to 1.0."""
        monkeypatch.setattr(
            "learnlock.duel._duel_llm",
            lambda prompt: "1|wrong_mechanism|Wrong explanation|2",
        )
        errors = _run_contradiction_detector(
            "wrong", [Claim("correct claim", "mechanism", 0)], 2,
        )
        assert len(errors) == 1
        assert errors[0].confidence == 1.0

    def test_confidence_zero_is_valid(self, monkeypatch):
        """Confidence of 0.0 should be accepted as a valid value."""
        monkeypatch.setattr(
            "learnlock.duel._duel_llm",
            lambda prompt: "1|wrong_mechanism|Wrong explanation|2|0.0",
        )
        errors = _run_contradiction_detector(
            "wrong", [Claim("correct claim", "mechanism", 0)], 2,
        )
        assert len(errors) == 1
        assert errors[0].confidence == 0.0
        assert errors[0].severity == 2

    def test_none_response(self, monkeypatch):
        monkeypatch.setattr("learnlock.duel._duel_llm", lambda prompt: "NONE")
        errors = _run_contradiction_detector("belief", [Claim("claim", "mechanism", 0)], 1)
        assert len(errors) == 0


class TestSaveDuelData:
    def test_stays_inside_data_dir(self, monkeypatch, tmp_path):
        monkeypatch.setattr(config, "DATA_DIR", tmp_path)
        saved_path = Path(save_duel_data(BeliefState(ground_truth="truth"), "../../escape/path"))
        assert saved_path.exists()
        assert tmp_path.resolve() in saved_path.resolve().parents
        assert ".." not in saved_path.name


class TestDuelEngineWithCachedClaims:
    def test_caches_claims_on_first_run(self, seeded_db, monkeypatch):
        """First duel should parse and cache claims."""
        from learnlock import storage

        concepts = storage.get_all_concepts()
        cid = concepts[0]["id"]

        # No cached claims yet
        assert storage.get_cached_claims(cid) is None

        # Mock the LLM to return predictable claims
        monkeypatch.setattr(
            "learnlock.duel._duel_llm",
            lambda prompt: (
                "definition|Widgets are reusable UI components\n"
                "mechanism|Widgets encapsulate state and rendering"
            ),
        )

        engine = DuelEngine(
            concept="Widget",
            ground_truth="Widgets encapsulate UI and state",
            concept_id=cid,
        )

        # Claims should now be cached
        cached = storage.get_cached_claims(cid)
        assert cached is not None
        assert len(cached) == len(engine.state.claims)

    def test_uses_cached_claims_on_second_run(self, seeded_db, monkeypatch):
        """Second duel should use cached claims without LLM calls."""
        from learnlock import storage

        concepts = storage.get_all_concepts()
        cid = concepts[0]["id"]

        # Pre-cache some claims
        storage.save_cached_claims(
            cid,
            [
                {"statement": "Cached claim 1", "claim_type": "definition", "claim_index": 0},
                {"statement": "Cached claim 2", "claim_type": "mechanism", "claim_index": 1},
            ],
        )

        # Track if _duel_llm is called (it shouldn't be for claim parsing)
        llm_called = False

        def tracking_llm(prompt):
            nonlocal llm_called
            llm_called = True
            return "NONE"

        monkeypatch.setattr("learnlock.duel._duel_llm", tracking_llm)

        engine = DuelEngine(
            concept="Widget",
            ground_truth="Widgets encapsulate UI and state",
            concept_id=cid,
        )

        assert not llm_called
        assert len(engine.state.claims) == 2
        assert engine.state.claims[0].statement == "Cached claim 1"


class TestCalcClaimCount:
    def test_short_content(self):
        min_c, max_c = _calc_claim_count(50)
        assert min_c == 2
        assert max_c >= 2

    def test_medium_content(self):
        min_c, max_c = _calc_claim_count(300)
        assert min_c >= 2
        assert max_c >= 3

    def test_long_content(self):
        min_c, max_c = _calc_claim_count(600)
        assert max_c >= 4
        assert max_c <= 6

    def test_very_long_content(self):
        min_c, max_c = _calc_claim_count(2000)
        assert max_c == 6

    def test_empty_content(self):
        min_c, max_c = _calc_claim_count(0)
        assert min_c == 2


class TestClaimsSimilar:
    def test_identical(self):
        assert _claims_similar("Widgets encapsulate UI state", "Widgets encapsulate UI state")

    def test_similar_overlap(self):
        assert _claims_similar(
            "A backend server mediates between clients and databases",
            "A server mediates between clients and data stores",
        )

    def test_no_overlap(self):
        assert not _claims_similar(
            "Python uses garbage collection",
            "HTTP is a stateless protocol",
        )

    def test_partial_overlap_below_threshold(self):
        assert not _claims_similar(
            "Widgets render components on screen",
            "Databases store persistent data on disk",
        )

    def test_empty_after_stop_words(self):
        assert not _claims_similar("the is a an", "to of in for")


class TestIntersectClaims:
    def test_keeps_matching(self):
        primary = [
            Claim("Widgets encapsulate UI state", "definition", 0),
            Claim("Widgets respond to user events", "mechanism", 1),
        ]
        secondary = [
            Claim("UI components encapsulate state in widgets", "definition", 0),
            Claim("HTTP is stateless", "definition", 1),
        ]
        result = _intersect_claims(primary, secondary)
        assert len(result) == 1
        assert result[0].statement == "Widgets encapsulate UI state"

    def test_empty_when_no_overlap(self):
        primary = [Claim("Python uses dynamic typing", "mechanism", 0)]
        secondary = [Claim("Rust enforces memory safety", "mechanism", 0)]
        assert _intersect_claims(primary, secondary) == []

    def test_empty_secondary(self):
        primary = [Claim("Some claim", "definition", 0)]
        assert _intersect_claims(primary, []) == []

    def test_empty_primary(self):
        secondary = [Claim("Some claim", "definition", 0)]
        assert _intersect_claims([], secondary) == []
