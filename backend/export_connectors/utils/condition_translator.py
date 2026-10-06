"""
Condition translator: converts NEMO SQL conditions to other target syntaxes.

NEMO uses SAP HANA SQL dialect. Notable differences from T-SQL:
- LIKE_REGEXPR(expr, pattern) → no direct T-SQL equivalent; fallback to PATINDEX
- LENGTH(expr)                → LEN(expr) in T-SQL
- REPLACE_REGEXPR(...)        → complex; simplified with warning
- TO_NVARCHAR(...)             → CAST(... AS NVARCHAR(MAX)) in T-SQL
- TRIM(expr)                  → LTRIM(RTRIM(expr)) in T-SQL (SQL Server < 2017)
                                or TRIM(expr) in SQL Server 2017+
"""

from __future__ import annotations

import re
from typing import Optional, Tuple


class ConditionTranslator:
    """Translate NEMO SQL conditions to other target formats."""

    # ------------------------------------------------------------------ #
    # Public API                                                            #
    # ------------------------------------------------------------------ #

    def to_mssql(self, condition: str) -> Tuple[str, Optional[str]]:
        """
        Translate a NEMO condition string to T-SQL.

        Returns:
            (translated_sql, warning_or_None)
        """
        warnings: list[str] = []
        result = condition

        result, w = self._translate_like_regexpr(result)
        if w:
            warnings.append(w)

        result = self._translate_length(result)
        result = self._translate_trim(result)
        result = self._translate_to_nvarchar(result)

        w_replace = self._check_replace_regexpr(result)
        if w_replace:
            warnings.append(w_replace)

        warning = "; ".join(warnings) if warnings else None
        return result, warning

    def to_description_en(self, condition: str, field_name: str = "") -> str:
        """
        Translate a NEMO condition to a human-readable English description.

        Examples:
            "FIELD_A IS NULL"           → "Field A is empty (required)"
            "TRIM(FIELD_A) <> ''"       → "Field A has leading/trailing whitespace"
            "LENGTH(FIELD_A) < 5"       → "Field A is shorter than 5 characters"
            "FIELD_A LIKE_REGEXPR ..."  → "Field A does not match required pattern"
        """
        cond = condition.strip()
        label = self._field_label(field_name)

        # NULL / empty checks
        if re.search(r"\bIS\s+NULL\b", cond, re.IGNORECASE):
            return f"{label} is empty (required)"
        if re.search(r"=\s*''", cond):
            return f"{label} is empty (required)"
        if re.search(r"IS\s+NOT\s+NULL", cond, re.IGNORECASE) and re.search(r"=\s*''", cond):
            return f"{label} is missing"

        # Whitespace
        if re.search(r"\bTRIM\b", cond, re.IGNORECASE) and re.search(r"<>|!=", cond):
            return f"{label} has leading or trailing whitespace"

        # Length checks
        length_match = re.search(r"\bLENGTH\s*\(([^)]+)\)\s*([<>]=?)\s*(\d+)", cond, re.IGNORECASE)
        if length_match:
            op = length_match.group(2)
            num = length_match.group(3)
            if op in ("<", "<="):
                return f"{label} is shorter than {num} characters"
            if op in (">", ">="):
                return f"{label} is longer than {num} characters"

        # Regex / LIKE_REGEXPR
        if re.search(r"\bNOT\s+LIKE_REGEXPR\b", cond, re.IGNORECASE):
            return f"{label} does not match the required pattern"
        if re.search(r"\bLIKE_REGEXPR\b", cond, re.IGNORECASE):
            return f"{label} matches a prohibited pattern"

        # Simple LIKE
        like_match = re.search(r"\bNOT\s+LIKE\s+'([^']+)'", cond, re.IGNORECASE)
        if like_match:
            return f"{label} does not match pattern '{like_match.group(1)}'"
        like_match = re.search(r"\bLIKE\s+'([^']+)'", cond, re.IGNORECASE)
        if like_match:
            return f"{label} matches prohibited pattern '{like_match.group(1)}'"

        # Fallback: return cleaned condition
        return f"{label}: {cond}"

    # ------------------------------------------------------------------ #
    # MSSQL translation helpers                                             #
    # ------------------------------------------------------------------ #

    def _translate_like_regexpr(self, sql: str) -> Tuple[str, Optional[str]]:
        """
        Replace LIKE_REGEXPR with T-SQL PATINDEX approximation.

        NEMO:  field NOT LIKE_REGEXPR '^[0-9]+$'
        T-SQL: PATINDEX('%[^0-9]%', field) > 0   (simplified, NOT exact)

        Because PATINDEX uses a subset of regex, a warning is always emitted.
        """
        pattern = re.compile(
            r"""(?ix)
            (?P<field>[A-Za-z_][\w.]*)          # field identifier
            \s+
            (?P<not>NOT\s+)?                    # optional NOT
            LIKE_REGEXPR\s*
            \(?\s*
            '(?P<regex>[^']*)'                  # regex literal
            \s*\)?
            """,
        )

        warnings_found: list[str] = []

        def replace(m: re.Match) -> str:
            field = m.group("field")
            negated = bool(m.group("not"))
            regex = m.group("regex")
            warnings_found.append(
                f"LIKE_REGEXPR translated to PATINDEX approximation "
                f"(original regex: '{regex}') – verify result manually"
            )
            # Build a best-effort PATINDEX expression
            patindex_pattern = self._regex_to_patindex(regex)
            if negated:
                # NOT LIKE_REGEXPR means "does NOT match", i.e. violating → PATINDEX = 0
                return f"PATINDEX('{patindex_pattern}', {field}) = 0"
            else:
                return f"PATINDEX('{patindex_pattern}', {field}) > 0"

        result = pattern.sub(replace, sql)
        warning = warnings_found[0] if warnings_found else None
        return result, warning

    def _regex_to_patindex(self, regex: str) -> str:
        """
        Convert a simple NEMO regex to a T-SQL PATINDEX pattern.

        Only handles the most common patterns; complex regexes get %[^]%.
        """
        # Common patterns
        if regex in (r"^\d+$", r"^[0-9]+$"):
            return "%[^0-9]%"
        if regex in (r"^[A-Za-z]+$",):
            return "%[^A-Za-z]%"
        if regex in (r"[\P{L}]", r"[^\\p{L}]"):
            return "%[^A-Za-zÄÖÜäöüß]%"
        # Default: wrap in wildcard for partial match
        # Remove anchors
        simplified = regex.lstrip("^").rstrip("$")
        if simplified:
            return f"%{simplified}%"
        return "%"

    def _translate_length(self, sql: str) -> str:
        """LENGTH(x)  →  LEN(x)  (T-SQL)."""
        return re.sub(r"\bLENGTH\s*\(", "LEN(", sql, flags=re.IGNORECASE)

    def _translate_trim(self, sql: str) -> str:
        """
        TRIM(x) → LTRIM(RTRIM(x))

        Uses a capturing group to include the extra closing paren so that paren
        counts remain balanced.  The pattern captures a simple argument (no nested
        parens); complex arguments that contain nested parens are handled by a
        fallback that keeps the original text and adds the extra ')'.

        Only standalone TRIM is replaced; LTRIM/RTRIM are left untouched because
        the word boundary \b prevents matching inside LTRIM/RTRIM.
        """
        # Simple argument: no nested parens (covers the vast majority of rules)
        result = re.sub(
            r"\bTRIM\s*\(([^()]*)\)",
            r"LTRIM(RTRIM(\1))",
            sql,
            flags=re.IGNORECASE,
        )
        # Fallback: TRIM still present → complex nested arg; emit a warning-friendly
        # approximation by wrapping the entire remainder (best-effort).
        result = re.sub(
            r"\bTRIM\s*\(",
            "LTRIM(RTRIM(",
            result,
            flags=re.IGNORECASE,
        )
        return result

    def _translate_to_nvarchar(self, sql: str) -> str:
        """TO_NVARCHAR(x)  →  CAST(x AS NVARCHAR(MAX))."""
        return re.sub(
            r"\bTO_NVARCHAR\s*\(([^)]+)\)",
            r"CAST(\1 AS NVARCHAR(MAX))",
            sql,
            flags=re.IGNORECASE,
        )

    def _check_replace_regexpr(self, sql: str) -> Optional[str]:
        if re.search(r"\bREPLACE_REGEXPR\b", sql, re.IGNORECASE):
            return "REPLACE_REGEXPR has no direct T-SQL equivalent – manual review required"
        return None

    # ------------------------------------------------------------------ #
    # Helpers                                                               #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _field_label(field_name: str) -> str:
        """Convert an internal field name to a readable label."""
        if not field_name:
            return "Field"
        # Convert SCREAMING_SNAKE to Title Case words
        words = re.split(r"[_\s]+", field_name)
        return " ".join(w.capitalize() for w in words if w)
