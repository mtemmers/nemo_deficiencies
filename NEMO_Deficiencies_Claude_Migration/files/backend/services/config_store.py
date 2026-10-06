import configparser
import os
import re
import sqlite3
import tempfile
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Dict, Iterator, List, Optional

from cryptography.fernet import Fernet, InvalidToken

from backend.services.config_discovery import DEFAULT_CONFIG_CANDIDATES, config_file_id, find_config_files

DEFAULT_NEMO_URL = "https://enter.nemo-ai.com"
DEFAULT_NEMO_ENVIRONMENT = "prod"


@dataclass(frozen=True)
class ConfigProfile:
    id: str
    name: str
    source: str
    sourceFile: str
    tenant: str
    createdAt: str
    updatedAt: str

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


class ConfigStoreError(RuntimeError):
    pass


class ConfigNotFoundError(ConfigStoreError):
    pass


class ConfigDecryptError(ConfigStoreError):
    pass


class ConfigStore:
    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root.resolve()
        self.data_dir = self.project_root / "data"
        self.db_path = self.data_dir / "nemo_deficiencies.sqlite"
        self.key_path = self.data_dir / "nemo_config.key"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._fernet = Fernet(self._load_or_create_key())
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

    def _load_or_create_key(self) -> bytes:
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
                CREATE TABLE IF NOT EXISTS config_profiles (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    source TEXT NOT NULL,
                    source_file TEXT NOT NULL DEFAULT '',
                    encrypted_ini BLOB NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.execute(
                "CREATE UNIQUE INDEX IF NOT EXISTS idx_config_profiles_name ON config_profiles(name)"
            )

    def _encrypt(self, content: str) -> bytes:
        return self._fernet.encrypt(content.encode("utf-8"))

    def _decrypt(self, encrypted_content: bytes) -> str:
        try:
            return self._fernet.decrypt(encrypted_content).decode("utf-8")
        except InvalidToken as exc:
            raise ConfigDecryptError("Config konnte nicht entschluesselt werden.") from exc

    def list_profiles(self) -> List[ConfigProfile]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, name, source, source_file, encrypted_ini, created_at, updated_at
                FROM config_profiles
                ORDER BY name COLLATE NOCASE
                """
            ).fetchall()
        return [self._profile_from_row(row) for row in rows]

    def get_profile(self, config_id: str) -> ConfigProfile:
        row = self._get_row(config_id)
        return self._profile_from_row(row)

    def resolve_profile(self, config_ref: Optional[str]) -> ConfigProfile:
        profiles = self.list_profiles()
        if not profiles:
            raise ConfigNotFoundError("Keine Config-Profile vorhanden.")
        if not config_ref:
            return self.default_profile(profiles)

        wanted = config_ref.strip().casefold()
        for profile in profiles:
            identifiers = {profile.id.casefold(), profile.name.casefold(), profile.sourceFile.casefold()}
            if wanted in identifiers:
                return profile
        raise ConfigNotFoundError(f"Config nicht gefunden: {config_ref}")

    def default_profile(self, profiles: Optional[List[ConfigProfile]] = None) -> ConfigProfile:
        candidates = profiles if profiles is not None else self.list_profiles()
        if not candidates:
            raise ConfigNotFoundError("Keine Config-Profile vorhanden.")
        by_file = {profile.sourceFile.casefold(): profile for profile in candidates if profile.sourceFile}
        for candidate in DEFAULT_CONFIG_CANDIDATES:
            profile = by_file.get(candidate.casefold())
            if profile:
                return profile
        return candidates[0]

    def upsert_config(
        self,
        config_id: str,
        name: str,
        ini_content: str,
        source: str,
        source_file: str = "",
    ) -> ConfigProfile:
        now = _utc_now()
        encrypted = self._encrypt(ini_content)
        with self._connect() as connection:
            existing = connection.execute(
                "SELECT created_at FROM config_profiles WHERE id = ?",
                (config_id,),
            ).fetchone()
            created_at = existing["created_at"] if existing else now
            connection.execute(
                """
                INSERT INTO config_profiles (id, name, source, source_file, encrypted_ini, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    source = excluded.source,
                    source_file = excluded.source_file,
                    encrypted_ini = excluded.encrypted_ini,
                    updated_at = excluded.updated_at
                """,
                (config_id, name.strip(), source, source_file, encrypted, created_at, now),
            )
        return self.get_profile(config_id)

    def create_config(self, name: str, ini_content: str, source_file: str = "") -> ConfigProfile:
        import uuid

        config_id = uuid.uuid4().hex[:16]
        return self.upsert_config(
            config_id=config_id,
            name=name,
            ini_content=ini_content,
            source="manual",
            source_file=source_file,
        )

    def update_config(
        self,
        config_id: str,
        name: Optional[str] = None,
        ini_content: Optional[str] = None,
        source_file: Optional[str] = None,
    ) -> ConfigProfile:
        row = self._get_row(config_id)
        next_name = name.strip() if name else row["name"]
        next_content = ini_content if ini_content is not None else self._decrypt(row["encrypted_ini"])
        next_source_file = source_file if source_file is not None else row["source_file"]
        return self.upsert_config(
            config_id=config_id,
            name=next_name,
            ini_content=next_content,
            source=row["source"],
            source_file=next_source_file,
        )

    def delete_config(self, config_id: str) -> None:
        with self._connect() as connection:
            cursor = connection.execute("DELETE FROM config_profiles WHERE id = ?", (config_id,))
        if cursor.rowcount == 0:
            raise ConfigNotFoundError(f"Config nicht gefunden: {config_id}")

    def decrypt_config(self, config_id: str) -> str:
        row = self._get_row(config_id)
        return self._decrypt(row["encrypted_ini"])

    @contextmanager
    def temporary_config_file(self, config_id: str) -> Iterator[Path]:
        content = self.decrypt_config(config_id)
        temp_path: Optional[Path] = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                suffix=".ini",
                prefix="nemo_config_",
                delete=False,
            ) as handle:
                temp_path = Path(handle.name)
                handle.write(content)
            yield temp_path
        finally:
            if temp_path and temp_path.exists():
                temp_path.unlink(missing_ok=True)

    def import_ini_files(self, overwrite: bool = False) -> List[ConfigProfile]:
        imported: List[ConfigProfile] = []
        for path in find_config_files(self.project_root):
            config_id = self._imported_config_id(path.name) or config_file_id(path)
            if not overwrite and self._exists(config_id):
                imported.append(self.get_profile(config_id))
                continue
            imported.append(
                self.upsert_config(
                    config_id=config_id,
                    name=path.stem,
                    ini_content=path.read_text(encoding="utf-8-sig"),
                    source="imported-ini",
                    source_file=path.name,
                )
            )
        return imported

    def _imported_config_id(self, source_file: str) -> Optional[str]:
        with self._connect() as connection:
            row = connection.execute(
                """
                SELECT id
                FROM config_profiles
                WHERE lower(source_file) = lower(?) AND source = 'imported-ini'
                ORDER BY created_at
                LIMIT 1
                """,
                (source_file,),
            ).fetchone()
        return str(row["id"]) if row else None

    def _exists(self, config_id: str) -> bool:
        with self._connect() as connection:
            row = connection.execute("SELECT 1 FROM config_profiles WHERE id = ?", (config_id,)).fetchone()
        return row is not None

    def _get_row(self, config_id: str) -> sqlite3.Row:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM config_profiles WHERE id = ?",
                (config_id,),
            ).fetchone()
        if not row:
            raise ConfigNotFoundError(f"Config nicht gefunden: {config_id}")
        return row

    def _profile_from_row(self, row: sqlite3.Row) -> ConfigProfile:
        tenant = ""
        if "encrypted_ini" in row.keys():
            try:
                tenant = _extract_tenant(self._decrypt(row["encrypted_ini"]))
            except ConfigDecryptError:
                tenant = ""

        return ConfigProfile(
            id=row["id"],
            name=row["name"],
            source=row["source"],
            sourceFile=row["source_file"],
            tenant=tenant,
            createdAt=row["created_at"],
            updatedAt=row["updated_at"],
        )

def _extract_tenant(ini_content: str) -> str:
    parser = configparser.ConfigParser()
    try:
        parser.read_file(StringIO(ini_content))
    except configparser.Error:
        return _extract_flat_tenant(ini_content)

    for section in parser.sections():
        tenant = parser.get(section, "tenant", fallback="").strip()
        if tenant:
            return tenant

    default_tenant = parser.defaults().get("tenant", "").strip()
    return default_tenant or _extract_flat_tenant(ini_content)


def _extract_flat_tenant(ini_content: str) -> str:
    for raw_line in ini_content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith(("#", ";", "[")):
            continue
        separator = "=" if "=" in line else ":" if ":" in line else ""
        if not separator:
            continue
        key, value = line.split(separator, 1)
        if key.strip().casefold() == "tenant":
            return value.strip().strip("\"'")
    return ""


def build_nemo_config_content(
    tenant: str,
    userid: str,
    password: str,
    nemo_url: str = DEFAULT_NEMO_URL,
    environment: str = DEFAULT_NEMO_ENVIRONMENT,
) -> str:
    tenant_value = tenant.strip()
    userid_value = userid.strip()
    nemo_url_value = nemo_url.strip().rstrip("/")
    environment_value = environment.strip()
    if not tenant_value or not userid_value or not password or not nemo_url_value or not environment_value:
        raise ValueError("Tenant, User-ID, Passwort, NEMO-URL und Environment sind erforderlich.")

    parser = configparser.ConfigParser(interpolation=None)
    parser["nemo_library"] = {
        "nemo_url": nemo_url_value,
        "tenant": tenant_value,
        "userid": userid_value,
        "password": password.replace("%", "%%"),
        "environment": environment_value,
        "hubspot_api_token": "",
    }
    output = StringIO()
    parser.write(output)
    return output.getvalue()


def read_nemo_config_settings(ini_content: str) -> Dict[str, object]:
    parser, section = _parse_nemo_config(ini_content)
    values = parser[section]
    return {
        "tenant": values.get("tenant", "").strip(),
        "userid": values.get("userid", "").strip(),
        "nemoUrl": values.get("nemo_url", DEFAULT_NEMO_URL).strip().rstrip("/"),
        "environment": values.get("environment", DEFAULT_NEMO_ENVIRONMENT).strip(),
        "hasPassword": bool(values.get("password", "")),
    }


def update_nemo_config_content(
    ini_content: str,
    *,
    tenant: str,
    userid: str,
    password: str,
    nemo_url: str,
    environment: str,
) -> str:
    parser, section = _parse_nemo_config(ini_content)
    values = parser[section]
    tenant_value = tenant.strip()
    userid_value = userid.strip()
    nemo_url_value = nemo_url.strip().rstrip("/")
    environment_value = environment.strip()
    if not tenant_value or not userid_value or not nemo_url_value or not environment_value:
        raise ValueError("Tenant, User-ID, NEMO-URL und Environment sind erforderlich.")
    if not password and not values.get("password", ""):
        raise ValueError("Für diese Konfiguration ist ein Passwort erforderlich.")

    values["tenant"] = tenant_value
    values["userid"] = userid_value
    values["nemo_url"] = nemo_url_value
    values["environment"] = environment_value
    if password:
        values["password"] = password.replace("%", "%%")

    output = StringIO()
    parser.write(output)
    return output.getvalue()


def _parse_nemo_config(ini_content: str) -> tuple[configparser.ConfigParser, str]:
    parser = configparser.ConfigParser(interpolation=None)
    try:
        parser.read_string(ini_content)
    except configparser.Error as exc:
        raise ValueError("Die gespeicherte NEMO-Konfiguration ist keine gültige INI-Datei.") from exc
    if parser.has_section("nemo_library"):
        return parser, "nemo_library"
    sections = parser.sections()
    if not sections:
        parser.add_section("nemo_library")
        return parser, "nemo_library"
    return parser, sections[0]


def config_profile_name(tenant: str) -> str:
    normalized = re.sub(r"[^A-Za-z0-9._-]+", "_", tenant.strip()).strip("._-").casefold()
    if not normalized:
        raise ValueError("Der Tenant ergibt keinen gültigen Profilnamen.")
    return f"config_{normalized}"[:120]

def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def get_config_store(project_root: Path) -> ConfigStore:
    store = ConfigStore(project_root)
    store.import_ini_files(overwrite=False)
    return store
