"""Local SQLite storage for learn-lock."""

import os
import sqlite3
from collections.abc import Mapping
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from . import __version__, config

_initialized_dbs: set[str] = set()
EXPORT_SCHEMA_VERSION = 1


class ImportValidationError(ValueError):
    """Raised when an import payload is missing required structure."""


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _parse_timestamp(value: object) -> datetime:
    """Best-effort ISO timestamp parsing for import/export merges."""
    if not isinstance(value, str) or not value:
        return datetime.min.replace(tzinfo=timezone.utc)
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return datetime.min.replace(tzinfo=timezone.utc)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _earliest_timestamp(*values: object) -> str:
    timestamps = [
        (parsed, raw)
        for raw in values
        if isinstance(raw, str) and raw
        for parsed in [_parse_timestamp(raw)]
        if parsed != datetime.min.replace(tzinfo=timezone.utc)
    ]
    return min(timestamps, key=lambda item: item[0])[1] if timestamps else _utcnow().isoformat()


def _latest_timestamp(*values: object) -> str:
    timestamps = [
        (parsed, raw)
        for raw in values
        if isinstance(raw, str) and raw
        for parsed in [_parse_timestamp(raw)]
        if parsed != datetime.min.replace(tzinfo=timezone.utc)
    ]
    return max(timestamps, key=lambda item: item[0])[1] if timestamps else _utcnow().isoformat()


def _prefer_text(existing: object, incoming: object) -> str | None:
    """Prefer richer non-empty text when merging exports into local state."""
    existing_text = existing if isinstance(existing, str) else None
    incoming_text = incoming if isinstance(incoming, str) else None
    if not existing_text:
        return incoming_text
    if not incoming_text:
        return existing_text
    return incoming_text if len(incoming_text) > len(existing_text) else existing_text


def _validated_list(data: Mapping[str, object], key: str) -> list[dict]:
    value = data.get(key)
    if not isinstance(value, list):
        raise ImportValidationError(f"Invalid export: '{key}' must be a list.")

    rows: list[dict] = []
    for index, row in enumerate(value):
        if not isinstance(row, Mapping):
            raise ImportValidationError(f"Invalid export: '{key}[{index}]' must be an object.")
        rows.append(dict(row))
    return rows


def _require_keys(row: Mapping[str, object], key: str, required: set[str], index: int) -> None:
    missing = sorted(required - row.keys())
    if missing:
        missing_text = ", ".join(missing)
        raise ImportValidationError(
            f"Invalid export: '{key}[{index}]' is missing required field(s): {missing_text}."
        )


def validate_import_data(data: object) -> dict:
    """Validate and normalize an export payload before import."""
    if not isinstance(data, Mapping):
        raise ImportValidationError("Invalid export: top-level JSON value must be an object.")

    schema_version = data.get("schema_version", 0)
    if not isinstance(schema_version, int):
        raise ImportValidationError("Invalid export: 'schema_version' must be an integer.")
    if schema_version > EXPORT_SCHEMA_VERSION:
        raise ImportValidationError(
            f"Unsupported export schema version {schema_version}. "
            f"This build supports up to {EXPORT_SCHEMA_VERSION}."
        )

    normalized = {
        "schema_version": schema_version,
        "version": data.get("version"),
        "exported_at": data.get("exported_at"),
    }

    required_rows = {
        "sources": {"id", "url", "title", "source_type", "raw_content"},
        "concepts": {"id", "source_id", "name", "source_quote"},
        "progress": {"concept_id", "due_date"},
        "explanations": {"concept_id", "text"},
        "duel_memory": {"concept_id"},
        "cached_claims": {"concept_id", "statement", "claim_type", "claim_index"},
    }

    for key, required in required_rows.items():
        rows = _validated_list(data, key)
        for index, row in enumerate(rows):
            _require_keys(row, key, required, index)
        normalized[key] = rows

    source_ids = {row["id"] for row in normalized["sources"]}
    concept_ids = {row["id"] for row in normalized["concepts"]}
    missing_source_refs = {
        row["source_id"]
        for row in normalized["concepts"]
        if row["source_id"] not in source_ids
    }
    if missing_source_refs:
        raise ImportValidationError(
            "Invalid export: one or more concepts reference unknown source ids."
        )

    for key in ("progress", "explanations", "duel_memory", "cached_claims"):
        missing_concepts = {
            row["concept_id"]
            for row in normalized[key]
            if row["concept_id"] not in concept_ids
        }
        if missing_concepts:
            raise ImportValidationError(
                f"Invalid export: '{key}' references unknown concept ids."
            )

    return normalized


