#!/usr/bin/env python3
"""Focused source-identity and Cortex-M55 gates for the Ambiq LVGL backend."""

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
BUILDER = ROOT / "tools/build_g2_lvgl_ambiq_backend.py"
MANIFEST = ROOT / "tools/manifests/g2-lvgl-ambiq-backend-readiness.json"
BACKEND = ROOT / "third_party/lvgl-ambiq-backend"
NEMA = ROOT / "third_party/nema-sdk-headers"
OFFICIAL_IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"


def load_builder():
    spec = importlib.util.spec_from_file_location("build_g2_lvgl_ambiq_backend", BUILDER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def archive_members(data: bytes) -> list[tuple[str, bytes]]:
    """Read the deterministic BSD extended-name archive emitted by the builder."""

    if not data.startswith(b"!<arch>\n"):
        raise AssertionError("missing ar magic")
    members: list[tuple[str, bytes]] = []
    offset = 8
    while offset < len(data):
        header = data[offset : offset + 60]
        if len(header) != 60 or header[58:60] != b"`\n":
            raise AssertionError("malformed ar member header")
        encoded_name = header[0:16].rstrip()
        if not encoded_name.startswith(b"#1/"):
            raise AssertionError("archive member is not a BSD extended name")
        name_size = int(encoded_name[3:])
        member_size = int(header[48:58].strip())
        body_start = offset + 60
        body = data[body_start : body_start + member_size]
        if len(body) != member_size:
            raise AssertionError("truncated ar member")
        members.append((body[:name_size].decode("ascii"), body[name_size:]))
        offset = body_start + member_size + (member_size & 1)
    if offset != len(data):
        raise AssertionError("archive has trailing bytes")
    return members


class LVGLAmbiqBackendBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder()
        cls.report = cls.builder.audit_inputs()

    def test_exact_source_and_interface_identities_are_pinned(self) -> None:
        self.assertEqual(
            self.report["source"]["subtree_git_tree_sha1"],
            "1e774257495fa43177e04fc5c8a42a77c2d7d619",
        )
        self.assertEqual(self.report["source"]["files"], 16)
        self.assertEqual(self.report["source"]["bytes"], 170_833)
        self.assertEqual(len(self.report["source"]["linked_g2_translation_units"]), 11)
        self.assertEqual(self.report["nema_interface"]["imported_interface_files"], 32)
        self.assertEqual(self.report["nema_interface"]["imported_interface_bytes"], 251_655)
        self.assertEqual(
            self.report["nema_interface"]["imported_interface_digest"],
            "186008f77de1bfa3942b4ad0de8f2a8932fcc834558fb1641d87e94f3ccd36a8",
        )
        self.assertEqual(self.report["nema_interface"]["nemagfx_version"], "1.4.12")
        self.assertEqual(self.report["nema_interface"]["nemavg_version"], "1.1.8")
        stack = self.report["draw_thread_stack"]
        self.assertEqual(stack["bytes"], 32_768)
        self.assertEqual(stack["stock_function"]["start"], "0x004C73D6")
        self.assertEqual(stack["argument_evidence"]["start"], "0x004C74CE")
        self.assertIn("mov.w r0,#0x8000", stack["argument_evidence"]["decoded_sequence"])
        self.assertFalse(stack["hardware_stack_qualified"])

    def test_checked_readiness_manifest_is_reproducible_and_fail_closed(self) -> None:
        checked = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(checked, self.report)
        status = checked["software_status"]
        self.assertTrue(status["exact_source_imported"])
        self.assertFalse(status["production_overlay_registered"])
        self.assertFalse(status["production_ready"])
        self.assertEqual(len(checked["remaining_gates"]), 4)
        self.assertIn("hardware validation", checked["remaining_gates"][-1])
        self.assertIn("no hardware or flash operation", checked["analysis_mode"])

    def test_source_or_header_mutation_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="opencfw-lvgl-ambiq-mutate-") as temp:
            root = Path(temp)
            backend = root / "backend"
            nema = root / "nema"
            shutil.copytree(BACKEND, backend)
            shutil.copytree(NEMA, nema)

            source = backend / "src/draw/ambiq/lv_draw_ambiq.c"
            source.write_bytes(source.read_bytes() + b"\n")
            with self.assertRaisesRegex(self.builder.BuildError, "source identity changed"):
                self.builder.audit_inputs(backend_root=backend, nema_root=nema)

            shutil.rmtree(backend)
            shutil.copytree(BACKEND, backend)
            header = nema / "headers/include/tsi/NemaGFX/nema_core.h"
            payload = bytearray(header.read_bytes())
            payload[0] ^= 1
            header.write_bytes(payload)
            with self.assertRaisesRegex(self.builder.BuildError, "Nema interface snapshot identity changed"):
                self.builder.audit_inputs(backend_root=backend, nema_root=nema)

            image = root / "official.bin"
            shutil.copy2(OFFICIAL_IMAGE, image)
            payload = bytearray(image.read_bytes())
            payload[0x004C74D2 - 0x00437FE0] ^= 1
            image.write_bytes(payload)
            with self.assertRaisesRegex(self.builder.BuildError, "firmware image identity changed"):
                self.builder.audit_inputs(official_image=image)

    def test_compatibility_patch_is_separate_and_pinned(self) -> None:
        patch = (BACKEND / "g2-compat/lvgl-g2-hybrid-compile.patch").read_text(encoding="utf-8")
        compat = (BACKEND / "g2-compat/lvgl_ambiq_nema_compat.h").read_text(encoding="utf-8")
        sw_mask = (BACKEND / "g2-compat/lvgl_ambiq_sw_mask_compat.h").read_text(encoding="utf-8")
        self.assertIn("lv_image_decoder_close(decoder_dsc);", patch)
        self.assertIn("return LV_RESULT_OK;", patch)
        self.assertIn("#include \"lvgl_ambiq_nema_compat.h\"", patch)
        self.assertIn("#include \"lvgl_ambiq_sw_mask_compat.h\"", patch)
        self.assertIn("void nema_buffer_invalidate(nema_buffer_t * buffer);", compat)
        self.assertIn("bool nema_buffer_is_within_pool", compat)
        self.assertIn("#if !LV_DRAW_SW_COMPLEX", sw_mask)
        self.assertIn("struct _lv_draw_sw_mask_radius_param_t", sw_mask)
        self.assertIn("void lv_draw_sw_mask_radius_init", sw_mask)
        self.assertEqual(self.report["software_status"]["lv_draw_sw_complex"], 0)
        self.assertTrue(self.report["software_status"]["cache_free_radius_mask_provider"])
        self.assertEqual(
            self.report["compatibility_inputs"]["lvgl-g2-hybrid-compile.patch"],
            "bd31e6967c795ba21a3c4320d30262fe71f0a297d6c2970979c51dbbb3cf6b7c",
        )

    def test_cortex_m55_objects_and_archive_are_deterministic(self) -> None:
        clang = shutil.which("clang")
        if clang is None:
            self.skipTest("clang is unavailable")

        with tempfile.TemporaryDirectory(prefix="opencfw-lvgl-ambiq-compile-") as temp:
            root = Path(temp)
            first_dir = root / "first"
            second_dir = root / "second"
            first = self.builder.compile_backend(first_dir, clang)
            second = self.builder.compile_backend(second_dir, clang)

            self.assertEqual(first["target"], "arm-none-eabi/cortex-m55/thumb/short-enums/gnu11")
            self.assertEqual(first["object_count"], 12)
            self.assertEqual(first["objects"], second["objects"])
            self.assertTrue(first["qualification_only"])
            self.assertEqual(first["warning_count"], 0)
            self.assertEqual(first["unresolved_stack_warning_count"], 0)
            self.assertEqual(first["warnings"], [])
            self.assertFalse(first["archive"]["symbol_index"])
            self.assertEqual(first["archive"]["member_count"], 12)
            self.assertEqual(first["radius_mask"]["box_shadow_imports"], [
                "lv_draw_sw_mask_free_param", "lv_draw_sw_mask_radius_init",
            ])
            self.assertEqual(first["radius_mask"]["provider_exports"], [
                "lv_draw_sw_mask_free_param", "lv_draw_sw_mask_radius_init",
            ])
            self.assertEqual(first["radius_mask"]["provider_external_dependencies"], [
                "lv_free", "lv_malloc", "lv_malloc_zeroed", "lv_memset",
            ])
            self.assertFalse(first["radius_mask"]["global_cache_dependency"])

            first_archive = (first_dir / first["archive"]["path"]).read_bytes()
            second_archive = (second_dir / second["archive"]["path"]).read_bytes()
            self.assertEqual(first_archive, second_archive)
            members = archive_members(first_archive)
            self.assertEqual(
                [name for name, _ in members],
                [Path(unit).stem + ".o" for unit in self.builder.QUALIFICATION_UNITS],
            )
            for name, payload in members:
                with self.subTest(member=name):
                    self.assertTrue(payload.startswith(b"\x7fELF"))
                    self.assertEqual(payload[4:6], b"\x01\x01")  # 32-bit, little-endian
                    self.assertEqual(int.from_bytes(payload[16:18], "little"), 1)  # relocatable
                    self.assertEqual(int.from_bytes(payload[18:20], "little"), 40)  # EM_ARM

    def test_cli_json_mode_performs_no_compile_or_hardware_operation(self) -> None:
        parsed = json.loads(
            subprocess.run(
                [sys.executable, str(BUILDER), "--json"],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            ).stdout
        )
        self.assertEqual(parsed, self.report)
        self.assertNotIn("compile", parsed)
        self.assertIn("no hardware or flash operation", parsed["analysis_mode"])


if __name__ == "__main__":
    unittest.main()
