#!/usr/bin/env python3
"""Verify the DaveGamble/cJSON snapshot and its Cortex-M55 compile probe."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "third_party/cJSON"
sys.path.insert(0, str(ROOT / "tools"))
import apollo_overlay  # noqa: E402


EXPECTED_PUBLIC_SECTIONS = {
    ".text.cJSON_Parse",
    ".text.cJSON_ParseWithOpts",
    ".text.cJSON_Delete",
    ".text.cJSON_GetObjectItem",
    ".text.cJSON_GetArraySize",
    ".text.cJSON_GetArrayItem",
    ".text.cJSON_IsArray",
}
PRODUCTION_SOURCE = ROOT / "components/shared/cjson/runtime_cjson_parse.c"
PROBE = ROOT / "tests/fixtures/cjson_parse_probe.c"
EXPECTED_PRODUCTION_FUNCTIONS = {
    "case_insensitive_strcmp", "cJSON_New_Item", "cJSON_Delete",
    "get_decimal_point", "parse_number", "parse_hex4",
    "utf16_literal_to_utf8", "parse_string", "buffer_skip_whitespace",
    "skip_utf8_bom", "cJSON_ParseWithOpts", "cJSON_Parse", "parse_value",
    "parse_array", "parse_object", "cJSON_GetArraySize", "get_array_item",
    "cJSON_GetArrayItem", "get_object_item", "cJSON_GetObjectItem",
    "cJSON_IsArray",
}


class CjsonSnapshotTests(unittest.TestCase):
    def test_offline_snapshot_verifier(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SNAPSHOT / "verify_snapshot.py")],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("snapshot verification passed", result.stdout)
        self.assertIn("production: routed", result.stdout)

    def test_production_admission_decision_is_explicit(self) -> None:
        import json

        provenance = json.loads((SNAPSHOT / "PROVENANCE.json").read_text(encoding="utf-8"))
        boundary = provenance["g2_boundary"]
        self.assertTrue(boundary["production_routed"])
        self.assertIn("21 strict dual-profile relocated leaves", boundary["production_decision"])
        self.assertEqual(
            boundary["production_source"]["path"],
            "components/shared/cjson/runtime_cjson_parse.c",
        )
        self.assertEqual(boundary["linked_functions"], 21)
        self.assertEqual(boundary["stock_body_bytes"], 2572)
        self.assertEqual(boundary["stock_span"], "[0x004D798C,0x004D83D8)")

    def test_apple_clang_cortex_m55_compile_profile(self) -> None:
        clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if not clang:
            self.skipTest("clang is unavailable")
        with tempfile.TemporaryDirectory(prefix="opencfw-cjson-") as tmp:
            obj = Path(tmp) / "cjson.o"
            subprocess.run(
                [
                    clang,
                    "--target=arm-none-eabi",
                    "-mcpu=cortex-m55",
                    "-mthumb",
                    "-Oz",
                    "-std=c11",
                    "-ffunction-sections",
                    "-fdata-sections",
                    "-fno-builtin",
                    "-fno-ident",
                    "-fno-unwind-tables",
                    "-fno-asynchronous-unwind-tables",
                    "-nostdinc",
                    "-I",
                    str(SNAPSHOT / "g2-compat"),
                    "-I",
                    str(SNAPSHOT),
                    "-c",
                    str(SNAPSHOT / "cJSON.c"),
                    "-o",
                    str(obj),
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            _data, sections = apollo_overlay.parse_elf32(obj)
            observed = {
                str(section["name"]): int(section["size"])
                for section in sections
                if str(section["name"]) in EXPECTED_PUBLIC_SECTIONS
            }
            self.assertEqual(set(observed), EXPECTED_PUBLIC_SECTIONS)
            self.assertTrue(all(size > 0 for size in observed.values()))

    def test_production_source_is_freestanding_and_closed(self) -> None:
        clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if not clang:
            self.skipTest("clang is unavailable")
        with tempfile.TemporaryDirectory(prefix="opencfw-cjson-production-") as tmp:
            obj = Path(tmp) / "cjson-production.o"
            subprocess.run(
                [
                    clang, "--target=thumbv7em-none-eabi", "-mthumb",
                    "-mcpu=cortex-m55", "-mfpu=fp-armv8", "-mfloat-abi=hard",
                    "-Oz", "-ffreestanding", "-fno-builtin",
                    "-fno-jump-tables", "-fomit-frame-pointer",
                    "-mno-unaligned-access", "-fno-unwind-tables",
                    "-fno-asynchronous-unwind-tables", "-fropi",
                    "-ffunction-sections", "-fdata-sections", "-fno-ident",
                    "-mllvm", "-enable-machine-outliner=never",
                    "-DOPEN_CFW_CJSON_G2=1", "-nostdinc", "-I",
                    str(SNAPSHOT / "g2-compat"), "-I", str(SNAPSHOT),
                    "-c", str(PRODUCTION_SOURCE), "-o", str(obj),
                ],
                cwd=ROOT, check=True, capture_output=True, text=True,
            )
            data, sections = apollo_overlay.parse_elf32(obj)
            symbols = apollo_overlay.parse_elf32_symbols(data, sections)
            functions = {
                str(section["name"])[6:]
                for section in sections
                if str(section["name"]).startswith(".text.")
            }
            self.assertEqual(functions, EXPECTED_PRODUCTION_FUNCTIONS)
            undefined = {
                str(symbol["name"])
                for symbol in symbols
                if int(symbol["section_index"]) == 0 and symbol["name"]
            }
            self.assertEqual(undefined, set())
            alloc_data = [
                str(section["name"])
                for section in sections
                if int(section["size"]) > 0
                and int(section["flags"]) & apollo_overlay.SHF_ALLOC
                and not int(section["flags"]) & apollo_overlay.SHF_EXECINSTR
                and not str(section["name"]).startswith(".ARM.exidx")
            ]
            self.assertEqual(alloc_data, [])

    def test_production_source_matches_upstream_behavior_corpus(self) -> None:
        clang = shutil.which("clang")
        if not clang:
            self.skipTest("host clang is unavailable")
        with tempfile.TemporaryDirectory(prefix="opencfw-cjson-differential-") as tmp:
            temporary = Path(tmp)
            upstream = temporary / "upstream"
            production = temporary / "production"
            common = [clang, "-std=c11", "-O2", "-I", str(SNAPSHOT)]
            for output, source in (
                (upstream, SNAPSHOT / "cJSON.c"),
                (production, PRODUCTION_SOURCE),
            ):
                subprocess.run(
                    [*common, str(source), str(PROBE), "-o", str(output)],
                    cwd=ROOT, check=True, capture_output=True, text=True,
                )
            corpus = (
                "null", "false", "true", "0", "-0", "-12.5", "1e3",
                "1e-3", "2147483648", "-2147483649", "\ufeff{\"Name\":1}",
                "\"hello\"", "\"\\u0041\\u03a9\"",
                "\"\\ud83d\\ude03\"", "[]", "[1,true,null,\"x\"]",
                "{}", "{\"Name\":1,\"nested\":{\"x\":[1,2,3]}}",
                "1e", "-", "[1,]", "{\"a\":}", "\"\\ud800\"",
            )
            for value in corpus:
                expected = subprocess.run(
                    [str(upstream), value], check=True, capture_output=True,
                    text=True,
                ).stdout
                observed = subprocess.run(
                    [str(production), value], check=True, capture_output=True,
                    text=True,
                ).stdout
                self.assertEqual(observed, expected, value)


if __name__ == "__main__":
    unittest.main()
