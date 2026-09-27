import json
import subprocess
import sys
import unittest

from tools import verify_g2_macos_source_closure as verifier


class G2MacOSSourceClosureWitnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = verifier.analyze()

    def test_macos_source_only_build_is_verified(self) -> None:
        build = self.report["macos_build"]
        self.assertTrue(build["verified"])
        self.assertEqual(build["manifest"], "manifests/g2-2.2.6.10-source-only.json")
        self.assertEqual(build["toolchain_profile"], "apple-clang")
        self.assertEqual(
            build["deterministic_package_sha256"],
            "bf2f6f7a8e5986cb8ecd06783db7bdffd38d1b50ee25bc47be46b6434868dc9f",
        )

    def test_build_witness_keeps_source_closure_gates_visible(self) -> None:
        self.assertFalse(self.report["release_authorized"])
        self.assertTrue(self.report["classification_complete"])
        self.assertFalse(self.report["source_complete"])
        self.assertFalse(self.report["source_ownership_quality_clean"])
        self.assertTrue(self.report["project_license_policy_clean"])
        self.assertEqual(self.report["release_blocking_bytes"], 3739673)
        self.assertEqual(self.report["source_owned_bytes_currently_overstated"], 1830)

    def test_build_witness_includes_next_pull_through_frontier(self) -> None:
        frontier = self.report["closure_frontier"]
        self.assertEqual(
            frontier["primary_global_gate"]["raw_transcript_bytes"],
            584954,
        )
        self.assertEqual(
            frontier["component_priority"][0]["scope"],
            "apollo_main",
        )
        self.assertEqual(
            frontier["component_priority"][0]["blocking_bytes"],
            3032198,
        )
        self.assertEqual(
            frontier["apollo_retained_hot_target_frontier"][
                "source_pull_through_recovery_rollup"]["work_items"][0],
            {
                "arithmetic_motif_kind": "squared_delta_accumulator",
                "byte_length": 148,
                "dependency_class": "isolated_window",
                "end_address": 0x0059A3A6,
                "entrypoint_count": 2,
                "implementation_readiness": "ready_for_direct_c_translation",
                "dependency_barrier": None,
                "instruction_count": 44,
                "memory_instruction_count": 9,
                "priority": 1,
                "start_address": 0x0059A312,
                "status": "requires_c_pull_through",
                "terminal_instruction": "bge #0x59a45c",
                "translation_shape": "straight_line_to_terminal_branch",
                "vfp_instruction_count": 26,
            },
        )

    def test_build_witness_records_goal_requirements(self) -> None:
        requirements = self.report["requirements"]
        self.assertTrue(requirements["macos_source_only_build_verified"]["satisfied"])
        self.assertTrue(
            requirements[
                "apollo_am115_pullthrough_candidate_target_compiles"][
                    "satisfied"]
        )
        self.assertEqual(
            requirements[
                "apollo_am115_pullthrough_candidate_target_compiles"][
                    "evidence"]["object_sha256"],
            "b4c524b0194a0f9781ebc2916cde7067c4dc78e83a7010579800094c00f8be71",
        )
        self.assertEqual(
            requirements[
                "apollo_am115_pullthrough_candidate_target_compiles"][
                    "evidence"]["firmware_routing_status"],
            "not_yet_routed_into_overlay",
        )
        self.assertTrue(
            requirements[
                "apollo_am145_pullthrough_candidate_target_compiles"][
                    "satisfied"]
        )
        self.assertEqual(
            requirements[
                "apollo_am145_pullthrough_candidate_target_compiles"][
                    "evidence"]["object_sha256"],
            "a7c99942b924a6f9b202d226b9a88431e45c2d9e9c39af88c6fa2be16e93c3d3",
        )
        self.assertEqual(
            requirements[
                "apollo_am145_pullthrough_candidate_target_compiles"][
                    "evidence"]["firmware_routing_status"],
            "not_yet_routed_into_overlay",
        )
        self.assertTrue(
            requirements[
                "apollo_am142_pullthrough_candidate_target_compiles"][
                    "satisfied"]
        )
        self.assertEqual(
            requirements[
                "apollo_am142_pullthrough_candidate_target_compiles"][
                    "evidence"]["object_sha256"],
            "273ca76794e7ba222098acaaa9913a6d5e5effb741f95c23bc755c3eecfcf43c",
        )
        self.assertEqual(
            requirements[
                "apollo_am142_pullthrough_candidate_target_compiles"][
                    "evidence"]["firmware_routing_status"],
            "not_yet_routed_into_overlay",
        )
        self.assertTrue(requirements["classification_complete"]["satisfied"])
        self.assertTrue(
            requirements[
                "all_release_blocking_components_have_explicit_frontier"][
                    "satisfied"]
        )
        self.assertFalse(requirements["source_complete"]["satisfied"])
        self.assertFalse(requirements["source_ownership_quality_clean"]["satisfied"])
        self.assertFalse(requirements["release_authorized"]["satisfied"])
        self.assertEqual(
            requirements["release_authorized"]["evidence"][
                "release_blocking_bytes"],
            3739673,
        )
        self.assertEqual(
            requirements["release_authorized"]["evidence"][
                "next_remediation"]["scope"],
            "source_ownership_quality",
        )
        self.assertEqual(
            self.report["frontier_coverage"]["missing_frontier_components"],
            [],
        )

    def test_build_witness_carries_remediation_queue(self) -> None:
        self.assertEqual(
            [
                (row["priority"], row["scope"], row["kind"])
                for row in self.report["remediation_queue"]
            ],
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
        self.assertIn(
            "Reduce public_unrouted_raw_instruction_transcript_files and public_unrouted_raw_instruction_transcript_bytes to zero.",
            self.report["remediation_queue"][0]["exit_criteria"],
        )

    def test_cli_summary_exposes_pullthrough_target_compile_requirements(self) -> None:
        completed = subprocess.run(
            [sys.executable, "tools/verify_g2_macos_source_closure.py"],
            cwd=verifier.ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        summary = json.loads(completed.stdout)
        self.assertTrue(summary["macos_build_verified"])
        self.assertTrue(summary["apollo_am115_pullthrough_target_compiles"])
        self.assertEqual(
            summary["apollo_am115_pullthrough_object_sha256"],
            "b4c524b0194a0f9781ebc2916cde7067c4dc78e83a7010579800094c00f8be71",
        )
        self.assertTrue(summary["apollo_am145_pullthrough_target_compiles"])
        self.assertEqual(
            summary["apollo_am145_pullthrough_object_sha256"],
            "a7c99942b924a6f9b202d226b9a88431e45c2d9e9c39af88c6fa2be16e93c3d3",
        )
        self.assertTrue(summary["apollo_am142_pullthrough_target_compiles"])
        self.assertEqual(
            summary["apollo_am142_pullthrough_object_sha256"],
            "273ca76794e7ba222098acaaa9913a6d5e5effb741f95c23bc755c3eecfcf43c",
        )

    def test_summary_is_json_serializable(self) -> None:
        json.dumps(self.report, sort_keys=True)


if __name__ == "__main__":
    unittest.main()
