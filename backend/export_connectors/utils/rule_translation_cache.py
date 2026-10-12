"""
Persistent rule translation cache and error logging for InfoZoom exports.

Stores translated rules in JSON to avoid re-translation on every export.
Logs translation errors for debugging and manual correction.
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from hashlib import md5

log = logging.getLogger(__name__)


class RuleTranslationError:
    """Record of a single translation error."""

    def __init__(self, rule_id: str, error: str, rule_data: Dict[str, Any]):
        self.rule_id = rule_id
        self.error = error
        self.rule_data = rule_data
        self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "error": self.error,
            "timestamp": self.timestamp,
            "rule_data": self.rule_data,
        }


class RuleTranslationCache:
    """
    Persistent cache for translated NEMO rules → InfoZoom expressions.

    Storage:
        - Cache: {project_dir}/.cache/infozoom_rules.json
        - Errors: {project_dir}/.cache/infozoom_errors.json

    Structure:
        cache.json:
        {
            "rules": {
                "<rule_hash>": {
                    "rule_id": "check_group_1_rule_0",
                    "field": "CUSTOMER_ID",
                    "condition_nemo": "CUSTOMER_ID IS NOT NULL",
                    "expression_infozoom": "CUSTOMER_ID IS NOT NULL",
                    "message": "Customer ID is required",
                    "translated_at": "2026-10-06T15:00:00",
                    "translator_version": "1.0"
                },
                ...
            },
            "metadata": {
                "last_updated": "2026-10-06T15:00:00",
                "total_cached": 42
            }
        }

        errors.json:
        {
            "failed_translations": [
                {
                    "rule_id": "check_group_5_rule_2",
                    "error": "REGEXPR function not supported",
                    "timestamp": "2026-10-06T15:00:00",
                    "rule_data": { ... }
                },
                ...
            ]
        }
    """

    TRANSLATOR_VERSION = "1.0"

    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize cache.

        Args:
            cache_dir: Directory to store cache files. Defaults to {project}/.cache
        """
        if cache_dir is None:
            # Use .cache in the project root
            cache_dir = Path(__file__).parent.parent.parent / ".cache"

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.cache_path = self.cache_dir / "infozoom_rules.json"
        self.errors_path = self.cache_dir / "infozoom_errors.json"

        self._cache = self._load_cache()
        self._errors = self._load_errors()

    def _load_cache(self) -> Dict[str, Any]:
        """Load cache from disk."""
        if not self.cache_path.exists():
            return {"rules": {}, "metadata": {}}

        try:
            with open(self.cache_path) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            log.warning(f"Failed to load cache from {self.cache_path}: {e}")
            return {"rules": {}, "metadata": {}}

    def _load_errors(self) -> Dict[str, Any]:
        """Load error log from disk."""
        if not self.errors_path.exists():
            return {"failed_translations": []}

        try:
            with open(self.errors_path) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            log.warning(f"Failed to load errors from {self.errors_path}: {e}")
            return {"failed_translations": []}

    def _save_cache(self) -> None:
        """Save cache to disk."""
        self._cache["metadata"]["last_updated"] = datetime.now(timezone.utc).isoformat()
        self._cache["metadata"]["total_cached"] = len(self._cache["rules"])

        try:
            with open(self.cache_path, "w") as f:
                json.dump(self._cache, f, indent=2)
        except IOError as e:
            log.error(f"Failed to save cache to {self.cache_path}: {e}")

    def _save_errors(self) -> None:
        """Save error log to disk."""
        try:
            with open(self.errors_path, "w") as f:
                json.dump(self._errors, f, indent=2)
        except IOError as e:
            log.error(f"Failed to save errors to {self.errors_path}: {e}")

    def _make_rule_hash(self, condition: str, field: str) -> str:
        """Create hash of rule for cache key."""
        key = f"{field}::{condition}"
        return md5(key.encode()).hexdigest()[:16]

    def lookup(self, condition: str, field: str) -> Optional[str]:
        """
        Look up a cached translation.

        Args:
            condition: NEMO SQL condition
            field: Field name

        Returns:
            InfoZoom expression, or None if not cached
        """
        rule_hash = self._make_rule_hash(condition, field)
        entry = self._cache["rules"].get(rule_hash)

        if entry:
            log.debug(f"Cache HIT for {field}: {rule_hash}")
            return entry.get("expression_infozoom")

        log.debug(f"Cache MISS for {field}: {rule_hash}")
        return None

    def store(
        self,
        condition: str,
        field: str,
        expression_infozoom: str,
        rule_id: str,
        message: str,
    ) -> None:
        """
        Store a translation in cache.

        Args:
            condition: NEMO SQL condition
            field: Field name
            expression_infozoom: Translated InfoZoom expression
            rule_id: Unique rule identifier
            message: Rule message/description
        """
        rule_hash = self._make_rule_hash(condition, field)

        self._cache["rules"][rule_hash] = {
            "rule_id": rule_id,
            "field": field,
            "condition_nemo": condition,
            "expression_infozoom": expression_infozoom,
            "message": message,
            "translated_at": datetime.now(timezone.utc).isoformat(),
            "translator_version": self.TRANSLATOR_VERSION,
        }

        self._save_cache()
        log.info(f"Cached translation for {field}: {rule_id}")

    def log_error(
        self, rule_id: str, error: str, condition: str, field: str, message: str
    ) -> None:
        """
        Log a translation error.

        Args:
            rule_id: Unique rule identifier
            error: Error message/reason
            condition: NEMO SQL condition that failed
            field: Field name
            message: Rule message/description
        """
        error_record = RuleTranslationError(
            rule_id=rule_id,
            error=error,
            rule_data={
                "field": field,
                "condition": condition,
                "message": message,
            },
        )

        self._errors["failed_translations"].append(error_record.to_dict())
        self._save_errors()

        log.error(
            f"Translation error for {rule_id} ({field}): {error}\n"
            f"  Condition: {condition}\n"
            f"  Message: {message}"
        )

    def get_failed_translations(self) -> List[Dict[str, Any]]:
        """Get all logged translation errors."""
        return self._errors.get("failed_translations", [])

    def get_failed_count(self) -> int:
        """Get count of failed translations."""
        return len(self._errors.get("failed_translations", []))

    def clear_errors(self) -> None:
        """Clear all error logs."""
        self._errors = {"failed_translations": []}
        self._save_errors()
        log.info("Cleared error log")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "cached_rules": len(self._cache["rules"]),
            "failed_translations": len(self._errors["failed_translations"]),
            "cache_file": str(self.cache_path),
            "errors_file": str(self.errors_path),
            "last_updated": self._cache["metadata"].get("last_updated"),
        }

    def dump_cache(self) -> str:
        """Return cache as formatted JSON string."""
        return json.dumps(self._cache, indent=2)

    def dump_errors(self) -> str:
        """Return error log as formatted JSON string."""
        return json.dumps(self._errors, indent=2)
