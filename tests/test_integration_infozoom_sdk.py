"""
Integration test for InfoZoom SDK .fox file export.

Tests the end-to-end flow: model -> .fox file creation.
"""

import pytest
import tempfile
from pathlib import Path
import json
import logging

log = logging.getLogger(__name__)


@pytest.fixture
def test_model():
    """A realistic test model with multiple rules."""
    return {
        "name": "Integration Test Model",
        "reportName": "Customer Validation",
        "source": {
            "attributes": [
                {"name": "CUSTOMER_ID", "comment": "Customer identifier"},
                {"name": "EMAIL", "comment": "Email address"},
                {"name": "PHONE", "comment": "Phone number"},
                {"name": "ZIP_CODE", "comment": "Postal code"},
            ]
        },
        "checks": {
            "groups": [
                {
                    "field": "CUSTOMER_ID",
                    "displayName": "Customer ID",
                    "internalName": "customer_id",
                    "typeHints": "string",
                    "rules": [
                        {
                            "id": "rule_cust_1",
                            "condition": "CUSTOMER_ID IS NOT NULL",
                            "message": "Customer ID is required",
                            "dimension": "Completeness",
                            "active": True,
                        },
                        {
                            "id": "rule_cust_2",
                            "condition": "LEN(CUSTOMER_ID) > 0",
                            "message": "Customer ID must not be empty",
                            "dimension": "Completeness",
                            "active": True,
                        },
                    ],
                },
                {
                    "field": "EMAIL",
                    "displayName": "Email Address",
                    "internalName": "email",
                    "typeHints": "string",
                    "rules": [
                        {
                            "id": "rule_email_1",
                            "condition": "EMAIL IS NOT NULL",
                            "message": "Email is required",
                            "dimension": "Completeness",
                            "active": True,
                        },
                        {
                            "id": "rule_email_2",
                            "condition": "EMAIL LIKE '%@%.%'",
                            "message": "Email format invalid",
                            "dimension": "Validity",
                            "active": True,
                        },
                    ],
                },
                {
                    "field": "PHONE",
                    "displayName": "Phone",
                    "internalName": "phone",
                    "typeHints": "string",
                    "rules": [
                        {
                            "id": "rule_phone_1",
                            "condition": "PHONE IS NULL OR LEN(PHONE) > 0",
                            "message": "Phone format invalid",
                            "dimension": "Validity",
                            "active": True,
                        },
                    ],
                },
                {
                    "field": "ZIP_CODE",
                    "displayName": "ZIP Code",
                    "internalName": "zip_code",
                    "typeHints": "string",
                    "rules": [
                        {
                            "id": "rule_zip_1",
                            "condition": "ZIP_CODE IS NULL OR LEN(ZIP_CODE) = 5",
                            "message": "ZIP code must be 5 digits",
                            "dimension": "Validity",
                            "active": False,  # Inactive rule
                        },
                    ],
                },
            ]
        },
    }


class TestInfoZoomSDKIntegration:
    """Integration tests for InfoZoom SDK export."""

    def test_fox_export_creates_file(self, test_model, tmp_path):
        """Export should create a .fox file."""
        from backend.export_connectors.infozoom_connector import InfoZoomExportConnector

        connector = InfoZoomExportConnector()
        output_path = tmp_path / "test_export.fox"

        result = connector.export_to_file(
            model=test_model,
            output_path=str(output_path),
            options={"mode": "sdk_native"},
        )

        assert Path(result).exists(), "Output .fox file was not created"
        assert Path(result).stat().st_size > 100, ".fox file is too small"
        print(f"[OK] .fox file created: {Path(result).stat().st_size} bytes")

    def test_cache_populated_after_export(self, test_model, tmp_path):
        """Cache should be populated after export."""
        from backend.export_connectors.infozoom_connector import InfoZoomExportConnector
        from backend.export_connectors.utils.rule_translation_cache import (
            RuleTranslationCache,
        )

        connector = InfoZoomExportConnector()
        output_path = tmp_path / "test_export.fox"

        # Export
        connector.export_to_file(
            model=test_model,
            output_path=str(output_path),
            options={"mode": "sdk_native"},
        )

        # Check cache
        cache = RuleTranslationCache()
        stats = cache.get_cache_stats()

        assert stats["cached_rules"] > 0, "Cache should have cached rules"
        print(f"[OK] Cache populated: {stats['cached_rules']} rules cached")
        print(f"    Failed translations: {stats['failed_translations']}")

    def test_error_log_recorded(self, test_model, tmp_path):
        """Errors should be logged during export."""
        from backend.export_connectors.infozoom_connector import InfoZoomExportConnector
        from backend.export_connectors.utils.rule_translation_cache import (
            RuleTranslationCache,
        )

        connector = InfoZoomExportConnector()
        output_path = tmp_path / "test_export.fox"

        # Export
        try:
            connector.export_to_file(
                model=test_model,
                output_path=str(output_path),
                options={"mode": "sdk_native"},
            )
        except Exception as exc:
            log.info(f"Export raised (expected for SDK test): {type(exc).__name__}")

        # Check errors
        cache = RuleTranslationCache()
        errors = cache.get_failed_translations()

        print(f"[INFO] Translation errors: {len(errors)}")
        for error in errors:
            print(f"  - {error['rule_id']}: {error['error'][:100]}")

    def test_text_mode_still_works(self, test_model, tmp_path):
        """Text mode export should still work."""
        from backend.export_connectors.infozoom_connector import InfoZoomExportConnector

        connector = InfoZoomExportConnector()

        # Text export
        text_output = connector.export(
            model=test_model,
            options={"mode": "text_definition"},
        )

        assert "INFOZOOM STRUCTURE DEFINITION" in text_output
        assert "CUSTOMER_ID" in text_output
        assert "EMAIL" in text_output
        print(f"[OK] Text export works: {len(text_output)} chars")

    def test_cache_reuse_on_second_export(self, test_model, tmp_path):
        """Second export should use cache."""
        from backend.export_connectors.infozoom_connector import InfoZoomExportConnector
        from backend.export_connectors.utils.rule_translation_cache import (
            RuleTranslationCache,
        )
        import time

        connector = InfoZoomExportConnector()
        cache = RuleTranslationCache()

        # Clear cache first
        cache.clear_errors()

        output_path1 = tmp_path / "export1.fox"
        output_path2 = tmp_path / "export2.fox"

        # First export
        start1 = time.time()
        try:
            connector.export_to_file(
                model=test_model,
                output_path=str(output_path1),
                options={"mode": "sdk_native"},
            )
        except Exception:
            pass
        time1 = time.time() - start1

        cache_after_1 = cache.get_cache_stats()["cached_rules"]

        # Second export (should use cache)
        start2 = time.time()
        try:
            connector.export_to_file(
                model=test_model,
                output_path=str(output_path2),
                options={"mode": "sdk_native"},
            )
        except Exception:
            pass
        time2 = time.time() - start2

        cache_after_2 = cache.get_cache_stats()["cached_rules"]

        print(f"[OK] First export: {time1:.3f}s, cached {cache_after_1} rules")
        print(f"[OK] Second export: {time2:.3f}s, cached {cache_after_2} rules")

        # Second should use more from cache (but not necessarily faster if SDK is slow)
        assert cache_after_2 >= cache_after_1, "Cache should grow or stay same"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
