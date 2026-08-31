from __future__ import annotations

import ctypes
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/shared/nanopb/runtime_nanopb_iterator_cluster.c"
HEADER = ROOT / "components/shared/nanopb/runtime_nanopb_iterator_cluster.h"
INCLUDE = SOURCE.parent

SOURCE_SIZE = 14025
SOURCE_SHA256 = "825238916fc945c521c2f1bce8042c7725c42b82c92b08271dbba529991fa06e"
HEADER_SIZE = 2_995
HEADER_SHA256 = "f9664d9eb409a731dbf1a7c664ee91f10b58b3b0f818844eab5f77fbaac8f0b2"
APPLE_OBJECT_SIZE = 4_564
APPLE_OBJECT_SHA256 = "b4049aec70c47ed1b617661d44fc400894e409f00bf472af19b34a0ff69d2ebc"

HARNESS = r"""
#include <stdbool.h>
#include <stdint.h>
#include "runtime_nanopb_iterator_cluster.h"

static uint8_t message[64];

/* field 1: one-word required static scalar at +4, size 1, tag 1 */
#define FIELD1 ((1U << 2) | (4U << 16) | (1U << 28))
/* field 2: two-word optional static field, size flag at data-1. */
#define FIELD2_0 (1U | (2U << 2) | (0x10U << 8) | (3U << 16) | (1U << 28))
#define FIELD2_1 (8U | (4U << 16))
/* field 3: extension pseudo-field at +16, tag 3. */
#define FIELD3 ((3U << 2) | (0x0AU << 8) | (16U << 16) | (4U << 28))

static const uint32_t field_info[] = {FIELD1, FIELD2_0, FIELD2_1, FIELD3};
static const struct open_cfw_nanopb_msgdesc descriptor = {
    field_info, NULL, NULL, NULL, 3U, 1U, 3U
};
static struct open_cfw_nanopb_field_iter iter;

bool open_cfw_test_begin(void)
{
    return open_cfw_nanopb_field_iter_begin(&iter, &descriptor, message);
}

bool open_cfw_test_begin_null(void)
{
    return open_cfw_nanopb_field_iter_begin(&iter, &descriptor, NULL);
}

bool open_cfw_test_next(void) { return open_cfw_nanopb_field_iter_next(&iter); }
bool open_cfw_test_find(uint32_t tag) { return open_cfw_nanopb_field_iter_find(&iter, tag); }
bool open_cfw_test_find_extension(void) { return open_cfw_nanopb_field_iter_find_extension(&iter); }
uint16_t open_cfw_test_index(void) { return iter.index; }
uint16_t open_cfw_test_info_index(void) { return iter.field_info_index; }
uint16_t open_cfw_test_required_index(void) { return iter.required_field_index; }
uint16_t open_cfw_test_tag(void) { return iter.tag; }
uintptr_t open_cfw_test_field_offset(void)
{
    return iter.field == NULL ? UINTPTR_MAX : (uintptr_t)((uint8_t *)iter.field - message);
}
uintptr_t open_cfw_test_size_offset(void)
{
    return iter.size == NULL ? UINTPTR_MAX : (uintptr_t)((uint8_t *)iter.size - message);
}

static bool callback_decode(
    struct open_cfw_nanopb_istream *stream,
    const struct open_cfw_nanopb_field_iter *field,
    void **argument)
{
    (void)field;
    *(uint32_t *)*argument += 1U;
    return stream != NULL;
}

bool open_cfw_test_callback(void)
{
    struct open_cfw_nanopb_istream stream = {0};
    struct open_cfw_nanopb_callback callback;
    struct open_cfw_nanopb_field_iter field = {0};
    uint32_t count = 0U;
    callback.functions.decode = callback_decode;
    callback.argument = &count;
    field.data_size = sizeof(callback);
    field.data = &callback;
    return open_cfw_nanopb_default_field_callback(&stream, NULL, &field)
        && count == 1U;
}
"""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class NanopbIteratorClusterRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        directory = Path(cls.temporary.name)
        harness = directory / "harness.c"
        harness.write_text(HARNESS, encoding="utf-8")
        library = directory / "iterator.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-std=c11", "-shared", "-fPIC", "-O2",
             "-Wall", "-Wextra", "-Werror", f"-I{INCLUDE}", str(SOURCE),
             str(harness), "-o", str(library)],
            check=True,
            cwd=ROOT,
        )
        cls.library = ctypes.CDLL(str(library))
        for name in (
            "open_cfw_test_begin", "open_cfw_test_begin_null", "open_cfw_test_next",
            "open_cfw_test_find_extension", "open_cfw_test_callback",
        ):
            getattr(cls.library, name).restype = ctypes.c_bool
        cls.library.open_cfw_test_find.argtypes = [ctypes.c_uint32]
        cls.library.open_cfw_test_find.restype = ctypes.c_bool
        for name in (
            "open_cfw_test_index", "open_cfw_test_info_index",
            "open_cfw_test_required_index", "open_cfw_test_tag",
        ):
            getattr(cls.library, name).restype = ctypes.c_uint16
        cls.library.open_cfw_test_field_offset.restype = ctypes.c_size_t
        cls.library.open_cfw_test_size_offset.restype = ctypes.c_size_t

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_mixed_descriptor_lengths_and_wrap(self) -> None:
        self.assertTrue(self.library.open_cfw_test_begin())
        self.assertEqual(self.library.open_cfw_test_index(), 0)
        self.assertEqual(self.library.open_cfw_test_info_index(), 0)
        self.assertEqual(self.library.open_cfw_test_tag(), 1)
        self.assertEqual(self.library.open_cfw_test_field_offset(), 4)

        self.assertTrue(self.library.open_cfw_test_next())
        self.assertEqual(self.library.open_cfw_test_index(), 1)
        self.assertEqual(self.library.open_cfw_test_info_index(), 1)
        self.assertEqual(self.library.open_cfw_test_required_index(), 1)
        self.assertEqual(self.library.open_cfw_test_tag(), 2)
        self.assertEqual(self.library.open_cfw_test_field_offset(), 8)
        self.assertEqual(self.library.open_cfw_test_size_offset(), 7)

        self.assertTrue(self.library.open_cfw_test_find_extension())
        self.assertEqual(self.library.open_cfw_test_index(), 2)
        self.assertEqual(self.library.open_cfw_test_info_index(), 3)
        self.assertEqual(self.library.open_cfw_test_tag(), 3)
        self.assertFalse(self.library.open_cfw_test_next())
        self.assertEqual(self.library.open_cfw_test_index(), 0)

    def test_find_wrap_null_message_and_callback(self) -> None:
        self.assertTrue(self.library.open_cfw_test_begin())
        self.assertTrue(self.library.open_cfw_test_next())
        self.assertTrue(self.library.open_cfw_test_find(1))
        self.assertEqual(self.library.open_cfw_test_index(), 0)
        self.assertFalse(self.library.open_cfw_test_find(9))
        self.assertTrue(self.library.open_cfw_test_begin_null())
        self.assertEqual(self.library.open_cfw_test_field_offset(), ctypes.c_size_t(-1).value)
        self.assertTrue(self.library.open_cfw_test_callback())

    def test_source_pins_and_reviewed_target_object(self) -> None:
        self.assertEqual(SOURCE.stat().st_size, SOURCE_SIZE)
        self.assertEqual(sha256(SOURCE), SOURCE_SHA256)
        self.assertEqual(HEADER.stat().st_size, HEADER_SIZE)
        self.assertEqual(sha256(HEADER), HEADER_SHA256)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "iterator.o"
            subprocess.run(
                ["clang", "-target", "thumbv7em-none-eabi", "-mthumb", "-O2",
                 "-ffreestanding", "-fno-jump-tables", "-fomit-frame-pointer",
                 "-fno-builtin", "-mno-unaligned-access", "-fno-unwind-tables",
                 "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
                 "-fdata-sections", "-Wall", "-Wextra", "-Werror", "-fno-ident",
                 f"-I{INCLUDE}", "-c", str(SOURCE.relative_to(ROOT)), "-o", str(output)],
                check=True,
                cwd=ROOT,
            )
            self.assertEqual(output.stat().st_size, APPLE_OBJECT_SIZE)
            self.assertEqual(sha256(output), APPLE_OBJECT_SHA256)
            symbols = subprocess.run(
                ["objdump", "-t", str(output)], check=True, text=True,
                stdout=subprocess.PIPE,
            ).stdout
            self.assertNotIn("*UND*", symbols)


if __name__ == "__main__":
    unittest.main()
