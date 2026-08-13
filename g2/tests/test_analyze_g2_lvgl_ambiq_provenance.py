#!/usr/bin/env python3
"""Qualify the recovered Ambiq LVGL subtree and G2 draw-buffer ABI."""

from __future__ import annotations

import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools" / "analyze_g2_lvgl_ambiq_provenance.py"
MANIFEST = ROOT / "tools" / "manifests" / "g2-lvgl-ambiq-source-provenance.json"
SNAPSHOT = ROOT / "third_party" / "lvgl"
ABI_PATCH = ROOT / "tools" / "patches" / "lvgl-g2-ambiq-draw-buffer-abi.patch"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_lvgl_ambiq_provenance", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class LVGLAmbiqProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.data = cls.analyzer.IMAGE.read_bytes()
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.report = cls.analyzer.audit(cls.data, cls.manifest)

    def test_exact_subtree_state_and_commit_ambiguity_are_pinned(self) -> None:
        source = self.report["source_recovery"]
        self.assertEqual(source["subtree_git_tree_sha1"], "1e774257495fa43177e04fc5c8a42a77c2d7d619")
        self.assertEqual(source["canonical_default_branch_commit"], "5be8e0ae5077aa3880aba8a322b1487d6bc73c07")
        self.assertEqual(source["equivalent_replay_commit"], "67fd93e268f86b2ce90d4f1b14b53e36bf49ddd0")
        self.assertEqual(source["immediately_excluded_backend_commit"], "6770071cb7c4ab97b83669078fe461df812bc79e")
        self.assertIn("two-way ambiguous", source["commit_resolution"])
        self.assertEqual(source["candidate_file_count"], 16)
        self.assertEqual(source["candidate_bytes"], 170_833)

    def test_stock_handler_layout_and_patch_history_are_pinned(self) -> None:
        abi = self.report["draw_buffer_abi"]
        self.assertEqual(abi["lv_global_base"], 0x2006F548)
        self.assertEqual(abi["handler_offsets"], [0xC8, 0xE8, 0x108])
        self.assertEqual(abi["handler_size"], 0x20)
        self.assertEqual(abi["callback_offsets"]["clear_cb"], 0x18)
        self.assertEqual(abi["callback_offsets"]["copy_cb"], 0x1C)
        self.assertEqual(abi["generic_hook_origin_commit"], "d4dcd26bd97a0b09778ab9f789b6e7a7354bc967")
        self.assertEqual(abi["ambiq_wiring_origin_commit"], "925470ddbff5f445f6bca3905305ca9d0f2cf5c8")

    def test_retained_diagnostics_match_the_recovered_source(self) -> None:
        lines = self.report["source_line_fingerprints"]
        self.assertEqual(lines["lv_draw_ambiq_buffer.c"], [68, 107, 120, 181, 221, 255])
        self.assertEqual(lines["lv_draw_ambiq_letter.c"], [80, 112, 130, 134])
        self.assertEqual(lines["lv_draw_ambiq_vector_font.c"], [186, 199, 202, 209, 235, 240, 281, 297, 299, 312])
        self.assertEqual(len(self.report["retained_paths"]), 3)
        self.assertEqual(len(self.report["pinned_spans"]), 11)
        self.assertEqual(self.report["pinned_spans"]["lv_draw_ambiq_init_buf_handlers"]["size"], 130)

    def test_image_and_manifest_mutations_are_rejected(self) -> None:
        for run in (
            self.analyzer.PINNED_SPANS["lv_draw_ambiq_init_buf_handlers"][0],
            next(iter(self.analyzer.RETAINED_PATHS)),
            next(iter(self.analyzer.HANDLER_LITERAL_TABLE)),
        ):
            with self.subTest(run=f"0x{run:08x}"):
                mutated = bytearray(self.data)
                mutated[run - self.analyzer.LOAD_BASE] ^= 1
                with self.assertRaises(self.analyzer.AuditError):
                    self.analyzer.audit(bytes(mutated), self.manifest)

        mutated_manifest = copy.deepcopy(self.manifest)
        mutated_manifest["candidate_files"][0]["sha256"] = "0" * 64
        with self.assertRaises(self.analyzer.AuditError):
            self.analyzer.audit(self.data, mutated_manifest)

    def test_recovered_arm_layout_matches_every_stock_boundary(self) -> None:
        clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if clang is None:
            self.skipTest("clang is unavailable")

        source = r'''
#include <stddef.h>
#include "src/core/lv_global.h"
#include "src/display/lv_display_private.h"
#include "src/indev/lv_indev_private.h"
#include "src/draw/lv_draw_buf.h"
#include "src/draw/lv_draw_buf_private.h"
#define OFF(member, value) _Static_assert(offsetof(lv_global_t, member) == value, #member)
_Static_assert(sizeof(lv_draw_buf_handlers_t) == 0x20, "handlers");
_Static_assert(offsetof(lv_draw_buf_handlers_t, clear_cb) == 0x18, "clear_cb");
_Static_assert(offsetof(lv_draw_buf_handlers_t, copy_cb) == 0x1c, "copy_cb");
OFF(draw_buf_handlers, 0xc8);
OFF(font_draw_buf_handlers, 0xe8);
OFF(image_cache_draw_buf_handlers, 0x108);
OFF(img_decoder_ll, 0x128);
OFF(img_cache, 0x134);
OFF(img_header_cache, 0x138);
OFF(draw_info, 0x13c);
OFF(draw_sw_blend_handler_ll, 0x160);
OFF(custom_log_print_cb, 0x16c);
OFF(log_last_log_time, 0x170);
OFF(theme_simple, 0x174);
OFF(theme_default, 0x178);
OFF(theme_mono, 0x17c);
OFF(fsdrv_ll, 0x180);
OFF(littlefs_fs_drv, 0x18c);
OFF(ft_context, 0x1c0);
OFF(span_snippet_stack, 0x1c4);
OFF(objid_array, 0x1c8);
OFF(objid_count, 0x1cc);
OFF(lv_general_mutex, 0x1d0);
OFF(freertos_idle_time_sum, 0x1d8);
OFF(user_data, 0x1e8);
_Static_assert(sizeof(lv_global_t) == 0x1ec, "global");
_Static_assert(sizeof(lv_display_t) == 0x31c, "display");
_Static_assert(sizeof(lv_indev_t) == 0xdc, "indev");
_Static_assert(sizeof(lv_draw_buf_t) == 0x1c, "draw buffer");
'''
        with tempfile.TemporaryDirectory(prefix="opencfw-lvgl-ambiq-abi-") as temp:
            root = Path(temp)
            snapshot = root / "lvgl"
            shutil.copytree(SNAPSHOT, snapshot)
            applied = subprocess.run(
                ["patch", "-p1", "-i", str(ABI_PATCH)],
                cwd=snapshot,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(applied.returncode, 0, applied.stdout)
            (root / "inttypes.h").write_text(
                "#ifndef _INTTYPES_H\n#define _INTTYPES_H\n#include <stdint.h>\n"
                "#define PRIu32 \"u\"\n#define PRId32 \"d\"\n#define PRIx32 \"x\"\n#endif\n",
                encoding="ascii",
            )
            (root / "FreeRTOS.h").write_text(
                "#ifndef FREERTOS_H\n#define FREERTOS_H\n"
                "typedef int BaseType_t; typedef void * TaskHandle_t; typedef void * SemaphoreHandle_t;\n"
                "#endif\n",
                encoding="ascii",
            )
            (root / "task.h").write_text("#include \"FreeRTOS.h\"\n", encoding="ascii")
            (root / "semphr.h").write_text("#include \"FreeRTOS.h\"\n", encoding="ascii")
            macros = [
                "LV_COLOR_DEPTH=8", "LV_USE_OS=LV_OS_FREERTOS", "LV_USE_FREETYPE=1",
                "LV_USE_FLEX=1", "LV_USE_GRID=1", "LV_USE_FS_LITTLEFS=1", "LV_USE_BMP=1",
                "LV_USE_LOG=1", "LV_LOG_LEVEL=LV_LOG_LEVEL_WARN", "LV_USE_ASSERT_NULL=1",
                "LV_BIG_ENDIAN_SYSTEM=0", "LV_DRAW_SW_COMPLEX=0",
                "LV_USE_STDLIB_MALLOC=LV_STDLIB_CUSTOM", "LV_USE_SPAN=1", "LV_USE_OBJ_ID_BUILTIN=1",
            ]
            command = [
                clang, "-x", "c", "-", "-fsyntax-only", "--target=arm-none-eabi",
                "-mcpu=cortex-m55", "-mthumb", "-ffreestanding", "-std=c11", "-fshort-enums",
                "-I", str(root), "-I", str(snapshot), "-I", str(snapshot / "src"), "-DLV_CONF_SKIP=1",
                *[f"-D{macro}" for macro in macros],
            ]
            compiled = subprocess.run(
                command, input=source, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False
            )
            self.assertEqual(compiled.returncode, 0, compiled.stdout)

    def test_cli_json_mode(self) -> None:
        parsed = json.loads(subprocess.run(
            [sys.executable, str(ANALYZER), "--json"], cwd=ROOT, check=True,
            capture_output=True, text=True,
        ).stdout)
        self.assertEqual(parsed["source_recovery"]["subtree_git_tree_sha1"], "1e774257495fa43177e04fc5c8a42a77c2d7d619")
        self.assertEqual(parsed["draw_buffer_abi"]["handler_size"], 32)


if __name__ == "__main__":
    unittest.main()
