import os
import sqlite3
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterator, List, Optional
from urllib.parse import urlparse

from cryptography.fernet import Fernet, InvalidToken

from backend.services.ai_connector import (
    AIConnectionSettings,
    CLOUD_AI_PROVIDERS,
    DEFAULT_GROQ_BASE_URL,
    DEFAULT_GROQ_MODEL,
    SUPPORTED_AI_PROVIDERS,
)

GLOBAL_AI_SCOPE = "__global__"


@dataclass(frozen=True)
class AIConfigProfile:
    id: str
    name: str
    provider: str
    baseUrl: str
    model: str
    active: bool
    apiKeyConfigured: bool
    createdAt: str
    updatedAt: str

    def to_dict(self) -> Dict[str, object]:
        return asdict(self)


class AIConfigStoreError(RuntimeError):
    pass


class AIConfigNotFoundError(AIConfigStoreError):
    pass


class AIConfigStore:
    def __init__(self, project_root: Path) -> None:
        data_dir = project_root.resolve() / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = data_dir / "nemo_deficiencies.sqlite"
        self.key_path = data_dir / "nemo_config.key"
        self._fernet = Fernet(self._load_key())
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

    def _load_key(self) -> bytes:
        env_key = os.getenv("NEMO_CONFIG_KEY")
        if env_key:
            return env_key.encode("utf-8")
        if self.key_path.exists():
            return self.key_path.read_bytes().strip()
        key = Fernet.generate_key()
        self.key_path.write_bytes(key)
        return key

    def _init_db(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS ai_config_profiles (
                    id TEXT PRIMARY KEY,
                    nemo_config_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    base_url TEXT NOT NULL,
                    model TEXT NOT NULL,
                    encrypted_api_key BLOB NOT NULL,
                    is_active INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_ai_config_name ON ai_config_profiles(nemo_config_id, name)"
            )

    def list_profiles(self) -> List[AIConfigProfile]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM ai_config_profiles ORDER BY is_active DESC, updated_at DESC, name COLLATE NOCASE"
            ).fetchall()
        profiles: List[AIConfigProfile] = []
        seen = set()
        for row in rows:
            key = (str(row["provider"]).casefold(), str(row["name"]).casefold())
            if key in seen:
                continue
            seen.add(key)
            profiles.append(self._profile(row))
        return profiles

    def create_profile(
        self,
        name: str,
        api_key: str,
        provider: str = "groq",
        base_url: str = DEFAULT_GROQ_BASE_URL,
        model: str = DEFAULT_GROQ_MODEL,
        active: bool = True,
    ) -> AIConfigProfile:
        provider = provider.strip().casefold()
        if provider not in SUPPORTED_AI_PROVIDERS:
            raise AIConfigStoreError(f"Nicht unterstützter KI-Anbieter: {provider or '-'}")
        _validate_base_url(base_url)
        if provider in CLOUD_AI_PROVIDERS and not api_key.strip():
            raise AIConfigStoreError("Für diesen Cloud-Anbieter ist ein API-Key erforderlich.")
        now = _utc_now()
        with self._connect() as connection:
            existing = connection.execute(
                """
                SELECT id FROM ai_config_profiles
                WHERE nemo_config_id = ? AND name = ? COLLATE NOCASE
                ORDER BY updated_at DESC
                LIMIT 1
                """,
                (GLOBAL_AI_SCOPE, name.strip()),
            ).fetchone()
            profile_id = existing["id"] if existing else uuid.uuid4().hex[:16]
            if active:
                connection.execute("UPDATE ai_config_profiles SET is_active = 0")
            encrypted_key = self._fernet.encrypt(api_key.strip().encode("utf-8")) if api_key.strip() else b""
            if existing:
                connection.execute(
                    """
                    UPDATE ai_config_profiles SET
                        nemo_config_id = ?, name = ?, provider = ?, base_url = ?, model = ?,
                        encrypted_api_key = ?, is_active = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        GLOBAL_AI_SCOPE,
                        name.strip(),
                        provider,
                        base_url.rstrip("/"),
                        model.strip(),
                        encrypted_key,
                        int(active),
                        now,
                        profile_id,
                    ),
                )
            else:
                connection.execute(
                    """
                    INSERT INTO ai_config_profiles
                        (id, nemo_config_id, name, provider, base_url, model, encrypted_api_key, is_active, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        profile_id,
                        GLOBAL_AI_SCOPE,
                        name.strip(),
                        provider,
                        base_url.rstrip("/"),
                        model.strip(),
                        encrypted_key,
                        int(active),
                        now,
                        now,
                    ),
                )
        return self.get_profile(profile_id)

    def get_profile(self, profile_id: str) -> AIConfigProfile:
        return self._profile(self._row(profile_id))

    def resolve_settings(self, profile_id: Optional[str] = None) -> AIConnectionSettings:
        if profile_id:
            row = self._row(profile_id)
        else:
            with self._connect() as connection:
                row = connection.execute(
                    """
                    SELECT * FROM ai_config_profiles
                    ORDER BY is_active DESC, updated_at DESC
                    LIMIT 1
                    """
                ).fetchone()
            if row is None:
                raise AIConfigNotFoundError("Es ist noch kein globaler KI-Zugang eingerichtet.")
        encrypted_api_key = row["encrypted_api_key"]
        try:
            api_key = self._fernet.decrypt(encrypted_api_key).decode("utf-8") if encrypted_api_key else ""
        except InvalidToken as exc:
            raise AIConfigStoreError("Der KI-API-Key konnte nicht entschlüsselt werden.") from exc
        return AIConnectionSettings(
            provider=row["provider"],
            base_url=row["base_url"],
            model=row["model"],
            api_key=api_key,
        )

    def _row(self, profile_id: str) -> sqlite3.Row:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM ai_config_profiles WHERE id = ?",
                (profile_id,),
            ).fetchone()
        if row is None:
            raise AIConfigNotFoundError("KI-Konfiguration nicht gefunden.")
        return row

    @staticmethod
    def _profile(row: sqlite3.Row) -> AIConfigProfile:
        return AIConfigProfile(
            id=row["id"],
            name=row["name"],
            provider=row["provider"],
            baseUrl=row["base_url"],
            model=row["model"],
            active=bool(row["is_active"]),
            apiKeyConfigured=bool(row["encrypted_api_key"]),
            createdAt=row["created_at"],
            updatedAt=row["updated_at"],
        )


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _validate_base_url(base_url: str) -> None:
    parsed = urlparse(base_url.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise AIConfigStoreError("Die KI-API-Adresse muss eine gültige HTTP- oder HTTPS-URL sein.")
    if parsed.username or parsed.password:
        raise AIConfigStoreError("Zugangsdaten dürfen nicht Bestandteil der KI-API-Adresse sein.")
