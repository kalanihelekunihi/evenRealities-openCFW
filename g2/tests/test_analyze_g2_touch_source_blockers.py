import json
import unittest

from tools import analyze_g2_touch_source_blockers as analyzer


class G2TouchSourceBlockerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = analyzer.analyze()

    def test_touch_candidate_blockers_are_pinned(self) -> None:
        self.assertEqual(self.report["size"], 34464)
        self.assertEqual(self.report["release_blocking_bytes"], 33952)
        self.assertFalse(self.report["production_routed"])
        self.assertFalse(self.report["source_complete"])
        self.assertEqual(
            self.report["buckets"],
            {
                "production_source": 0,
                "generated_or_reconstructible": 512,
                "candidate_source_not_routed": 14510,
                "typed_retained_or_external": 19442,
                "unclassified": 0,
            },
        )
        self.assertEqual(
            self.report["candidate_admission_blocker_class"],
            "hardware-dependent-resident-abi",
        )
        self.assertFalse(self.report["resident_abi_available"])
        self.assertFalse(self.report["physical_board_services_routed"])

    def test_touch_source_image_is_software_complete_but_not_routed(self) -> None:
        self.assertTrue(self.report["software_image_link_complete"])
        self.assertTrue(self.report["software_fwpk_package_complete"])
        self.assertEqual(self.report["candidate_source_functions"], 178)
        self.assertEqual(self.report["remaining_callable_software_functions"], 0)
        self.assertEqual(self.report["remaining_source_or_implementation_functions"], 0)
        self.assertEqual(self.report["unimplemented_application_contracts"], 0)
        self.assertEqual(self.report["source_image_translation_units"], 31)
        self.assertEqual(self.report["source_image_undefined_symbols"], 0)

    def test_touch_source_only_macos_route_is_authenticated(self) -> None:
        route = self.report["source_only_macos_route"]
        self.assertEqual(route["manifest"], "manifests/g2-2.2.6.10-source-only.json")
        self.assertEqual(route["provider_kind"], "source_build")
        self.assertEqual(route["provider_path"], "build/touch-source-image/firmware_touch.bin")
        self.assertEqual(route["provider_size"], 15516)
        self.assertEqual(
            route["provider_sha256"],
            "128e8e2e6321b5bf3515317fe1935927afd0ec1dcd3be0e1e70f38a6a70c74ac",
        )
        self.assertEqual(route["toolchain_profile"], "apple-clang")
        self.assertTrue(route["software_link_complete"])
        self.assertTrue(route["software_package_complete"])
        self.assertEqual(route["source_translation_units"], 31)
        self.assertEqual(route["undefined_symbols"], 0)
        self.assertFalse(route["production_routed"])
        self.assertEqual(
            route["hardware_validation"],
            "blocked by unavailable physical evidence",
        )

    def test_touch_candidate_provenance_is_pinned(self) -> None:
        provenance = self.report["candidate_provenance"]
        self.assertEqual(provenance["candidate_bytes"], 14510)
        self.assertEqual(provenance["entry_claim_count"], 178)
        self.assertFalse(provenance["production_elf_ownership"])
        self.assertEqual(provenance["stock_byte_redistribution_authority"], "NOASSERTION")
        self.assertEqual(
            self.report["generation_receipt_sha256"],
            "656618c3fe2e7a05e127be38982efb7f261405a753e50f95d2fd4f7bd47781df",
        )

    def test_touch_final_physical_frontier_is_pinned(self) -> None:
        self.assertEqual(
            self.report["whole_blob_bucket_bytes"],
            {
                "generated_transport_fill": 512,
                "project_source_candidate": 14510,
                "still_unclassified": 0,
                "typed_external_or_unsupported": 19442,
            },
        )
        self.assertEqual(
            self.report["typed_physical_bucket_bytes"],
            {
                "typed_code_capsense_cat2_mixed_provider": 7000,
                "typed_code_owner_unresolved": 6686,
                "typed_code_referenced_literal_data": 1924,
                "typed_code_residual_arch_nop_padding": 8,
                "typed_code_residual_legacy_nop_padding": 126,
                "typed_code_residual_return_tail": 4,
                "typed_code_residual_typed_data": 60,
                "typed_code_residual_zero_halfword_alignment_or_data": 46,
                "typed_noncode_config_and_tables": 1756,
                "typed_noncode_strings": 1640,
                "typed_noncode_vectors": 192,
            },
        )
        self.assertEqual(len(self.report["physical_bucket_rows"]), 13)
        self.assertEqual(
            self.report["physical_bucket_digest"],
            "2e5bfaafd2f03a36f8eba68b0160be284ba91f9e22d2e10b1f3ce8b2297ab5f2",
        )
        self.assertEqual(
            [
                (row["category"], row["bytes"], row["license_status"])
                for row in self.report["physical_bucket_rows"][:4]
            ],
            [
                ("generated_transport_fill", 512, "MIT reconstruction"),
                (
                    "project_source_candidate",
                    14510,
                    "MIXED semantic routes: MIT; MIT OR GPL-3.0-only; "
                    "Apache-2.0; stock-byte authority NOASSERTION",
                ),
                (
                    "typed_code_capsense_cat2_mixed_provider",
                    7000,
                    "EULA-or-Apache-2.0 unresolved",
                ),
                ("typed_code_owner_unresolved", 6686, "NOASSERTION"),
            ],
        )

    def test_summary_is_json_serializable(self) -> None:
        json.dumps(self.report, sort_keys=True)


if __name__ == "__main__":
    unittest.main()
