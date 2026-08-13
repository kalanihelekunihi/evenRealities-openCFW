from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/shared/nanopb/runtime_nanopb_decode_inner.c"
INCLUDE = SOURCE.parent
ANALYZER = ROOT / "tools/analyze_g2_nanopb_decode_inner.py"

PROVIDER = r"""
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include "runtime_nanopb_decode_inner.h"

static int scenario;
static struct open_cfw_nanopb_istream stream;
static struct open_cfw_nanopb_msgdesc descriptor;
static void *extension_record;
static unsigned int tag_calls, skip_calls, extension_calls, field_calls;

bool open_cfw_nanopb_field_iter_begin(struct open_cfw_nanopb_field_iter *iter,
    const struct open_cfw_nanopb_msgdesc *fields, void *destination)
{
    memset(iter, 0, sizeof(*iter));
    iter->descriptor = fields;
    iter->message = destination;
    return scenario != 1;
}

bool open_cfw_nanopb_message_set_to_defaults(struct open_cfw_nanopb_field_iter *iter)
{ (void)iter; return scenario != 2; }

bool open_cfw_nanopb_decode_tag(struct open_cfw_nanopb_istream *unused,
    uint8_t *wire, uint32_t *tag, bool *eof)
{
    (void)unused; tag_calls++; *wire = 0U; *tag = 1U; *eof = false;
    if (scenario == 3) { *tag = 0U; return true; }
    if (scenario == 5) { *eof = true; return false; }
    if (scenario == 6) return false;
    return true;
}

bool open_cfw_nanopb_field_iter_find(struct open_cfw_nanopb_field_iter *iter,
    uint32_t tag)
{
    (void)tag;
    if (scenario == 7 || scenario == 8) return false;
    if (scenario == 10) {
        iter->type = 0x20U; iter->index = 1U; iter->array_size = 2U;
        iter->size = &iter->array_size;
    } else {
        iter->type = 0U; iter->required_field_index = 0U;
    }
    return true;
}

bool open_cfw_nanopb_field_iter_find_extension(struct open_cfw_nanopb_field_iter *iter)
{
    if (scenario != 8) return false;
    iter->data = &extension_record; iter->tag = 1U; return true;
}

bool open_cfw_nanopb_decode_extension(struct open_cfw_nanopb_istream *value,
    uint32_t tag, unsigned int wire, void *extensions)
{
    (void)tag; (void)wire; (void)extensions; extension_calls++;
    if (scenario == 8) value->bytes_left = 0U;
    return true;
}

bool open_cfw_nanopb_skip_field(struct open_cfw_nanopb_istream *value,
    uint8_t wire)
{ (void)wire; skip_calls++; value->bytes_left = 0U; return true; }

bool open_cfw_nanopb_decode_field(struct open_cfw_nanopb_istream *value,
    unsigned int wire, struct open_cfw_nanopb_field_iter *iter)
{
    (void)wire; field_calls++;
    if (scenario == 11) return false;
    if (scenario == 10) (*(uint16_t *)iter->size)++;
    value->bytes_left = 0U; return true;
}

bool open_cfw_test_run(int selected, unsigned int flags, const char *existing)
{
    static uint8_t destination;
    scenario = selected; tag_calls = skip_calls = extension_calls = field_calls = 0U;
    memset(&stream, 0, sizeof(stream)); memset(&descriptor, 0, sizeof(descriptor));
    extension_record = (void *)(uintptr_t)1U;
    stream.bytes_left = (selected == 1 || selected == 2 || selected == 9) ? 0U : 1U;
    stream.errmsg = existing;
    descriptor.required_field_count = selected == 9 ? 1U : 0U;
    return open_cfw_nanopb_decode_inner(&stream, &descriptor, &destination, flags);
}
const char *open_cfw_test_error(void) { return stream.errmsg; }
unsigned int open_cfw_test_skip_calls(void) { return skip_calls; }
unsigned int open_cfw_test_extension_calls(void) { return extension_calls; }
unsigned int open_cfw_test_field_calls(void) { return field_calls; }
"""


class NanopbDecodeInnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        directory = Path(cls.temporary.name)
        provider = directory / "provider.c"
        provider.write_text(PROVIDER, encoding="utf-8")
        library = directory / "decode_inner.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-std=c11", "-shared", "-fPIC", "-O2",
             "-Wall", "-Wextra", "-Werror", f"-I{INCLUDE}", str(SOURCE),
             str(provider), "-o", str(library)], check=True, cwd=ROOT,
        )
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_test_run.argtypes = [ctypes.c_int, ctypes.c_uint, ctypes.c_char_p]
        cls.lib.open_cfw_test_run.restype = ctypes.c_bool
        cls.lib.open_cfw_test_error.restype = ctypes.c_char_p

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def run_case(self, scenario: int, flags: int = 0, existing: bytes | None = None) -> bool:
        return self.lib.open_cfw_test_run(scenario, flags, existing)

    def test_initialization_and_sticky_errors(self) -> None:
        self.assertTrue(self.run_case(1))
        self.assertFalse(self.run_case(2))
        self.assertEqual(self.lib.open_cfw_test_error(), b"failed to set defaults")
        self.assertFalse(self.run_case(2, existing=b"prior"))
        self.assertEqual(self.lib.open_cfw_test_error(), b"prior")
        self.assertTrue(self.run_case(2, flags=1))

    def test_tag_termination_and_failure_paths(self) -> None:
        self.assertFalse(self.run_case(3))
        self.assertEqual(self.lib.open_cfw_test_error(), b"zero tag")
        self.assertTrue(self.run_case(3, flags=4))
        self.assertTrue(self.run_case(5))
        self.assertFalse(self.run_case(6))

    def test_unknown_extension_and_known_field_routing(self) -> None:
        self.assertTrue(self.run_case(7))
        self.assertEqual(self.lib.open_cfw_test_skip_calls(), 1)
        self.assertTrue(self.run_case(8))
        self.assertEqual(self.lib.open_cfw_test_extension_calls(), 1)
        self.assertEqual(self.lib.open_cfw_test_skip_calls(), 0)
        self.assertTrue(self.run_case(4))
        self.assertEqual(self.lib.open_cfw_test_field_calls(), 1)

    def test_required_fixed_count_and_field_failure(self) -> None:
        self.assertFalse(self.run_case(9))
        self.assertEqual(self.lib.open_cfw_test_error(), b"missing required field")
        self.assertFalse(self.run_case(10))
        self.assertEqual(self.lib.open_cfw_test_error(), b"wrong size for fixed count field")
        self.assertFalse(self.run_case(11))

    def test_fail_closed_analyzer(self) -> None:
        subprocess.run(["python3", str(ANALYZER)], check=True, cwd=ROOT)


if __name__ == "__main__":
    unittest.main()
