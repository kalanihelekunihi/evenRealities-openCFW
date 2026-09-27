import json
import unittest

from tools import analyze_g2_am_scalar_padding_candidates as analyzer


class G2AmScalarPaddingCandidateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = analyzer.analyze()

    def test_candidate_census_is_pinned(self) -> None:
        self.assertEqual(self.report["candidate_count"], 0)
        self.assertEqual(self.report["candidate_bytes"], 0)
        allowed = set(self.report["allowed_instructions"])
        for candidate in self.report["candidates"]:
            self.assertTrue(candidate["source"].startswith(
                "components/apollo_main/core_overlay/runtime_liblc3_am"))
            self.assertGreater(candidate["byte_length"], 0)
            for instruction in candidate["mnemonics"]:
                self.assertIn(instruction["text"], allowed)
                self.assertIn(instruction["size"], {2, 4})

    def test_summary_is_json_serializable(self) -> None:
        json.dumps(self.report, sort_keys=True)


if __name__ == "__main__":
    unittest.main()
