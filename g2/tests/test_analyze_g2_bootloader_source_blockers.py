import json
import unittest

from tools import analyze_g2_bootloader_source_blockers as analyzer


class G2BootloaderSourceBlockerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = analyzer.analyze()

    def test_bootloader_retained_complement_is_pinned(self) -> None:
        self.assertEqual(self.report["size"], 163840)
        self.assertEqual(self.report["release_blocking_bytes"], 81187)
        self.assertTrue(self.report["production_routed"])
        self.assertFalse(self.report["source_complete"])
        retained = self.report["retained_complement"]
        self.assertEqual(retained["retained_official_bytes"], 81187)
        self.assertEqual(
            retained["bytes_by_address_status"],
            {
                "generated_alignment": 16,
                "generated_source_entry_replacement": 16830,
                "official_blob": 81187,
                "source_compiled": 65807,
            },
        )
        self.assertEqual(
            retained["intervals_by_address_status"],
            {
                "generated_alignment": 9,
                "generated_source_entry_replacement": 238,
                "official_blob": 87,
                "source_compiled": 656,
            },
        )

    def test_bootloader_source_owned_progress_is_pinned(self) -> None:
        self.assertEqual(self.report["source_owned_in_place_bytes"], 46266)
        self.assertEqual(self.report["clkmgr_divider_source_functions"], 2)
        self.assertEqual(self.report["clkmgr_divider_source_stock_bytes"], 52)
        self.assertTrue(self.report["clkmgr_divider_production_routed"])

    def test_bootloader_source_build_route_is_authenticated(self) -> None:
        route = self.report["source_build_route"]
        self.assertEqual(route["manifest"], "manifests/g2-2.2.6.10-core-source.json")
        self.assertEqual(route["provider_kind"], "source_build")
        self.assertEqual(
            route["provider_path"],
            "components/bootloader/core_overlay/build/ota_s200_bootloader.bin",
        )
        self.assertEqual(route["provider_size"], 163840)
        self.assertEqual(
            route["provider_sha256"],
            "696a6bafaea197c8a6237a626bdee3b2742a1b83a39b2bd0a2f12c01c6c6b4f3",
        )
        self.assertEqual(route["toolchain_profile"], "apple-clang")
        self.assertEqual(route["toolchain_executable"], "/usr/bin/clang")
        self.assertEqual(route["source_owned_bytes"], 65807)
        self.assertEqual(route["source_owned_in_place_bytes"], 46266)
        self.assertEqual(route["opaque_base_bytes"], 81187)
        self.assertEqual(route["generated_patch_site_bytes"], 16830)
        self.assertEqual(route["hardware_operations"], [])

    def test_retained_official_frontier_is_pinned(self) -> None:
        frontier = self.report["retained_official_frontier"]
        self.assertEqual(frontier["interval_count"], 87)
        self.assertEqual(frontier["bytes"], 81187)
        self.assertEqual(
            frontier["bytes_by_family"],
            {
                "easylogger_replacement_frontier": 31870,
                "littlefs_replacement_frontier": 3146,
                "other_retained_official": 10310,
                "platform_services_source_in_place_frontier": 3600,
                "post_redirect_tail": 6821,
                "redirect_init_frontier": 18266,
                "spotmgr_source_in_place_frontier": 7174,
            },
        )
        self.assertEqual(
            [
                (row["file_offset"], row["size"], row["family"], row["name"])
                for row in frontier["largest_intervals"][:4]
            ],
            [
                (
                    3638,
                    18266,
                    "redirect_init_frontier",
                    "opaque_before_replace_bootloader_redirect_init",
                ),
                (
                    47202,
                    16566,
                    "easylogger_replacement_frontier",
                    "opaque_before_replace_bootloader_easylogger_channel_write_41f918",
                ),
                (
                    31672,
                    10896,
                    "easylogger_replacement_frontier",
                    "opaque_before_replace_bootloader_easylogger_mutex_create_41a648",
                ),
                (
                    141778,
                    6821,
                    "post_redirect_tail",
                    "opaque_after_source_redirects",
                ),
            ],
        )

    def test_summary_is_json_serializable(self) -> None:
        json.dumps(self.report, sort_keys=True)


if __name__ == "__main__":
    unittest.main()
