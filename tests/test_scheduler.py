"""Tests for SM-2 spaced repetition scheduler."""

import pytest

from learnlock import config, scheduler, storage


class TestUpdateAfterReview:
    def test_pass_first_review(self, seeded_db):
        concepts = storage.get_all_concepts()
        cid = concepts[0]["id"]

        result = scheduler.update_after_review(cid, 5)
        assert result["passed"] is True
        assert result["review_count"] == 1
        assert result["interval_days"] == config.SM2_INITIAL_INTERVAL

    def test_pass_second_review_jumps_to_6_days(self, seeded_db):
        concepts = storage.get_all_concepts()
        cid = concepts[0]["id"]

        scheduler.update_after_review(cid, 4)  # review_count becomes 1
        result = scheduler.update_after_review(cid, 4)  # review_count becomes 2
        assert result["review_count"] == 2
        assert result["interval_days"] == 6.0

    def test_fail_resets_review_count(self, seeded_db):
        concepts = storage.get_all_concepts()
        cid = concepts[0]["id"]

        scheduler.update_after_review(cid, 5)  # Pass once
        result = scheduler.update_after_review(cid, 1)  # Fail
        assert result["passed"] is False
        assert result["review_count"] == 0
        assert result["interval_days"] == config.SM2_INITIAL_INTERVAL

    def test_ease_never_below_minimum(self, seeded_db):
        concepts = storage.get_all_concepts()
        cid = concepts[0]["id"]

        # Repeatedly fail to drive ease down
        for _ in range(10):
            # Need to pass first to increment review_count, then fail
            scheduler.update_after_review(cid, 1)

        progress = storage.get_progress(cid)
        assert progress["ease_factor"] >= config.SM2_MIN_EASE

    def test_interval_capped_at_max(self, seeded_db):
        concepts = storage.get_all_concepts()
        cid = concepts[0]["id"]

        # Pass many times with perfect scores to grow interval
        for _ in range(20):
            scheduler.update_after_review(cid, 5)

        progress = storage.get_progress(cid)
        assert progress["interval_days"] <= config.SM2_MAX_INTERVAL

    def test_score_clamped_to_range(self, seeded_db):
        concepts = storage.get_all_concepts()
        cid = concepts[0]["id"]

        result = scheduler.update_after_review(cid, 99)
        assert result["passed"] is True  # 99 clamped to SCORE_MAX (5)

    def test_missing_progress_raises(self, tmp_db):
        with pytest.raises(ValueError, match="No progress found"):
            scheduler.update_after_review(99999, 3)


class TestGetDue:
    def test_next_due_returns_one(self, seeded_db):
        due = scheduler.get_next_due()
        assert due is not None
        assert "name" in due

    def test_all_due(self, seeded_db):
        due = scheduler.get_all_due()
        assert len(due) == 2

    def test_no_due_after_review(self, seeded_db):
        concepts = storage.get_all_concepts()
        for c in concepts:
            scheduler.update_after_review(c["id"], 5)

        assert scheduler.get_next_due() is None
        assert len(scheduler.get_all_due()) == 0


class TestStudySummary:
    def test_summary_keys(self, seeded_db):
        summary = scheduler.get_study_summary()
        assert "due_now" in summary
        assert "total_concepts" in summary
        assert "mastered" in summary
        assert "avg_score" in summary

    def test_summary_values(self, seeded_db):
        summary = scheduler.get_study_summary()
        assert summary["total_concepts"] == 2
        assert summary["due_now"] == 2
        assert summary["mastered"] == 0


class TestFormatInterval:
    def test_today(self):
        assert scheduler._format_interval(0.5) == "today"

    def test_tomorrow(self):
        assert scheduler._format_interval(1) == "tomorrow"

    def test_days(self):
        assert scheduler._format_interval(3) == "in 3 days"

    def test_weeks(self):
        assert scheduler._format_interval(14) == "in 2 weeks"

    def test_months(self):
        assert scheduler._format_interval(60) == "in 2 months"