def _connect(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, timeout=config.SQLITE_TIMEOUT_SECONDS)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute(f"PRAGMA busy_timeout = {int(config.SQLITE_TIMEOUT_SECONDS * 1000)}")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def init_db(db_path: Path | None = None) -> None:
    """Initialize database with schema. Only runs once per path."""
    if db_path is None:
        db_path = config.DB_PATH

    db_key = str(db_path.resolve())
    if db_key in _initialized_dbs:
        return

    db_path.parent.mkdir(parents=True, exist_ok=True)

    # Use hardcoded defaults in CREATE TABLE to prevent SQL injection via env vars
    with _connect(db_path) as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                source_type TEXT NOT NULL,
                raw_content TEXT NOT NULL,
                segments TEXT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS concepts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                source_quote TEXT NOT NULL,
                ground_truth TEXT,
                question TEXT,
                skipped INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS explanations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                concept_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                score INTEGER,
                covered TEXT,
                missed TEXT,
                feedback TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                concept_id INTEGER UNIQUE NOT NULL,
                ease_factor REAL DEFAULT 2.5,
                interval_days REAL DEFAULT 1.0,
                due_date TEXT NOT NULL,
                review_count INTEGER DEFAULT 0,
                last_score INTEGER,
                created_at TEXT NOT NULL,
                FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS duel_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                concept_id INTEGER UNIQUE NOT NULL,
                last_belief TEXT,
                last_errors TEXT,
                last_attack TEXT,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS cached_claims (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                concept_id INTEGER NOT NULL,
                statement TEXT NOT NULL,
                claim_type TEXT NOT NULL,
                claim_index INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_progress_due ON progress(due_date);
            CREATE INDEX IF NOT EXISTS idx_concepts_source ON concepts(source_id);
            CREATE INDEX IF NOT EXISTS idx_concepts_skipped ON concepts(skipped);
            CREATE INDEX IF NOT EXISTS idx_cached_claims_concept ON cached_claims(concept_id);
        """)

        # Migrations for older databases
        cursor = conn.execute("PRAGMA table_info(sources)")
        cols = [row[1] for row in cursor.fetchall()]
        if "segments" not in cols:
            conn.execute("ALTER TABLE sources ADD COLUMN segments TEXT")

        cursor = conn.execute("PRAGMA table_info(concepts)")
        cols = [row[1] for row in cursor.fetchall()]
        if "ground_truth" not in cols:
            conn.execute("ALTER TABLE concepts ADD COLUMN ground_truth TEXT")
            conn.execute(
                "UPDATE concepts SET ground_truth = source_quote WHERE ground_truth IS NULL"
            )

        # Add duel_memory table if missing (migration for pre-duel databases)
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='duel_memory'"
        )
        if not cursor.fetchone():
            conn.execute("""CREATE TABLE duel_memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                concept_id INTEGER UNIQUE NOT NULL,
                last_belief TEXT,
                last_errors TEXT,
                last_attack TEXT,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
            )""")

        # Add cached_claims table if missing (migration)
        cursor = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='cached_claims'"
        )
        if not cursor.fetchone():
            conn.execute("""CREATE TABLE cached_claims (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                concept_id INTEGER NOT NULL,
                statement TEXT NOT NULL,
                claim_type TEXT NOT NULL,
                claim_index INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
            )""")
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_cached_claims_concept ON cached_claims(concept_id)"
            )

    try:
        os.chmod(db_path, 0o600)
    except OSError:
        pass

    _initialized_dbs.add(db_key)


def reset_init_cache() -> None:
    """Reset the initialization cache. Useful for testing."""
    _initialized_dbs.clear()


@contextmanager
def get_db(db_path: Path | None = None):
    """Get database connection."""
    if db_path is None:
        db_path = config.DB_PATH

    init_db(db_path)
    conn = _connect(db_path)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


# ============ SOURCES ============


def add_source(
    url: str, title: str, source_type: str, raw_content: str, segments: str | None = None
) -> int:
    """Add a source. Returns source ID."""
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO sources (url, title, source_type, raw_content, segments, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (url, title, source_type, raw_content, segments, _utcnow().isoformat()),
        )
        return cursor.lastrowid


def add_source_with_concepts(
    *,
    url: str,
    title: str,
    source_type: str,
    raw_content: str,
    concepts: list[dict],
    segments: str | None = None,
) -> int:
    """Atomically save a source and its extracted concepts."""

    now = _utcnow()
    with get_db() as conn:
        source_cursor = conn.execute(
            """
            INSERT INTO sources (url, title, source_type, raw_content, segments, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (url, title, source_type, raw_content, segments, now.isoformat()),
        )
        source_id = source_cursor.lastrowid

        for concept in concepts:
            concept_cursor = conn.execute(
                """
                INSERT INTO concepts
                (source_id, name, source_quote, ground_truth, question, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    source_id,
                    concept["name"],
                    concept["source_quote"],
                    concept.get("ground_truth", concept["source_quote"]),
                    concept.get("question"),
                    now.isoformat(),
                ),
            )
            conn.execute(
                "INSERT INTO progress (concept_id, due_date, created_at) VALUES (?, ?, ?)",
                (concept_cursor.lastrowid, now.isoformat(), now.isoformat()),
            )

        return source_id


def get_source_by_url(url: str) -> Optional[dict]:
    """Get source by URL."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM sources WHERE url = ?", (url,)).fetchone()
        return dict(row) if row else None


