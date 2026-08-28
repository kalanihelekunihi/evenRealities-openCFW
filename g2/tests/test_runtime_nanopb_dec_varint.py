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
SOURCE = ROOT / "components/shared/nanopb/runtime_nanopb_dec_varint.c"
INCLUDE = SOURCE.parent
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
ANALYZER = ROOT / "tools/analyze_g2_nanopb_dec_varint.py"
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
#include <string.h>
#include "runtime_nanopb_dec_varint.h"

static bool unsigned_success;
static bool signed_success;
static uint64_t unsigned_value;
static int64_t signed_value;
static struct open_cfw_nanopb_istream stream;
static const char sticky_error[] = "sticky";

bool open_cfw_nanopb_decode_varint(
    struct open_cfw_nanopb_istream *unused,
    uint64_t *destination
)
{
    (void)unused;
    if (!unsigned_success) return false;
    *destination = unsigned_value;
    return true;
}

bool open_cfw_nanopb_decode_svarint(
    struct open_cfw_nanopb_istream *unused,
    int64_t *destination
)
{
    (void)unused;
    if (!signed_success) return false;
    *destination = signed_value;
    return true;
}

void open_cfw_test_configure(
    bool unsigned_ok,
    uint64_t unsigned_result,
    bool signed_ok,
    int64_t signed_result,
    bool sticky
)
{
    memset(&stream, 0, sizeof(stream));
    unsigned_success = unsigned_ok;
    unsigned_value = unsigned_result;
    signed_success = signed_ok;
    signed_value = signed_result;
    stream.errmsg = sticky ? sticky_error : (const char *)0;
}

bool open_cfw_test_run(uint8_t ltype, uint16_t data_size, uint64_t *storage)
{
    struct open_cfw_nanopb_field_iter field;
    memset(&field, 0, sizeof(field));
    field.type = ltype;
    field.data_size = data_size;
    field.data = storage;
    return open_cfw_nanopb_dec_varint(&stream, &field);
}

