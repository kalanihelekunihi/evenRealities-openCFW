#!/usr/bin/env python3
"""Focused authentication and fail-closed gates for the LVGL snapshot."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "third_party" / "lvgl"
VERIFIER = SNAPSHOT / "verify_snapshot.py"
PROVENANCE = SNAPSHOT / "PROVENANCE.json"
EXPECTED_PROVENANCE_SIZE = 119164
EXPECTED_PROVENANCE_SHA256 = (
    "f59bf7e498e0478186f24d020c3dd068892a024d18be7167630b4bc5853629c8"
)
EXPECTED_VERIFIER_SIZE = 21027
EXPECTED_VERIFIER_SHA256 = (
    "05412de7c284d2d311181bd847219691d5c4468b7cefdca524f4cc2b395aa86c"
)
EXPECTED_RECORDS_SHA256 = (
    "00a2d8eb9c47223c2bd3ff41568ed7921e42d29aae1f171ba0023fcf8242759f"
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return digest(encoded)


class LvglSnapshotTests(unittest.TestCase):
    maxDiff = None

    def run_verifier(self, verifier: Path = VERIFIER) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            ["python3", str(verifier)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
            check=False,
        )

    def test_offline_verifier_and_metadata_are_pinned(self) -> None:
        result = self.run_verifier()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(
            result.stdout,
            "LVGL 9.3.0-dev compatibility-ceiling snapshot verification passed\n",
        )
        provenance = PROVENANCE.read_bytes()
        verifier = VERIFIER.read_bytes()
        self.assertEqual(len(provenance), EXPECTED_PROVENANCE_SIZE)
        self.assertEqual(digest(provenance), EXPECTED_PROVENANCE_SHA256)
        self.assertEqual(len(verifier), EXPECTED_VERIFIER_SIZE)
        self.assertEqual(digest(verifier), EXPECTED_VERIFIER_SHA256)

    def test_selection_is_the_qualified_ceiling_not_g2_or_v9_3_release(self) -> None:
        value = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        upstream = value["upstream"]
        selection = value["selection"]
        self.assertEqual(
            upstream["selected_commit"],
            "344c7c318047b7348e1be8572a9fd4260c251cfa",
        )
        self.assertEqual(
            upstream["selected_tree"],
            "2c76db856ec570f3ee12565181e5cf52bdd33d78",
        )
        self.assertEqual(upstream["declared_version"]["info"], "dev")
        self.assertFalse(selection["exact_g2_checkout_proven"])
        self.assertFalse(selection["released_v9_3_0_selected"])
        self.assertEqual(
            selection["compatible_floor_commit"],
            "60d976c466e8619326edfbd193fd2a046c10113f",
        )
        self.assertEqual(
            selection["first_incompatible_commit"],
            "f35f0859eb477c79906cf531ed394306119097f8",
        )
        self.assertEqual(selection["integration_status"], "authenticated and verified offline; no production registration")

    def test_exact_source_header_license_closure_and_exclusions(self) -> None:
        value = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        records = value["files"]
        roles = [item["role"] for item in records]
        self.assertEqual(len(records), 318)
        self.assertEqual(roles.count("translation_unit"), 65)
        self.assertEqual(roles.count("header"), 252)
        self.assertEqual(roles.count("license"), 1)
        self.assertEqual(sum(item["size"] for item in records), 2503751)
        self.assertEqual(canonical_digest(records), EXPECTED_RECORDS_SHA256)
        self.assertEqual(
            sum(
                item["role"] == "translation_unit"
                and item["local_path"].startswith("src/libs/freetype/")
                for item in records
            ),
            4,
        )
        exclusions = value["exclusions"]
        self.assertEqual(exclusions["ambiq_draw_backend_count"], 11)
        self.assertEqual(len(exclusions["ambiq_draw_backend_translation_units"]), 11)
        for path in exclusions["ambiq_draw_backend_translation_units"]:
            self.assertFalse((SNAPSHOT / path).exists(), path)
        self.assertFalse((SNAPSHOT / "lvgl_ambiq_porting/lv_ambiq_display.c").exists())
        self.assertFalse((SNAPSHOT / "lvgl_ambiq_demo/lvgl_ttf/src/am_ftsystem.c").exists())

    def test_recovered_configuration_is_explicitly_incomplete(self) -> None:
        value = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        g2 = value["g2_boundary"]
        config = (SNAPSHOT / "g2-config/lv_conf_recovered.h").read_text()
        expected_defines = {
            "#define LV_COLOR_DEPTH 8",
            "#define LV_USE_OS LV_OS_FREERTOS",
            "#define LV_USE_FREETYPE 1",
            "#define LV_USE_FLEX 1",
            "#define LV_USE_GRID 1",
            "#define LV_USE_FS_LITTLEFS 1",
            "#define LV_USE_BMP 1",
            "#define LV_USE_SPAN 1",
            "#define LV_USE_OBJ_ID_BUILTIN 1",
            "#define LV_USE_DRAW_AMBIQ 1",
            "#define LV_USE_AMBIQ_VG 1",
            "#define LV_AMBIQ_COMMAND_LIST_SECTOR 100",
            "#define LV_AMBIQ_COMMAND_LIST_SECTOR_SIZE 1024",
            "#define LV_DRAW_SW_COMPLEX 0",
            "#define LV_USE_STDLIB_MALLOC LV_STDLIB_CUSTOM",
            "#define LV_USE_LOG 1",
            "#define LV_LOG_LEVEL LV_LOG_LEVEL_WARN",
            "#define LV_USE_ASSERT_NULL 1",
            "#define LV_BIG_ENDIAN_SYSTEM 0",
        }
        actual_defines = {
            line.strip()
            for line in config.splitlines()
            if line.startswith("#define LV_") and line != "#define LV_CONF_H"
        }
        self.assertEqual(actual_defines, expected_defines)
        self.assertIn("#define NEMAGFX_POWER_SAVE 1", config)
        self.assertFalse(g2["configuration_template"]["complete"])
        self.assertEqual(g2["abi"]["sizeof_lv_global_t"], 0x1EC)
        self.assertEqual(g2["reference_compile"]["sizeof_lv_global_t"], 0x1F8)
        self.assertFalse(g2["reference_compile"]["production_abi_complete"])
        self.assertEqual(g2["recovered_vendor_compile"]["sizeof_lv_global_t"], 0x1EC)
        self.assertTrue(g2["recovered_vendor_compile"]["stock_layout_match"])
        self.assertEqual(
            g2["ambiq_backend"]["subtree_git_tree_sha1"],
            "1e774257495fa43177e04fc5c8a42a77c2d7d619",
        )
        self.assertEqual(g2["nema_dependency"]["nemagfx_version"], "1.4.12")
        self.assertEqual(g2["nema_dependency"]["nemavg_version"], "1.1.8")
        self.assertEqual(
            g2["nema_dependency"]["public_reproduction_commit"],
            "b853fded7e545f005727e13bf2ce83018c7e242d",
        )

    def test_arm_short_enum_reference_abi_compile(self) -> None:
        clang = shutil.which("clang")
        if clang is None:
            self.skipTest("clang is unavailable")
        source = """
