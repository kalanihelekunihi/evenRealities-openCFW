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


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "components/shared/nanopb/runtime_nanopb_decode_bool.c"
ADAPTER = ROOT / "components/shared/nanopb/runtime_nanopb_dec_bool.c"
INCLUDE = PUBLIC.parent
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
ANALYZER = ROOT / "tools/analyze_g2_nanopb_bool_cluster.py"

TARGET_FLAGS = (
    "--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
    "-fdata-sections", "-Wall", "-Wextra", "-Werror", "-fno-ident",
)

HOST_PROVIDER = r"""
#include <stdbool.h>
#include <stdint.h>
#include "runtime_nanopb_dec_bool.h"

static bool test_success;
static uint32_t test_value;

bool open_cfw_nanopb_decode_varint32(
    struct open_cfw_nanopb_istream *stream,
    uint32_t *destination
)
{
    (void)stream;
    if (!test_success) return false;
    *destination = test_value;
    return true;
}

void open_cfw_test_configure(bool success, uint32_t value)
{
    test_success = success;
    test_value = value;
}

bool open_cfw_test_adapter(bool *destination)
{
    struct open_cfw_nanopb_field_iter field = {0};
    field.data = destination;
    return open_cfw_nanopb_dec_bool((void *)0, &field);
}
"""


class NanopbBoolClusterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.directory = Path(cls.temporary.name)
        provider = cls.directory / "provider.c"
        provider.write_text(HOST_PROVIDER, encoding="utf-8")
        cls.library_path = cls.directory / "bool_cluster.so"
        subprocess.run(
            [
                os.environ.get("CC", "cc"), "-std=c11", "-shared", "-fPIC",
                "-O2", "-Wall", "-Wextra", "-Werror", f"-I{INCLUDE}",
                str(PUBLIC), str(ADAPTER), str(provider), "-o", str(cls.library_path),
            ],
            check=True,
            cwd=ROOT,
        )
        cls.library = ctypes.CDLL(str(cls.library_path))
        cls.library.open_cfw_test_configure.argtypes = [ctypes.c_bool, ctypes.c_uint32]
        cls.library.open_cfw_nanopb_decode_bool.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_bool)]
        cls.library.open_cfw_nanopb_decode_bool.restype = ctypes.c_bool
        cls.library.open_cfw_test_adapter.argtypes = [ctypes.POINTER(ctypes.c_bool)]
        cls.library.open_cfw_test_adapter.restype = ctypes.c_bool

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_public_and_adapter_match_boolean_wire_semantics(self) -> None:
        for adapter in (False, True):
            invoke = self.library.open_cfw_test_adapter if adapter else (
                lambda destination: self.library.open_cfw_nanopb_decode_bool(None, destination)
            )
            for value, expected in ((0, False), (1, True), (2, True), (0xFFFFFFFF, True)):
                self.library.open_cfw_test_configure(True, value)
                destination = ctypes.c_bool(not expected)
                self.assertTrue(invoke(ctypes.byref(destination)))
                self.assertEqual(destination.value, expected)

            self.library.open_cfw_test_configure(False, 0)
            destination = ctypes.c_bool(True)
            self.assertFalse(invoke(ctypes.byref(destination)))
            self.assertTrue(destination.value)

    def test_analyzer_closes_exact_stock_pair(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ANALYZER), "--json"],
            check=True, capture_output=True, text=True, cwd=ROOT,
        )
        report = json.loads(result.stdout)
        self.assertEqual(report["functions"]["pb_decode_bool"]["stock"]["size"], 36)
        self.assertEqual(report["functions"]["pb_dec_bool"]["stock"]["size"], 10)
        self.assertEqual(report["decision"]["stock_data_seams"], 0)
        self.assertTrue(report["decision"]["production_integrated"])

    def test_apple_target_objects_are_pinned(self) -> None:
        clang = Path("/usr/bin/clang")
        version = subprocess.run([str(clang), "--version"], check=True, capture_output=True, text=True).stdout
        if not version.startswith("Apple clang version 21.0.0"):
            self.skipTest("reviewed Apple Clang 21.0.0 is unavailable")
        expected = {
            PUBLIC: (936, "52b965c6ba1ed396a5407bbe83b7a8793b3a7098e371507590ac5fbc70c798c3"),
            ADAPTER: (904, "29cb46491f2b9e0afc48bfc2ddc32bb57d6504a480220b7c1fc0e05a0f2c5d53"),
        }
        for source, pin in expected.items():
            output = self.directory / (source.stem + ".o")
            subprocess.run(
                [str(clang), *TARGET_FLAGS, f"-I{INCLUDE}", "-c", str(source), "-o", str(output)],
                check=True, cwd=ROOT,
            )
            data = output.read_bytes()
            self.assertEqual((len(data), hashlib.sha256(data).hexdigest()), pin)

    def test_overlay_and_manifest_register_complete_pair(self) -> None:
        overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
        leaves = {item["function"]: item for item in overlay["relocated_leaves"]}
        self.assertEqual(leaves["open_cfw_nanopb_decode_bool"]["expected"]["offset"], 125608)
        self.assertEqual(leaves["open_cfw_nanopb_dec_bool"]["expected"]["offset"], 125636)
        sites = {item["name"]: item for item in overlay["patch_sites"]}
        self.assertEqual(sites["replace_nanopb_decode_bool"]["expected_size"], 36)
        self.assertEqual(sites["replace_nanopb_dec_bool"]["expected_size"], 10)

        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        component = manifest["component_overrides"]["apollo_main"]
        regions = {item["name"]: item for item in component["regions"]}
        self.assertEqual(regions["nanopb_decode_bool_source_replacement"]["target_address"], 0x0049012C)
        self.assertEqual(regions["nanopb_dec_bool_source_replacement"]["target_address"], 0x004901CC)
        self.assertEqual(regions["apollo_nanopb_decode_bool_source_leaf"]["size"], 28)
        self.assertEqual(regions["apollo_nanopb_dec_bool_source_leaf"]["size"], 6)


if __name__ == "__main__":
    unittest.main()
