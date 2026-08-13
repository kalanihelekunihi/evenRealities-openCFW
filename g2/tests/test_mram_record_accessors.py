from __future__ import annotations

import os

import ctypes
import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
COMPONENT_ROOT = OPENCFW_ROOT / "components" / "apollo_main" / "core_overlay"
SOURCE = COMPONENT_ROOT / "mram_record_accessors.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "mram_record_accessors_host.c"
)
RECORD_SIZE = 200


class MramRecordAccessorsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "mram_record_accessors.dylib"
            if sys.platform == "darwin"
            else "mram_record_accessors.so"
        )
        command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(FIXTURE),
        ]
        if sys.platform == "darwin":
            command.extend(["-dynamiclib", "-o", str(library)])
        else:
            command.extend(["-shared", "-fPIC", "-o", str(library)])
        subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.loaded = ctypes.CDLL(str(library))
        cls.get_key = cls.loaded.open_cfw_mram_get_key
        cls.get_key.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint,
            ctypes.c_void_p,
        ]
        cls.get_key.restype = ctypes.c_void_p
        cls.get_address = cls.loaded.open_cfw_mram_get_peer_address
        cls.get_address.argtypes = [ctypes.c_void_p]
        cls.get_address.restype = ctypes.c_void_p
        cls.get_address_type = (
            cls.loaded.open_cfw_mram_get_peer_address_type
        )
        cls.get_address_type.argtypes = [ctypes.c_void_p]
        cls.get_address_type.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.record = (ctypes.c_ubyte * RECORD_SIZE)()
        self.base = ctypes.addressof(self.record)

    def key(
        self,
        requested_type: int,
        security_level: ctypes.c_ubyte | None,
    ) -> int | None:
        level_pointer = (
            ctypes.byref(security_level)
            if security_level is not None
            else None
        )
        return self.get_key(
            self.base,
            requested_type,
            level_pointer,
        )

    def test_local_ltk_returns_key_and_security_level(self) -> None:
        self.record[0x2E] = 0x01
        self.record[0x4E] = 0xA7
        security_level = ctypes.c_ubyte(0x5A)

        result = self.key(0x01, security_level)

        self.assertEqual(result, self.base + 0x34)
        self.assertEqual(security_level.value, 0xA7)

    def test_peer_ltk_returns_key_and_security_level(self) -> None:
        self.record[0x2E] = 0x02
        self.record[0x6A] = 0x39
        security_level = ctypes.c_ubyte(0x5A)

        result = self.key(0x02, security_level)

        self.assertEqual(result, self.base + 0x50)
        self.assertEqual(security_level.value, 0x39)

    def test_irk_and_csrk_do_not_touch_security_level(self) -> None:
        self.record[0x2E] = 0x0C
        security_level = ctypes.c_ubyte(0xD3)

        self.assertEqual(self.key(0x04, security_level), self.base + 0x07)
        self.assertEqual(security_level.value, 0xD3)
        self.assertEqual(self.key(0x08, None), self.base + 0x1E)
        self.assertEqual(security_level.value, 0xD3)

    def test_mask_miss_and_unsupported_types_return_null(self) -> None:
        self.record[0x2E] = 0x0F
        security_level = ctypes.c_ubyte(0x6C)

        self.record[0x2E] = 0x08
        self.assertIsNone(self.key(0x01, None))
        self.record[0x2E] = 0x0F
        self.assertIsNone(self.key(0x00, None))
        self.assertIsNone(self.key(0x03, security_level))
        self.assertIsNone(self.key(0x10, None))
        self.assertEqual(security_level.value, 0x6C)

    def test_requested_type_is_truncated_to_one_byte(self) -> None:
        self.record[0x2E] = 0x01
        self.record[0x4E] = 0x82
        security_level = ctypes.c_ubyte(0)

        result = self.key(0xABCD0101, security_level)

        self.assertEqual(result, self.base + 0x34)
        self.assertEqual(security_level.value, 0x82)

    def test_peer_address_accessors_preserve_stock_null_contract(self) -> None:
        self.record[0x06] = 0xA5

        self.assertEqual(self.get_address(self.base), self.base)
        self.assertIsNone(self.get_address(None))
        self.assertEqual(self.get_address_type(self.base), 0xA5)
        self.assertEqual(self.get_address_type(None), 0xFF)

    def test_randomized_model_covers_all_key_types(self) -> None:
        generator = random.Random(0x47AE78)
        offsets = {
            0x01: (0x34, 0x4E),
            0x02: (0x50, 0x6A),
            0x04: (0x07, None),
            0x08: (0x1E, None),
        }

        for _ in range(500):
            raw = bytes(
                generator.randrange(256)
                for _ in range(RECORD_SIZE)
            )
            for index, value in enumerate(raw):
                self.record[index] = value
            requested = generator.randrange(0x10000)
            key_type = requested & 0xFF
            security_level = ctypes.c_ubyte(
                generator.randrange(256)
            )
            initial_level = security_level.value

            result = self.key(requested, security_level)

            expected = None
            expected_level = initial_level
            if raw[0x2E] & key_type and key_type in offsets:
                key_offset, level_offset = offsets[key_type]
                expected = self.base + key_offset
                if level_offset is not None:
                    expected_level = raw[level_offset]
            self.assertEqual(result, expected)
            self.assertEqual(security_level.value, expected_level)


if __name__ == "__main__":
    unittest.main()
