"""Tests for storage module."""

import pytest

from learnlock import __version__, config, storage


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


class TestDeleteSource:
    def test_delete_removes_source_and_concepts(self, seeded_db):
        sources = storage.get_all_sources()
        assert len(sources) == 1

        removed = storage.delete_source(sources[0]["id"])
        assert removed == 2

        assert len(storage.get_all_sources()) == 0
        assert len(storage.get_all_concepts()) == 0

    def test_delete_cascades_to_progress(self, seeded_db):
        sources = storage.get_all_sources()
        concepts = storage.get_all_concepts()

        # Verify progress exists before
        for c in concepts:
            assert storage.get_progress(c["id"]) is not None

        storage.delete_source(sources[0]["id"])

        # Progress should be gone
        for c in concepts:
            assert storage.get_progress(c["id"]) is None

    def test_delete_nonexistent_returns_zero(self, tmp_db):
        assert storage.delete_source(99999) == 0


class TestUpdateCachedClaim:
    def test_update_claim_statement(self, seeded_db):
        concepts = storage.get_all_concepts()
        cid = concepts[0]["id"]

        storage.save_cached_claims(cid, [
            {"statement": "old text", "claim_type": "mechanism", "claim_index": 0},
        ])

        assert storage.update_cached_claim(cid, 0, "new text")

        cached = storage.get_cached_claims(cid)
        assert cached[0]["statement"] == "new text"

    def test_update_missing_returns_false(self, seeded_db):
        concepts = storage.get_all_concepts()
        assert not storage.update_cached_claim(concepts[0]["id"], 99, "x")


class TestDeleteCachedClaim:
    def test_delete_and_reindex(self, seeded_db):
        concepts = storage.get_all_concepts()
        cid = concepts[0]["id"]

        storage.save_cached_claims(cid, [
            {"statement": "A", "claim_type": "definition", "claim_index": 0},
            {"statement": "B", "claim_type": "mechanism", "claim_index": 1},
            {"statement": "C", "claim_type": "boundary", "claim_index": 2},
        ])

        assert storage.delete_cached_claim(cid, 1)

        cached = storage.get_cached_claims(cid)
        assert len(cached) == 2
        assert cached[0]["statement"] == "A"
        assert cached[0]["claim_index"] == 0
        assert cached[1]["statement"] == "C"
        assert cached[1]["claim_index"] == 1

    def test_delete_missing_returns_false(self, seeded_db):
        concepts = storage.get_all_concepts()
        assert not storage.delete_cached_claim(concepts[0]["id"], 99)


