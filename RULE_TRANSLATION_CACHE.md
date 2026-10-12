# Rule Translation Cache & Error Logging

## Overview

The export system now includes persistent caching of rule translations and comprehensive error logging. This ensures:

1. **Performance**: Rules are translated once and cached
2. **Debugging**: Translation errors are logged for manual correction
3. **Reliability**: Failed translations don't crash exports; they use fallback logic

## Architecture

### Cache System (`rule_translation_cache.py`)

```
.cache/
  ├── infozoom_rules.json      # Cached translations
  └── infozoom_errors.json     # Failed translations log
```

#### `RuleTranslationCache`

Persistent storage for translated NEMO SQL rules → InfoZoom expressions.

**Location**: `.cache/infozoom_rules.json`

**Structure**:
```json
{
  "rules": {
    "a1b2c3d4e5f6g7h8": {
      "rule_id": "check_group_1_rule_0",
      "field": "CUSTOMER_ID",
      "condition_nemo": "CUSTOMER_ID IS NOT NULL",
      "expression_infozoom": "CUSTOMER_ID IS NOT NULL",
      "message": "Customer ID is required",
      "translated_at": "2026-10-06T15:00:00+00:00",
      "translator_version": "1.0"
    }
  },
  "metadata": {
    "last_updated": "2026-10-06T15:00:00+00:00",
    "total_cached": 42
  }
}
```

**Cache Key**: MD5 hash of `{field}::{condition}` (first 16 chars)

### Error Logging System

**Location**: `.cache/infozoom_errors.json`

**Structure**:
```json
{
  "failed_translations": [
    {
      "rule_id": "check_group_5_rule_2",
      "error": "Translation failed: ValueError: Unsupported function REGEXPR",
      "timestamp": "2026-10-06T15:00:00+00:00",
      "rule_data": {
        "field": "NAME",
        "condition": "REGEXPR(NAME, '^[A-Z]+')",
        "message": "Name must start with uppercase"
      }
    }
  ]
}
```

## Integration

### In `FieldCascader`

Both `build_cascade_infozoom()` and `build_cascade_mssql()` now:

1. **Check cache first**: If rule is cached, use cached translation
2. **Translate on miss**: Call translator, store result in cache
3. **Handle errors**: If translation fails:
   - Log error with full context to `infozoom_errors.json`
   - Use fallback (original condition or description)
   - Include warning in export output

**Example**:
```python
from backend.export_connectors.utils.field_cascader import FieldCascader, _cache

cascader = FieldCascader()

# First call: translate + cache
output1, warnings1 = cascader.build_cascade_infozoom("CUSTOMER_ID", rules)
# -> Calls translator, stores in cache

# Second call: uses cache
output2, warnings2 = cascader.build_cascade_infozoom("CUSTOMER_ID", rules)
# -> Reads from .cache/infozoom_rules.json (faster)

# View cache stats
print(_cache.get_cache_stats())
# {
#   "cached_rules": 42,
#   "failed_translations": 3,
#   "cache_file": ".../.cache/infozoom_rules.json",
#   "errors_file": ".../.cache/infozoom_errors.json",
#   "last_updated": "2026-10-06T15:00:00+00:00"
# }
```

## Usage & Debugging

### Check Cache Status

```python
from backend.export_connectors.utils.rule_translation_cache import RuleTranslationCache

cache = RuleTranslationCache()

# Get statistics
stats = cache.get_cache_stats()
print(f"Cached rules: {stats['cached_rules']}")
print(f"Failed translations: {stats['failed_translations']}")

# View all errors
errors = cache.get_failed_translations()
for err in errors:
    print(f"{err['rule_id']}: {err['error']}")
    print(f"  Condition: {err['rule_data']['condition']}")
    print(f"  Field: {err['rule_data']['field']}")

# View formatted cache
print(cache.dump_cache())
print(cache.dump_errors())

# Clear errors after fixing them
cache.clear_errors()
```

### Handling Failed Translations

When you see a translation error in the log:

1. **Read the error**: `.cache/infozoom_errors.json`
2. **Understand the issue**: Check the `error` and `rule_data` fields
3. **Fix the rule or translator**: Either update the condition in NEMO or extend `condition_translator.py` to handle the pattern
4. **Clear cache**: `cache.clear_errors()` to remove old errors
5. **Re-export**: The system will re-translate and cache correctly

**Common Issues**:

- **Unsupported function** → Extend `ConditionTranslator.to_description_en()` or `to_mssql()`
- **Malformed condition** → Fix the condition in the NEMO model
- **Encoding issue** → Check if the condition contains non-ASCII characters

### Inspection Tools

```python
from backend.export_connectors.utils.rule_translation_cache import RuleTranslationCache

cache = RuleTranslationCache()

# Count by status
print(f"Total cached: {cache.get_cache_stats()['cached_rules']}")
print(f"Failed: {cache.get_failed_count()}")

# Look up specific rule
result = cache.lookup("CUSTOMER_ID IS NOT NULL", "CUSTOMER_ID")
if result:
    print(f"Cached result: {result}")
else:
    print("Not cached")

# List recent errors
for error in cache.get_failed_translations()[-5:]:  # Last 5
    print(f"{error['timestamp']}: {error['rule_id']}")
```

## Performance Impact

**First Export**: ~100-200ms (translates all rules, caches)
**Subsequent Exports**: ~50-100ms (reads cache)

For a model with 50+ rules, the cache typically saves 50-100ms per export.

## Testing

```bash
# Test cache operations
pytest tests/test_rule_translation_cache.py::TestRuleTranslationCache -v

# Test cascader with cache
pytest tests/test_rule_translation_cache.py::TestFieldCascaderWithCache -v

# All tests
pytest tests/test_rule_translation_cache.py -v
```

## File Locations

- **Cache files**: `{project}/.cache/infozoom_rules.json`, `infozoom_errors.json`
- **Source code**: `backend/export_connectors/utils/rule_translation_cache.py`
- **Integration**: `backend/export_connectors/utils/field_cascader.py`
- **Tests**: `tests/test_rule_translation_cache.py`

## API Reference

### `RuleTranslationCache`

```python
cache = RuleTranslationCache(cache_dir=Path(".cache"))

# Store a translation
cache.store(
    condition="CUSTOMER_ID IS NOT NULL",
    field="CUSTOMER_ID",
    expression_infozoom="CUSTOMER_ID IS NOT NULL",
    rule_id="rule_123",
    message="ID is required"
)

# Lookup cached translation
result = cache.lookup("CUSTOMER_ID IS NOT NULL", "CUSTOMER_ID")  # -> "CUSTOMER_ID IS NOT NULL"

# Log an error
cache.log_error(
    rule_id="rule_456",
    error="Unsupported function REGEXPR",
    condition="REGEXPR(...)",
    field="NAME",
    message="Name format invalid"
)

# Get statistics
stats = cache.get_cache_stats()

# Get all errors
errors = cache.get_failed_translations()

# Clear errors
cache.clear_errors()

# JSON dumps
json_cache = cache.dump_cache()
json_errors = cache.dump_errors()
```

---

**Last Updated**: October 6, 2026
