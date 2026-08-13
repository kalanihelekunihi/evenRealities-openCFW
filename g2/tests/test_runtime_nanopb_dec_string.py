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
SOURCE = ROOT / "components/shared/nanopb/runtime_nanopb_dec_string.c"
INCLUDE = SOURCE.parent
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
ANALYZER = ROOT / "tools/analyze_g2_nanopb_dec_string.py"
TARGET_FLAGS = (
    "--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
    "-fdata-sections", "-Wall", "-Wextra", "-Werror", "-fno-ident",
)

HOST_PROVIDER = r"""
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include "runtime_nanopb_dec_string.h"

static bool decode_success;
static bool read_success;
static uint32_t decoded_size;
static size_t observed_count;
static uint8_t *observed_buffer;
static struct open_cfw_nanopb_istream stream;
static struct open_cfw_nanopb_field_iter field;
static uint8_t storage[16];
static const char sticky_error[] = "sticky";

bool open_cfw_nanopb_decode_varint32(
    struct open_cfw_nanopb_istream *unused,
    uint32_t *destination
)
{
    (void)unused;
    if (!decode_success) return false;
    *destination = decoded_size;
    return true;
}

bool open_cfw_nanopb_read(
    struct open_cfw_nanopb_istream *unused,
    uint8_t *buffer,
    size_t count
)
{
    size_t i;
    (void)unused;
    observed_buffer = buffer;
    observed_count = count;
    if (!read_success) return false;
    for (i = 0; i < count; ++i) buffer[i] = (uint8_t)('a' + i);
    return true;
}

void open_cfw_test_configure(
    uint32_t size,
    bool decode_ok,
    bool read_ok,
    uint8_t type,
    uint16_t data_size,
    bool sticky
)
{
    memset(&stream, 0, sizeof(stream));
    memset(&field, 0, sizeof(field));
    memset(storage, 0xA5, sizeof(storage));
    decode_success = decode_ok;
    read_success = read_ok;
    decoded_size = size;
    observed_count = (size_t)-1;
    observed_buffer = (uint8_t *)0;
    stream.errmsg = sticky ? sticky_error : (const char *)0;
    field.type = type;
    field.data_size = data_size;
    field.data = storage;
}

bool open_cfw_test_run(void) { return open_cfw_nanopb_dec_string(&stream, &field); }
const char *open_cfw_test_error(void) { return stream.errmsg; }
uint8_t open_cfw_test_byte(size_t index) { return storage[index]; }
size_t open_cfw_test_observed_count(void) { return observed_count; }
bool open_cfw_test_buffer_is_destination(void) { return observed_buffer == storage; }
"""


class NanopbDecStringTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.directory = Path(cls.temporary.name)
        provider = cls.directory / "provider.c"
        provider.write_text(HOST_PROVIDER, encoding="utf-8")
        cls.library_path = cls.directory / "dec_string.so"
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
            ctypes.c_uint32, ctypes.c_bool, ctypes.c_bool, ctypes.c_uint8,
            ctypes.c_uint16, ctypes.c_bool,
        ]
        cls.library.open_cfw_test_run.restype = ctypes.c_bool
        cls.library.open_cfw_test_error.restype = ctypes.c_char_p
        cls.library.open_cfw_test_byte.argtypes = [ctypes.c_size_t]
        cls.library.open_cfw_test_byte.restype = ctypes.c_uint8
        cls.library.open_cfw_test_observed_count.restype = ctypes.c_size_t
        cls.library.open_cfw_test_buffer_is_destination.restype = ctypes.c_bool

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def configure(
        self,
        size: int,
        *,
        decode_ok: bool = True,
        read_ok: bool = True,
        type_: int = 0,
        data_size: int = 16,
        sticky: bool = False,
    ) -> None:
        self.library.open_cfw_test_configure(
            size, decode_ok, read_ok, type_, data_size, sticky,
        )

    def test_success_reads_string_and_retains_terminator(self) -> None:
        self.configure(4, data_size=5)
        self.assertTrue(self.library.open_cfw_test_run())
        self.assertEqual(self.library.open_cfw_test_observed_count(), 4)
        self.assertTrue(self.library.open_cfw_test_buffer_is_destination())
        self.assertEqual(
            [self.library.open_cfw_test_byte(i) for i in range(5)],
            [ord("a"), ord("b"), ord("c"), ord("d"), 0],
        )

    def test_decode_and_read_failures_preserve_write_order(self) -> None:
        self.configure(4, decode_ok=False)
        self.assertFalse(self.library.open_cfw_test_run())
        self.assertEqual(self.library.open_cfw_test_byte(4), 0xA5)

        self.configure(4, read_ok=False)
        self.assertFalse(self.library.open_cfw_test_run())
        self.assertEqual(self.library.open_cfw_test_byte(4), 0)
        self.assertEqual(self.library.open_cfw_test_observed_count(), 4)

    def test_size_pointer_storage_and_sticky_failures(self) -> None:
        self.configure(0xFFFFFFFF)
        self.assertFalse(self.library.open_cfw_test_run())
        self.assertEqual(self.library.open_cfw_test_error(), b"size too large")

        self.configure(4, type_=0x80)
        self.assertFalse(self.library.open_cfw_test_run())
        self.assertEqual(self.library.open_cfw_test_error(), b"no malloc support")

        self.configure(4, data_size=4)
        self.assertFalse(self.library.open_cfw_test_run())
        self.assertEqual(self.library.open_cfw_test_error(), b"string overflow")
        self.assertEqual(self.library.open_cfw_test_byte(4), 0xA5)

        self.configure(0xFFFFFFFF, sticky=True)
        self.assertFalse(self.library.open_cfw_test_run())
        self.assertEqual(self.library.open_cfw_test_error(), b"sticky")

    def test_zero_length_string_is_terminated_and_read(self) -> None:
        self.configure(0, data_size=1)
        self.assertTrue(self.library.open_cfw_test_run())
        self.assertEqual(self.library.open_cfw_test_byte(0), 0)
        self.assertEqual(self.library.open_cfw_test_observed_count(), 0)

    def test_analyzer_closes_complete_stock_boundary(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ANALYZER), "--json"],
            check=True, capture_output=True, text=True, cwd=ROOT,
        )
        report = json.loads(result.stdout)
        self.assertEqual(report["stock"]["size"], 158)
        self.assertEqual(report["ingress"]["interior"], [])
        self.assertEqual(report["ingress"]["stored_patterns"], [])
        self.assertEqual(len(report["outgoing"]), 2)
        self.assertEqual(report["decision"]["executable_stock_seams"], 0)
        self.assertEqual(report["decision"]["stock_data_seams"], 0)
        self.assertTrue(report["decision"]["production_integrated"])

    def test_apple_object_and_production_registration_are_pinned(self) -> None:
        clang = Path("/usr/bin/clang")
        version = subprocess.run(
            [str(clang), "--version"], check=True, capture_output=True, text=True,
        ).stdout
        if not version.startswith("Apple clang version 21.0.0"):
            self.skipTest("reviewed Apple Clang 21.0.0 is unavailable")
        object_path = self.directory / "dec_string.o"
        subprocess.run(
            [str(clang), *TARGET_FLAGS, f"-I{INCLUDE}", "-c", str(SOURCE), "-o", str(object_path)],
            check=True, cwd=ROOT,
        )
        data = object_path.read_bytes()
        self.assertEqual(
            (len(data), hashlib.sha256(data).hexdigest()),
            (1260, "ffbb4295bfecc6a32306669cf6b367e1692cfc56766f5bcefa72aa45c29b3f91"),
        )

        overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
        leaf = next(x for x in overlay["relocated_leaves"] if x["function"] == "open_cfw_nanopb_dec_string")
        self.assertEqual((leaf["expected"]["offset"], leaf["expected"]["closure_size"]), (126132, 163))
        site = next(x for x in overlay["patch_sites"] if x["name"] == "replace_nanopb_dec_string")
        self.assertEqual((site["runtime_address"], site["expected_size"]), (0x004903EA, 158))

        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        regions = {x["name"]: x for x in manifest["component_overrides"]["apollo_main"]["regions"]}
        self.assertEqual(regions["nanopb_dec_string_source_replacement"]["size"], 158)
        self.assertEqual(regions["apollo_nanopb_dec_string_source_alignment"]["size"], 2)
        self.assertEqual(regions["apollo_nanopb_dec_string_source_leaf"]["size"], 114)
        self.assertEqual(regions["apollo_nanopb_dec_string_error_rodata"]["size"], 49)


if __name__ == "__main__":
    unittest.main()
