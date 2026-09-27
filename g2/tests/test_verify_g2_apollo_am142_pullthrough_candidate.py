import json
import unittest

from tools import verify_g2_apollo_am142_pullthrough_candidate as verifier


class G2ApolloAm142PullthroughCandidateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = verifier.analyze()

    def test_am142_semantic_model_target_compiles_on_macos(self) -> None:
        self.assertTrue(self.report["target_compile_verified"])
        self.assertEqual(self.report["toolchain_profile"], "apple-clang")
        self.assertEqual(self.report["target"], "thumbv7em-none-eabi")
        self.assertEqual(self.report["compiler"], "/usr/bin/clang")
        self.assertEqual(self.report["object_size"], 4976)
        self.assertEqual(
            self.report["object_sha256"],
            "273ca76794e7ba222098acaaa9913a6d5e5effb741f95c23bc755c3eecfcf43c",
        )
        self.assertEqual(
            self.report["source_sha256"],
            "fe06bf45dd19a0c595fdb0c4277f12f37cd801d79e130f6271a0889aeceb64e9",
        )
        self.assertEqual(
            self.report["firmware_routing_status"],
            "not_yet_routed_into_overlay",
        )
        self.assertEqual(self.report["undefined_symbols"], [])
        self.assertEqual(self.report["relocation_count"], 28)
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
                    "count": 28,
                    "section": ".ARM.exidx",
                    "type": "R_ARM_PREL31",
                    "value": ".text",
                },
            ],
        )

    def test_am142_candidate_exports_expected_symbols(self) -> None:
        self.assertEqual(
            self.report["exported_text_symbols"],
            [
                "open_cfw_am142_0x4ec718_semantic_model",
                "open_cfw_am142_0x4ec774_semantic_model",
                "open_cfw_am142_0x59a312_semantic_model",
                "open_cfw_am142_0x59a3d2_semantic_model",
                "open_cfw_am142_0x59aa84_semantic_model",
                "open_cfw_am142_0x59aec8_semantic_model",
                "open_cfw_am142_0x59af1e_semantic_model",
                "open_cfw_am142_0x59af42_semantic_model",
                "open_cfw_am142_0x59af54_semantic_model",
                "open_cfw_am142_0x59afa0_semantic_model",
                "open_cfw_am142_0x59b00e_semantic_model",
                "open_cfw_am142_0x59b272_semantic_model",
                "open_cfw_am142_0x59b2aa_semantic_model",
                "open_cfw_am142_0x59b33e_semantic_model",
                "open_cfw_am142_0x59b382_semantic_model",
                "open_cfw_am142_0x59b3de_semantic_model",
                "open_cfw_am142_0x59b454_semantic_model",
                "open_cfw_am142_0x59b52c_semantic_model",
                "open_cfw_am142_0x59b53c_semantic_model",
                "open_cfw_am142_0x59b654_semantic_model",
                "open_cfw_am142_0x59ba4a_semantic_model",
                "open_cfw_am142_0x59c052_semantic_model",
                "open_cfw_am142_0x59c060_semantic_model",
                "open_cfw_am142_0x59c530_semantic_model",
                "open_cfw_am142_0x59cb1e_semantic_model",
                "open_cfw_am142_0x59cb44_semantic_model",
                "open_cfw_am142_0x59cb6c_semantic_model",
                "open_cfw_am142_0x59cb98_semantic_model",
            ],
        )
        self.assertEqual(
            self.report["candidate_addresses"],
            [
                "0x004ec718",
                "0x004ec774",
                "0x0059aa84",
                "0x0059aec8",
                "0x0059af1e",
                "0x0059af42",
                "0x0059af54",
                "0x0059afa0",
                "0x0059a312",
                "0x0059a3d2",
                "0x0059b00e",
                "0x0059b272",
                "0x0059b2aa",
                "0x0059b33e",
                "0x0059b382",
                "0x0059b3de",
                "0x0059b454",
                "0x0059b52c",
                "0x0059b53c",
                "0x0059b654",
                "0x0059ba4a",
                "0x0059cb1e",
                "0x0059cb44",
                "0x0059cb6c",
                "0x0059cb98",
                "0x0059c052",
                "0x0059c060",
                "0x0059c530",
            ],
        )

    def test_summary_is_json_serializable(self) -> None:
        json.dumps(self.report, sort_keys=True)


if __name__ == "__main__":
    unittest.main()
