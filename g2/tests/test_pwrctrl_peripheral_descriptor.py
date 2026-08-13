from __future__ import annotations

import os

import ctypes
import hashlib
import random
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
COMPONENT_ROOT = OPENCFW_ROOT / "components" / "apollo_main" / "core_overlay"
SOURCE = COMPONENT_ROOT / "pwrctrl_peripheral_descriptor.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "pwrctrl_peripheral_descriptor_host.c"
)

EXPECTED_DESCRIPTORS = (
    (0x40021004, 0x00000001, 0x40021008, 0x30000001),
    (0x40021004, 0x10000000, 0x40021008, 0x30000001),
    (0x40021004, 0x20000000, 0x40021008, 0x30000001),
    (0x40021004, 0x00000002, 0x40021008, 0x0000001E),
    (0x40021004, 0x00000004, 0x40021008, 0x0000001E),
    (0x40021004, 0x00000008, 0x40021008, 0x0000001E),
    (0x40021004, 0x00000010, 0x40021008, 0x0000001E),
    (0x40021004, 0x00000020, 0x40021008, 0x000001E0),
    (0x40021004, 0x00000040, 0x40021008, 0x000001E0),
    (0x40021004, 0x00000080, 0x40021008, 0x000001E0),
    (0x40021004, 0x00000100, 0x40021008, 0x000001E0),
    (0x40021004, 0x00000200, 0x40021008, 0x00001E00),
    (0x40021004, 0x00000400, 0x40021008, 0x00001E00),
    (0x40021004, 0x00000800, 0x40021008, 0x00001E00),
    (0x40021004, 0x00001000, 0x40021008, 0x00001E00),
    (0x40021004, 0x00002000, 0x40021008, 0x00002000),
    (0x40021004, 0x00004000, 0x40021008, 0x00004000),
    (0x40021004, 0x00008000, 0x40021008, 0x00008000),
    (0x40021004, 0x00010000, 0x40021008, 0x00010000),
    (0x40021004, 0x00020000, 0x40021008, 0x00020000),
    (0x40021004, 0x00040000, 0x40021008, 0x00040000),
    (0x40021004, 0x00080000, 0x40021008, 0x00080000),
    (0x40021004, 0x00100000, 0x40021008, 0x00100000),
    (0x40021004, 0x00200000, 0x40021008, 0x00200000),
    (0x40021004, 0x00400000, 0x40021008, 0x00400000),
    (0x40021004, 0x00800000, 0x40021008, 0x00800000),
    (0x40021004, 0x01000000, 0x40021008, 0x01000000),
    (0x40021004, 0x02000000, 0x40021008, 0x02000000),
    (0x40021004, 0x04000000, 0x40021008, 0x04000000),
    (0x40021004, 0x08000000, 0x40021008, 0x08000000),
    (0x4002100C, 0x00000004, 0x40021010, 0x00000004),
    (0x4002100C, 0x00000040, 0x40021010, 0x000000C0),
    (0x4002100C, 0x00000080, 0x40021010, 0x000000C0),
    (0x4002100C, 0x00000400, 0x40021010, 0x00000400),
)


class PeripheralDescriptor(ctypes.Structure):
    _fields_ = [
        ("power_enable_register", ctypes.c_uint),
        ("peripheral_enable_mask", ctypes.c_uint),
        ("power_status_register", ctypes.c_uint),
        ("peripheral_status_mask", ctypes.c_uint),
    ]


class PwrctrlPeripheralDescriptorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "pwrctrl_peripheral_descriptor.dylib"
            if sys.platform == "darwin"
            else "pwrctrl_peripheral_descriptor.so"
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
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.get_descriptor = (
            cls.loaded.open_cfw_pwrctrl_peripheral_descriptor_get
        )
        cls.get_descriptor.argtypes = [
            ctypes.POINTER(PeripheralDescriptor),
            ctypes.c_uint,
        ]
        cls.get_descriptor.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @staticmethod
    def values(descriptor: PeripheralDescriptor) -> tuple[int, ...]:
        return tuple(
            getattr(descriptor, field_name)
            for field_name, _ in PeripheralDescriptor._fields_
        )

    def test_all_34_peripheral_descriptors_match_shipped_table(self) -> None:
        for peripheral, expected in enumerate(EXPECTED_DESCRIPTORS):
            with self.subTest(peripheral=peripheral):
                descriptor = PeripheralDescriptor(
                    0xDEADBEEF,
                    0xDEADBEEF,
                    0xDEADBEEF,
                    0xDEADBEEF,
                )

                result = self.get_descriptor(
                    ctypes.byref(descriptor),
                    peripheral,
                )

                self.assertEqual(result, 0)
                self.assertEqual(self.values(descriptor), expected)

    def test_null_output_returns_invalid_argument(self) -> None:
        self.assertEqual(self.get_descriptor(None, 0), 6)
        self.assertEqual(self.get_descriptor(None, 33), 6)

    def test_out_of_range_indices_do_not_modify_output(self) -> None:
        initial = (0x01234567, 0x89ABCDEF, 0x55AA55AA, 0xA55AA55A)
        for peripheral in (34, 35, 0x7FFFFFFF, 0xFFFFFFFF):
            with self.subTest(peripheral=peripheral):
                descriptor = PeripheralDescriptor(*initial)

                result = self.get_descriptor(
                    ctypes.byref(descriptor),
                    peripheral,
                )

                self.assertEqual(result, 6)
                self.assertEqual(self.values(descriptor), initial)

    def test_valid_copy_is_exactly_16_little_endian_bytes(self) -> None:
        for peripheral in (0, 3, 14, 29, 30, 33):
            with self.subTest(peripheral=peripheral):
                descriptor = PeripheralDescriptor()

                self.assertEqual(
                    self.get_descriptor(
                        ctypes.byref(descriptor),
                        peripheral,
                    ),
                    0,
                )

                self.assertEqual(
                    ctypes.string_at(
                        ctypes.byref(descriptor),
                        ctypes.sizeof(descriptor),
                    ),
                    struct.pack("<4I", *EXPECTED_DESCRIPTORS[peripheral]),
                )

    def test_deterministic_randomized_valid_lookups(self) -> None:
        generator = random.Random(0x47EF18)
        for _ in range(1000):
            peripheral = generator.randrange(len(EXPECTED_DESCRIPTORS))
            initial = tuple(generator.getrandbits(32) for _ in range(4))
            descriptor = PeripheralDescriptor(*initial)

            result = self.get_descriptor(
                ctypes.byref(descriptor),
                peripheral,
            )

            self.assertEqual(result, 0)
            self.assertEqual(
                self.values(descriptor),
                EXPECTED_DESCRIPTORS[peripheral],
            )

    def test_source_and_fixture_are_pinned(self) -> None:
        expected = {
            SOURCE:
                "5eac8ba6a9d7d8674d2ce762d29cbd23"
                "4eb8cc5bc18e8da6213e350ae61e9741",
            FIXTURE:
                "71ea23d04f2c54b91ba146064222f5e1"
                "38e58957654f935c584e69acc8e33a96",
        }
        for path, digest in expected.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                digest,
            )


if __name__ == "__main__":
    unittest.main()