def get_all_sources() -> list[dict]:
    """Get all sources."""
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM sources ORDER BY created_at DESC").fetchall()
        return [dict(row) for row in rows]


def get_source(source_id: int) -> Optional[dict]:
    """Get source by ID."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM sources WHERE id = ?", (source_id,)
        ).fetchone()
        return dict(row) if row else None


def delete_source(source_id: int) -> int:
    """Delete a source and all its concepts/progress/claims (cascade).

    Returns the number of concepts that were removed.
    """
    with get_db() as conn:
        count = conn.execute(
            "SELECT COUNT(*) FROM concepts WHERE source_id = ?",
            (source_id,),
        ).fetchone()[0]
        conn.execute("DELETE FROM sources WHERE id = ?", (source_id,))
        return count


# ============ CONCEPTS ============


def add_concept(
    source_id: int,
    name: str,
    source_quote: str,
    question: str | None = None,
    ground_truth: str | None = None,
) -> int:
    """Add a concept with initial progress. Returns concept ID.

    New concepts are due immediately so user can study right after adding.
    """
    now = _utcnow()
    # Due immediately - user should study right after adding
    due = now

    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO concepts
            (source_id, name, source_quote, ground_truth, question, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                source_id,
                name,
                source_quote,
                ground_truth or source_quote,
                question,
                now.isoformat(),
            ),
        )
        concept_id = cursor.lastrowid

        conn.execute(
            "INSERT INTO progress (concept_id, due_date, created_at) VALUES (?, ?, ?)",
            (concept_id, due.isoformat(), now.isoformat()),
        )
        return concept_id


def get_concept(concept_id: int) -> Optional[dict]:
    """Get concept by ID with source info."""
    with get_db() as conn:
        row = conn.execute(
            """
            SELECT c.*, s.title as source_title, s.url as source_url
            FROM concepts c
            JOIN sources s ON c.source_id = s.id
            WHERE c.id = ?
        """,
            (concept_id,),
        ).fetchone()
        return dict(row) if row else None


def get_concepts_for_source(source_id: int) -> list[dict]:
    """Get all concepts for a source."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM concepts WHERE source_id = ? ORDER BY id", (source_id,)
        ).fetchall()
        return [dict(row) for row in rows]


