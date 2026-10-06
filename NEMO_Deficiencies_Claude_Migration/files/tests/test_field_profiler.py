import json
import unittest

from backend.services.field_profiler import build_anonymized_field_profile


class FieldProfilerTest(unittest.TestCase):
    def test_profile_contains_patterns_but_no_raw_values(self) -> None:
        profile = build_anonymized_field_profile(
            [None, " AB-123 ", "CD-456", "CD-456", "person@example.org", ""]
        )
        serialized = json.dumps(profile)

        self.assertEqual(6, profile["sampleSize"])
        self.assertEqual(1, profile["nullCount"])
        self.assertEqual(1, profile["emptyCount"])
        self.assertEqual(1, profile["duplicateCount"])
        self.assertEqual("anonymized-profile-without-raw-values", profile["privacy"])
        self.assertNotIn("AB-123", serialized)
        self.assertNotIn("person@example.org", serialized)
        self.assertTrue(profile["shapeDistribution"])


if __name__ == "__main__":
    unittest.main()
