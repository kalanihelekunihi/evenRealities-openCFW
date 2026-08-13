from __future__ import annotations

import ctypes
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/shared/nanopb/runtime_nanopb_dec_submessage.c"
INCLUDE = SOURCE.parent
ANALYZER = ROOT / "tools/analyze_g2_nanopb_dec_submessage.py"

HOST_PROVIDER = r"""
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include "runtime_nanopb_dec_submessage.h"

static struct open_cfw_nanopb_istream parent_stream;
static struct open_cfw_nanopb_field_iter field;
static struct open_cfw_nanopb_callback callback_record;
static uint8_t destination[8];
static uint8_t descriptor;
static bool make_ok, close_ok, callback_ok, inner_ok;
static bool callback_enabled, callback_consumes;
static unsigned int callback_calls, inner_calls, close_calls;
static unsigned int observed_flags;
static void *observed_destination;
static const void *observed_descriptor;
static void *initial_argument = (void *)(uintptr_t)0x1234U;
static void *updated_argument = (void *)(uintptr_t)0x5678U;

bool open_cfw_nanopb_make_string_substream(
    struct open_cfw_nanopb_istream *stream,
    struct open_cfw_nanopb_istream *substream)
{
    (void)stream;
    if (!make_ok) return false;
    memset(substream, 0, sizeof(*substream));
    substream->bytes_left = 7U;
    return true;
}

bool open_cfw_nanopb_close_string_substream(
    struct open_cfw_nanopb_istream *stream,
    struct open_cfw_nanopb_istream *substream)
{
    (void)stream; (void)substream;
    close_calls++;
    return close_ok;
}

bool open_cfw_nanopb_decode_inner(
    struct open_cfw_nanopb_istream *stream,
    const void *fields,
    void *dest,
    unsigned int flags)
{
    (void)stream;
    inner_calls++;
    observed_flags = flags;
    observed_destination = dest;
    observed_descriptor = fields;
    return inner_ok;
}

static bool message_callback(
    struct open_cfw_nanopb_istream *stream,
    const struct open_cfw_nanopb_field_iter *unused,
    void **argument)
{
    (void)unused;
    callback_calls++;
    *argument = updated_argument;
    if (callback_consumes) stream->bytes_left = 0U;
    return callback_ok;
}

void open_cfw_test_configure(
    bool make_success, bool close_success, bool callback_success,
    bool inner_success, bool use_callback, bool consume,
    bool valid_descriptor, uint8_t type)
{
    memset(&parent_stream, 0, sizeof(parent_stream));
    memset(&field, 0, sizeof(field));
    memset(&callback_record, 0, sizeof(callback_record));
    make_ok = make_success; close_ok = close_success;
    callback_ok = callback_success; inner_ok = inner_success;
    callback_enabled = use_callback; callback_consumes = consume;
    callback_calls = inner_calls = close_calls = observed_flags = 0U;
    observed_destination = NULL; observed_descriptor = NULL;
    field.type = type;
    field.data = destination;
    field.submessage_descriptor = valid_descriptor ? &descriptor : NULL;
    callback_record.decode = callback_enabled ? message_callback : NULL;
    callback_record.argument = initial_argument;
    field.size = &callback_record + 1;
}

bool open_cfw_test_run(void) { return open_cfw_nanopb_dec_submessage(&parent_stream, &field); }
unsigned int open_cfw_test_callback_calls(void) { return callback_calls; }
unsigned int open_cfw_test_inner_calls(void) { return inner_calls; }
unsigned int open_cfw_test_close_calls(void) { return close_calls; }
unsigned int open_cfw_test_flags(void) { return observed_flags; }
bool open_cfw_test_inner_arguments_match(void) {
    return observed_destination == destination && observed_descriptor == &descriptor;
}
bool open_cfw_test_callback_argument_updated(void) {
    return callback_record.argument == updated_argument;
}
const char *open_cfw_test_error(void) { return parent_stream.errmsg; }
"""


class NanopbDecSubmessageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.directory = Path(cls.temporary.name)
        provider = cls.directory / "provider.c"
        provider.write_text(HOST_PROVIDER, encoding="utf-8")
        library_path = cls.directory / "dec_submessage.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-std=c11", "-shared", "-fPIC", "-O2",
             "-Wall", "-Wextra", "-Werror", f"-I{INCLUDE}", str(SOURCE), str(provider),
             "-o", str(library_path)],
            check=True, cwd=ROOT,
        )
        cls.library = ctypes.CDLL(str(library_path))
        cls.library.open_cfw_test_configure.argtypes = [ctypes.c_bool] * 7 + [ctypes.c_uint8]
        cls.library.open_cfw_test_run.restype = ctypes.c_bool
        for name in ("callback_calls", "inner_calls", "close_calls", "flags"):
            getattr(cls.library, f"open_cfw_test_{name}").restype = ctypes.c_uint
        cls.library.open_cfw_test_inner_arguments_match.restype = ctypes.c_bool
        cls.library.open_cfw_test_callback_argument_updated.restype = ctypes.c_bool
        cls.library.open_cfw_test_error.restype = ctypes.c_char_p

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def configure(self, *, make=True, close=True, callback=True, inner=True,
                  use_callback=False, consume=False, descriptor=True, type_=0) -> None:
        self.library.open_cfw_test_configure(
            make, close, callback, inner, use_callback, consume, descriptor, type_)

    def test_static_nonrepeated_submessage_uses_noinit_and_closes(self) -> None:
        self.configure()
        self.assertTrue(self.library.open_cfw_test_run())
        self.assertEqual(self.library.open_cfw_test_inner_calls(), 1)
        self.assertEqual(self.library.open_cfw_test_flags(), 1)
        self.assertTrue(self.library.open_cfw_test_inner_arguments_match())
        self.assertEqual(self.library.open_cfw_test_close_calls(), 1)

    def test_repeated_or_nonstatic_submessage_is_initialized(self) -> None:
        for type_ in (0x20, 0x40, 0x80):
            with self.subTest(type_=type_):
                self.configure(type_=type_)
                self.assertTrue(self.library.open_cfw_test_run())
                self.assertEqual(self.library.open_cfw_test_flags(), 0)

    def test_message_callback_can_consume_or_defer_decode(self) -> None:
        self.configure(use_callback=True, consume=True, type_=0x09)
        self.assertTrue(self.library.open_cfw_test_run())
        self.assertEqual(self.library.open_cfw_test_callback_calls(), 1)
        self.assertEqual(self.library.open_cfw_test_inner_calls(), 0)
        self.assertTrue(self.library.open_cfw_test_callback_argument_updated())

        self.configure(use_callback=True, consume=False, type_=0x09)
        self.assertTrue(self.library.open_cfw_test_run())
        self.assertEqual(self.library.open_cfw_test_callback_calls(), 1)
        self.assertEqual(self.library.open_cfw_test_inner_calls(), 1)

    def test_callback_decode_and_close_failure_order_is_preserved(self) -> None:
        self.configure(use_callback=True, callback=False, type_=0x09)
        self.assertFalse(self.library.open_cfw_test_run())
        self.assertEqual(self.library.open_cfw_test_inner_calls(), 0)
        self.assertEqual(self.library.open_cfw_test_close_calls(), 1)

        self.configure(close=False)
        self.assertFalse(self.library.open_cfw_test_run())
        self.assertEqual(self.library.open_cfw_test_inner_calls(), 1)
        self.assertEqual(self.library.open_cfw_test_close_calls(), 1)

    def test_make_and_descriptor_failures_match_upstream_early_returns(self) -> None:
        self.configure(make=False)
        self.assertFalse(self.library.open_cfw_test_run())
        self.assertEqual(self.library.open_cfw_test_close_calls(), 0)
        self.configure(descriptor=False)
        self.assertFalse(self.library.open_cfw_test_run())
        self.assertEqual(self.library.open_cfw_test_error(), b"invalid field descriptor")
        self.assertEqual(self.library.open_cfw_test_close_calls(), 0)

    def test_analyzer_pins_boundary_ingress_and_both_seam_classes(self) -> None:
        result = subprocess.run([sys.executable, str(ANALYZER), "--json"], check=True,
                                capture_output=True, text=True, cwd=ROOT)
        report = json.loads(result.stdout)
        self.assertEqual(report["stock"]["size"], 172)
        self.assertEqual(report["ingress"]["interior"], [])
        self.assertEqual(len(report["ingress"]["stored_patterns"]), 1)
        self.assertEqual([x["ownership"] for x in report["outgoing"]],
                         ["source", "stock", "source"])
        self.assertEqual(report["decision"]["executable_stock_seams"], 1)
        self.assertEqual(report["decision"]["dynamic_callback_seams"], 1)
        self.assertTrue(report["decision"]["production_integrated"])


if __name__ == "__main__":
    unittest.main()
