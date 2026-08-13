from __future__ import annotations

import os

import ctypes
import hashlib
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
COMPONENT_ROOT = OPENCFW_ROOT / "components" / "apollo_main" / "core_overlay"
SOURCE = COMPONENT_ROOT / "runtime_lookup_bucket_index.c"
FIXTURE = (
    OPENCFW_ROOT / "tests" / "fixtures" / "runtime_lookup_bucket_index_host.c"
)
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
STOCK_START = 0x0048277E
STOCK_END = 0x0048278C


def _sign_extend(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return value - (1 << bits) if value & sign else value


class RuntimeLookupBucketIndexTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "runtime_lookup_bucket_index.dylib"
            if sys.platform == "darwin"
            else "runtime_lookup_bucket_index.so"
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
        cls.bucket_index = cls.loaded.open_cfw_runtime_lookup_bucket_index
        cls.bucket_index.argtypes = [ctypes.c_ubyte]
        cls.bucket_index.restype = ctypes.c_ubyte

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_all_byte_values_match_shift_and_clamp_oracle(self) -> None:
        for key in range(256):
            expected = min(key >> 2, 31)
            with self.subTest(key=key):
                self.assertEqual(self.bucket_index(key), expected)

    def test_bucket_boundaries_and_saturation_are_exact(self) -> None:
        cases = {
            0x00: 0,
            0x03: 0,
            0x04: 1,
            0x07: 1,
            0x78: 30,
            0x7B: 30,
            0x7C: 31,
            0x7F: 31,
            0x80: 31,
            0xFE: 31,
            0xFF: 31,
        }
        for key, expected in cases.items():
            with self.subTest(key=f"{key:#04x}"):
                self.assertEqual(self.bucket_index(key), expected)

    def test_stock_boundary_caller_and_adjacent_functions_are_pinned(
        self,
    ) -> None:
        application = OFFICIAL.read_bytes()[32:]

        def span(start: int, end: int) -> bytes:
            return application[
                start - APPLICATION_BASE:end - APPLICATION_BASE
            ]

        previous = span(0x00482716, STOCK_START)
        self.assertEqual(len(previous), 104)
        self.assertEqual(
            hashlib.sha256(previous).hexdigest(),
            "094798629ce86c61f6c7e0aee2be6867"
            "6cb8e7629dba07c4d0a2959a63dabcce",
        )

        stock = span(STOCK_START, STOCK_END)
        self.assertEqual(len(stock), 14)
        self.assertEqual(
            stock.hex(),
            "c0b28008c0b21f2800d31f207047",
        )
        self.assertEqual(
            hashlib.sha256(stock).hexdigest(),
            "859ac3abf53bb7eae92a12e11c26682b"
            "6bd049ee5b4b0dfb8adb541e8f201910",
        )

        following = span(STOCK_END, 0x00482796)
        self.assertEqual(len(following), 10)
        self.assertEqual(
            hashlib.sha256(following).hexdigest(),
            "32dde2f27cf8bbf895887f8ee6cb5b8a"
            "3c984cbd1c06e5c14187215bc9884e61",
        )

        caller = span(0x00482928, 0x00482942)
        self.assertEqual(
            hashlib.sha256(caller).hexdigest(),
            "671f472345d42a3d61a2ff3edc7b4f26"
            "a053c785927120b81cf830604b6b8bd5",
        )
        self.assertEqual(
            span(0x00482930, 0x0048293A).hex(),
            "2800c0b2fff723ff6168",
        )

    def test_wide_call_and_dependency_topology_is_complete(self) -> None:
        application = OFFICIAL.read_bytes()[32:]
        sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
        import apollo_overlay

        callers = []
        jumps = []
        interior = []
        dependencies = []
        for offset in range(0, len(application) - 3, 2):
            address = APPLICATION_BASE + offset
            encoded = application[offset:offset + 4]
            for link, observed in ((True, callers), (False, jumps)):
                try:
                    target = apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=link,
                    )
                except apollo_overlay.BuildError:
                    continue
                if target == STOCK_START:
                    observed.append((address, encoded.hex()))
                if (
                    STOCK_START < target < STOCK_END
                    and not STOCK_START <= address < STOCK_END
                ):
                    interior.append((address, target, link))
                if link and STOCK_START <= address < STOCK_END:
                    dependencies.append(
                        (address, target, encoded.hex())
                    )

        self.assertEqual(callers, [(0x00482934, "fff723ff")])
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(dependencies, [])

    def test_no_narrow_entry_interior_or_stored_pointer_exists(self) -> None:
        application = OFFICIAL.read_bytes()[32:]
        narrow_entry = []
        narrow_interior = []
        for offset in range(0, len(application) - 1, 2):
            address = APPLICATION_BASE + offset
            halfword = struct.unpack_from("<H", application, offset)[0]
            candidates = []
            if halfword & 0xF800 == 0xE000:
                candidates.append(
                    address
                    + 4
                    + _sign_extend((halfword & 0x7FF) << 1, 12)
                )
            condition = (halfword >> 8) & 0xF
            if halfword & 0xF000 == 0xD000 and condition < 0xE:
                candidates.append(
                    address
                    + 4
                    + _sign_extend((halfword & 0xFF) << 1, 9)
                )
            if halfword & 0xF500 == 0xB100:
                immediate = (
                    ((halfword >> 9) & 1) << 6
                    | ((halfword >> 3) & 0x1F) << 1
                )
                candidates.append(address + 4 + immediate)
            if STOCK_START in candidates:
                narrow_entry.append((address, halfword))
            for target in candidates:
                if (
                    STOCK_START < target < STOCK_END
                    and not STOCK_START <= address < STOCK_END
                ):
                    narrow_interior.append((address, target, halfword))

        stored = []
        for offset in range(0, len(application) - 3):
            value = struct.unpack_from("<I", application, offset)[0]
            target = value & ~1
            if value & 1 and STOCK_START <= target < STOCK_END:
                stored.append((APPLICATION_BASE + offset, target))

        self.assertEqual(narrow_entry, [])
        self.assertEqual(narrow_interior, [])
        self.assertEqual(stored, [])

    def test_source_and_fixture_are_bounded(self) -> None:
        source = SOURCE.read_text()
        for token in (
            "unsigned char open_cfw_runtime_lookup_bucket_index(",
            "unsigned char key",
            "unsigned char index = (unsigned char)(key >> 2);",
            "if (index > 31U)",
            "index = 31U;",
        ):
            self.assertIn(token, source)
        self.assertNotIn("#include <", source)
        self.assertIn("runtime_lookup_bucket_index.c", FIXTURE.read_text())


if __name__ == "__main__":
    unittest.main()