class TestExportImport:
    def test_export_has_all_tables(self, seeded_db):
        data = storage.export_all_data()
        assert data["schema_version"] == storage.EXPORT_SCHEMA_VERSION
        assert data["version"] == __version__
        assert "sources" in data
        assert "concepts" in data
        assert "progress" in data
        assert len(data["sources"]) == 1
        assert len(data["concepts"]) == 2

    def test_import_into_empty_db(self, seeded_db, tmp_path, monkeypatch):
        # Export from seeded
        data = storage.export_all_data()

        # Create a fresh DB
        new_db = tmp_path / "import_test.db"
        monkeypatch.setattr(config, "DB_PATH", new_db)
        storage.reset_init_cache()
        storage.init_db(new_db)

        result = storage.import_all_data(data)
        assert result["sources_added"] == 1
        assert result["sources_merged"] == 0
        assert result["concepts_added"] == 2
        assert result["concepts_merged"] == 0

        # Verify data is there
        assert len(storage.get_all_sources()) == 1
        assert len(storage.get_all_concepts()) == 2

    def test_import_merges_duplicates(self, seeded_db):
        data = storage.export_all_data()
        result = storage.import_all_data(data)
        assert result["sources_added"] == 0
        assert result["sources_merged"] == 1
        assert result["concepts_merged"] == 2

    def test_roundtrip_preserves_progress(self, seeded_db, tmp_path, monkeypatch):
        # Update progress on a concept
        concepts = storage.get_all_concepts()
        from datetime import datetime, timezone
        future = datetime(2030, 1, 1, tzinfo=timezone.utc)
        storage.update_progress(concepts[0]["id"], 3.0, 7.0, future, 5, 4)

        data = storage.export_all_data()

        # Fresh DB
        new_db = tmp_path / "roundtrip.db"
        monkeypatch.setattr(config, "DB_PATH", new_db)
        storage.reset_init_cache()
        storage.init_db(new_db)

        storage.import_all_data(data)

        imported_concepts = storage.get_all_concepts()
        prog = storage.get_progress(imported_concepts[0]["id"])
        assert prog is not None
        assert prog["ease_factor"] == 3.0
        assert prog["review_count"] == 5

    def test_import_merges_progress_memory_and_claims(self, seeded_db, tmp_path, monkeypatch):
        from datetime import datetime, timezone

        concepts = storage.get_all_concepts()
        widget = next(concept for concept in concepts if concept["name"] == "Widget")
        future = datetime(2030, 1, 1, tzinfo=timezone.utc)

        storage.update_progress(widget["id"], 3.0, 7.0, future, 5, 4)
        storage.add_explanation(widget["id"], "imported explanation", 4, None, None, "belief")
        storage.save_duel_memory(widget["id"], "fresh belief", "fresh errors", "fresh attack")
        storage.save_cached_claims(
            widget["id"],
            [
                {
                    "statement": "Imported claim",
                    "claim_type": "definition",
                    "claim_index": 0,
                },
            ],
        )
        exported = storage.export_all_data()

        new_db = tmp_path / "merge.db"
        monkeypatch.setattr(config, "DB_PATH", new_db)
        storage.reset_init_cache()
        storage.init_db(new_db)

        storage.add_source_with_concepts(
            url="https://example.com/test",
            title="Older title",
            source_type="article",
            raw_content="short content",
            concepts=[
                {
                    "name": "Widget",
                    "source_quote": "Widgets are reusable components",
                    "ground_truth": "old truth",
                    "question": "old question",
                },
                {
                    "name": "Gadget",
                    "source_quote": "Gadgets extend widgets",
                    "ground_truth": "old gadget truth",
                    "question": "old gadget question",
                },
            ],
        )
        local_widget = next(
            concept for concept in storage.get_all_concepts() if concept["name"] == "Widget"
        )
        local_future = datetime(2028, 1, 1, tzinfo=timezone.utc)
        storage.update_progress(local_widget["id"], 2.1, 1.0, local_future, 1, 2)
        storage.save_duel_memory(local_widget["id"], "old belief", "old errors", "old attack")
        storage.save_cached_claims(
            local_widget["id"],
            [
                {
                    "statement": "Old local claim",
                    "claim_type": "definition",
                    "claim_index": 0,
                },
            ],
        )

        result = storage.import_all_data(exported)
        assert result["sources_added"] == 0
        assert result["sources_merged"] == 1
        assert result["concepts_merged"] == 2

        merged_widget = next(
            concept for concept in storage.get_all_concepts() if concept["name"] == "Widget"
        )
        progress = storage.get_progress(merged_widget["id"])
        assert progress["review_count"] == 5
        assert storage.get_duel_memory(merged_widget["id"])["last_belief"] == "fresh belief"
        assert storage.get_cached_claims(merged_widget["id"])[0]["statement"] == "Imported claim"
        explanations = storage.get_explanations(merged_widget["id"])
        assert any(explanation["text"] == "imported explanation" for explanation in explanations)

    def test_import_rejects_missing_required_fields(self, tmp_db):
        with pytest.raises(storage.ImportValidationError, match="missing required field"):
            storage.import_all_data(
                {
                    "schema_version": storage.EXPORT_SCHEMA_VERSION,
                    "sources": [{"id": 1, "url": "https://example.com"}],
                    "concepts": [],
                    "progress": [],
                    "explanations": [],
                    "duel_memory": [],
                    "cached_claims": [],
                }
            )

    def test_import_rejects_future_schema_version(self, tmp_db):
        with pytest.raises(
            storage.ImportValidationError,
            match="Unsupported export schema version",
        ):
            storage.import_all_data(
                {
                    "schema_version": storage.EXPORT_SCHEMA_VERSION + 1,
                    "sources": [],
                    "concepts": [],
                    "progress": [],
                    "explanations": [],
                    "duel_memory": [],
                    "cached_claims": [],
                }
            )


class TestStats:
    def test_stats_empty(self, tmp_db):
        stats = storage.get_stats()
        assert stats["total_sources"] == 0
        assert stats["total_concepts"] == 0
        assert stats["successful_reviews"] == 0

    def test_stats_with_data(self, seeded_db):
        concept = storage.get_all_concepts()[0]
        storage.add_explanation(concept["id"], "good", 4, None, None, "solid")
        stats = storage.get_stats()
        assert stats["total_sources"] == 1
        assert stats["total_concepts"] == 2
        assert stats["due_now"] == 2
        assert stats["successful_reviews"] == 1
