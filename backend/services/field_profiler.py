import math
import re
from collections import Counter
from typing import Any, Dict, Iterable


def build_anonymized_field_profile(values: Iterable[Any]) -> Dict[str, Any]:
    rows = list(values)
    null_count = sum(_is_null(value) for value in rows)
    texts = [str(value) for value in rows if not _is_null(value)]
    empty_count = sum(not value.strip() for value in texts)
    nonempty = [value for value in texts if value.strip()]
    lengths = [len(value) for value in nonempty]
    value_counts = Counter(nonempty)
    shape_counts = Counter(_value_shape(value) for value in nonempty)

    return {
        "sampleSize": len(rows),
        "nullCount": null_count,
        "emptyCount": empty_count,
        "nonEmptyCount": len(nonempty),
        "distinctCount": len(value_counts),
        "duplicateCount": max(0, len(nonempty) - len(value_counts)),
        "minLength": min(lengths) if lengths else 0,
        "maxLength": max(lengths) if lengths else 0,
        "averageLength": round(sum(lengths) / len(lengths), 2) if lengths else 0,
        "lengthDistribution": _length_distribution(lengths),
        "patternCounts": _pattern_counts(nonempty),
        "shapeDistribution": [
            {"shape": shape, "count": count}
            for shape, count in shape_counts.most_common(15)
        ],
        "frequencyDistribution": sorted(value_counts.values(), reverse=True)[:15],
        "privacy": "anonymized-profile-without-raw-values",
    }


def _is_null(value: Any) -> bool:
    if value is None:
        return True
    try:
        return bool(math.isnan(value))
    except (TypeError, ValueError):
        return False


def _length_distribution(lengths: list[int]) -> Dict[str, int]:
    buckets = {"0": 0, "1-2": 0, "3-5": 0, "6-10": 0, "11-20": 0, "21-50": 0, "51+": 0}
    for length in lengths:
        if length == 0:
            buckets["0"] += 1
        elif length <= 2:
            buckets["1-2"] += 1
        elif length <= 5:
            buckets["3-5"] += 1
        elif length <= 10:
            buckets["6-10"] += 1
        elif length <= 20:
            buckets["11-20"] += 1
        elif length <= 50:
            buckets["21-50"] += 1
        else:
            buckets["51+"] += 1
    return buckets


def _pattern_counts(values: list[str]) -> Dict[str, int]:
    checks = {
        "digitsOnly": lambda value: value.isdigit(),
        "lettersOnly": lambda value: value.isalpha(),
        "alphaNumericOnly": lambda value: value.isalnum(),
        "leadingOrTrailingWhitespace": lambda value: value != value.strip(),
        "containsWhitespace": lambda value: bool(re.search(r"\s", value)),
        "containsLowercase": lambda value: any(character.islower() for character in value),
        "containsUppercase": lambda value: any(character.isupper() for character in value),
        "containsNonAscii": lambda value: not value.isascii(),
        "containsSpecialCharacters": lambda value: bool(re.search(r"[^\w\s]", value, re.UNICODE)),
        "emailShape": lambda value: bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value)),
        "dateIsoShape": lambda value: bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", value)),
        "decimalShape": lambda value: bool(re.fullmatch(r"[+-]?\d+(?:[.,]\d+)?", value)),
    }
    return {
        name: sum(1 for value in values if check(value))
        for name, check in checks.items()
    }


def _value_shape(value: str) -> str:
    symbols = []
    for character in value[:120]:
        if character.isupper():
            symbols.append("A")
        elif character.islower():
            symbols.append("a")
        elif character.isdigit():
            symbols.append("9")
        elif character.isspace():
            symbols.append("_")
        elif character in "-_/.,:@+()":
            symbols.append(character)
        else:
            symbols.append("#")
    if len(value) > 120:
        symbols.append("…")
    return _compress_shape(symbols)


def _compress_shape(symbols: list[str]) -> str:
    if not symbols:
        return "<empty>"
    compressed = []
    current = symbols[0]
    count = 1
    for symbol in symbols[1:]:
        if symbol == current:
            count += 1
            continue
        compressed.append(current if count == 1 else f"{current}{{{count}}}")
        current = symbol
        count = 1
    compressed.append(current if count == 1 else f"{current}{{{count}}}")
    return "".join(compressed)
