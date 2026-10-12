"""
Tests for rule translation cache and error logging.
"""

import pytest
import tempfile
from pathlib import Path
import json
from unittest.mock import patch, MagicMock

from backend.export_connectors.utils.rule_translation_cache import (
    RuleTranslationCache,
    RuleTranslationError,
)


class TestRuleTranslationCache:
    """Tests for persistent rule translation cache."""

    @pytest.fixture
    def cache_dir(self):
        """Temporary cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_cache_initialization(self, cache_dir):
        """Cache should initialize with empty state."""
        cache = RuleTranslationCache(cache_dir=cache_dir)
        
        assert cache.cache_dir == cache_dir
        assert len(cache._cache["rules"]) == 0
        assert len(cache._errors["failed_translations"]) == 0

    def test_cache_store_and_lookup(self, cache_dir):
        """Storing and looking up translations."""
        cache = RuleTranslationCache(cache_dir=cache_dir)
        
        condition = "CUSTOMER_ID IS NOT NULL"
        field = "CUSTOMER_ID"
        expression = "CUSTOMER_ID IS NOT NULL"
        
        # Store
        cache.store(
            condition=condition,
            field=field,
            expression_infozoom=expression,
            rule_id="rule_1",
            message="ID is required",
        )
        
        # Lookup
        result = cache.lookup(condition, field)
        assert result == expression

    def test_cache_miss(self, cache_dir):
        """Lookup should return None for uncached rule."""
        cache = RuleTranslationCache(cache_dir=cache_dir)
        result = cache.lookup("UNKNOWN_CONDITION", "UNKNOWN_FIELD")
        assert result is None

    def test_cache_persistence(self, cache_dir):
        """Cache should persist to disk."""
        cache1 = RuleTranslationCache(cache_dir=cache_dir)
        cache1.store(
            condition="X > 0",
            field="COL",
            expression_infozoom="COL > 0",
            rule_id="rule_1",
            message="X is positive",
        )
        
        # Create new cache instance pointing to same directory
        cache2 = RuleTranslationCache(cache_dir=cache_dir)
        result = cache2.lookup("X > 0", "COL")
        assert result == "COL > 0"

    def test_error_logging(self, cache_dir):
        """Errors should be logged and persisted."""
        cache = RuleTranslationCache(cache_dir=cache_dir)
        
        cache.log_error(
            rule_id="rule_broken",
            error="Unsupported function REGEXPR",
            condition="REGEXPR(field, '^[A-Z]+')",
            field="NAME",
            message="Name must start with uppercase",
        )
        
        errors = cache.get_failed_translations()
        assert len(errors) == 1
        assert errors[0]["rule_id"] == "rule_broken"
        assert "Unsupported function" in errors[0]["error"]

    def test_error_persistence(self, cache_dir):
        """Errors should persist to disk."""
        cache1 = RuleTranslationCache(cache_dir=cache_dir)
        cache1.log_error(
            rule_id="rule_1",
            error="Test error",
            condition="TEST",
            field="TEST_FIELD",
            message="Test message",
        )
        
        # New instance should see the error
        cache2 = RuleTranslationCache(cache_dir=cache_dir)
        assert cache2.get_failed_count() == 1

    def test_cache_stats(self, cache_dir):
        """Cache stats should be accurate."""
        cache = RuleTranslationCache(cache_dir=cache_dir)
        
        cache.store("A", "F1", "A", "r1", "m1")
        cache.store("B", "F2", "B", "r2", "m2")
        cache.log_error("r3", "error", "C", "F3", "m3")
        
        stats = cache.get_cache_stats()
        assert stats["cached_rules"] == 2
        assert stats["failed_translations"] == 1

    def test_clear_errors(self, cache_dir):
        """clear_errors should remove all logged errors."""
        cache = RuleTranslationCache(cache_dir=cache_dir)
        
        cache.log_error("r1", "err1", "C1", "F1", "m1")
        cache.log_error("r2", "err2", "C2", "F2", "m2")
        assert cache.get_failed_count() == 2
        
        cache.clear_errors()
        assert cache.get_failed_count() == 0

    def test_dump_cache(self, cache_dir):
        """dump_cache should return valid JSON."""
        cache = RuleTranslationCache(cache_dir=cache_dir)
        cache.store("X > 0", "X", "X > 0", "r1", "X positive")
        
        json_str = cache.dump_cache()
        parsed = json.loads(json_str)
        
        assert "rules" in parsed
        assert len(parsed["rules"]) == 1

    def test_dump_errors(self, cache_dir):
        """dump_errors should return valid JSON."""
        cache = RuleTranslationCache(cache_dir=cache_dir)
        cache.log_error("r1", "error", "C1", "F1", "m1")
        
        json_str = cache.dump_errors()
        parsed = json.loads(json_str)
        
        assert "failed_translations" in parsed
        assert len(parsed["failed_translations"]) == 1


class TestFieldCascaderWithCache:
    """Tests for FieldCascader with caching and error handling."""

    @pytest.fixture
    def cascader_with_cache(self):
        """FieldCascader instance with isolated cache."""
        from backend.export_connectors.utils.field_cascader import FieldCascader
        with tempfile.TemporaryDirectory() as tmpdir:
            # Patch the module-level cache to use temp dir
            with patch("backend.export_connectors.utils.field_cascader._cache") as mock_cache:
                mock_cache.lookup = MagicMock(return_value=None)
                mock_cache.store = MagicMock()
                mock_cache.log_error = MagicMock()
                
                cascader = FieldCascader()
                yield cascader

    def test_cascader_caches_infozoom_translations(self, cascader_with_cache):
        """FieldCascader should store translations in cache."""
        from backend.export_connectors.utils.field_cascader import _cache as module_cache
        
        rules = [
            {
                "id": "rule_1",
                "condition": "CUSTOMER_ID IS NOT NULL",
                "message": "ID is required",
                "dimension": "Vollstaendigkeit",
                "active": True,
            }
        ]
        
        text, warnings = cascader_with_cache.build_cascade_infozoom("CUSTOMER_ID", rules)
        
        # Should have called store
        assert module_cache.store.called
        assert "IS NOT NULL" in text or "ID is required" in text

    def test_cascader_uses_cached_translations(self, cascader_with_cache):
        """FieldCascader should use cached translations."""
        from backend.export_connectors.utils.field_cascader import _cache as module_cache
        
        # Mock cache to return a cached description
        module_cache.lookup.return_value = "CACHED_DESCRIPTION"
        
        rules = [
            {
                "id": "rule_1",
                "condition": "FIELD = 'value'",
                "message": "Must be value",
                "active": True,
            }
        ]
        
        text, warnings = cascader_with_cache.build_cascade_infozoom("FIELD", rules)
        
        # Should use the cached value
        assert "CACHED_DESCRIPTION" in text
        assert module_cache.lookup.called

    def test_cascader_logs_translation_errors(self, cascader_with_cache):
        """FieldCascader should log translation errors."""
        from backend.export_connectors.utils.field_cascader import _cache as module_cache
        
        # Mock translator to raise an error
        with patch("backend.export_connectors.utils.field_cascader._translator") as mock_translator:
            mock_translator.to_description_en.side_effect = ValueError("Unsupported syntax")
            
            rules = [
                {
                    "id": "broken_rule",
                    "condition": "INVALID_SYNTAX",
                    "message": "Test",
                    "active": True,
                }
            ]
            
            text, warnings = cascader_with_cache.build_cascade_infozoom("FIELD", rules)
            
            # Should have logged the error
            assert module_cache.log_error.called
            call_args = module_cache.log_error.call_args
            assert "broken_rule" in str(call_args)
            
            # Should still include the rule with fallback
            assert "INVALID_SYNTAX" in text
            assert len(warnings) > 0

    def test_cascader_mssql_caches_translations(self, cascader_with_cache):
        """FieldCascader should cache MSSQL translations too."""
        from backend.export_connectors.utils.field_cascader import _cache as module_cache
        
        rules = [
            {
                "id": "rule_1",
                "condition": "LEN(FIELD) > 0",
                "message": "Field must not be empty",
                "active": True,
            }
        ]
        
        sql, warnings = cascader_with_cache.build_cascade_mssql("FIELD", rules)
        
        # Should have called store
        assert module_cache.store.called
        assert "CASE" in sql
        assert "WHEN" in sql
