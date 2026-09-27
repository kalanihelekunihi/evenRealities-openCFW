import json
import unittest

from tools import analyze_g2_untracked_overlay_inputs as analyzer


class G2UntrackedOverlayInputTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = analyzer.analyze()

    def test_untracked_overlay_inputs_are_pinned(self) -> None:
        self.assertEqual(self.report["input_count"], 0)
        self.assertEqual(self.report["family_counts"], {})
        self.assertEqual(
            self.report["am_helper_range"],
            {"first": None, "last": None, "count": 0, "missing": []},
        )
        self.assertEqual(self.report["total_inst_directive_bytes"], 0)
        self.assertEqual(self.report["raw_bearing_input_count"], 0)
        self.assertEqual(self.report["non_raw_input_count"], 0)
        self.assertEqual(self.report["raw_bearing_am_helper_ranges"], [])
        self.assertEqual(self.report["non_raw_am_helper_ranges"], [])

    def test_largest_untracked_inputs_are_pinned(self) -> None:
        self.assertEqual(self.report["largest_inputs"], [])

    def test_summary_is_json_serializable(self) -> None:
        json.dumps(self.report, sort_keys=True)


if __name__ == "__main__":
    unittest.main()
