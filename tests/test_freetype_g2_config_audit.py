#!/usr/bin/env python3
"""Focused gates for the production-excluded G2 FreeType configuration audit."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "freetype_g2_config_audit.py"
IMAGE = ROOT / "blobs" / "official" / "g2-2.2.6.10" / "ota_s200_firmware_ota.bin"
EXPECTED_TOOL_SIZE = 25_281
EXPECTED_TOOL_SHA256 = "49bfb2fe29472fe101c709a740d3cec847fcec66f94f1d26ef1367f5659f6278"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class FreeTypeG2ConfigurationAuditTests(unittest.TestCase):
    maxDiff = None

    def run_tool(self, image: Path = IMAGE) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            ["python3", str(TOOL), "--compact", "--image", str(image)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            check=False,
        )

    def report(self) -> dict[str, object]:
        result = self.run_tool()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(result.stdout.count("\n"), 1)
        return json.loads(result.stdout)

    def test_tool_and_authenticated_evidence_spans_are_pinned(self) -> None:
        data = TOOL.read_bytes()
        self.assertEqual(len(data), EXPECTED_TOOL_SIZE)
        self.assertEqual(digest(data), EXPECTED_TOOL_SHA256)
        report = self.report()
        self.assertEqual(report["schema_version"], 1)
        self.assertEqual(report["status"], "production-excluded static recovery")
        self.assertEqual(report["image"]["size"], 3_523_396)
        self.assertEqual(
            report["image"]["sha256"],
            "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863",
        )
        self.assertEqual(
            set(report["spans"]),
            {
                "font_manager_init",
                "create_single_font",
                "autofit_module_init",
                "cff_driver_init",
                "default_module_table",
                "face_internal_incremental",
                "ft_done_face",
                "ft_open_face_failure_done",
                "ft_open_face_no_output_done",
                "ft_memory_callbacks",
                "ft_new_done_memory",
                "lv_face_cache_destroy",
                "smooth_lcd_emulation",
                "tt_driver_class",
                "tt_driver_init",
                "tt_gx_multi_masters",
                "tt_metrics_variations",
                "tt_property_set",
                "tt_services",
                "xip_font_callback",
                "xip_font_registration",
            },
        )

    def test_true_type_default_gx_and_selected_compile_guards_are_exact(self) -> None:
        configuration = self.report()["configuration"]
        true_type = configuration["true_type"]
        self.assertEqual(true_type["interpreter_default"], 40)
        self.assertEqual(true_type["supported_interpreter_versions"], [35, 40])
        self.assertEqual(true_type["TT_CONFIG_OPTION_SUBPIXEL_HINTING"], 2)
        self.assertTrue(true_type["minimal_v40"])
        self.assertFalse(true_type["infinality_v38"])
        self.assertTrue(true_type["TT_CONFIG_OPTION_GX_VAR_SUPPORT"])
        self.assertTrue(true_type["TT_CONFIG_OPTION_EMBEDDED_BITMAPS"])
        self.assertEqual(
            configuration["gx_variations"],
            {
                "metrics_variations_callable_slots": 3,
                "metrics_variations_record": "0x00767290",
                "multi_masters_callable_slots": 8,
                "multi_masters_record": "0x007505A4",
                "scope": (
                    "fvar/gvar/cvar/avar plus HVAR/VVAR/MVAR service paths "
                    "selected by the 2.9.1 guard"
                ),
            },
        )
        self.assertEqual(
            configuration["base"],
            {
                "FT_CONFIG_OPTION_ENVIRONMENT_PROPERTIES": False,
                "FT_CONFIG_OPTION_INCREMENTAL": True,
                "FT_CONFIG_OPTION_PIC": False,
                "FT_CONFIG_OPTION_SUBPIXEL_RENDERING": False,
                "stream_support": True,
            },
        )
        self.assertEqual(
            configuration["cff"],
            {
                "CFF_CONFIG_OPTION_OLD_ENGINE": False,
                "default_hinting_engine": "Adobe",
            },
        )
        autofit = configuration["autofit"]
        self.assertTrue(autofit["AF_CONFIG_OPTION_USE_WARPER"])
        self.assertTrue(autofit["AF_CONFIG_OPTION_CJK"])
        self.assertTrue(autofit["AF_CONFIG_OPTION_INDIC"])
        self.assertEqual(autofit["fallback_style"]["name"], "AF_STYLE_HANI_DFLT")
        self.assertEqual(autofit["fallback_style"]["enum"], 83)

    def test_exact_default_module_inventory_is_source_reusable(self) -> None:
        modules = self.report()["configuration"]["built_in_modules"]
        self.assertEqual(
            [module["name"] for module in modules],
            [
                "autofitter",
                "truetype",
                "cff",
                "psaux",
                "psnames",
                "pshinter",
                "sfnt",
                "smooth",
                "smooth-lcd",
                "smooth-lcdv",
            ],
        )
        self.assertEqual(modules[0]["class"], "0x00752520")
        self.assertEqual(modules[1]["flags"], "0x00000501")
        self.assertEqual(modules[2]["object_size"], 72)
        self.assertEqual(modules[-1]["class"], "0x00718E14")

    def test_allocator_lifecycle_abi_and_external_font_boundary_are_exact(self) -> None:
        report = self.report()
        allocator = report["allocator"]
        self.assertEqual(allocator["FT_Memory_size"], 16)
        self.assertEqual(allocator["heap_descriptor"], "0x20000354")
        self.assertEqual(allocator["generic_allocate"], "0x00484180")
        self.assertEqual(allocator["generic_reallocate"], "0x00484234")
        self.assertEqual(allocator["generic_free"], "0x0048429E")
        self.assertTrue(allocator["source_path"].endswith(r"lvgl_ttf\src\am_ftsystem.c"))
        self.assertEqual(report["abi"]["compiler_family"], "IAR Arm (source-tree evidence)")
        self.assertEqual(report["abi"]["pointer_bits"], 32)

        lifecycle = allocator["lifecycle"]
        self.assertEqual(
            lifecycle["FT_Done_Face"],
            {
                "caller_roles": [
                    "LVGL/FTC face-cache destructor",
                    "FT_Open_Face failure cleanup",
                    "FT_Open_Face no-output cleanup",
                ],
                "direct_callers": [
                    {"address": "0x004B2310", "kind": "BL"},
                    {"address": "0x0052659C", "kind": "BL"},
                    {"address": "0x005267D0", "kind": "BL"},
                ],
                "end": "0x0052687E",
                "entry": "0x00526814",
            },
        )
        self.assertIsNone(lifecycle["FT_Done_FreeType"]["entry"])
        self.assertFalse(lifecycle["FT_Done_FreeType"]["stock_entry_recoverable"])
        self.assertEqual(
            lifecycle["FT_Done_FreeType"]["done_memory_direct_references"],
            [{"address": "0x0052433E", "kind": "BL"}],
        )

        registration = report["font_registration"]
        self.assertEqual(registration["header_magic"], "0x5A5A5A5A")
        self.assertEqual(registration["header_name_offset"], 4)
        self.assertEqual(registration["header_font_pointer_offset"], 52)
        self.assertEqual(registration["header_size_fields"], [56, 58])
        self.assertEqual(registration["font_chain_entries_per_role"], 4)
        self.assertEqual(
            registration["configuration_record"],
            {
                "font_pointer_or_face_path": {"offset": 4, "size": 4},
                "pixel_size": {"offset": 8, "size": 2},
                "size": 12,
                "style": {"offset": 10, "size": 1},
                "type": {"offset": 0, "size": 1},
                "type_semantics": {
                    "0": "native lv_font_t pointer",
                    "1": "FreeType face path passed to lv_freetype_font_create",
                    "2": "binary-font path disabled in this build",
                },
            },
        )
        self.assertEqual(
            [item["base"] for item in registration["external_headers"]],
            ["0x80100000", "0x80700000"],
        )
        self.assertIn("remain unresolved", registration["qualification"])
        self.assertIn(
            "external font payload identities and runtime configuration-array contents",
            report["unresolved"],
        )

    def test_tool_fails_closed_on_official_image_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            altered = Path(temporary) / IMAGE.name
            shutil.copyfile(IMAGE, altered)
            data = bytearray(altered.read_bytes())
            data[0x005F903C - 0x00437FE0] ^= 1
            altered.write_bytes(data)
            result = self.run_tool(altered)
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertIn("G2 FreeType configuration audit failed:", result.stdout)

    def test_each_new_static_recovery_span_fails_closed_under_mutation(self) -> None:
        spec = importlib.util.spec_from_file_location("freetype_g2_config_audit", TOOL)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        audit = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(audit)

        new_spans = [
            "default_module_table",
            "ft_done_face",
            "lv_face_cache_destroy",
            "ft_open_face_failure_done",
            "ft_open_face_no_output_done",
            "face_internal_incremental",
            "smooth_lcd_emulation",
            "cff_driver_init",
            "autofit_module_init",
        ]
        original = IMAGE.read_bytes()
        for name in new_spans:
            with self.subTest(span=name), tempfile.TemporaryDirectory() as temporary:
                start = audit.SPAN_DIGESTS[name][0]
                altered_data = bytearray(original)
                altered_data[start - audit.MAPPING_BIAS] ^= 1
                altered = Path(temporary) / IMAGE.name
                altered.write_bytes(altered_data)

                old_image_sha256 = audit.IMAGE_SHA256
                audit.IMAGE_SHA256 = digest(altered_data)
                try:
                    with self.assertRaisesRegex(SystemExit, f"{name} span changed"):
                        audit.authenticate(audit.Image(altered))
                finally:
                    audit.IMAGE_SHA256 = old_image_sha256

    def test_audit_remains_absent_from_production_inputs(self) -> None:
        configured = list((ROOT / "manifests").glob("*.json"))
        configured.extend(
            path
            for path in (ROOT / "components").glob("**/*")
            if path.is_file()
            and path.suffix in {".json", ".c", ".h", ".py", ".s", ".S", ".ld", ".lds", ".mk"}
            and "build" not in path.relative_to(ROOT / "components").parts
        )
        offenders = [
            path.relative_to(ROOT).as_posix()
            for path in configured
            if "freetype_g2_config_audit" in path.read_text(encoding="utf-8").lower()
        ]
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