def get_all_concepts() -> list[dict]:
    """Get all concepts with source info (excluding skipped)."""
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT c.*, s.title as source_title, s.url as source_url
            FROM concepts c
            JOIN sources s ON c.source_id = s.id
            WHERE c.skipped = 0
            ORDER BY c.created_at DESC
        """
        ).fetchall()
        return [dict(row) for row in rows]


def skip_concept(concept_id: int) -> None:
    """Mark concept as skipped."""
    with get_db() as conn:
        conn.execute("UPDATE concepts SET skipped = 1 WHERE id = ?", (concept_id,))


def unskip_concept(concept_id: int) -> None:
    """Unmark concept as skipped."""
    with get_db() as conn:
        conn.execute("UPDATE concepts SET skipped = 0 WHERE id = ?", (concept_id,))


def get_skipped_concepts() -> list[dict]:
    """Get all skipped concepts with source info."""
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT c.*, s.title as source_title
            FROM concepts c JOIN sources s ON c.source_id = s.id
            WHERE c.skipped = 1
        """
        ).fetchall()
        return [dict(r) for r in rows]


# ============ PROGRESS ============


def get_due_concepts(limit: int | None = None) -> list[dict]:
    """Get concepts due for review (not skipped)."""
    if limit is None:
        limit = 100  # Reasonable default

    now = _utcnow().isoformat()
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT c.*, p.ease_factor, p.interval_days, p.due_date,
                   p.review_count, p.last_score,
                   s.title as source_title, s.url as source_url
            FROM concepts c
            JOIN progress p ON c.id = p.concept_id
            JOIN sources s ON c.source_id = s.id
            WHERE p.due_date <= ? AND c.skipped = 0
            ORDER BY p.due_date ASC
            LIMIT ?
        """,
            (now, limit),
        ).fetchall()
        return [dict(row) for row in rows]


def get_progress(concept_id: int) -> Optional[dict]:
    """Get progress for a concept."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM progress WHERE concept_id = ?", (concept_id,)).fetchone()
        return dict(row) if row else None


def update_progress(
    concept_id: int,
    ease_factor: float,
    interval_days: float,
    due_date: datetime,
    review_count: int,
    last_score: int,
) -> None:
    """Update progress for a concept."""
    with get_db() as conn:
        conn.execute(
            """
            UPDATE progress
            SET ease_factor = ?, interval_days = ?, due_date = ?,
                review_count = ?, last_score = ?
            WHERE concept_id = ?
        """,
            (
                ease_factor,
                interval_days,
                due_date.isoformat(),
                review_count,
                last_score,
                concept_id,
            ),
        )


# ============ EXPLANATIONS ============


def add_explanation(
    concept_id: int,
    text: str,
    score: int | None = None,
    covered: str | None = None,
    missed: str | None = None,
    feedback: str | None = None,
) -> int:
    """Add an explanation with evaluation results."""
    with get_db() as conn:
        cursor = conn.execute(
            """INSERT INTO explanations
               (concept_id, text, score, covered, missed, feedback, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (concept_id, text, score, covered, missed, feedback, _utcnow().isoformat()),
        )
        return cursor.lastrowid


def get_explanations(concept_id: int) -> list[dict]:
    """Get all explanations for a concept."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM explanations WHERE concept_id = ? ORDER BY created_at DESC",
            (concept_id,),
        ).fetchall()
        return [dict(row) for row in rows]


# ============ STATS ============


def get_stats() -> dict:
    """Get overall statistics."""
    with get_db() as conn:
        total_sources = conn.execute("SELECT COUNT(*) FROM sources").fetchone()[0]
        total_concepts = conn.execute("SELECT COUNT(*) FROM concepts WHERE skipped = 0").fetchone()[
            0
        ]
        skipped_concepts = conn.execute(
            "SELECT COUNT(*) FROM concepts WHERE skipped = 1"
        ).fetchone()[0]
        total_explanations = conn.execute("SELECT COUNT(*) FROM explanations").fetchone()[0]

        now = _utcnow().isoformat()
        due_count = conn.execute(
            """
            SELECT COUNT(*) FROM progress p
            JOIN concepts c ON p.concept_id = c.id
            WHERE p.due_date <= ? AND c.skipped = 0
        """,
            (now,),
        ).fetchone()[0]

        avg_score = conn.execute(
            "SELECT AVG(score) FROM explanations WHERE score IS NOT NULL"
        ).fetchone()[0]

        mastered = conn.execute(
            """
            SELECT COUNT(*) FROM progress
            WHERE ease_factor >= ? AND review_count >= ?
        """,
            (config.MASTERY_MIN_EASE, config.MASTERY_MIN_REVIEWS),
        ).fetchone()[0]
        successful_reviews = conn.execute(
            "SELECT COUNT(*) FROM explanations WHERE score >= 4"
        ).fetchone()[0]

        return {
            "total_sources": total_sources,
            "total_concepts": total_concepts,
            "skipped_concepts": skipped_concepts,
            "total_reviews": total_explanations,
            "successful_reviews": successful_reviews,
            "due_now": due_count,
            "avg_score": round(avg_score, 1) if avg_score else 0,
            "mastered": mastered,
        }