const char *open_cfw_test_error(void)
{
    return stream.errmsg;
}
"""


class NanopbDecVarintTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.directory = Path(cls.temporary.name)
        provider = cls.directory / "provider.c"
        provider.write_text(HOST_PROVIDER, encoding="utf-8")
        cls.library_path = cls.directory / "dec_varint.so"
        subprocess.run(
            [
                os.environ.get("CC", "cc"), "-std=c11", "-shared", "-fPIC",
                "-O2", "-Wall", "-Wextra", "-Werror", f"-I{INCLUDE}",
                str(SOURCE), str(provider), "-o", str(cls.library_path),
            ],
            check=True,
            cwd=ROOT,
        )
        cls.library = ctypes.CDLL(str(cls.library_path))
        cls.library.open_cfw_test_configure.argtypes = [
            ctypes.c_bool, ctypes.c_uint64, ctypes.c_bool, ctypes.c_int64,
            ctypes.c_bool,
        ]
        cls.library.open_cfw_test_run.argtypes = [
            ctypes.c_uint8, ctypes.c_uint16, ctypes.POINTER(ctypes.c_uint64),
        ]
        cls.library.open_cfw_test_run.restype = ctypes.c_bool
        cls.library.open_cfw_test_error.restype = ctypes.c_char_p

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def run_case(
        self,
        ltype: int,
        size: int,
        *,
        unsigned: int = 0,
        signed: int = 0,
        unsigned_ok: bool = True,
        signed_ok: bool = True,
        sticky: bool = False,
        initial: int = 0xA5A5A5A5A5A5A5A5,
    ) -> tuple[bool, int, bytes | None]:
        self.library.open_cfw_test_configure(
            unsigned_ok, unsigned, signed_ok, signed, sticky,
        )
        storage = ctypes.c_uint64(initial)
        status = self.library.open_cfw_test_run(ltype, size, ctypes.byref(storage))
        return status, storage.value, self.library.open_cfw_test_error()

    def test_upstream_size_dispatch_and_range_semantics(self) -> None:
        self.assertEqual(self.run_case(2, 8, unsigned=2**64 - 1)[:2], (True, 2**64 - 1))
        self.assertEqual(self.run_case(2, 4, unsigned=0xFFFFFFFF)[:2], (True, 0xA5A5A5A5FFFFFFFF))
        status, value, error = self.run_case(2, 4, unsigned=0x1_0000_0000)
        self.assertFalse(status)
        self.assertEqual(value, 0xA5A5A5A500000000)
        self.assertEqual(error, b"integer too large")

        self.assertEqual(self.run_case(1, 4, unsigned=0xFFFFFFFF)[:2], (True, 0xA5A5A5A5FFFFFFFF))
        self.assertEqual(self.run_case(1, 8, unsigned=2**64 - 1)[:2], (True, 2**64 - 1))
        self.assertEqual(self.run_case(3, 1, signed=127)[:2], (True, 0xA5A5A5A5A5A5A57F))
        status, value, error = self.run_case(3, 1, signed=128)
        self.assertFalse(status)
        self.assertEqual(value, 0xA5A5A5A5A5A5A580)
        self.assertEqual(error, b"integer too large")

    def test_failures_invalid_size_and_sticky_error(self) -> None:
        initial = 0x0123456789ABCDEF
        self.assertEqual(
            self.run_case(2, 8, unsigned_ok=False, initial=initial),
            (False, initial, None),
        )
        status, value, error = self.run_case(2, 3, unsigned=7, initial=initial)
        self.assertEqual((status, value, error), (False, initial, b"invalid data_size"))
        status, _, error = self.run_case(2, 3, unsigned=7, sticky=True)
        self.assertFalse(status)
        self.assertEqual(error, b"sticky")

    def test_analyzer_closes_complete_stock_boundary(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ANALYZER), "--json"],
            check=True, capture_output=True, text=True, cwd=ROOT,
        )
        report = json.loads(result.stdout)
        self.assertEqual(report["stock"]["size"], 380)
        self.assertEqual(report["ingress"]["interior"], [])
        self.assertEqual(report["ingress"]["pointers"], [])
        self.assertEqual(len(report["outgoing"]), 3)
        self.assertEqual(report["decision"]["executable_stock_seams"], 0)
        self.assertEqual(report["decision"]["stock_data_seams"], 0)

    def test_apple_target_object_and_production_registration_are_pinned(self) -> None:
        clang = Path("/usr/bin/clang")
        version = subprocess.run(
            [str(clang), "--version"], check=True, capture_output=True, text=True,
        ).stdout
        if not version.startswith("Apple clang version 21.0.0"):
            self.skipTest("reviewed Apple Clang 21.0.0 is unavailable")
        object_path = self.directory / "dec_varint.o"
        subprocess.run(
            [str(clang), *TARGET_FLAGS, f"-I{INCLUDE}", "-c", str(SOURCE), "-o", str(object_path)],
            check=True, cwd=ROOT,
        )
        data = object_path.read_bytes()
        self.assertEqual(
            (len(data), hashlib.sha256(data).hexdigest()),
            (1452, "02f0886edcb5466cafec9d3904bda0a1ab88a8ab1ae5b9ecd12fb0f5d2c82e20"),
        )

        overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
        leaf = next(
            item for item in overlay["relocated_leaves"]
            if item["function"] == "open_cfw_nanopb_dec_varint"
        )
        self.assertEqual(leaf["expected"]["offset"], 185396)
        self.assertEqual(leaf["expected"]["closure_size"], 340)
        site = next(
            item for item in overlay["patch_sites"]
            if item["name"] == "replace_nanopb_dec_varint"
        )
        self.assertEqual((site["runtime_address"], site["expected_size"]), (0x004901D6, 380))

        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        regions = {
            item["name"]: item
            for item in manifest["component_overrides"]["apollo_main"]["regions"]
        }
        self.assertEqual(regions["nanopb_dec_varint_source_replacement"]["size"], 380)
        self.assertEqual(regions["apollo_nanopb_dec_varint_source_leaf"]["size"], 304)
        self.assertEqual(regions["apollo_nanopb_dec_varint_error_rodata"]["size"], 36)


if __name__ == "__main__":
    unittest.main()
