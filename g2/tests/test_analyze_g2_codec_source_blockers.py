import json
import unittest

from tools import analyze_g2_codec_source_blockers as analyzer


class G2CodecSourceBlockerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = analyzer.analyze()

    def test_codec_external_provider_blockers_are_pinned(self) -> None:
        self.assertEqual(self.report["size"], 326092)
        self.assertEqual(self.report["release_blocking_bytes"], 326000)
        self.assertFalse(self.report["production_routed"])
        self.assertFalse(self.report["source_complete"])
        self.assertEqual(self.report["typed_external_spans"], 11)
        self.assertEqual(
            self.report["external_provider"]["bytes_by_class"],
            {
                "opaque_executable": 190912,
                "opaque_npu_commands": 9164,
                "opaque_runtime_data": 5124,
                "proprietary_model_data": 120800,
            },
        )

    def test_codec_does_not_claim_open_provider_availability(self) -> None:
        provider = self.report["external_provider"]
        self.assertFalse(provider["open_source_available"])
        self.assertEqual(provider["payload_redistribution_authority"], "unresolved")

    def test_codec_source_only_macos_route_is_authenticated(self) -> None:
        route = self.report["source_only_macos_route"]
        self.assertEqual(route["manifest"], "manifests/g2-2.2.6.10-source-only.json")
        self.assertEqual(route["provider_kind"], "source_build")
        self.assertEqual(
            route["provider_path"],
            "build/gx8002-source-candidate/firmware_codec.hybrid-candidate.bin",
        )
        self.assertEqual(route["provider_size"], 326092)
        self.assertEqual(
            route["provider_sha256"],
            "ea1228240563deb21e2093793c50295bfe76e9a0c12cd77963ae581d7c270956",
        )
        self.assertEqual(route["toolchain_profile"], "apple-clang")
        self.assertFalse(route["source_only"])
        self.assertFalse(route["hardware_qualified"])
        self.assertEqual(route["source_replacement_occurrences"], 754)
        self.assertEqual(route["byte_ownership"]["retained_stock"], 262745)
        self.assertEqual(route["byte_ownership"]["compiled_c"], 43850)

    def test_codec_typed_external_span_map_is_exact(self) -> None:
        span_map = self.report["typed_external_span_map"]
        self.assertEqual(span_map["span_count"], 11)
        self.assertEqual(span_map["bytes"], 326000)
        self.assertEqual(
            span_map["bytes_by_class"],
            self.report["external_provider"]["bytes_by_class"],
        )
        self.assertEqual(
            [span["region"] for span in span_map["spans"]],
            [
                "boot_stage1",
                "boot_stage2",
                "image_a_stage1",
                "image_a_xip_text",
                "image_a_sram_text",
                "image_a_sram_data",
                "image_a_kws_command",
                "image_a_kws_weights",
                "image_b_stage1",
                "image_b_sram_text",
                "image_b_sram_data",
            ],
        )
        self.assertEqual(
            [
                (span["file_offset"], span["size"], span["byte_class"])
                for span in span_map["spans"]
            ],
            [
                (80, 10240, "opaque_executable"),
                (10320, 27964, "opaque_executable"),
                (38284, 12288, "opaque_executable"),
                (50576, 36484, "opaque_executable"),
                (87060, 12516, "opaque_executable"),
                (99580, 2196, "opaque_runtime_data"),
                (101776, 9164, "opaque_npu_commands"),
                (110940, 120800, "proprietary_model_data"),
                (231740, 12288, "opaque_executable"),
                (244032, 79132, "opaque_executable"),
                (323164, 2928, "opaque_runtime_data"),
            ],
        )
        self.assertTrue(all(
            span["payload_redistribution"] == "unresolved" and
            span["production_route"] == "none"
            for span in span_map["spans"]
        ))

    def test_summary_is_json_serializable(self) -> None:
        json.dumps(self.report, sort_keys=True)


if __name__ == "__main__":
    unittest.main()