# ============ DUEL MEMORY ============


def save_duel_memory(concept_id: int, belief: str, errors: str, attack: str) -> None:
    """Save last duel state for a concept."""
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO duel_memory (concept_id, last_belief, last_errors, last_attack, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(concept_id) DO UPDATE SET
                last_belief = excluded.last_belief,
                last_errors = excluded.last_errors,
                last_attack = excluded.last_attack,
                updated_at = excluded.updated_at
        """,
            (concept_id, belief, errors, attack, _utcnow().isoformat()),
        )


def get_duel_memory(concept_id: int) -> Optional[dict]:
    """Get last duel state for a concept."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT last_belief, last_errors, last_attack FROM duel_memory WHERE concept_id = ?",
            (concept_id,),
        ).fetchone()
        if row:
            return {
                "last_belief": row[0],
                "last_errors": row[1],
                "last_attack": row[2],
            }
        return None


# ============ CACHED CLAIMS ============


def get_cached_claims(concept_id: int) -> list[dict] | None:
    """Get cached claims for a concept. Returns None if no cache exists."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT statement, claim_type, claim_index FROM cached_claims "
            "WHERE concept_id = ? ORDER BY claim_index",
            (concept_id,),
        ).fetchall()

        if not rows:
            return None

        return [{"statement": row[0], "claim_type": row[1], "claim_index": row[2]} for row in rows]


def save_cached_claims(concept_id: int, claims: list[dict]) -> None:
    """Cache parsed claims for a concept. Replaces any existing cache."""
    with get_db() as conn:
        conn.execute(
            "DELETE FROM cached_claims WHERE concept_id = ?",
            (concept_id,),
        )
        now = _utcnow().isoformat()
        for claim in claims:
            conn.execute(
                "INSERT INTO cached_claims "
                "(concept_id, statement, claim_type, claim_index, created_at) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    concept_id,
                    claim["statement"],
                    claim["claim_type"],
                    claim["claim_index"],
                    now,
                ),
            )


def update_cached_claim(
    concept_id: int, claim_index: int, statement: str
) -> bool:
    """Update a single cached claim's statement. Returns True if updated."""
    with get_db() as conn:
        now = _utcnow().isoformat()
        cursor = conn.execute(
            "UPDATE cached_claims SET statement = ?, created_at = ? "
            "WHERE concept_id = ? AND claim_index = ?",
            (statement, now, concept_id, claim_index),
        )
        return cursor.rowcount > 0


def delete_cached_claim(concept_id: int, claim_index: int) -> bool:
    """Delete a single cached claim. Returns True if deleted."""
    with get_db() as conn:
        cursor = conn.execute(
            "DELETE FROM cached_claims "
            "WHERE concept_id = ? AND claim_index = ?",
            (concept_id, claim_index),
        )
        if cursor.rowcount > 0:
            now = _utcnow().isoformat()
            # Re-index remaining claims
            rows = conn.execute(
                "SELECT id FROM cached_claims "
                "WHERE concept_id = ? ORDER BY claim_index",
                (concept_id,),
            ).fetchall()
            for i, row in enumerate(rows):
                conn.execute(
                    "UPDATE cached_claims SET claim_index = ?, created_at = ? WHERE id = ?",
                    (i, now, row[0]),
                )
            return True
        return False


# ============ EXPORT / IMPORT ============


