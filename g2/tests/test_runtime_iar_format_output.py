"""Host semantics and freestanding target gates for IAR printf replacement."""

from __future__ import annotations

import ctypes
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "tests" / "fixtures" / "runtime_iar_format_output_host.c"
ENGINE = ROOT / "components" / "apollo_main" / "core_overlay" / "runtime_vsnprintf.c"
PRODUCTION_ENGINE = ROOT / "components" / "shared" / "runtime" / "runtime_iar_vsnprintf_engine.c"
ADAPTER = ROOT / "components" / "shared" / "runtime" / "runtime_iar_format_output.c"
OVERLAY_CONFIG = ROOT / "components" / "apollo_main" / "core_overlay" / "overlay.json"
OVERLAY_REPORT = ROOT / "components" / "apollo_main" / "core_overlay" / "build" / "build-report.json"
MANIFEST = ROOT / "manifests" / "g2-2.2.6.10-core-source.json"
PACKAGE = ROOT / "build" / "source" / "package" / "g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
FLASH_PLAN = ROOT / "build" / "source" / "flash-plan.json"
PRODUCTION_LEAVES = {
    "open_cfw_runtime_iar_vsnprintf_engine": (336_316, 3_508),
    "open_cfw_runtime_iar_format_bridge": (339_828, 50),
    "open_cfw_runtime_iar_vformat": (339_880, 84),
    "open_cfw_runtime_iar_printf_core": (339_964, 14),
}
OVERLAY_PIN = (362_272, "8c80c3fa53a89c77d145533f59f63389dfa31f968642f783323ed81ac81be5ae")
COMPONENT_PIN = (3_956_672, "79323dd5ae9211e9d1c393f26593c98c96c53d928c44c4447c946e67ef0fbeef")
PACKAGE_PIN = (4_750_780, "49c61010614d5db51c9e97f3ca549e47644a32805411d0ff5dc96ea7445d3e27")
FLASH_PLAN_PIN = (4_961_300, "f2625775d8a7b3c81c8862db00979cdcf4965eeb003e4b6b84e8cb2d8c1293b9")
TARGET_FLAGS = [
    "--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
    "-fdata-sections", "-Wall", "-Wextra", "-Werror",
]


class RuntimeIarFormatOutputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        library = temporary / ("iar-output.dylib" if sys.platform == "darwin" else "iar-output.so")
        command = [clang, "-std=gnu11", "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE)]
        command += ["-dynamiclib", "-o", str(library)] if sys.platform == "darwin" else ["-shared", "-fPIC", "-o", str(library)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.reset = cls.loaded.open_cfw_test_iar_output_reset
        cls.reset.argtypes = [ctypes.c_uint]
        cls.standard = cls.loaded.open_cfw_test_iar_output_standard
        cls.standard.argtypes = [
            ctypes.c_char_p, ctypes.c_int, ctypes.c_uint, ctypes.c_double,
            ctypes.POINTER(ctypes.c_int), ctypes.c_int,
        ]
        cls.standard.restype = ctypes.c_int
        cls.embedded = cls.loaded.open_cfw_test_iar_output_embedded_nul
        cls.embedded.argtypes = [ctypes.c_int]
        cls.embedded.restype = ctypes.c_int
        cls.hexfloat = cls.loaded.open_cfw_test_iar_output_hexfloat
        cls.hexfloat.argtypes = [ctypes.c_double, ctypes.c_char_p]
        cls.hexfloat.restype = ctypes.c_int
        cls.q_integer = cls.loaded.open_cfw_test_iar_output_q
        cls.q_integer.argtypes = [ctypes.c_longlong]
        cls.q_integer.restype = ctypes.c_int
        cls.output = (ctypes.c_ubyte * 256).in_dll(cls.loaded, "open_cfw_test_iar_output")
        cls.count = ctypes.c_uint.in_dll(cls.loaded, "open_cfw_test_iar_output_count")

        cls.engine_object = temporary / "engine.o"
        cls.adapter_object = temporary / "adapter.o"
        subprocess.run(
            [clang, *TARGET_FLAGS, "-c", str(PRODUCTION_ENGINE),
             "-o", str(cls.engine_object)],
            check=True, capture_output=True, text=True,
        )
        subprocess.run(
            [clang, *TARGET_FLAGS, "-I", str(ADAPTER.parent),
             "-c", str(ADAPTER), "-o", str(cls.adapter_object)],
            check=True, capture_output=True, text=True,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def rendered(self) -> bytes:
        return bytes(self.output[: self.count.value])

    def test_standard_formats_count_and_no_synthetic_nul(self) -> None:
        self.reset(256)
        count = ctypes.c_int(-1)
        result = self.standard(b"value", -7, 0x2A, 1.25, ctypes.byref(count), 0)
        self.assertEqual(result, len(b"value -7 0x2a 1.25!"))
        self.assertEqual(count.value, len(b"value -7 0x2a 1.25"))
        self.assertEqual(self.rendered(), b"value -7 0x2a 1.25!")
        self.assertEqual(self.output[self.count.value], 0xCC)

    def test_embedded_nul_is_data_but_final_nul_is_suppressed(self) -> None:
        self.reset(256)
        self.assertEqual(self.embedded(0), 3)
        self.assertEqual(self.rendered(), b"A\0B")
        self.assertEqual(self.output[3], 0xCC)

    def test_iar_hexfloat_and_q_length_formats(self) -> None:
        vectors = (
            (1.0, b"%a", b"0x1p+0"),
            (1.0, b"%#a", b"0x1.p+0"),
            (1.5, b"%.1a", b"0x1.8p+0"),
            (1.5, b"%.1A", b"0X1.8P+0"),
            (float.fromhex("0x1.fffffffffffffp+0"), b"%.0a", b"0x2p+0"),
            (1.0, b"%020a", b"0x000000000000001p+0"),
            (float.fromhex("0x0.0000000000001p-1022"), b"%a", b"0x1p-1074"),
            (float("inf"), b"%A", b"INF"),
            (float("nan"), b"%-5a", b"nan  "),
        )
        for value, format_string, expected in vectors:
            with self.subTest(format=format_string, value=value):
                self.reset(256)
                self.assertEqual(self.hexfloat(value, format_string), len(expected))
                self.assertEqual(self.rendered(), expected)

        self.reset(256)
        expected = b"-9223372036854775807"
        self.assertEqual(self.q_integer(-9_223_372_036_854_775_807), len(expected))
        self.assertEqual(self.rendered(), expected)

    def test_writer_failure_and_secure_mode_fail_closed(self) -> None:
        count = ctypes.c_int(-1)
        self.reset(4)
        self.assertEqual(self.standard(b"value", -7, 0x2A, 1.25, ctypes.byref(count), 0), -1)
        self.assertEqual(self.rendered(), b"valu")
        self.reset(256)
        self.assertEqual(self.standard(b"value", -7, 0x2A, 1.25, ctypes.byref(count), 1), -1)
        self.assertEqual(self.count.value, 0)

    def test_target_exports_and_dependencies_are_explicit(self) -> None:
        engine = subprocess.run(["/usr/bin/nm", "-g", str(self.engine_object)], check=True, capture_output=True, text=True).stdout
        adapter = subprocess.run(["/usr/bin/nm", "-g", str(self.adapter_object)], check=True, capture_output=True, text=True).stdout
        self.assertIn("open_cfw_runtime_iar_vsnprintf_engine", engine)
        for symbol in (
            "open_cfw_runtime_iar_format_bridge", "open_cfw_runtime_iar_vformat",
            "open_cfw_runtime_iar_printf_core",
        ):
            self.assertIn(symbol, adapter)
        undefined = {
            line.strip().split()[-1] for line in adapter.splitlines()
            if line.strip().startswith("U ")
        }
        self.assertEqual(undefined, {"open_cfw_runtime_iar_vsnprintf_engine"})
        engine_undefined = {
            line.strip().split()[-1] for line in engine.splitlines()
            if line.strip().startswith("U ")
        }
        self.assertEqual(engine_undefined, {
            "open_cfw_runtime_ascii_is_digit", "open_cfw_runtime_etoa",
            "open_cfw_runtime_ftoa", "open_cfw_runtime_noop_output",
            "open_cfw_runtime_ntoa_long", "open_cfw_runtime_ntoa_long_long",
            "open_cfw_runtime_parse_decimal", "open_cfw_runtime_strnlen_s",
        })

    def test_production_route_and_complete_image_are_pinned(self) -> None:
        config = json.loads(OVERLAY_CONFIG.read_text(encoding="utf-8"))
        configured = {
            item["function"]: (
                item["expected"]["offset"], item["expected"]["size"]
            )
            for item in config["relocated_leaves"]
            if item["function"] in PRODUCTION_LEAVES
        }
        self.assertEqual(configured, PRODUCTION_LEAVES)
        engine = next(
            item for item in config["relocated_leaves"]
            if item["function"] == "open_cfw_runtime_iar_vsnprintf_engine"
        )
        self.assertEqual(
            (
                engine["source"]["path"], engine["source"]["size"],
                engine["source"]["sha256"], len(engine["relocations"]),
            ),
            (
                "components/shared/runtime/runtime_iar_vsnprintf_engine.c",
                656,
                "0003cb77941835e990c5892fe5b87e2d4f753a4711ab9372f959e1e3dd990740",
                12,
            ),
        )
        patch = next(
            item for item in config["patch_sites"]
            if item["name"] == "replace_iar_printf_core"
        )
        self.assertEqual(
            (
                patch["runtime_address"], patch["expected_size"],
                patch["expected_sha256"], patch["branch"],
                patch["target_function"], patch["profiles"],
            ),
            (
                0x00481836, 3_256,
                "0ace800002b34fa464fd3a816691e77df43a7919b2747ef608d0b89213786fb0",
                "b_w", "open_cfw_runtime_iar_printf_core", ["apple-clang"],
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
            (report["overlay"]["size"], report["overlay"]["sha256"]),
            OVERLAY_PIN,
        )
        self.assertEqual(
            (report["component"]["size"], report["component"]["sha256"]),
            COMPONENT_PIN,
        )

        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        main = manifest["component_overrides"]["apollo_main"]
        self.assertEqual(
            (main["provider"]["size"], main["provider"]["sha256"]),
            COMPONENT_PIN,
        )
        region = next(
            item for item in main["regions"]
            if item["name"] == "iar_format_output_source_closure"
        )
        self.assertEqual(
            (
                region["file_offset"], region["size"],
                region["target_address"], region["address_status"],
            ),
            (3_859_712, 3_662, 0x007E64E0, "source_compiled"),
        )
        self.assertEqual(
            (manifest["package"]["expected_size"], manifest["package"]["expected_sha256"]),
            PACKAGE_PIN,
        )

        package = PACKAGE.read_bytes()
        self.assertEqual(
            (len(package), hashlib.sha256(package).hexdigest()), PACKAGE_PIN
        )
        plan_bytes = FLASH_PLAN.read_bytes()
        self.assertEqual(
            (len(plan_bytes), hashlib.sha256(plan_bytes).hexdigest()),
            FLASH_PLAN_PIN,
        )
        plan = json.loads(plan_bytes)
        self.assertEqual(plan["package_sha256"], PACKAGE_PIN[1])
        self.assertEqual(
            tuple(
                len(plan[key]) for key in (
                    "flash_regions", "unresolved_flash_regions",
                    "container_only_regions", "protected_regions",
                )
            ),
            (7_104, 0, 8, 6),
        )


if __name__ == "__main__":
    unittest.main()
