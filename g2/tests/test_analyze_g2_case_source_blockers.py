import json
import unittest

from tools import analyze_g2_case_source_blockers as analyzer


class G2CaseSourceBlockerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = analyzer.analyze()

    def test_case_candidate_blockers_are_pinned(self) -> None:
        self.assertEqual(self.report["size"], 55784)
        self.assertEqual(self.report["release_blocking_bytes"], 55752)
        self.assertFalse(self.report["production_routed"])
        self.assertFalse(self.report["source_complete"])
        self.assertEqual(
            self.report["buckets"],
            {
                "production_source": 0,
                "generated_or_reconstructible": 32,
                "candidate_source_not_routed": 14886,
                "typed_retained_or_external": 40866,
                "unclassified": 0,
            },
        )
        self.assertEqual(
            self.report["candidate_admission_blocker_class"],
            "hardware-dependent-board-routing",
        )
        self.assertEqual(self.report["candidate_source_functions"], 222)
        self.assertEqual(self.report["remaining_callable_software_functions"], 0)

    def test_case_source_image_is_software_complete_but_not_board_routed(self) -> None:
        self.assertTrue(self.report["software_image_link_complete"])
        self.assertTrue(self.report["software_even_package_complete"])
        self.assertFalse(self.report["physical_board_services_routed"])
        self.assertEqual(self.report["source_image_translation_units"], 8)
        self.assertEqual(self.report["source_image_undefined_symbols"], 0)

    def test_case_source_only_macos_route_is_authenticated(self) -> None:
        route = self.report["source_only_macos_route"]
        self.assertEqual(route["manifest"], "manifests/g2-2.2.6.10-source-only.json")
        self.assertEqual(route["provider_kind"], "source_build")
        self.assertEqual(route["provider_path"], "build/case-source-image/firmware_box.bin")
        self.assertEqual(route["provider_size"], 18948)
        self.assertEqual(
            route["provider_sha256"],
            "5af2623dba3e4316f03a368510be02b2cfb5aace7331030110472b375d2b5fa8",
        )
        self.assertEqual(route["toolchain_profile"], "apple-clang")
        self.assertTrue(route["software_link_complete"])
        self.assertTrue(route["software_package_complete"])
        self.assertEqual(route["source_translation_units"], 8)
        self.assertEqual(route["undefined_symbols"], 0)
        self.assertFalse(route["production_routed"])
        self.assertEqual(
            route["hardware_validation"],
            "blocked by unavailable physical evidence",
        )

    def test_case_final_frontier_is_pinned(self) -> None:
        self.assertEqual(
            self.report["whole_blob_bucket_bytes"],
            {
                "generated_transport_fill": 32,
                "project_source_candidate": 14886,
                "still_unclassified": 0,
                "typed_external_or_unsupported": 40866,
            },
        )
        self.assertEqual(
            self.report["candidate_source_breakdown"],
            {
                "g2-case-pure-helpers-admission.tsv": {
                    "functions": 7,
                    "instruction_bytes": 248,
                },
                "g2-case-register-policies-admission.tsv": {
                    "functions": 8,
                    "instruction_bytes": 214,
                },
                "g2-case-register-primitives-admission.tsv": {
                    "functions": 13,
                    "instruction_bytes": 120,
                },
                "g2-case-register-transforms-admission.tsv": {
                    "functions": 5,
                    "instruction_bytes": 96,
                },
                "g2-case-semantic-leaves-admission.tsv": {
                    "functions": 189,
                    "instruction_bytes": 14208,
                },
            },
        )
        self.assertEqual(
            self.report["gap_classification_counts"],
            {
                "typed_unsupported_interfunction_code_or_data_boundary": 198,
                "typed_zero_alignment_or_data": 31,
            },
        )
        self.assertEqual(
            self.report["physical_bucket_digest"],
            "126efe6801410d0051201a4a0a7f04a3a0ddd917117cb305afad35772e907a89",
        )

    def test_summary_is_json_serializable(self) -> None:
        json.dumps(self.report, sort_keys=True)


if __name__ == "__main__":
    unittest.main()
