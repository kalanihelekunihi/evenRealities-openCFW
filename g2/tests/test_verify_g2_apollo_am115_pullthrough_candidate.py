import json
import unittest

from tools import verify_g2_apollo_am115_pullthrough_candidate as verifier


class G2ApolloAm115PullthroughCandidateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = verifier.analyze()

    def test_am115_semantic_model_target_compiles_on_macos(self) -> None:
        self.assertTrue(self.report["target_compile_verified"])
        self.assertEqual(self.report["toolchain_profile"], "apple-clang")
        self.assertEqual(self.report["target"], "thumbv7em-none-eabi")
        self.assertEqual(self.report["compiler"], "/usr/bin/clang")
        self.assertEqual(self.report["object_size"], 1104)
        self.assertEqual(
            self.report["object_sha256"],
            "b4c524b0194a0f9781ebc2916cde7067c4dc78e83a7010579800094c00f8be71",
        )
        self.assertEqual(
            self.report["source_sha256"],
            "ae5803793f6b9c4a24e04673b2f03cf2bd0f2ccc0036b9c8242d66083f6b58af",
        )
        self.assertEqual(
            self.report["firmware_routing_status"],
            "not_yet_routed_into_overlay",
        )
        self.assertEqual(self.report["undefined_symbols"], [])
        self.assertEqual(self.report["relocation_count"], 3)
        self.assertEqual(
            self.report["allowed_relocation"],
            {
                "section": ".ARM.exidx",
                "type": "R_ARM_PREL31",
                "value": ".text",
            },
        )
        self.assertEqual(
            self.report["relocation_summary"],
            [
                {
                    "count": 3,
                    "section": ".ARM.exidx",
                    "type": "R_ARM_PREL31",
                    "value": ".text",
                },
            ],
        )

    def test_am115_candidate_exports_expected_symbols(self) -> None:
        self.assertEqual(
            self.report["exported_text_symbols"],
            [
                "open_cfw_am115_0x5455c6_semantic_model",
                "open_cfw_am115_0x545ec4_semantic_model",
                "open_cfw_am115_0x546e02_semantic_model",
            ],
        )
        self.assertEqual(
            self.report["candidate_addresses"],
            ["0x005455c6", "0x00545ec4", "0x00546e02"],
        )

    def test_summary_is_json_serializable(self) -> None:
        json.dumps(self.report, sort_keys=True)


if __name__ == "__main__":
    unittest.main()
