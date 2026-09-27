import json
import unittest

from tools import analyze_g2_apollo_main_source_blockers as analyzer


class G2ApolloMainSourceBlockerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = analyzer.analyze()

    def test_apollo_main_source_blockers_are_pinned(self) -> None:
        self.assertEqual(self.report["release_blocking_bytes"], 3030368)
        self.assertEqual(
            self.report["release_readiness_partition"],
            {
                "candidate_source_not_routed": 0,
                "typed_retained_or_external": 3030368,
            },
        )
        self.assertEqual(
            self.report["unanchored_frontier_partition"],
            {
                "candidate_source_not_routed": 0,
                "typed_retained_unanchored_without_candidate": 576221,
            },
        )
        self.assertEqual(self.report["raw_public_unrouted_bytes"], 595020)

    def test_pt_protocol_retained_boundaries_are_pinned(self) -> None:
        pt = self.report["pt_protocol"]
        self.assertFalse(pt["pt_protocol_board_source_complete"])
        self.assertEqual(pt["pt_protocol_retained_provider_bindings_remaining"], 12)
        self.assertEqual(pt["pt_protocol_top_level_retained_provider_bindings_remaining"], 4)
        self.assertEqual(pt["pt_protocol_production_text_placement_shortfall_bytes"], 22547)

    def test_apollo_main_source_build_route_is_authenticated(self) -> None:
        route = self.report["source_build_route"]
        self.assertEqual(route["manifest"], "manifests/g2-2.2.6.10-core-source.json")
        self.assertEqual(route["provider_kind"], "source_build")
        self.assertEqual(
            route["provider_path"],
            "components/apollo_main/core_overlay/build/ota_s200_firmware_ota.bin",
        )
        self.assertEqual(route["provider_size"], 3956672)
        self.assertEqual(
            route["provider_sha256"],
            "97c0f4191de23eb9a46ea25c963a53dff57f8084c422c33ee7f07e486eebd8c9",
        )
        self.assertEqual(route["toolchain_profile"], "apple-clang")
        self.assertEqual(route["toolchain_executable"], "/usr/bin/clang")
        self.assertEqual(route["source_owned_bytes"], 530980)
        self.assertEqual(route["source_owned_in_place_bytes"], 10928)
        self.assertEqual(route["opaque_base_bytes"], 3030368)
        self.assertEqual(route["generated_patch_site_bytes"], 395292)

    def test_summary_is_json_serializable(self) -> None:
        json.dumps(self.report, sort_keys=True)


if __name__ == "__main__":
    unittest.main()