def export_all_data() -> dict:
    """Export entire database to a JSON-serializable dict."""
    with get_db() as conn:
        sources = [
            dict(r) for r in conn.execute(
                "SELECT * FROM sources ORDER BY id"
            ).fetchall()
        ]
        concepts = [
            dict(r) for r in conn.execute(
                "SELECT * FROM concepts ORDER BY id"
            ).fetchall()
        ]
        progress = [
            dict(r) for r in conn.execute(
                "SELECT * FROM progress ORDER BY id"
            ).fetchall()
        ]
        explanations = [
            dict(r) for r in conn.execute(
                "SELECT * FROM explanations ORDER BY id"
            ).fetchall()
        ]
        duel_memory = [
            dict(r) for r in conn.execute(
                "SELECT * FROM duel_memory ORDER BY id"
            ).fetchall()
        ]
        cached_claims = [
            dict(r) for r in conn.execute(
                "SELECT * FROM cached_claims ORDER BY id"
            ).fetchall()
        ]

    return {
        "schema_version": EXPORT_SCHEMA_VERSION,
        "version": __version__,
        "exported_at": _utcnow().isoformat(),
        "sources": sources,
        "concepts": concepts,
        "progress": progress,
        "explanations": explanations,
        "duel_memory": duel_memory,
        "cached_claims": cached_claims,
    }


