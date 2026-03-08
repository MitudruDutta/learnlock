"""Local SQLite storage for learn-lock."""

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from . import config

_initialized_dbs: set[str] = set()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


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
        row = conn.execute("SELECT * FROM sources WHERE id = ?", (source_id,)).fetchone()
        return dict(row) if row else None


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

        return {
            "total_sources": total_sources,
            "total_concepts": total_concepts,
            "skipped_concepts": skipped_concepts,
            "total_reviews": total_explanations,
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
        conn.execute("DELETE FROM cached_claims WHERE concept_id = ?", (concept_id,))
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
