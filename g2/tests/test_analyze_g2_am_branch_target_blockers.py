import json
import unittest

from tools import analyze_g2_am_branch_target_blockers as analyzer


class G2AmBranchTargetBlockerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = analyzer.analyze()

    def test_branch_target_census_is_pinned(self) -> None:
        self.assertEqual(self.report["function_count"], 658)
        self.assertEqual(self.report["byte_count"], 66032)
        self.assertEqual(self.report["site_count"], 5680)
        self.assertEqual(
            self.report["relation_counts"],
            {
                "branch:indirect_or_no_imm": 63,
                "branch:inside_body": 1967,
                "branch:known_am_helper_entry": 35,
                "branch:outside_unmodeled": 1392,
                "call:indirect_or_no_imm": 55,
                "call:inside_body": 345,
                "call:known_am_helper_entry": 1,
                "call:outside_unmodeled": 1822,
            },
        )

    def test_summary_is_json_serializable(self) -> None:
        json.dumps(self.report, sort_keys=True)


if __name__ == "__main__":
    unittest.main()
