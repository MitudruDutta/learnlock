"""Tests for storage module."""

import pytest

from learnlock import storage


class TestInitDb:
    def test_creates_tables(self, tmp_db):
        with storage.get_db() as conn:
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            ).fetchall()
            names = {r[0] for r in tables}

        assert "sources" in names
        assert "concepts" in names
        assert "explanations" in names
        assert "progress" in names
        assert "duel_memory" in names
        assert "cached_claims" in names

    def test_lazy_init_runs_once(self, tmp_db, monkeypatch):
        """init_db should not re-run schema creation on subsequent calls."""
        call_count = 0
        original_connect = storage._connect

        def counting_connect(db_path):
            nonlocal call_count
            call_count += 1
            return original_connect(db_path)

        monkeypatch.setattr(storage, "_connect", counting_connect)

        # First get_db triggers init_db which is already cached from fixture
        with storage.get_db():
            pass
        with storage.get_db():
            pass

        # _connect is called by get_db each time, but init_db should NOT call it again
        # (init_db was already run by fixture, so the cache prevents re-init)
        assert call_count == 2  # Only from get_db, not from init_db

    def test_reset_init_cache(self, tmp_db):
        storage.reset_init_cache()
        # Should not error - just re-runs init
        storage.init_db(tmp_db)


class TestSources:
    def test_add_and_get_source(self, tmp_db):
        sid = storage.add_source("https://example.com", "Test", "article", "content")
        source = storage.get_source(sid)
        assert source is not None
        assert source["title"] == "Test"
        assert source["source_type"] == "article"

    def test_get_source_by_url(self, tmp_db):
        storage.add_source("https://example.com", "Test", "article", "content")
        found = storage.get_source_by_url("https://example.com")
        assert found is not None
        assert found["title"] == "Test"

    def test_get_source_by_url_missing(self, tmp_db):
        assert storage.get_source_by_url("https://nonexistent.com") is None

    def test_duplicate_url_raises(self, tmp_db):
        storage.add_source("https://example.com", "Test", "article", "content")
        with pytest.raises(Exception):
            storage.add_source("https://example.com", "Test2", "article", "content2")

    def test_get_all_sources(self, tmp_db):
        storage.add_source("https://a.com", "A", "article", "a")
        storage.add_source("https://b.com", "B", "article", "b")
        sources = storage.get_all_sources()
        assert len(sources) == 2

    def test_add_source_with_concepts(self, seeded_db):
        concepts = storage.get_all_concepts()
        assert len(concepts) == 2
        names = {c["name"] for c in concepts}
        assert "Widget" in names
        assert "Gadget" in names


class TestConcepts:
    def test_add_concept_with_progress(self, tmp_db):
        sid = storage.add_source("https://example.com", "Test", "article", "content")
        cid = storage.add_concept(sid, "Concept1", "quote1", "question1", "truth1")
        concept = storage.get_concept(cid)
        assert concept is not None
        assert concept["name"] == "Concept1"

        progress = storage.get_progress(cid)
        assert progress is not None
        assert progress["review_count"] == 0

    def test_skip_and_unskip(self, seeded_db):
        concepts = storage.get_all_concepts()
        cid = concepts[0]["id"]

        storage.skip_concept(cid)
        active = storage.get_all_concepts()
        assert len(active) == 1  # One skipped, one remaining

        skipped = storage.get_skipped_concepts()
        assert len(skipped) == 1
        assert skipped[0]["id"] == cid

        storage.unskip_concept(cid)
        active = storage.get_all_concepts()
        assert len(active) == 2

    def test_get_concepts_for_source(self, seeded_db):
        concepts = storage.get_concepts_for_source(seeded_db)
        assert len(concepts) == 2


class TestProgress:
    def test_due_concepts_immediately_due(self, seeded_db):
        due = storage.get_due_concepts()
        assert len(due) == 2  # New concepts are due immediately

    def test_update_progress(self, seeded_db):
        from datetime import datetime, timedelta, timezone

        concepts = storage.get_all_concepts()
        cid = concepts[0]["id"]

        future = datetime.now(timezone.utc) + timedelta(days=7)
        storage.update_progress(cid, 2.6, 7.0, future, 1, 4)

        progress = storage.get_progress(cid)
        assert progress["ease_factor"] == 2.6
        assert progress["interval_days"] == 7.0
        assert progress["review_count"] == 1
        assert progress["last_score"] == 4


class TestExplanations:
    def test_add_and_get_explanations(self, seeded_db):
        concepts = storage.get_all_concepts()
        cid = concepts[0]["id"]

        eid = storage.add_explanation(cid, "my explanation", 4, "covered", "missed", "good")
        assert eid > 0

        explanations = storage.get_explanations(cid)
        assert len(explanations) == 1
        assert explanations[0]["score"] == 4


class TestDuelMemory:
    def test_save_and_get(self, seeded_db):
        concepts = storage.get_all_concepts()
        cid = concepts[0]["id"]

        storage.save_duel_memory(cid, "they think X", "wrong about Y", "why not Z?")
        mem = storage.get_duel_memory(cid)
        assert mem is not None
        assert mem["last_belief"] == "they think X"
        assert mem["last_errors"] == "wrong about Y"

    def test_upsert_overwrites(self, seeded_db):
        concepts = storage.get_all_concepts()
        cid = concepts[0]["id"]

        storage.save_duel_memory(cid, "belief1", "err1", "atk1")
        storage.save_duel_memory(cid, "belief2", "err2", "atk2")

        mem = storage.get_duel_memory(cid)
        assert mem["last_belief"] == "belief2"

    def test_get_missing_returns_none(self, seeded_db):
        assert storage.get_duel_memory(99999) is None


class TestCachedClaims:
    def test_save_and_get(self, seeded_db):
        concepts = storage.get_all_concepts()
        cid = concepts[0]["id"]

        claims = [
            {"statement": "X does Y", "claim_type": "mechanism", "claim_index": 0},
            {"statement": "X requires Z", "claim_type": "requirement", "claim_index": 1},
        ]
        storage.save_cached_claims(cid, claims)

        cached = storage.get_cached_claims(cid)
        assert cached is not None
        assert len(cached) == 2
        assert cached[0]["statement"] == "X does Y"
        assert cached[1]["claim_type"] == "requirement"

    def test_get_missing_returns_none(self, seeded_db):
        concepts = storage.get_all_concepts()
        cid = concepts[0]["id"]
        assert storage.get_cached_claims(cid) is None

    def test_save_replaces_existing(self, seeded_db):
        concepts = storage.get_all_concepts()
        cid = concepts[0]["id"]

        storage.save_cached_claims(
            cid,
            [
                {"statement": "old", "claim_type": "definition", "claim_index": 0},
            ],
        )
        storage.save_cached_claims(
            cid,
            [
                {"statement": "new1", "claim_type": "mechanism", "claim_index": 0},
                {"statement": "new2", "claim_type": "boundary", "claim_index": 1},
            ],
        )

        cached = storage.get_cached_claims(cid)
        assert len(cached) == 2
        assert cached[0]["statement"] == "new1"


class TestStats:
    def test_stats_empty(self, tmp_db):
        stats = storage.get_stats()
        assert stats["total_sources"] == 0
        assert stats["total_concepts"] == 0

    def test_stats_with_data(self, seeded_db):
        stats = storage.get_stats()
        assert stats["total_sources"] == 1
        assert stats["total_concepts"] == 2
        assert stats["due_now"] == 2
