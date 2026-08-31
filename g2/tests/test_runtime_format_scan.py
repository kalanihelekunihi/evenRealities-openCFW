"""Host behavior and Cortex-M55 build gates for freestanding format input."""

from __future__ import annotations

import ctypes
import hashlib
import json
import math
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "components" / "shared" / "runtime" / "runtime_format_scan.c"
HEADER = ROOT / "components" / "shared" / "runtime" / "runtime_format_scan.h"
FIXTURE = ROOT / "tests" / "fixtures" / "runtime_format_scan_host.c"
OVERLAY_CONFIG = ROOT / "components" / "apollo_main" / "core_overlay" / "overlay.json"
OVERLAY_REPORT = ROOT / "components" / "apollo_main" / "core_overlay" / "build" / "build-report.json"
MANIFEST = ROOT / "manifests" / "g2-2.2.6.10-core-source.json"
PACKAGE = ROOT / "build" / "source" / "package" / "g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
FLASH_PLAN = ROOT / "build" / "source" / "flash-plan.json"

PRODUCTION_LEAVES = {
    "__aeabi_dadd": (330_812, 18),
    "__aeabi_dmul": (330_832, 18),
    "__aeabi_ddiv": (330_852, 18),
    "__aeabi_ui2d": (330_872, 14),
    "__aeabi_d2f": (330_888, 14),
    "open_cfw_runtime_strtod_bounded": (330_908, 2_696),
    "open_cfw_runtime_strtod": (333_604, 10),
    "open_cfw_runtime_scanset_match": (333_616, 126),
    "open_cfw_runtime_vsscanf": (333_744, 2_530),
    "open_cfw_runtime_sscanf": (336_276, 28),
    "open_cfw_runtime_iar_scanf_core": (336_304, 12),
}

OVERLAY_PIN = (362_272, "8c80c3fa53a89c77d145533f59f63389dfa31f968642f783323ed81ac81be5ae")
COMPONENT_PIN = (3_885_668, "898d5efb1430dc0c3e0b8b7e26823a653952114ffeab0d3ae6e89d8925301ef5")
PACKAGE_PIN = (4_678_740, "d569793138c6bc2ee456536daee59dcef0bb6051034ed966f7144083790a777a")
FLASH_PLAN_PIN = (4_595_610, "b217e924841c0fda423dfc7727d76d31499f8057aade7339e4bc3b338104c127")


class RuntimeFormatScanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        library = temporary / (
            "runtime_format_scan.dylib" if sys.platform == "darwin"
            else "runtime_format_scan.so"
        )
        command = [clang, "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE)]
        command += ["-dynamiclib", "-o", str(library)] if sys.platform == "darwin" else ["-shared", "-fPIC", "-o", str(library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.target = temporary / "runtime_format_scan.o"
        subprocess.run(
            [
                clang, "--target=thumbv7em-none-eabi", "-mthumb",
                "-ffreestanding", "-fno-builtin", "-fropi", "-std=c11",
                "-O2", "-Wall", "-Wextra",
                "-Werror", "-c", str(SOURCE), "-o", str(cls.target),
            ],
            check=True, capture_output=True, text=True,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_integer_bases_signs_and_lengths(self) -> None:
        values = [ctypes.c_int(), ctypes.c_uint(), ctypes.c_uint(), ctypes.c_int()]
        fn = self.loaded.open_cfw_test_scan_integers
        self.assertEqual(fn(b"-42 ff 17 0x20", *(ctypes.byref(v) for v in values)), 4)
        self.assertEqual([v.value for v in values], [-42, 255, 15, 32])
        byte, half, wide, size = ctypes.c_int8(), ctypes.c_int16(), ctypes.c_longlong(), ctypes.c_size_t()
        fn = self.loaded.open_cfw_test_scan_lengths
        self.assertEqual(fn(b"-7 -300 5000000000 123", ctypes.byref(byte), ctypes.byref(half), ctypes.byref(wide), ctypes.byref(size)), 4)
        self.assertEqual((byte.value, half.value, wide.value, size.value), (-7, -300, 5_000_000_000, 123))

    def test_strings_scansets_raw_width_and_count(self) -> None:
        word, letters, raw, consumed = ctypes.create_string_buffer(8), ctypes.create_string_buffer(8), ctypes.create_string_buffer(4), ctypes.c_int()
        fn = self.loaded.open_cfw_test_scan_text
        self.assertEqual(fn(b"hello abcXY", word, letters, raw, ctypes.byref(consumed)), 3)
        self.assertEqual((word.value, letters.value, raw.raw[:2], consumed.value), (b"hello", b"abc", b"XY", 11))
        inverted = ctypes.create_string_buffer(8)
        self.assertEqual(self.loaded.open_cfw_test_scan_inverted(b"ab-_7", inverted), 1)
        self.assertEqual(inverted.value, b"ab-_")

    def test_float_decimal_hex_inf_nan_and_strtod_end(self) -> None:
        first, second, third = ctypes.c_float(), ctypes.c_double(), ctypes.c_double()
        fn = self.loaded.open_cfw_test_scan_floats
        self.assertEqual(fn(b"1.25 -2.5e2 0x1.8p+2", ctypes.byref(first), ctypes.byref(second), ctypes.byref(third)), 3)
        self.assertAlmostEqual(first.value, 1.25)
        self.assertAlmostEqual(second.value, -250.0)
        self.assertAlmostEqual(third.value, 6.0)
        parser = self.loaded.open_cfw_runtime_strtod
        parser.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_char_p)]
        parser.restype = ctypes.c_double
        end = ctypes.c_char_p()
        self.assertTrue(math.isinf(parser(b"-infinity!", ctypes.byref(end))))
        self.assertEqual(end.value, b"!")
        self.assertTrue(math.isnan(parser(b"nan(payload)", ctypes.byref(end))))

    def test_float_field_width_bounds_token_during_parse(self) -> None:
        first, second, third = ctypes.c_float(), ctypes.c_float(), ctypes.c_double()
        fn = self.loaded.open_cfw_test_scan_bounded_float
        self.assertEqual(
            fn(b"12.34 0x1.8p2", ctypes.byref(first), ctypes.byref(second), ctypes.byref(third)),
            3,
        )
        self.assertAlmostEqual(first.value, 12.0)
        self.assertAlmostEqual(second.value, 0.34)
        self.assertAlmostEqual(third.value, 1.5)

        # A width ending at an exponent marker keeps the marker unconsumed.
        value = ctypes.c_float()
        consumed = ctypes.c_int()
        scanner = self.loaded.open_cfw_test_scan_exponent_width
        self.assertEqual(scanner(b"1e+2", ctypes.byref(value), ctypes.byref(consumed)), 1)
        self.assertAlmostEqual(value.value, 1.0)
        self.assertEqual(consumed.value, 1)

    def test_suppression_and_failure_stop(self) -> None:
        value = ctypes.c_uint()
        self.assertEqual(self.loaded.open_cfw_test_scan_suppressed(b"drop 19", ctypes.byref(value)), 1)
        self.assertEqual(value.value, 19)
        self.assertEqual(self.loaded.open_cfw_test_scan_suppressed(b"drop nope", ctypes.byref(value)), 0)

    def test_scanset_matcher_recovered_range_contract(self) -> None:
        match = self.loaded.open_cfw_runtime_scanset_match
        match.argtypes = [ctypes.c_char_p, ctypes.c_uint, ctypes.c_uint]
        match.restype = ctypes.c_int
        self.assertEqual(match(b"a-cx", 4, ord("b")), 1)
        self.assertEqual(match(b"a-cx", 4, ord("x")), 1)
        self.assertEqual(match(b"a-cx", 4, ord("z")), 0)

    def test_target_object_exports_complete_api_and_exact_provider_seam(self) -> None:
        output = subprocess.run(["/usr/bin/nm", "-g", str(self.target)], check=True, capture_output=True, text=True).stdout
        for symbol in (
            "open_cfw_runtime_strtod", "open_cfw_runtime_strtod_bounded",
            "open_cfw_runtime_vsscanf",
            "open_cfw_runtime_sscanf", "open_cfw_runtime_scanset_match",
        ):
            self.assertIn(symbol, output)
        undefined = {
            line.strip().split()[-1]
            for line in output.splitlines()
            if line.strip().startswith("U ")
        }
        self.assertEqual(undefined, {
            "__aeabi_d2f", "__aeabi_dadd", "__aeabi_ddiv",
            "__aeabi_dmul", "__aeabi_ui2d",
        })
        self.assertGreater(self.target.stat().st_size, 0)

    def test_sources_are_c_not_generated_binary_payloads(self) -> None:
        self.assertIn("open_cfw_runtime_vsscanf", SOURCE.read_text())
        self.assertIn("open_cfw_runtime_strtod", HEADER.read_text())

    def test_production_route_manifest_and_complete_image_are_pinned(self) -> None:
        config = json.loads(OVERLAY_CONFIG.read_text(encoding="utf-8"))
        configured = {
            item["function"]: (item["expected"]["offset"], item["expected"]["size"])
            for item in config["relocated_leaves"]
            if item["function"] in PRODUCTION_LEAVES
        }
        self.assertEqual(configured, PRODUCTION_LEAVES)
        source = next(
            item["source"] for item in config["relocated_leaves"]
            if item["function"] == "open_cfw_runtime_vsscanf"
        )
        self.assertEqual(
            (source["path"], source["size"], source["sha256"]),
            (
                "components/shared/runtime/runtime_format_scan.c",
                20_951,
                "624de0a792b351a87e0e6c3373ea8c8026093850b782e31ece32158f1c164a5f",
            ),
        )
        patch = next(
            item for item in config["patch_sites"]
            if item["name"] == "replace_iar_scanf_core"
        )
        self.assertEqual(
            (
                patch["runtime_address"], patch["expected_size"],
                patch["expected_sha256"], patch["branch"],
                patch["target_function"], patch["profiles"],
            ),
            (
                0x004D1638, 2_778,
                "54dcd834ea6fcf74db400e38df7635f5b0686f4253db1a9fe6b05af7c2a3a120",
                "b_w", "open_cfw_runtime_iar_scanf_core", ["apple-clang"],
            ),
        )
        self.assertEqual(
            (config["expected"]["overlay_size"], config["expected"]["overlay_sha256"]),
            OVERLAY_PIN,
        )
        self.assertEqual(
            (config["expected"]["component_size"], config["expected"]["component_sha256"]),
            COMPONENT_PIN,
        )

        report = json.loads(OVERLAY_REPORT.read_text(encoding="utf-8"))
        reported = {
            item["extraction"]["function"]: (
                item["placement"]["offset"], item["placement"]["size"]
            )
            for item in report["relocated_leaves"]
            if item["extraction"]["function"] in PRODUCTION_LEAVES
        }
        self.assertEqual(reported, PRODUCTION_LEAVES)
        self.assertEqual(
            (report["overlay"]["size"], report["overlay"]["sha256"]), OVERLAY_PIN
        )
        self.assertEqual(
            (report["component"]["size"], report["component"]["sha256"]), COMPONENT_PIN
        )

        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        main = manifest["component_overrides"]["apollo_main"]
        self.assertEqual((main["provider"]["size"], main["provider"]["sha256"]), COMPONENT_PIN)
        region = next(item for item in main["regions"] if item["name"] == "iar_format_input_source_closure")
        self.assertEqual(
            (region["file_offset"], region["size"], region["target_address"], region["address_status"]),
            (3_854_208, 5_504, 0x007E4F60, "source_compiled"),
        )
        self.assertEqual(
            (manifest["package"]["expected_size"], manifest["package"]["expected_sha256"]),
            PACKAGE_PIN,
        )

        package_bytes = PACKAGE.read_bytes()
        self.assertEqual((len(package_bytes), hashlib.sha256(package_bytes).hexdigest()), PACKAGE_PIN)
        plan_bytes = FLASH_PLAN.read_bytes()
        self.assertEqual((len(plan_bytes), hashlib.sha256(plan_bytes).hexdigest()), FLASH_PLAN_PIN)
        plan = json.loads(plan_bytes)
        self.assertEqual(plan["package_sha256"], PACKAGE_PIN[1])
        self.assertEqual(
            tuple(
                len(plan[key]) for key in (
                    "flash_regions", "unresolved_flash_regions",
                    "container_only_regions", "protected_regions",
                )
            ),
            (6_598, 0, 6, 6),
        )


if __name__ == "__main__":
    unittest.main()
