import json
import unittest

from tools import analyze_g2_am_linear_raw_blockers as analyzer


class G2AmLinearRawBlockerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = analyzer.analyze()

    def test_linear_raw_blockers_are_pinned(self) -> None:
        self.assertEqual(self.report["function_count"], 704)
        self.assertEqual(self.report["byte_count"], 70026)
        classes = self.report["blocker_class_counts"]
        self.assertEqual(
            classes[
                "external_call_or_indirect_branch,"
                "external_or_unmodeled_branch_target,"
                "local_branch_control_flow_needs_source_model,"
                "pc_relative_operand"
            ],
            {"functions": 89, "bytes": 14456},
        )
        self.assertEqual(
            classes["external_or_unmodeled_branch_target"],
            {"functions": 80, "bytes": 7736},
        )
        self.assertEqual(
            classes["system_or_undefined_decode"],
            {"functions": 21, "bytes": 1874},
        )

    def test_summary_is_json_serializable(self) -> None:
        json.dumps(self.report, sort_keys=True)


if __name__ == "__main__":
    unittest.main()
