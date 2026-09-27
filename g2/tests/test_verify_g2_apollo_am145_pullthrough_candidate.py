import json
import unittest

from tools import verify_g2_apollo_am145_pullthrough_candidate as verifier


class G2ApolloAm145PullthroughCandidateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = verifier.analyze()

    def test_am145_semantic_model_target_compiles_on_macos(self) -> None:
        self.assertTrue(self.report["target_compile_verified"])
        self.assertEqual(self.report["toolchain_profile"], "apple-clang")
        self.assertEqual(self.report["target"], "thumbv7em-none-eabi")
        self.assertEqual(self.report["compiler"], "/usr/bin/clang")
        self.assertEqual(self.report["object_size"], 7476)
        self.assertEqual(
            self.report["object_sha256"],
            "a7c99942b924a6f9b202d226b9a88431e45c2d9e9c39af88c6fa2be16e93c3d3",
        )
        self.assertEqual(
            self.report["source_sha256"],
            "96c1dd3034a9d200c3a731a3183bbfcf352eaac19f69b12b4cc5d33744465869",
        )
        self.assertEqual(
            self.report["firmware_routing_status"],
            "not_yet_routed_into_overlay",
        )
        self.assertEqual(self.report["undefined_symbols"], [])
        self.assertEqual(self.report["relocation_count"], 38)
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
                    "count": 38,
                    "section": ".ARM.exidx",
                    "type": "R_ARM_PREL31",
                    "value": ".text",
                },
            ],
        )

    def test_am145_candidate_exports_expected_symbols(self) -> None:
        self.assertEqual(
            self.report["exported_text_symbols"],
            [
                "open_cfw_am145_0x5a340c_semantic_model",
                "open_cfw_am145_0x5a34ca_semantic_model",
                "open_cfw_am145_0x5a35a4_semantic_model",
                "open_cfw_am145_0x5a36ac_semantic_model",
                "open_cfw_am145_0x5a3798_semantic_model",
                "open_cfw_am145_0x5a3980_semantic_model",
                "open_cfw_am145_0x5a3a10_semantic_model",
                "open_cfw_am145_0x5a3ab0_semantic_model",
                "open_cfw_am145_0x5a3bcc_semantic_model",
                "open_cfw_am145_0x5a3cc6_semantic_model",
                "open_cfw_am145_0x5a3e24_semantic_model",
                "open_cfw_am145_0x5a3fe8_semantic_model",
                "open_cfw_am145_0x5a40ca_semantic_model",
                "open_cfw_am145_0x5a4802_semantic_model",
                "open_cfw_am145_0x5a487a_semantic_model",
                "open_cfw_am145_0x5a490c_semantic_model",
                "open_cfw_am145_0x5a4a66_semantic_model",
                "open_cfw_am145_0x5a4b36_semantic_model",
                "open_cfw_am145_0x5a63c8_semantic_model",
                "open_cfw_am145_0x5a6596_semantic_model",
                "open_cfw_am145_0x5a659a_semantic_model",
                "open_cfw_am145_0x5a65a2_semantic_model",
                "open_cfw_am145_0x5a65b0_semantic_model",
                "open_cfw_am145_0x5a66cc_semantic_model",
                "open_cfw_am145_0x5a674a_semantic_model",
                "open_cfw_am145_0x5a67d2_semantic_model",
                "open_cfw_am145_0x5a6822_semantic_model",
                "open_cfw_am145_0x5a6c52_semantic_model",
                "open_cfw_am145_0x5a6c5e_semantic_model",
                "open_cfw_am145_0x5a6c7c_semantic_model",
                "open_cfw_am145_0x5a6c94_semantic_model",
                "open_cfw_am145_0x5a6ca2_semantic_model",
                "open_cfw_am145_0x5a6cb0_semantic_model",
                "open_cfw_am145_0x5a6d10_semantic_model",
                "open_cfw_am145_0x5a6e34_semantic_model",
                "open_cfw_am145_0x5a6e4a_semantic_model",
                "open_cfw_am145_0x5a6eb6_semantic_model",
                "open_cfw_am145_0x5a6f5c_semantic_model",
            ],
        )
        self.assertEqual(
            self.report["candidate_addresses"],
            [
                "0x005a340c",
                "0x005a34ca",
                "0x005a35a4",
                "0x005a36ac",
                "0x005a3798",
                "0x005a3980",
                "0x005a3a10",
                "0x005a3ab0",
                "0x005a3bcc",
                "0x005a3cc6",
                "0x005a3e24",
                "0x005a3fe8",
                "0x005a40ca",
                "0x005a4a66",
                "0x005a4b36",
                "0x005a4802",
                "0x005a487a",
                "0x005a490c",
                "0x005a63c8",
                "0x005a6596",
                "0x005a659a",
                "0x005a65a2",
                "0x005a65b0",
                "0x005a66cc",
                "0x005a674a",
                "0x005a6c52",
                "0x005a6c5e",
                "0x005a6c7c",
                "0x005a6c94",
                "0x005a6ca2",
                "0x005a6cb0",
                "0x005a6d10",
                "0x005a67d2",
                "0x005a6822",
                "0x005a6e34",
                "0x005a6e4a",
                "0x005a6eb6",
                "0x005a6f5c",
            ],
        )

    def test_summary_is_json_serializable(self) -> None:
        json.dumps(self.report, sort_keys=True)


if __name__ == "__main__":
    unittest.main()
