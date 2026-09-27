import json
import unittest

from tools import analyze_g2_am_pc_relative_blockers as analyzer


class G2AmPcRelativeBlockerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = analyzer.analyze()

    def test_pc_relative_only_blockers_are_pinned(self) -> None:
        self.assertEqual(self.report["blocker_count"], 6)
        self.assertEqual(self.report["blocker_bytes"], 174)
        self.assertEqual(self.report["outside_body_reference_count"], 7)
        self.assertTrue(all(
            blocker["outside_body_reference_count"] >= 1
            for blocker in self.report["blockers"]
        ))

    def test_summary_is_json_serializable(self) -> None:
        json.dumps(self.report, sort_keys=True)


if __name__ == "__main__":
    unittest.main()
