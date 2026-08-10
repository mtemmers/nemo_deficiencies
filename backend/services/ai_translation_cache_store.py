import hashlib
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Optional


class AITranslationCacheStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def _init_db(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS ai_translation_cache (
                    cache_key TEXT PRIMARY KEY,
                    ai_signature TEXT NOT NULL,
                    source_language TEXT NOT NULL,
                    target_language TEXT NOT NULL,
                    source_text TEXT NOT NULL,
                    translated_text TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE INDEX IF NOT EXISTS idx_ai_translation_lookup "
                "ON ai_translation_cache(ai_signature, source_language, target_language)"
            )

    def get(
        self,
        ai_signature: str,
        source_language: str,
        target_language: str,
        source_text: str,
    ) -> Optional[str]:
        cache_key = self._cache_key(ai_signature, source_language, target_language, source_text)
        with self._connect() as connection:
            row = connection.execute(
                "SELECT translated_text FROM ai_translation_cache WHERE cache_key = ?",
                (cache_key,),
            ).fetchone()
        return str(row["translated_text"]) if row else None

    def put(
        self,
        ai_signature: str,
        source_language: str,
        target_language: str,
        source_text: str,
        translated_text: str,
    ) -> None:
        source_language = _language(source_language)
        target_language = _language(target_language)
        source_text = str(source_text).strip()
        translated_text = str(translated_text).strip()
        if not source_text or not translated_text:
            return
        cache_key = self._cache_key(ai_signature, source_language, target_language, source_text)
        now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO ai_translation_cache (
                    cache_key, ai_signature, source_language, target_language,
                    source_text, translated_text, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(cache_key) DO UPDATE SET
                    translated_text = excluded.translated_text,
                    updated_at = excluded.updated_at
                """,
                (
                    cache_key,
                    ai_signature,
                    source_language,
                    target_language,
                    source_text,
                    translated_text,
                    now,
                    now,
                ),
            )

    @staticmethod
    def _cache_key(ai_signature: str, source_language: str, target_language: str, source_text: str) -> str:
        raw = "\0".join(
            (
                str(ai_signature).strip(),
                _language(source_language),
                _language(target_language),
                str(source_text).strip(),
            )
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _language(value: str) -> str:
    return "en" if str(value).strip().casefold() == "en" else "de"
