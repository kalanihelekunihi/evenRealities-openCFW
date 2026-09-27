import json
import unittest

from tools import analyze_g2_source_only_blockers as analyzer


class G2SourceOnlyBlockerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = analyzer.analyze()

    def test_source_only_blockers_are_pinned(self) -> None:
        self.assertFalse(self.report["ready"])
        self.assertEqual(self.report["global_blockers"], ["source_ownership_quality"])
        self.assertEqual(self.report["blocking_component_count"], 6)
        self.assertEqual(self.report["release_blocking_bytes"], 3737843)
        self.assertEqual(
            {
                name: row["release_blocking_bytes"]
                for name, row in self.report["components"].items()
            },
            {
                "apollo_bootloader": 81187,
                "apollo_main": 3030368,
                "ble_em9305": 210584,
                "case": 55752,
                "codec": 326000,
                "touch": 33952,
            },
        )

    def test_not_production_routed_blockers_are_explicit(self) -> None:
        self.assertFalse(self.report["components"]["case"]["production_routed"])
        self.assertFalse(self.report["components"]["codec"]["production_routed"])
        self.assertFalse(self.report["components"]["touch"]["production_routed"])

    def test_exit_criteria_are_explicit(self) -> None:
        self.assertIn(
            "Reduce public_unrouted_raw_instruction_transcript_files and public_unrouted_raw_instruction_transcript_bytes to zero.",
            self.report["global_exit_criteria"]["source_ownership_quality"],
        )
        self.assertIn(
            "Resolve PC-relative/PC operand, nonlinear literal/data island, vector, IT-block, branch-target, and linear raw instruction text blockers without raw instruction transcript production routing.",
            self.report["components"]["apollo_main"]["exit_criteria"],
        )
        self.assertIn(
            "Provide source-owned or redistributable exact-provider implementations for all 11 GX8002 typed external spans.",
            self.report["components"]["codec"]["exit_criteria"],
        )
        self.assertIn(
            "Production-route project source candidates and typed physical buckets including CapSense/CAT2 provider bytes, owner-unresolved code, literals, vectors, strings, and configuration tables.",
            self.report["components"]["touch"]["exit_criteria"],
        )
        self.assertTrue(all(
            self.report["components"][name]["exit_criteria"]
            for name in self.report["components"]
        ))

    def test_remediation_queue_is_ranked(self) -> None:
        queue = self.report["remediation_queue"]
        self.assertEqual(
            [(row["priority"], row["scope"], row["kind"]) for row in queue],
            [
                (0, "source_ownership_quality", "global_gate"),
                (1, "apollo_main", "component_release_blocker"),
                (2, "codec", "component_release_blocker"),
                (3, "ble_em9305", "component_release_blocker"),
                (4, "apollo_bootloader", "component_release_blocker"),
                (5, "case", "component_release_blocker"),
                (6, "touch", "component_release_blocker"),
            ],
        )
        self.assertIsNone(queue[0]["blocking_bytes"])
        self.assertEqual(queue[1]["blocking_bytes"], 3030368)
        self.assertEqual(queue[2]["scope"], "codec")
        self.assertEqual(queue[2]["blocker_class"], "not-production-routed")
        self.assertEqual(queue[6]["blocker_class"], "hardware-dependent-resident-abi")

    def test_summary_is_json_serializable(self) -> None:
        json.dumps(self.report, sort_keys=True)


if __name__ == "__main__":
    unittest.main()
