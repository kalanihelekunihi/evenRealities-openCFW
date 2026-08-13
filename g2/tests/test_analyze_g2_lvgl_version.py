#!/usr/bin/env python3
"""Guard the fail-closed G2 LVGL version/configuration recovery."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools" / "analyze_g2_lvgl_version.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_lvgl_version", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class LVGLVersionRecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.data = cls.analyzer._load()
        cls.report = cls.analyzer.audit(cls.data)

    def test_image_and_analysis_mode_are_pinned(self) -> None:
        self.assertEqual(self.report["component"], "LVGL 9.3.0-dev-compatible vendor stack")
        self.assertEqual(
            self.report["analysis_mode"],
            "read-only; no hardware or flash operation",
        )
        self.assertEqual(self.report["image"]["size"], 3_523_396)
        self.assertEqual(
            self.report["image"]["sha256"],
            "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863",
        )

    def test_narrowest_official_history_interval_is_pinned(self) -> None:
        version = self.report["version_recovery"]
        self.assertIsNone(version["exact_vendor_commit_or_tree"])
        self.assertIsNone(version["exact_released_tag"])
        self.assertEqual(
            version["classification"],
            "vendor fork of official LVGL 9.3.0-dev lineage",
        )
        self.assertEqual(
            version["narrowest_official_history_source_equivalence_interval"],
            {
                "first": "60d976c466e8619326edfbd193fd2a046c10113f",
                "last": "344c7c318047b7348e1be8572a9fd4260c251cfa",
                "first_date": "2025-03-25T12:18:02+01:00",
                "last_date": "2025-04-10T14:25:23+02:00",
            },
        )
        self.assertIn("137", version["lower_bound"])
        self.assertIn("66", version["upper_bound"])
        self.assertIn("deinitialization", version["why_interval_cannot_select_one_commit"])

    def test_release_tag_is_identified_but_provably_not_exact(self) -> None:
        upstream = self.report["upstream_provenance"]
        tag = upstream["release_reference"]
        self.assertEqual(tag["tag"], "v9.3.0")
        self.assertEqual(tag["annotated_tag_object"], "108e5aff3c90cc4d969331ed61aff2bbd365d430")
        self.assertEqual(tag["commit"], "c033a98afddd65aaafeebea625382a94020fe4a7")
        self.assertEqual(tag["tree"], "66bc30b9a8ecd144ba8b9ebfc984ac3028f55767")
        self.assertFalse(tag["tag_cryptographically_signed"])
        reasons = self.report["version_recovery"]["why_v9_3_0_tag_is_not_exact"]
        self.assertTrue(any("LV_EVENT_LAST=67" in item for item in reasons))
        self.assertTrue(any("lv_cache_lru_rb.c" in item for item in reasons))
        self.assertEqual(
            upstream["first_excluded_commit"]["commit"],
            "f35f0859eb477c79906cf531ed394306119097f8",
        )

    def test_decisive_version_and_init_order_discriminators(self) -> None:
        values = self.report["version_discriminators"]
        self.assertEqual(values["LV_STYLE_LAST_BUILT_IN_PROP"], 137)
        self.assertEqual(values["LV_EVENT_LAST"], 66)
        self.assertEqual(values["LV_LAYOUT_LAST"], 3)
        self.assertEqual(values["freetype_cache_glyph_count"], 64)
        self.assertTrue(values["freetype_initialized_before_draw"])
        targets = [item["target"] for item in self.report["lv_init_direct_branches"]]
        self.assertEqual(targets, self.analyzer.LV_INIT_CALLS)
        self.assertLess(targets.index(0x004B1B98), targets.index(0x0048438C))
        self.assertLess(targets.index(0x0048438C), targets.index(0x004C73D6))

    def test_effective_configuration_is_pinned(self) -> None:
        config = self.report["effective_configuration"]
        self.assertEqual(config["LV_COLOR_DEPTH"], 8)
        self.assertEqual(
            config["LV_COLOR_FORMAT_NATIVE"],
            {"ordinal": 6, "name": "LV_COLOR_FORMAT_L8", "bpp": 8},
        )
        self.assertEqual(
            config["ambiq_output_color_format"],
            {"ordinal": 13, "name": "LV_COLOR_FORMAT_A4", "bpp": 4},
        )
        self.assertEqual(config["LV_USE_OS"], "LV_OS_FREERTOS")
        for name in (
            "LV_USE_FREETYPE",
            "LV_USE_FLEX",
            "LV_USE_GRID",
            "LV_USE_FS_LITTLEFS",
            "LV_USE_BMP",
            "LV_USE_LOG",
            "LV_USE_ASSERT_NULL",
            "LV_USE_SPAN",
            "LV_USE_OBJ_ID_BUILTIN",
        ):
            self.assertTrue(config[name], name)
        self.assertTrue(config["built_in_bin_decoder"])
        self.assertEqual(config["LV_LOG_LEVEL"], "LV_LOG_LEVEL_WARN")
        self.assertEqual(config["LV_BIG_ENDIAN_SYSTEM"], 0)
        self.assertFalse(config["LV_DRAW_SW_COMPLEX"])
        self.assertEqual(config["LV_USE_STDLIB_MALLOC"], "LV_STDLIB_CUSTOM")
        self.assertEqual(config["enum_abi"], "short enums (-fshort-enums-compatible)")
        self.assertEqual(
            config["display"],
            {"width": 576, "height": 288, "output_allocation": 0x14400},
        )
        self.assertIn("unique mapping", config["notes"][0])

    def test_vendor_configuration_abi_is_pinned(self) -> None:
        abi = self.report["abi"]
        self.assertEqual(abi["sizeof_lv_global_t"], 0x1EC)
        self.assertEqual(abi["sizeof_lv_display_t"], 0x31C)
        self.assertEqual(abi["sizeof_lv_indev_t"], 0xDC)
        self.assertEqual(abi["sizeof_lv_draw_buf_t"], 0x1C)
        self.assertEqual(abi["pointer_size"], 4)
        self.assertEqual(abi["enum_abi"], "short enums")
        self.assertEqual(abi["draw_buffer_handler_size"], 0x20)
        self.assertEqual(abi["draw_buffer_handler_offsets"], [0xC8, 0xE8, 0x108])
        self.assertEqual(
            abi["lv_async_info_t"],
            {"size": 8, "fields": ["callback@0", "user_data@4"]},
        )
        self.assertIn("not make an unconfigured tag drop-in safe", abi["qualification"])

    def test_complete_source_path_inventory_separates_vendor_layers(self) -> None:
        inventory = self.report["path_inventory"]
        self.assertEqual(inventory["total_unique_paths"], 78)
        self.assertEqual(inventory["class_counts"], self.analyzer.PATH_CLASS_COUNTS)
        relative = {item["relative"] for item in inventory["paths"]}
        self.assertTrue(self.analyzer.REQUIRED_RELATIVE_PATHS <= relative)
        self.assertIn(r"LVGL\src\misc\cache\lv_cache_lru_rb.c", relative)
        self.assertIn(r"LVGL\src\draw\ambiq\lv_draw_ambiq.c", relative)
        self.assertIn(r"lvgl_ambiq_porting\lv_ambiq_display.c", relative)
        self.assertIn(r"lvgl_ambiq_demo\lvgl_ttf\src\am_ftsystem.c", relative)

        boundary = self.report["boundary_classification"]
        self.assertIn("FreeType 2.9.1", boundary["lvgl_freetype_wrappers"])
        self.assertIn("absent from official LVGL", boundary["ambiq_backend"])
        self.assertIn("1e774257", boundary["ambiq_backend"])
        ambiq = self.report["ambiq_backend_provenance"]
        self.assertEqual(ambiq["subtree_git_tree_sha1"], "1e774257495fa43177e04fc5c8a42a77c2d7d619")
        self.assertEqual(ambiq["canonical_default_branch_commit"], "5be8e0ae5077aa3880aba8a322b1487d6bc73c07")
        nema = self.report["nema_dependency_provenance"]
        self.assertEqual(nema["ambiqsuite_revision"], "release_sdk5p1p0-634f7c117b")
        self.assertEqual(nema["nemagfx_version"], "1.4.12")
        self.assertEqual(nema["nemavg_version"], "1.1.8")
        self.assertEqual(
            nema["public_reproduction_commit"],
            "b853fded7e545f005727e13bf2ce83018c7e242d",
        )
        self.assertEqual(nema["command_list_geometry"], {"bytes": 102400, "sectors": 100, "sector_bytes": 1024})
        first_party = {item["path"] for item in boundary["first_party_path_pins"]}
        self.assertTrue(any(r"platform\display_mgr" in path for path in first_party))
        self.assertTrue(any(r"platform\input" in path for path in first_party))
        self.assertTrue(any(r"app\gui\common\lvgl_font_manager.c" in path for path in first_party))

    def test_pinned_core_spans_and_official_blobs_are_complete(self) -> None:
        spans = self.report["pinned_spans"]
        self.assertEqual(set(spans), set(self.analyzer.PINNED_SPANS))
        self.assertEqual(spans["lv_global_init"]["size"], 124)
        self.assertEqual(spans["lv_init"]["size"], 222)
        self.assertEqual(spans["lv_display_create"]["size"], 602)
        self.assertEqual(spans["lv_async_call"]["size"], 62)
        self.assertEqual(spans["lv_async_call_cancel"]["size"], 88)
        self.assertEqual(spans["lv_async_timer_cb"]["size"], 26)

        stable = self.report["upstream_provenance"]["stable_interval_blobs"]
        self.assertEqual(stable["src/misc/lv_async.c"], "b2e718dd3a3aefe274b6b962714c4e010bbd7f91")
        self.assertEqual(stable["src/misc/lv_style.h"], "2da6cd1f8c903aebc142b473f4b1f846deb2073f")
        self.assertEqual(stable["src/misc/lv_event.h"], "ca52d18e454b745ea5302d32e5f49152de9e9643")
        self.assertEqual(stable["src/misc/cache/lv_cache_lru_rb.c"], "be651dda9c22343444662acd204ec8a5ca37d516")
        self.assertEqual(stable["src/display/lv_display.c"], "695d38b2652decc2362b283dd69ee08b8b4f7582")
        color = self.report["upstream_provenance"]["endpoint_variant_blobs"]["src/misc/lv_color.h"]
        self.assertEqual(color["floor"], "c5ea01f82feb95f10e9c61788b42417477a1a51b")
        self.assertEqual(color["ceiling"], "1a160b4a56b8a7bc01b59a20b72ae35f5fff518c")

    def test_mit_license_identity_is_pinned(self) -> None:
        license_info = self.report["upstream_provenance"]["license"]
        self.assertEqual(license_info["spdx"], "MIT")
        self.assertEqual(license_info["git_blob_sha1"], "690d2dfd7e97ca8e06535a496761c5e81aece439")
        self.assertEqual(license_info["size"], 1072)
        self.assertEqual(
            license_info["sha256"],
            "27a80bd36832ab42d35ad60c08b2b230a807a9bc0d58e94ec1531543dc49cbe8",
        )

    def test_mutated_image_is_rejected(self) -> None:
        runs = [
            self.analyzer.PINNED_SPANS["lv_global_init"][0],
            self.analyzer.PINNED_SPANS["lv_init"][0] + 0x48,
            self.analyzer.PINNED_SPANS["ambiq_display_setup"][0] + 0x10,
            self.analyzer.PINNED_SPANS["lv_async_call_cancel"][0] + 0x20,
            next(iter(self.analyzer.FIRST_PARTY_PATHS)),
        ]
        for run in runs:
            with self.subTest(run=f"0x{run:08x}"):
                mutated = bytearray(self.data)
                mutated[run - self.analyzer.LOAD_BASE] ^= 1
                with self.assertRaises(self.analyzer.AuditError):
                    self.analyzer.audit(bytes(mutated))

    def test_cli_text_and_json_modes(self) -> None:
        text = subprocess.run(
            [sys.executable, str(ANALYZER)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        self.assertIn("60d976c4..344c7c31", text)
        self.assertIn("exact v9.3.0 release tag: excluded", text)
        self.assertIn("78 total", text)
        parsed = json.loads(
            subprocess.run(
                [sys.executable, str(ANALYZER), "--json"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            ).stdout
        )
        self.assertEqual(parsed["version_discriminators"]["LV_EVENT_LAST"], 66)
        self.assertEqual(parsed["path_inventory"]["total_unique_paths"], 78)


if __name__ == "__main__":
    unittest.main()
