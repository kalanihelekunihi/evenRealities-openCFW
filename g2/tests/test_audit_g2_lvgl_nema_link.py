#!/usr/bin/env python3
"""Fail-closed target-link gates for the G2 LVGL/Ambiq/Nema boundary."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/audit_g2_lvgl_nema_link.py"
MANIFEST = ROOT / "tools/manifests/g2-lvgl-nema-link-admission.json"
SDK_ROOT = Path(
    "/Users/kalani/Repo/evenrealitiesg2-swiftsdk/openCFW/sdks/AmbiqSuite_v5"
)
EVB_ROOT = Path(
    "/Users/kalani/Repo/evenrealitiesg2-swiftsdk/openCFW/sdks/Apollo510-EVB"
)


def load_analyzer():
    spec = importlib.util.spec_from_file_location("audit_g2_lvgl_nema_link", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class LVGLNemaAtomicLinkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.audit()

    def test_checked_manifest_and_maximal_boundary_are_exact(self) -> None:
        self.assertEqual(json.loads(MANIFEST.read_text(encoding="utf-8")), self.report)
        self.assertEqual(self.report["local_target_compile"]["object_count"], 15)
        self.assertEqual(self.report["direct_nema_requirement_count"], 96)
        self.assertEqual(self.report["missing_provider_count"], 11)
        self.assertEqual(self.report["missing_nema_hal_provider_count"], 0)
        maximal = self.report["maximal_scoped_candidate_closure"]
        self.assertFalse(maximal["performed"])
        self.assertEqual(maximal["expected_residual_symbol_count"], 11)
        self.assertEqual(
            maximal["expected_residual_symbol_digest"],
            "f9d7f5b3fc8db9a19441ec0c4991ac9161c0ae46583e56c2a2298f2794732744",
        )
        self.assertEqual(maximal["expected_remaining_nema_hal_symbols"], [])
        self.assertEqual(maximal["expected_section_gc_root_count"], 39)
        self.assertEqual(
            maximal["expected_section_gc_root_digest"],
            "81c9819050afa8b9e07fd08ee11f1023bcf577b7f466fc2577d2b597bcde91f3",
        )
        self.assertEqual(maximal["expected_section_gc_elided_imports"], [
            "utf8_codepoint_size",
        ])
        helper = self.report["local_buffer_helper_provider"]
        self.assertEqual(helper["defined_symbols"], [
            "nema_buffer_invalidate", "nema_buffer_is_within_pool",
        ])
        self.assertEqual(helper["undefined_symbols"], [
            "am_hal_cachectrl_dcache_invalidate",
        ])
        platform = self.report["local_apollo_hal_provider"]
        self.assertEqual(platform["artifact"], {
            "path": "lvgl-ambiq-apollo-hal-provider.o",
            "size": 11_320,
            "sha256": "04504e7e026eb53a08a187e037269d0f42a2e818842fc5320710c2a5952a06b7",
        })
        self.assertEqual(platform["required_exports"], [
            "am_hal_cachectrl_dcache_clean",
            "am_hal_cachectrl_dcache_invalidate",
            "am_hal_pwrctrl_periph_disable",
            "am_hal_pwrctrl_periph_enable",
            "am_hal_pwrctrl_periph_enabled",
        ])
        self.assertEqual(platform["elf_undefined_symbols"], [])
        self.assertEqual(platform["fixed_address_import_count"], 11)
        self.assertTrue(platform["source_admitted"])
        self.assertFalse(platform["production_overlay_registered"])
        self.assertFalse(platform["hardware_qualified"])
        freertos = self.report["local_freertos_queue_provider"]
        self.assertEqual(freertos["artifact"], {
            "path": "lvgl-ambiq-freertos-queue-provider.o",
            "size": 6_404,
            "sha256": "926b0597a2d78ea441151b2c21cfc813be29bb246606b2a6b0c5d84e5b175608",
        })
        self.assertEqual(freertos["required_exports"], [
            "xQueueGenericCreate", "xQueueGiveFromISR", "xQueueSemaphoreTake",
        ])
        self.assertEqual(freertos["elf_undefined_symbols"], [])
        self.assertEqual(freertos["fixed_address_import_count"], 27)
        self.assertTrue(freertos["source_admitted"])
        self.assertFalse(freertos["production_overlay_registered"])
        self.assertFalse(freertos["hardware_qualified"])
        lvgl_core = self.report["local_lvgl_core_provider"]
        self.assertEqual(lvgl_core["artifact"], {
            "path": "lvgl-ambiq-lvgl-core-provider.o",
            "size": 7_452,
            "sha256": "9342103b5ae256c72221216d754d21020a92218fbd3024d7e17303ed6ef7111a",
        })
        self.assertEqual(len(lvgl_core["required_exports"]), 14)
        self.assertEqual(lvgl_core["elf_undefined_symbols"], [])
        self.assertEqual(lvgl_core["fixed_address_import_count"], 0)
        self.assertTrue(lvgl_core["source_admitted"])
        self.assertFalse(lvgl_core["production_overlay_registered"])
        self.assertFalse(lvgl_core["hardware_qualified"])
        lvgl_stateless = self.report["local_lvgl_stateless_provider"]
        self.assertEqual(lvgl_stateless["artifact"], {
            "path": "lvgl-ambiq-lvgl-stateless-provider.o",
            "size": 6_692,
            "sha256": "bcebd4a63cc1366be7ab0006fdab5f31e6645a3583c4aa9a0d72d9ea9ce932a4",
        })
        self.assertEqual(len(lvgl_stateless["required_exports"]), 11)
        self.assertEqual(lvgl_stateless["elf_undefined_symbols"], [])
        self.assertEqual(lvgl_stateless["fixed_address_import_count"], 0)
        self.assertEqual(lvgl_stateless["closed_consumer_relocation_count"], 28)
        self.assertTrue(lvgl_stateless["source_admitted"])
        self.assertFalse(lvgl_stateless["production_overlay_registered"])
        self.assertFalse(lvgl_stateless["hardware_qualified"])
        target_runtime = self.report["local_target_runtime_provider"]
        self.assertEqual(target_runtime["artifact"], {
            "path": "lvgl-ambiq-target-runtime-provider.o",
            "size": 2_736,
            "sha256": "c009f816e4d59547783e88272d77bf9fccaf765f5d66d6339fc3296ca4256bf7",
        })
        self.assertEqual(len(target_runtime["required_exports"]), 5)
        self.assertEqual(target_runtime["elf_undefined_symbols"], [])
        self.assertEqual(target_runtime["fixed_address_import_count"], 0)
        self.assertEqual(target_runtime["closed_consumer_relocation_count"], 21)
        self.assertTrue(target_runtime["source_admitted"])
        self.assertFalse(target_runtime["production_overlay_registered"])
        self.assertFalse(target_runtime["hardware_qualified"])
        math_provider = self.report["local_math_provider"]
        self.assertEqual(math_provider["artifact"], {
            "path": "lvgl-ambiq-math-provider.o",
            "size": 6_576,
            "sha256": "123f1163b67fa953c3a77aa9ce3da7652fa6aae1001dc206b9f742f75f14a1af",
        })
        self.assertEqual(len(math_provider["required_exports"]), 5)
        self.assertEqual(math_provider["elf_undefined_symbols"], [])
        self.assertEqual(math_provider["fixed_address_import_count"], 0)
        self.assertEqual(math_provider["closed_consumer_relocation_count"], 46)
        self.assertTrue(math_provider["source_admitted"])
        self.assertFalse(math_provider["production_overlay_registered"])
        self.assertFalse(math_provider["hardware_qualified"])
        math_dp_provider = self.report["local_math_dp_provider"]
        self.assertEqual(math_dp_provider["artifact"], {
            "path": "lvgl-ambiq-math-dp-provider.o",
            "size": 13_144,
            "sha256": "3b67eea354a8f12f48faed3177b9d170fa7c8191ced9e30803cbe6b31b2e8c8a",
        })
        self.assertEqual(len(math_dp_provider["required_exports"]), 4)
        self.assertEqual(math_dp_provider["elf_undefined_symbols"], [])
        self.assertEqual(math_dp_provider["fixed_address_import_count"], 0)
        self.assertEqual(math_dp_provider["closed_consumer_relocation_count"], 35)
        self.assertTrue(math_dp_provider["source_admitted"])
        self.assertFalse(math_dp_provider["production_overlay_registered"])
        self.assertFalse(math_dp_provider["hardware_qualified"])
        mutex_provider = self.report["local_lvgl_mutex_provider"]
        self.assertEqual(mutex_provider["artifact"], {
            "path": "lvgl-ambiq-lvgl-mutex-provider.o",
            "size": 2_168,
            "sha256": "5067d94d102f8f6ce7090534a482657761ddee527f796db2cb330bedb36baf3a",
        })
        self.assertEqual(len(mutex_provider["required_exports"]), 4)
        self.assertEqual(mutex_provider["elf_undefined_symbols"], [])
        self.assertEqual(mutex_provider["fixed_address_import_count"], 6)
        self.assertEqual(mutex_provider["closed_consumer_relocation_count"], 4)
        self.assertTrue(mutex_provider["source_admitted"])
        self.assertFalse(mutex_provider["production_overlay_registered"])
        self.assertFalse(mutex_provider["hardware_qualified"])
        heap_array = self.report["local_lvgl_heap_array_provider"]
        self.assertEqual(heap_array["artifact"], {
            "path": "lvgl-ambiq-lvgl-heap-array-provider.o",
            "size": 3_060,
            "sha256": "e37759628d884e20f3c788d7b16e21997a667fddd8a6271e2cdd818a74661458",
        })
        self.assertEqual(len(heap_array["required_exports"]), 5)
        self.assertEqual(heap_array["elf_undefined_symbols"], [])
        self.assertEqual(heap_array["fixed_address_import_count"], 3)
        self.assertEqual(heap_array["closed_consumer_relocation_count"], 41)
        self.assertTrue(heap_array["source_admitted"])
        self.assertFalse(heap_array["production_overlay_registered"])
        self.assertFalse(heap_array["hardware_qualified"])
        draw_buf_lifecycle = self.report["local_lvgl_draw_buf_lifecycle_provider"]
        self.assertEqual(draw_buf_lifecycle["artifact"], {
            "path": "lvgl-ambiq-lvgl-draw-buf-lifecycle-provider.o",
            "size": 1_192,
            "sha256": "4b633e5f8f0b2fe765678d8525317aa4c8df3e10d4c22a5e216baeb6393888ca",
        })
        self.assertEqual(draw_buf_lifecycle["elf_undefined_symbols"], ["lv_free"])
        self.assertEqual(draw_buf_lifecycle["aggregate_elf_undefined_symbols"], [])
        self.assertEqual(draw_buf_lifecycle["fixed_address_import_count"], 0)
        self.assertEqual(draw_buf_lifecycle["closed_consumer_relocation_count"], 4)
        self.assertTrue(draw_buf_lifecycle["source_admitted"])
        self.assertFalse(draw_buf_lifecycle["production_overlay_registered"])
        self.assertFalse(draw_buf_lifecycle["hardware_qualified"])
        global_storage = self.report["local_lvgl_global_storage_provider"]
        self.assertEqual(global_storage["artifact"], {
            "path": "lvgl-ambiq-lvgl-global-storage-provider.o",
            "size": 796,
            "sha256": "a11c7c766758ae759bd4f0fc198246d3eab4425cb1a9b57b5d12905a6687966a",
        })
        self.assertEqual(global_storage["symbol_type"], "OBJECT/BSS")
        self.assertEqual(global_storage["symbol_size"], 0x1EC)
        self.assertEqual(global_storage["elf_undefined_symbols"], [])
        self.assertEqual(global_storage["closed_consumer_relocation_count"], 2)
        self.assertTrue(global_storage["source_admitted"])
        self.assertFalse(global_storage["production_overlay_registered"])
        self.assertFalse(global_storage["hardware_qualified"])
        freetype_event = self.report["local_lvgl_freetype_event_provider"]
        self.assertEqual(freetype_event["artifact"], {
            "path": "lvgl-ambiq-lvgl-freetype-event-provider.o",
            "size": 1_208,
            "sha256": "f4d90b85f22b784d3922cc16b7cb58c5f3df8c1c1b937e2a44332498eb07774e",
        })
        self.assertEqual(freetype_event["elf_undefined_symbols"], ["lv_global"])
        self.assertEqual(freetype_event["aggregate_elf_undefined_symbols"], [])
        self.assertEqual(freetype_event["closed_consumer_relocation_count"], 1)
        self.assertTrue(freetype_event["source_admitted"])
        self.assertFalse(freetype_event["production_overlay_registered"])
        self.assertFalse(freetype_event["hardware_qualified"])
        draw_buf_shape = self.report["local_lvgl_draw_buf_shape_provider"]
        self.assertEqual(draw_buf_shape["artifact"], {
            "path": "lvgl-ambiq-lvgl-draw-buf-shape-provider.o",
            "size": 2_296,
            "sha256": "2cf520c1f7d814e9594f93520b638d15e107128c1882fadabff3342eb5448933",
        })
        self.assertEqual(draw_buf_shape["elf_undefined_symbols"], [
            "lv_free", "lv_global", "lv_malloc_zeroed",
        ])
        self.assertEqual(draw_buf_shape["aggregate_elf_undefined_symbols"], [])
        self.assertEqual(draw_buf_shape["closed_consumer_relocation_count"], 4)
        self.assertTrue(draw_buf_shape["source_admitted"])
        self.assertFalse(draw_buf_shape["production_overlay_registered"])
        self.assertFalse(draw_buf_shape["hardware_qualified"])
        font_fmt = self.report["local_lvgl_font_fmt_provider"]
        self.assertEqual(font_fmt["artifact"], {
            "path": "lvgl-ambiq-lvgl-font-fmt-provider.o",
            "size": 4_688,
            "sha256": "9d4333cf6277960f46d5ce5e0cb8ef0b49e203861bb275afbcf7e409a789ef66",
        })
        self.assertEqual(font_fmt["elf_undefined_symbols"], [])
        self.assertEqual(font_fmt["closed_consumer_relocation_count"], 2)
        self.assertTrue(font_fmt["source_admitted"])
        self.assertFalse(font_fmt["production_overlay_registered"])
        self.assertFalse(font_fmt["hardware_qualified"])
        vector_destroy = self.report["local_lvgl_vector_destroy_provider"]
        self.assertEqual(vector_destroy["artifact"], {
            "path": "lvgl-ambiq-lvgl-vector-destroy-provider.o",
            "size": 1_388,
            "sha256": "ed7735e3535a5f1e13760986a598be99b8703335a5acae36279acf4a0a56e72c",
        })
        self.assertEqual(vector_destroy["elf_undefined_symbols"], [
            "lv_array_deinit", "lv_free",
        ])
        self.assertEqual(vector_destroy["aggregate_elf_undefined_symbols"], [])
        self.assertEqual(vector_destroy["closed_consumer_relocation_count"], 1)
        self.assertTrue(vector_destroy["source_admitted"])
        self.assertFalse(vector_destroy["production_overlay_registered"])
        self.assertFalse(vector_destroy["hardware_qualified"])
        draw_unit = self.report["local_lvgl_draw_unit_provider"]
        self.assertEqual(draw_unit["artifact"], {
            "path": "lvgl-ambiq-lvgl-draw-unit-provider.o",
            "size": 1_260,
            "sha256": "67c6f571e7d904438deccaa9de331449a59cecdf9d26ab78c618dbaf96489206",
        })
        self.assertEqual(draw_unit["elf_undefined_symbols"], [
            "lv_global", "lv_malloc_zeroed",
        ])
        self.assertEqual(draw_unit["aggregate_elf_undefined_symbols"], [])
        self.assertEqual(draw_unit["closed_consumer_relocation_count"], 1)
        self.assertTrue(draw_unit["source_admitted"])
        self.assertFalse(draw_unit["production_overlay_registered"])
        self.assertFalse(draw_unit["hardware_qualified"])
        draw_dispatch = self.report["local_lvgl_draw_dispatch_provider"]
        self.assertEqual(draw_dispatch["artifact"], {
            "path": "lvgl-ambiq-lvgl-draw-dispatch-provider.o",
            "size": 1_248,
            "sha256": "5add8d9b27247a4d2e059cbf5783f6f9961de975adb4509e594641fef235ee62",
        })
        self.assertEqual(draw_dispatch["elf_undefined_symbols"], [
            "lv_global", "lv_thread_sync_signal",
        ])
        self.assertEqual(draw_dispatch["aggregate_elf_undefined_symbols"], [
            "lv_thread_sync_signal",
        ])
        self.assertTrue(draw_dispatch["dependency_admitted"])
        self.assertEqual(draw_dispatch["closed_consumer_relocation_count"], 1)
        self.assertTrue(draw_dispatch["source_admitted"])
        self.assertFalse(draw_dispatch["production_overlay_registered"])
        self.assertFalse(draw_dispatch["hardware_qualified"])
        sync_signal = self.report["local_lvgl_thread_sync_signal_provider"]
        self.assertEqual(sync_signal["artifact"], {
            "path": "lvgl-ambiq-lvgl-thread-sync-signal-provider.o",
            "size": 1_140,
            "sha256": "48251997ef18222cd29f8397f049ad5ca3c20b95b789d8917bbb03632db69269",
        })
        self.assertEqual(sync_signal["elf_undefined_symbols"], [])
        self.assertEqual(sync_signal["aggregate_elf_undefined_symbols"], [])
        self.assertEqual(sync_signal["fixed_address_import_count"], 3)
        self.assertEqual(sync_signal["closed_consumer_relocation_count"], 2)
        self.assertEqual(sync_signal["closed_transitive_relocation_count"], 2)
        self.assertTrue(sync_signal["source_admitted"])
        self.assertFalse(sync_signal["production_overlay_registered"])
        self.assertFalse(sync_signal["hardware_qualified"])
        self.assertFalse(self.report["production_admission"]["ready"])
        self.assertFalse(self.report["production_admission"]["hardware_qualified"])

    def test_direct_provider_and_missing_consumer_ledgers_are_exhaustive(self) -> None:
        direct = self.report["direct_nema_requirement_ledger"]
        self.assertEqual(
            sum(row["api_family"] in {"nemagfx", "nemavg"} for row in direct), 82
        )
        self.assertEqual(sum(row["api_family"] == "ambiq-gpu-patch" for row in direct), 6)
        self.assertEqual(sum(row["api_family"] == "apollo510-nema-hal" for row in direct), 8)
        for row in direct:
            self.assertTrue(row["consumer_objects"])
            self.assertGreater(
                sum(owner["relocation_count"] for owner in row["consumer_objects"]), 0
            )
            self.assertFalse(row["provider_admitted"])

        missing = {row["symbol"]: row for row in self.report["missing_provider_ledger"]}
        self.assertEqual(set(missing), set(self.analyzer.EXPECTED_MAXIMAL_RESIDUAL_SYMBOLS))
        for row in missing.values():
            self.assertTrue(row["consumer_objects"])
            self.assertTrue(row["api_family"])
            self.assertTrue(row["exact_unavailable_input"])
            self.assertFalse(row["provider_admitted"])
        self.assertNotIn("nema_buffer_invalidate", missing)
        self.assertNotIn("nema_buffer_is_within_pool", missing)
        self.assertNotIn("utf8_codepoint_size", missing)
        self.assertFalse(any(symbol.startswith("am_hal_") for symbol in missing))
        self.assertFalse(any(symbol.startswith("xQueue") for symbol in missing))
        self.assertFalse(set(self.analyzer.LVGL_CORE_PROVIDER_SYMBOLS) & set(missing))
        self.assertFalse(set(self.analyzer.LVGL_STATELESS_PROVIDER_SYMBOLS) & set(missing))
        self.assertFalse(set(self.analyzer.TARGET_RUNTIME_PROVIDER_SYMBOLS) & set(missing))
        self.assertFalse(set(self.analyzer.MATH_PROVIDER_SYMBOLS) & set(missing))
        self.assertFalse(set(self.analyzer.LVGL_MUTEX_PROVIDER_SYMBOLS) & set(missing))
        self.assertFalse(set(self.analyzer.LVGL_HEAP_ARRAY_PROVIDER_SYMBOLS) & set(missing))
        self.assertFalse(
            set(self.analyzer.LVGL_DRAW_BUF_LIFECYCLE_PROVIDER_SYMBOLS) & set(missing)
        )
        self.assertFalse(
            set(self.analyzer.LVGL_GLOBAL_STORAGE_PROVIDER_SYMBOLS) & set(missing)
        )
        self.assertFalse(
            set(self.analyzer.LVGL_FREETYPE_EVENT_PROVIDER_SYMBOLS) & set(missing)
        )
        self.assertFalse(
            set(self.analyzer.LVGL_DRAW_BUF_SHAPE_PROVIDER_SYMBOLS) & set(missing)
        )

    def test_workspace_candidates_are_not_misrepresented_as_providers(self) -> None:
        inventory = self.report["workspace_implementation_inventory"]
        self.assertEqual(inventory["files"], 20)
        self.assertEqual(inventory["bytes"], 57_754)
        self.assertEqual(
            inventory["digest"],
            "2f1b92bed322b40987cd96850afbbde963cc7d33af49dd39080249a161d49fbd",
        )
        self.assertTrue(all(row["license"] == "MIT" for row in inventory["candidate_files"]))
        self.assertFalse(any(row["production_provider"] for row in inventory["candidate_files"]))
        scoped = self.report["scoped_source_inventory"]
        self.assertFalse(scoped["broad_home_scan_performed"])
        self.assertFalse(scoped["current_repository_implementation_archives"])

    def test_static_ledger_omission_fails_closed(self) -> None:
        original = self.analyzer.EXPECTED_MAXIMAL_RESIDUAL_SYMBOLS
        try:
            self.analyzer.EXPECTED_MAXIMAL_RESIDUAL_SYMBOLS = original[:-1]
            with self.assertRaisesRegex(self.analyzer.AuditError, "omission"):
                self.analyzer._validate_static_boundary()
        finally:
            self.analyzer.EXPECTED_MAXIMAL_RESIDUAL_SYMBOLS = original

    def test_scoped_evb_input_mutation_fails_closed(self) -> None:
        if not EVB_ROOT.is_dir():
            self.skipTest("precise scoped sibling EVB root is unavailable")
        with tempfile.TemporaryDirectory(prefix="opencfw-nema-evb-mutate-") as temporary:
            root = Path(temporary)
            for name in ("source", "sys_defs", "freertos_config", "makefile"):
                relative = Path(self.analyzer.EVB_EVIDENCE[name]["path"])
                (root / relative).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(EVB_ROOT / relative, root / relative)
            source = root / self.analyzer.EVB_EVIDENCE["source"]["path"]
            source.write_bytes(source.read_bytes() + b"\n")
            with self.assertRaisesRegex(self.analyzer.AuditError, "identity changed"):
                self.analyzer._audit_evb_inputs(root)

    def test_scoped_external_sources_reproduce_public_and_evb_links(self) -> None:
        if not SDK_ROOT.is_dir() or not EVB_ROOT.is_dir():
            self.skipTest("precise scoped sibling SDK roots are unavailable")
        with tempfile.TemporaryDirectory(prefix="opencfw-nema-link-") as temporary:
            report = self.analyzer.audit(
                sdk_root=SDK_ROOT, evb_root=EVB_ROOT, output_dir=Path(temporary)
            )
        public = report["maximal_public_archive_closure"]
        self.assertTrue(public["performed"])
        self.assertEqual(public["direct_requirements_resolved"], 88)
        self.assertEqual(public["residual_symbol_count"], 89)
        self.assertEqual(public["artifact"], {
            "path": "lvgl-ambiq-nema-public-partial.o",
            "size": 1_377_972,
            "sha256": "a713fbf4eaf8554ec4e31b431dbc833831e9c93a92ad8eb31bcc8ee25cba7346",
        })
        maximal = report["maximal_scoped_candidate_closure"]
        self.assertTrue(maximal["performed"])
        self.assertEqual(maximal["residual_symbol_count"], 11)
        self.assertEqual(maximal["remaining_nema_hal_symbols"], [])
        self.assertEqual(maximal["artifact"], {
            "path": "lvgl-ambiq-nema-evb-maximal-partial.o",
            "size": 1_370_696,
            "sha256": "d1c96688dfd7e7c845a9b4e0bcb2610bc239d881c89aa79e09faefc8d0bcd8cf",
        })
        self.assertEqual(maximal["compile"]["warning_count"], 0)
        section_gc = maximal["section_gc"]
        self.assertTrue(section_gc["enabled"])
        self.assertEqual(section_gc["root_symbol_count"], 39)
        self.assertEqual(
            section_gc["root_symbol_digest"],
            "81c9819050afa8b9e07fd08ee11f1023bcf577b7f466fc2577d2b597bcde91f3",
        )
        self.assertEqual(section_gc["direct_nema_symbols_retained"], 96)
        self.assertEqual(section_gc["elided_unreferenced_exports"], [
            "lv_ambiq_get_glyph",
        ])
        self.assertEqual(section_gc["elided_unreferenced_imports"], [
            "utf8_codepoint_size",
        ])
        self.assertFalse(maximal["production_admitted"])

    def test_cli_default_mode_is_offline_and_fail_closed(self) -> None:
        parsed = json.loads(subprocess.run(
            [sys.executable, str(ANALYZER), "--json"], cwd=ROOT,
            check=True, capture_output=True, text=True,
        ).stdout)
        self.assertEqual(parsed, self.report)
        self.assertIn("no hardware or flash operation", parsed["analysis_mode"])


if __name__ == "__main__":
    unittest.main()
