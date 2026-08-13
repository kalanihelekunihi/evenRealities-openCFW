from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/shared/nanopb/runtime_nanopb_decode_tag.c"
INCLUDE = SOURCE.parent
ANALYZER = ROOT / "tools/analyze_g2_nanopb_decode_tag.py"

PROVIDER = r"""
#include <stdbool.h>
#include <stdint.h>
#include "runtime_nanopb_decode_tag.h"

static bool provider_status;
static bool provider_eof;
static uint32_t provider_value;
static uint8_t wire;
static uint32_t tag;
static bool eof_value;

bool open_cfw_nanopb_decode_varint32_eof(
    struct open_cfw_nanopb_istream *stream, uint32_t *destination, bool *eof)
{
    (void)stream;
    if (!provider_status) {
        if (provider_eof) *eof = true;
        return false;
    }
    *destination = provider_value;
    return true;
}

bool open_cfw_test_run(bool status, bool at_eof, uint32_t value)
{
    struct open_cfw_nanopb_istream stream = {0};
    provider_status = status; provider_eof = at_eof; provider_value = value;
    wire = 0xAAU; tag = 0xAAAAAAAAU; eof_value = true;
    return open_cfw_nanopb_decode_tag(&stream, &wire, &tag, &eof_value);
}
uint8_t open_cfw_test_wire(void) { return wire; }
uint32_t open_cfw_test_tag(void) { return tag; }
bool open_cfw_test_eof(void) { return eof_value; }
"""


class NanopbDecodeTagTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        directory = Path(cls.temporary.name)
        provider = directory / "provider.c"
        provider.write_text(PROVIDER, encoding="utf-8")
        library = directory / "decode_tag.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-std=c11", "-shared", "-fPIC", "-O2",
             "-Wall", "-Wextra", "-Werror", f"-I{INCLUDE}", str(SOURCE),
             str(provider), "-o", str(library)], check=True, cwd=ROOT,
        )
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_test_run.argtypes = [ctypes.c_bool, ctypes.c_bool, ctypes.c_uint32]
        cls.lib.open_cfw_test_run.restype = ctypes.c_bool
        cls.lib.open_cfw_test_wire.restype = ctypes.c_uint8
        cls.lib.open_cfw_test_tag.restype = ctypes.c_uint32
        cls.lib.open_cfw_test_eof.restype = ctypes.c_bool

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_success_splits_tag_and_one_byte_wire_type(self) -> None:
        self.assertTrue(self.lib.open_cfw_test_run(True, False, (0x12345 << 3) | 5))
        self.assertEqual(self.lib.open_cfw_test_tag(), 0x12345)
        self.assertEqual(self.lib.open_cfw_test_wire(), 5)
        self.assertFalse(self.lib.open_cfw_test_eof())

    def test_failure_preserves_initialized_outputs_and_eof_signal(self) -> None:
        self.assertFalse(self.lib.open_cfw_test_run(False, False, 0))
        self.assertEqual(self.lib.open_cfw_test_tag(), 0)
        self.assertEqual(self.lib.open_cfw_test_wire(), 0)
        self.assertFalse(self.lib.open_cfw_test_eof())
        self.assertFalse(self.lib.open_cfw_test_run(False, True, 0))
        self.assertTrue(self.lib.open_cfw_test_eof())

    def test_fail_closed_analyzer(self) -> None:
        subprocess.run(["python3", str(ANALYZER)], check=True, cwd=ROOT)


if __name__ == "__main__":
    unittest.main()