def _merge_progress_row(
    conn: sqlite3.Connection,
    concept_id: int,
    imported: Mapping[str, object] | None,
    imported_activity_at: str,
    now: str,
) -> bool:
    """Merge progress by keeping the row with stronger evidence of recency."""
    existing = conn.execute(
        "SELECT * FROM progress WHERE concept_id = ?",
        (concept_id,),
    ).fetchone()

    if imported is None:
        if existing is None:
            conn.execute(
                "INSERT INTO progress (concept_id, due_date, created_at) VALUES (?, ?, ?)",
                (concept_id, now, now),
            )
        return False

    if existing is None:
        conn.execute(
            """
            INSERT INTO progress
            (concept_id, ease_factor, interval_days, due_date, review_count, last_score, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                concept_id,
                imported.get("ease_factor", 2.5),
                imported.get("interval_days", 1.0),
                imported.get("due_date", now),
                imported.get("review_count", 0),
                imported.get("last_score"),
                imported.get("created_at", now),
            ),
        )
        return True

    existing_activity_at = conn.execute(
        "SELECT MAX(created_at) FROM explanations WHERE concept_id = ?",
        (concept_id,),
    ).fetchone()[0] or existing["due_date"]

    imported_rank = (
        int(imported.get("review_count", 0) or 0),
        _parse_timestamp(imported_activity_at),
        _parse_timestamp(imported.get("due_date")),
    )
    existing_rank = (
        int(existing["review_count"] or 0),
        _parse_timestamp(existing_activity_at),
        _parse_timestamp(existing["due_date"]),
    )

    if imported_rank > existing_rank:
        conn.execute(
            """
            UPDATE progress
            SET ease_factor = ?, interval_days = ?, due_date = ?,
                review_count = ?, last_score = ?, created_at = ?
            WHERE concept_id = ?
            """,
            (
                imported.get("ease_factor", existing["ease_factor"]),
                imported.get("interval_days", existing["interval_days"]),
                imported.get("due_date", existing["due_date"]),
                imported.get("review_count", existing["review_count"]),
                imported.get("last_score", existing["last_score"]),
                imported.get("created_at", existing["created_at"]),
                concept_id,
            ),
        )
        return True
    return False


def _merge_duel_memory(
    conn: sqlite3.Connection,
    concept_id: int,
    imported: Mapping[str, object] | None,
    *,
    prefer_import: bool = False,
) -> bool:
    if imported is None:
        return False

    existing = conn.execute(
        "SELECT updated_at FROM duel_memory WHERE concept_id = ?",
        (concept_id,),
    ).fetchone()
    imported_updated_at = imported.get("updated_at") or _utcnow().isoformat()
    if (
        existing
        and not prefer_import
        and _parse_timestamp(existing["updated_at"])
        > _parse_timestamp(imported_updated_at)
    ):
        return False

    conn.execute(
        """
        INSERT INTO duel_memory (concept_id, last_belief, last_errors, last_attack, updated_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(concept_id) DO UPDATE SET
            last_belief = excluded.last_belief,
            last_errors = excluded.last_errors,
            last_attack = excluded.last_attack,
            updated_at = excluded.updated_at
        """,
        (
            concept_id,
            imported.get("last_belief"),
            imported.get("last_errors"),
            imported.get("last_attack"),
            imported_updated_at,
        ),
    )
    return True


def _replace_cached_claims(
    conn: sqlite3.Connection,
    concept_id: int,
    claims: list[dict],
) -> None:
    conn.execute("DELETE FROM cached_claims WHERE concept_id = ?", (concept_id,))
    for claim in sorted(claims, key=lambda row: row["claim_index"]):
        conn.execute(
            """
            INSERT INTO cached_claims
            (concept_id, statement, claim_type, claim_index, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                concept_id,
                claim["statement"],
                claim["claim_type"],
                claim["claim_index"],
                claim.get("created_at", _utcnow().isoformat()),
            ),
        )


def _merge_cached_claims(
    conn: sqlite3.Connection,
    concept_id: int,
    imported_claims: list[dict],
    *,
    prefer_import: bool = False,
) -> bool:
    if not imported_claims:
        return False

    existing = conn.execute(
        """
        SELECT statement, claim_type, claim_index, created_at
        FROM cached_claims
        WHERE concept_id = ?
        ORDER BY claim_index
        """,
        (concept_id,),
    ).fetchall()
    existing_rows = [dict(row) for row in existing]
    if not existing_rows:
        _replace_cached_claims(conn, concept_id, imported_claims)
        return True

    imported_latest = max(
        (_parse_timestamp(claim.get("created_at")) for claim in imported_claims),
        default=datetime.min.replace(tzinfo=timezone.utc),
    )
    existing_latest = max(
        (_parse_timestamp(claim.get("created_at")) for claim in existing_rows),
        default=datetime.min.replace(tzinfo=timezone.utc),
    )

    normalized_imported = [
        (claim["statement"], claim["claim_type"], claim["claim_index"]) for claim in imported_claims
    ]
    normalized_existing = [
        (claim["statement"], claim["claim_type"], claim["claim_index"]) for claim in existing_rows
    ]

    if (
        (prefer_import or imported_latest >= existing_latest)
        and normalized_imported != normalized_existing
    ):
        _replace_cached_claims(conn, concept_id, imported_claims)
        return True

    return False


def _merge_explanations(
    conn: sqlite3.Connection,
    concept_id: int,
    explanations: list[dict],
) -> int:
    existing_keys = {
        (row["text"], row["created_at"])
        for row in conn.execute(
            "SELECT text, created_at FROM explanations WHERE concept_id = ?",
            (concept_id,),
        ).fetchall()
    }
    added = 0
    for explanation in explanations:
        key = (
            explanation["text"],
            explanation.get("created_at") or _utcnow().isoformat(),
        )
        if key in existing_keys:
            continue
        conn.execute(
            """
            INSERT INTO explanations
            (concept_id, text, score, covered, missed, feedback, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                concept_id,
                explanation["text"],
                explanation.get("score"),
                explanation.get("covered"),
                explanation.get("missed"),
                explanation.get("feedback"),
                key[1],
            ),
        )
        existing_keys.add(key)
        added += 1
    return added


def import_all_data(data: dict) -> dict:
    """Import data from an export dict and merge it into the local database."""
    payload = validate_import_data(data)
    sources = payload["sources"]
    concepts = payload["concepts"]
    progress_rows = payload["progress"]
    explanations = payload["explanations"]
    duel_mem = payload["duel_memory"]
    claims = payload["cached_claims"]

    concepts_by_source: dict[int, list[dict]] = {}
    for concept in concepts:
        concepts_by_source.setdefault(concept["source_id"], []).append(concept)

    progress_by_concept = {row["concept_id"]: row for row in progress_rows}
    explanations_by_concept: dict[int, list[dict]] = {}
    for explanation in explanations:
        explanations_by_concept.setdefault(explanation["concept_id"], []).append(explanation)
    mem_by_concept = {row["concept_id"]: row for row in duel_mem}
    claims_by_concept: dict[int, list[dict]] = {}
    for claim in claims:
        claims_by_concept.setdefault(claim["concept_id"], []).append(claim)

    sources_added = 0
    sources_merged = 0
    concepts_added = 0
    concepts_merged = 0
    explanations_added = 0
    duel_memories_updated = 0
    cached_claim_sets_updated = 0
    now = _utcnow().isoformat()

    with get_db() as conn:
        for src in sources:
            existing_source = conn.execute(
                "SELECT * FROM sources WHERE url = ?",
                (src["url"],),
            ).fetchone()

            if existing_source:
                source_id = existing_source["id"]
                conn.execute(
                    """
                    UPDATE sources
                    SET title = ?, source_type = ?, raw_content = ?, segments = ?, created_at = ?
                    WHERE id = ?
                    """,
                    (
                        _prefer_text(existing_source["title"], src["title"])
                        or existing_source["title"],
                        existing_source["source_type"] or src["source_type"],
                        _prefer_text(existing_source["raw_content"], src["raw_content"])
                        or existing_source["raw_content"],
                        _prefer_text(existing_source["segments"], src.get("segments")),
                        _earliest_timestamp(existing_source["created_at"], src.get("created_at")),
                        source_id,
                    ),
                )
                sources_merged += 1
            else:
                cursor = conn.execute(
                    """
                    INSERT INTO sources (url, title, source_type, raw_content, segments, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        src["url"],
                        src["title"],
                        src["source_type"],
                        src["raw_content"],
                        src.get("segments"),
                        src.get("created_at", now),
                    ),
                )
                source_id = cursor.lastrowid
                sources_added += 1

            for concept in concepts_by_source.get(src["id"], []):
                existing_concept = conn.execute(
                    """
                    SELECT *
                    FROM concepts
                    WHERE source_id = ? AND LOWER(name) = LOWER(?)
                    ORDER BY id
                    LIMIT 1
                    """,
                    (source_id, concept["name"]),
                ).fetchone()

                if existing_concept:
                    concept_id = existing_concept["id"]
                    conn.execute(
                        """
                        UPDATE concepts
                        SET source_quote = ?, ground_truth = ?, question = ?,
                            skipped = ?, created_at = ?
                        WHERE id = ?
                        """,
                        (
                            _prefer_text(existing_concept["source_quote"], concept["source_quote"])
                            or existing_concept["source_quote"],
                            _prefer_text(
                                existing_concept["ground_truth"],
                                concept.get("ground_truth"),
                            ),
                            _prefer_text(existing_concept["question"], concept.get("question")),
                            max(
                                int(existing_concept["skipped"]),
                                int(concept.get("skipped", 0) or 0),
                            ),
                            _earliest_timestamp(
                                existing_concept["created_at"],
                                concept.get("created_at"),
                            ),
                            concept_id,
                        ),
                    )
                    concepts_merged += 1
                else:
                    cursor = conn.execute(
                        """
                        INSERT INTO concepts
                        (source_id, name, source_quote, ground_truth, question, skipped, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            source_id,
                            concept["name"],
                            concept["source_quote"],
                            concept.get("ground_truth"),
                            concept.get("question"),
                            concept.get("skipped", 0),
                            concept.get("created_at", now),
                        ),
                    )
                    concept_id = cursor.lastrowid
                    concepts_added += 1

                imported_explanations = explanations_by_concept.get(concept["id"], [])
                imported_activity_at = max(
                    (
                        explanation.get("created_at", now)
                        for explanation in imported_explanations
                    ),
                    default=progress_by_concept.get(concept["id"], {}).get("due_date", now),
                    key=_parse_timestamp,
                )
                imported_state_won = _merge_progress_row(
                    conn,
                    concept_id,
                    progress_by_concept.get(concept["id"]),
                    imported_activity_at,
                    now,
                )
                explanations_added += _merge_explanations(conn, concept_id, imported_explanations)

                if _merge_duel_memory(
                    conn,
                    concept_id,
                    mem_by_concept.get(concept["id"]),
                    prefer_import=imported_state_won,
                ):
                    duel_memories_updated += 1

                if _merge_cached_claims(
                    conn,
                    concept_id,
                    claims_by_concept.get(concept["id"], []),
                    prefer_import=imported_state_won,
                ):
                    cached_claim_sets_updated += 1

    return {
        "schema_version": payload["schema_version"],
        "sources_added": sources_added,
        "sources_merged": sources_merged,
        "concepts_added": concepts_added,
        "concepts_merged": concepts_merged,
        "explanations_added": explanations_added,
        "duel_memories_updated": duel_memories_updated,
        "cached_claim_sets_updated": cached_claim_sets_updated,
    }
