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
SOURCE = ROOT / "components/shared/nanopb/runtime_nanopb_dec_bytes.c"
INCLUDE = SOURCE.parent
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
ANALYZER = ROOT / "tools/analyze_g2_nanopb_dec_bytes.py"
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
#include "runtime_nanopb_dec_bytes.h"

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
    for (i = 0; i < count; ++i) buffer[i] = (uint8_t)(0x30U + i);
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

bool open_cfw_test_run(void)
{
    return open_cfw_nanopb_dec_bytes(&stream, &field);
}

const char *open_cfw_test_error(void) { return stream.errmsg; }
uint16_t open_cfw_test_stored_size(void)
{
    uint16_t value;
    memcpy(&value, storage, sizeof(value));
    return value;
}
uint8_t open_cfw_test_byte(size_t index) { return storage[index]; }
size_t open_cfw_test_observed_count(void) { return observed_count; }
bool open_cfw_test_buffer_is_payload(void) { return observed_buffer == storage + 2; }
"""


class NanopbDecBytesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.directory = Path(cls.temporary.name)
        provider = cls.directory / "provider.c"
        provider.write_text(HOST_PROVIDER, encoding="utf-8")
        cls.library_path = cls.directory / "dec_bytes.so"
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
        cls.library.open_cfw_test_stored_size.restype = ctypes.c_uint16
        cls.library.open_cfw_test_byte.argtypes = [ctypes.c_size_t]
        cls.library.open_cfw_test_byte.restype = ctypes.c_uint8
        cls.library.open_cfw_test_observed_count.restype = ctypes.c_size_t
        cls.library.open_cfw_test_buffer_is_payload.restype = ctypes.c_bool

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

    def test_success_writes_header_and_reads_payload(self) -> None:
        self.configure(4, data_size=6)
        self.assertTrue(self.library.open_cfw_test_run())
        self.assertEqual(self.library.open_cfw_test_stored_size(), 4)
        self.assertEqual(self.library.open_cfw_test_observed_count(), 4)
        self.assertTrue(self.library.open_cfw_test_buffer_is_payload())
        self.assertEqual([self.library.open_cfw_test_byte(i) for i in range(2, 6)], [0x30, 0x31, 0x32, 0x33])

    def test_decode_and_read_failures_preserve_upstream_ordering(self) -> None:
        self.configure(4, decode_ok=False)
        self.assertFalse(self.library.open_cfw_test_run())
        self.assertEqual(self.library.open_cfw_test_stored_size(), 0xA5A5)

        self.configure(4, read_ok=False)
        self.assertFalse(self.library.open_cfw_test_run())
        self.assertEqual(self.library.open_cfw_test_stored_size(), 4)
        self.assertEqual(self.library.open_cfw_test_observed_count(), 4)

    def test_bounds_pointer_mode_and_sticky_error(self) -> None:
        self.configure(0x10000)
        self.assertFalse(self.library.open_cfw_test_run())
        self.assertEqual(self.library.open_cfw_test_error(), b"bytes overflow")
        self.assertEqual(self.library.open_cfw_test_stored_size(), 0xA5A5)

        self.configure(4, data_size=5)
        self.assertFalse(self.library.open_cfw_test_run())
        self.assertEqual(self.library.open_cfw_test_error(), b"bytes overflow")

        self.configure(4, type_=0x80)
        self.assertFalse(self.library.open_cfw_test_run())
        self.assertEqual(self.library.open_cfw_test_error(), b"no malloc support")

        self.configure(0x10000, sticky=True)
        self.assertFalse(self.library.open_cfw_test_run())
        self.assertEqual(self.library.open_cfw_test_error(), b"sticky")

    def test_analyzer_closes_stock_boundary_and_classifies_data_pairs(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ANALYZER), "--json"],
            check=True, capture_output=True, text=True, cwd=ROOT,
        )
        report = json.loads(result.stdout)
        self.assertEqual(report["stock"]["size"], 146)
        self.assertEqual(report["ingress"]["interior"], [])
        self.assertEqual(len(report["ingress"]["classified_data_collisions"]), 2)
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
        object_path = self.directory / "dec_bytes.o"
        subprocess.run(
            [str(clang), *TARGET_FLAGS, f"-I{INCLUDE}", "-c", str(SOURCE), "-o", str(object_path)],
            check=True, cwd=ROOT,
        )
        data = object_path.read_bytes()
        self.assertEqual(
            (len(data), hashlib.sha256(data).hexdigest()),
            (1224, "976f145657ac31e8cc1561667dc970de0704377e52f32b72ad5b205f23891395"),
        )

        overlay = json.loads(OVERLAY.read_text(encoding="utf-8"))
        leaf = next(x for x in overlay["relocated_leaves"] if x["function"] == "open_cfw_nanopb_dec_bytes")
        self.assertEqual((leaf["expected"]["offset"], leaf["expected"]["closure_size"]), (125984, 146))
        site = next(x for x in overlay["patch_sites"] if x["name"] == "replace_nanopb_dec_bytes")
        self.assertEqual((site["runtime_address"], site["expected_size"]), (0x00490358, 146))

        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        regions = {x["name"]: x for x in manifest["component_overrides"]["apollo_main"]["regions"]}
        self.assertEqual(regions["nanopb_dec_bytes_source_replacement"]["size"], 146)
        self.assertEqual(regions["apollo_nanopb_dec_bytes_source_leaf"]["size"], 98)
        self.assertEqual(regions["apollo_nanopb_dec_bytes_error_rodata"]["size"], 48)


if __name__ == "__main__":
    unittest.main()
