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
SOURCE = COMPONENT_ROOT / "runtime_byte_map_lookup_u8.c"
FIXTURE = (
    OPENCFW_ROOT / "tests" / "fixtures" / "runtime_byte_map_lookup_u8_host.c"
)
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
STOCK_START = 0x00482946
STOCK_END = 0x00482950


def _sign_extend(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return value - (1 << bits) if value & sign else value


class RuntimeByteMapLookupU8Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "runtime_byte_map_lookup_u8.dylib"
            if sys.platform == "darwin"
            else "runtime_byte_map_lookup_u8.so"
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
        cls.lookup = cls.loaded.open_cfw_runtime_byte_map_lookup_u8
        cls.lookup.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32),
        ]
        cls.lookup.restype = ctypes.c_uint32
        cls.reset = cls.loaded.open_cfw_test_runtime_byte_map_lookup_reset
        cls.reset.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.reset.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def uint(self, name: str) -> ctypes.c_uint32:
        return ctypes.c_uint32.in_dll(self.loaded, name)

    def pointer(self, name: str) -> ctypes.c_void_p:
        return ctypes.c_void_p.in_dll(self.loaded, name)

    def test_full_width_keys_are_normalized_to_the_low_byte(self) -> None:
        context = (ctypes.c_ubyte * 12)()
        output = ctypes.c_uint32(0xAAAAAAAA)
        for key in (
            0x00000000,
            0x000000FF,
            0x00000100,
            0x12345678,
            0xFFFFFF80,
            0xFFFFFFFF,
        ):
            self.reset(1, 0x13579BDF, 1)
            output.value = 0xAAAAAAAA
            with self.subTest(key=f"{key:#010x}"):
                observed = self.lookup(context, key, ctypes.byref(output))
                self.assertEqual(observed, 1)
                self.assertEqual(output.value, 0x13579BDF)
                self.assertEqual(
                    self.uint(
                        "open_cfw_test_runtime_byte_map_lookup_calls"
                    ).value,
                    1,
                )
                self.assertEqual(
                    self.uint(
                        "open_cfw_test_runtime_byte_map_lookup_key"
                    ).value,
                    key & 0xFF,
                )
                self.assertEqual(
                    self.pointer(
                        "open_cfw_test_runtime_byte_map_lookup_map"
                    ).value,
                    ctypes.addressof(context),
                )
                self.assertEqual(
                    self.pointer(
                        "open_cfw_test_runtime_byte_map_lookup_result"
                    ).value,
                    ctypes.addressof(output),
                )

    def test_dependency_return_and_output_behavior_are_transparent(self) -> None:
        context = (ctypes.c_ubyte * 12)()
        cases = (
            (0, 0x11111111, 0, 0xA5A5A5A5),
            (1, 0x22222222, 1, 0x22222222),
            (0xFFFFFFFF, 0x33333333, 1, 0x33333333),
        )
        for return_value, write_value, write_output, expected in cases:
            output = ctypes.c_uint32(0xA5A5A5A5)
            self.reset(return_value, write_value, write_output)
            with self.subTest(
                return_value=f"{return_value:#010x}",
                write_output=write_output,
            ):
                self.assertEqual(
                    self.lookup(context, 0xABCDEF42, ctypes.byref(output)),
                    return_value,
                )
                self.assertEqual(output.value, expected)

    def test_stock_boundary_and_adjacent_functions_are_pinned(self) -> None:
        application = OFFICIAL.read_bytes()[32:]

        def span(start: int, end: int) -> bytes:
            return application[
                start - APPLICATION_BASE:end - APPLICATION_BASE
            ]

        previous = span(0x00482868, STOCK_START)
        self.assertEqual(len(previous), 222)
        self.assertEqual(
            hashlib.sha256(previous).hexdigest(),
            "1071391c48262cafb1f72a5bba29b3ba"
            "e4eeb52a15908faf9dee60435c214a84",
        )

        stock = span(STOCK_START, STOCK_END)
        self.assertEqual(len(stock), 10)
        self.assertEqual(
            stock.hex(),
            "80b5c9b2fff7e4fe02bd",
        )
        self.assertEqual(
            hashlib.sha256(stock).hexdigest(),
            "152db6bc74bffc0424ceeb1dc3eeaffa"
            "bef107ac09a125bfbfc4c0093ccfb7af",
        )

        following = span(STOCK_END, 0x0048297C)
        self.assertEqual(len(following), 44)
        self.assertEqual(
            hashlib.sha256(following).hexdigest(),
            "fabbb1b5b1efc42178859412578c1d81"
            "4e2d03d28032144c156e8125460b70f2",
        )

    def test_wide_call_and_dependency_topology_is_complete(self) -> None:
        application = OFFICIAL.read_bytes()[32:]
        sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
        import apollo_overlay

        expected_callers = [
            (0x0044BEE8, "36f02dfd"),
            (0x0044C19C, "36f0d3fb"),
            (0x0044C20E, "36f09afb"),
            (0x0044C222, "36f090fb"),
            (0x0044C236, "36f086fb"),
            (0x0044C24A, "36f07cfb"),
            (0x0044C25E, "36f072fb"),
            (0x0044C272, "36f068fb"),
            (0x0044C286, "36f05efb"),
            (0x0044C29A, "36f054fb"),
            (0x0044C2AE, "36f04afb"),
            (0x0044C2C2, "36f040fb"),
            (0x0044C2D6, "36f036fb"),
            (0x0044C2EA, "36f02cfb"),
            (0x0044C2FE, "36f022fb"),
            (0x0044C312, "36f018fb"),
            (0x0044C326, "36f00efb"),
            (0x0044C33A, "36f004fb"),
            (0x0044C356, "36f0f6fa"),
            (0x0044C36C, "36f0ebfa"),
            (0x0044C37E, "36f0e2fa"),
            (0x0044C390, "36f0d9fa"),
            (0x0044C3A2, "36f0d0fa"),
            (0x0044C3B4, "36f0c7fa"),
            (0x0044C3C6, "36f0befa"),
            (0x0044C3D8, "36f0b5fa"),
            (0x0044C3EA, "36f0acfa"),
            (0x0044C3FC, "36f0a3fa"),
            (0x0044C40E, "36f09afa"),
            (0x0044C420, "36f091fa"),
            (0x0044C432, "36f088fa"),
            (0x0044CC36, "35f086fe"),
            (0x005CAEF2, "b7f628fd"),
            (0x005CAF12, "b7f618fd"),
            (0x005CAF46, "b7f6fefc"),
            (0x005CAFA6, "b7f6cefc"),
            (0x005CAFC6, "b7f6befc"),
            (0x005CAFFA, "b7f6a4fc"),
            (0x005CB01E, "b7f692fc"),
            (0x005CB052, "b7f678fc"),
            (0x005CB0CC, "b7f63bfc"),
            (0x005CB102, "b7f620fc"),
            (0x005CB128, "b7f60dfc"),
            (0x005CB14A, "b7f6fcfb"),
        ]
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

        self.assertEqual(callers, expected_callers)
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(
            dependencies,
            [(0x0048294A, 0x00482716, "fff7e4fe")],
        )

    def test_narrow_topology_and_stored_pointer_false_positive_are_pinned(
        self,
    ) -> None:
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
                stored.append(
                    (APPLICATION_BASE + offset, target, value)
                )

        self.assertEqual(narrow_entry, [])
        self.assertEqual(narrow_interior, [])
        self.assertEqual(
            stored,
            [(0x004CFC47, 0x00482948, 0x00482949)],
        )

    def test_source_and_fixture_are_bounded(self) -> None:
        source = SOURCE.read_text()
        for token in (
            "unsigned int open_cfw_runtime_byte_map_lookup(",
            "unsigned int open_cfw_runtime_byte_map_lookup_u8(",
            "(unsigned char)key",
            "OPEN_CFW_RUNTIME_BYTE_MAP_LOOKUP(",
        ):
            self.assertIn(token, source)
        self.assertNotIn("#include <", source)
        self.assertIn("runtime_byte_map_lookup_u8.c", FIXTURE.read_text())


if __name__ == "__main__":
    unittest.main()