#include "src/core/lv_global.h"
#include "src/display/lv_display_private.h"
#include "src/indev/lv_indev_private.h"
#include "src/draw/lv_draw_buf.h"
_Static_assert(sizeof(lv_display_t) == 0x31c, "display");
_Static_assert(sizeof(lv_indev_t) == 0xdc, "indev");
_Static_assert(sizeof(lv_draw_buf_t) == 0x1c, "draw buffer");
_Static_assert(sizeof(lv_global_t) == 0x1f8, "reference global");
"""
        with tempfile.TemporaryDirectory(prefix="opencfw-lvgl-abi-") as temp:
            include = Path(temp)
            (include / "inttypes.h").write_text(
                "#ifndef _INTTYPES_H\n#define _INTTYPES_H\n"
                "#include <stdint.h>\n#define PRIu32 \"u\"\n"
                "#define PRId32 \"d\"\n#define PRIx32 \"x\"\n#endif\n",
                encoding="ascii",
            )
            common = [
                clang,
                "-x",
                "c",
                "-",
                "-fsyntax-only",
                "--target=arm-none-eabi",
                "-mcpu=cortex-m55",
                "-mthumb",
                "-ffreestanding",
                "-std=c11",
                "-I",
                str(include),
                "-I",
                str(SNAPSHOT),
                "-I",
                str(SNAPSHOT / "src"),
                "-DLV_CONF_SKIP=1",
                "-DLV_COLOR_DEPTH=8",
                "-DLV_USE_FLEX=1",
                "-DLV_USE_GRID=1",
            ]
            short = subprocess.run(
                common + ["-fshort-enums"],
                input=source,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertEqual(short.returncode, 0, short.stdout)
            ordinary = subprocess.run(
                common,
                input=source,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                check=False,
            )
            self.assertNotEqual(ordinary.returncode, 0, ordinary.stdout)

    def test_verifier_rejects_source_provenance_tree_config_and_inventory_tampering(self) -> None:
        def alter_source(copy: Path) -> None:
            path = copy / "src/misc/lv_event.h"
            path.write_bytes(path.read_bytes().replace(b"LV_EVENT_LAST", b"LV_EVENT_LASX", 1))

        def alter_provenance(copy: Path) -> None:
            path = copy / "PROVENANCE.json"
            value = json.loads(path.read_text(encoding="utf-8"))
            value["selection"]["exact_g2_checkout_proven"] = True
            path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

        def alter_tree(copy: Path) -> None:
            path = copy / "upstream/trees.json"
            value = json.loads(path.read_text(encoding="utf-8"))
            value["root_tree"] = "0" * 40
            path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

        def alter_config(copy: Path) -> None:
            path = copy / "g2-config/lv_conf_recovered.h"
            path.write_bytes(path.read_bytes().replace(b"LV_COLOR_DEPTH 8", b"LV_COLOR_DEPTH 16", 1))

        def add_inventory_file(copy: Path) -> None:
            (copy / "src/draw/ambiq").mkdir(parents=True)
            (copy / "src/draw/ambiq/lv_draw_ambiq.c").write_text("/* forbidden */\n")

        mutations = [alter_source, alter_provenance, alter_tree, alter_config, add_inventory_file]
        for mutation in mutations:
            with self.subTest(mutation=mutation.__name__), tempfile.TemporaryDirectory(
                prefix="opencfw-lvgl-tamper-"
            ) as temp:
                copy = Path(temp) / "lvgl"
                shutil.copytree(SNAPSHOT, copy)
                mutation(copy)
                result = self.run_verifier(copy / "verify_snapshot.py")
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn("LVGL snapshot verification failed:", result.stdout)


if __name__ == "__main__":
    unittest.main()
