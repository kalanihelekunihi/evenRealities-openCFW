import json
import unittest

from tools import analyze_g2_am_mixed_boundary_debt as analyzer


class G2AmMixedBoundaryDebtTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = analyzer.analyze()

    def test_remaining_am_boundary_debt_is_pinned(self) -> None:
        self.assertEqual(self.report["source_count"], 102)
        self.assertEqual(self.report["inst_directive_bytes"], 584954)
        reasons = self.report["reason_counts"]
        self.assertGreaterEqual(reasons["nonlinear_data_or_literal_island"], 1)
        self.assertGreaterEqual(
            reasons["it_block_requires_conditional_text_or_whole_body_source"], 1)
        self.assertGreaterEqual(
            reasons["vector_instruction_text_not_apple_clang_roundtrip_safe"], 1)
        self.assertEqual(
            reasons["linear_raw_instruction_text_still_needs_source_model"], 89)
        classes = self.report["function_class_counts"]
        self.assertEqual(
            classes["linear:linear_raw_instruction_text_still_needs_source_model"],
            {"functions": 693, "bytes": 69030},
        )
        self.assertEqual(
            classes["linear:pc_relative_or_pc_operand_needs_boundary_model"],
            {"functions": 639, "bytes": 143958},
        )
        self.assertEqual(
            classes["mixed:nonlinear_data_or_literal_island"],
            {"functions": 742, "bytes": 117534},
        )

    def test_am145_blocked_function_frontier_is_largest_first(self) -> None:
        source = next(
            row for row in self.report["sources"]
            if row["source"].endswith("runtime_liblc3_am145_helpers.c")
        )
        self.assertEqual(source["inst_directive_bytes"], 9850)
        self.assertEqual(source["blocked_function_count"], 32)
        self.assertEqual(source["blocked_function_bytes"], 9850)
        self.assertEqual(
            [
                (row["function"], row["byte_length"])
                for row in source["blocked_functions"][:5]
            ],
            [
                ("open_cfw_runtime_am145_0x005a490c", 1012),
                ("open_cfw_runtime_am145_0x005a45d0", 782),
                ("open_cfw_runtime_am145_0x005a6d10", 674),
                ("open_cfw_runtime_am145_0x005a65de", 632),
                ("open_cfw_runtime_am145_0x005a326c", 606),
            ],
        )
        self.assertEqual(len(source["blocked_functions"]), 32)

    def test_am115_blocked_function_frontier_exposes_full_backlog(self) -> None:
        source = next(
            row for row in self.report["sources"]
            if row["source"].endswith("runtime_liblc3_am115_helpers.c")
        )
        self.assertEqual(source["blocked_function_count"], 27)
        self.assertEqual(len(source["blocked_functions"]), 27)
        self.assertEqual(
            [
                (row["function"], row["byte_length"], row["reasons"])
                for row in source["blocked_functions"][15:18]
            ],
            [
                (
                    "open_cfw_runtime_am115_0x0054566c",
                    106,
                    ["pc_relative_or_pc_operand_needs_boundary_model"],
                ),
                (
                    "open_cfw_runtime_am115_0x0054503a",
                    100,
                    ["nonlinear_data_or_literal_island"],
                ),
                (
                    "open_cfw_runtime_am115_0x005455e4",
                    96,
                    ["nonlinear_data_or_literal_island"],
                ),
            ],
        )

    def test_summary_manifest_is_json_serializable(self) -> None:
        json.dumps(self.report, sort_keys=True)


if __name__ == "__main__":
    unittest.main()
