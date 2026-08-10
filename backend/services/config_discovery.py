import hashlib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_CONFIG_CANDIDATES = ("config_gmt.ini", "config.ini")
CONFIG_DIRECTORY = "config"


@dataclass(frozen=True)
class ConfigProfile:
    id: str
    name: str
    fileName: str
    source: str = "ini-file"

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


def config_file_id(path: Path) -> str:
    resolved = str(path.resolve()).casefold()
    return hashlib.sha256(resolved.encode("utf-8")).hexdigest()[:16]


def config_profile_from_path(path: Path) -> ConfigProfile:
    return ConfigProfile(
        id=config_file_id(path),
        name=path.stem,
        fileName=path.name,
    )


def find_config_files(search_root: Path = Path(".")) -> List[Path]:
    search_root = search_root.resolve()
    config_root = search_root if search_root.name.casefold() == CONFIG_DIRECTORY else search_root / CONFIG_DIRECTORY
    files: List[Path] = []
    seen = set()

    def add(path: Path) -> None:
        if not path.exists() or not path.is_file():
            return
        resolved = path.resolve()
        key = str(resolved).casefold()
        if key not in seen:
            seen.add(key)
            files.append(resolved)

    for candidate in DEFAULT_CONFIG_CANDIDATES:
        add(config_root / candidate)

    for path in sorted(config_root.glob("*.ini"), key=lambda item: item.name.casefold()):
        add(path)

    return files


def discover_config_profiles(search_root: Path = Path(".")) -> List[ConfigProfile]:
    return [config_profile_from_path(path) for path in find_config_files(search_root)]


def find_default_config(search_root: Path = Path(".")) -> Optional[Path]:
    files = find_config_files(search_root)
    if files:
        return files[0]
    return None


def resolve_config_path(config_arg: Optional[str], search_root: Path = Path(".")) -> Optional[Path]:
    if config_arg:
        requested = Path(config_arg)
        if requested.is_absolute() or requested.parent != Path("."):
            return requested
        return search_root / CONFIG_DIRECTORY / requested
    return find_default_config(search_root)


def resolve_config_profile(config_id: Optional[str], search_root: Path = Path(".")) -> Optional[Path]:
    files = find_config_files(search_root)
    if not files:
        return None
    if not config_id:
        return files[0]

    wanted = config_id.strip().casefold()
    for path in files:
        profile = config_profile_from_path(path)
        if wanted in {profile.id.casefold(), profile.fileName.casefold(), profile.name.casefold()}:
            return path

    return None
