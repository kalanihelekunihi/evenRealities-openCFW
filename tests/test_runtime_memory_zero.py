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
SOURCE = COMPONENT_ROOT / "runtime_memory_zero.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "runtime_memory_zero_host.c"
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
STOCK_START = 0x004826FC
STOCK_END = 0x00482708


def _sign_extend(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return value - (1 << bits) if value & sign else value


class RuntimeMemoryZeroTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "runtime_memory_zero.dylib"
            if sys.platform == "darwin"
            else "runtime_memory_zero.so"
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
        cls.zero = cls.loaded.open_cfw_runtime_memory_zero
        cls.zero.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        cls.zero.restype = ctypes.c_void_p
        cls.reset = cls.loaded.open_cfw_test_runtime_memory_zero_reset
        cls.reset.argtypes = []
        cls.reset.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def uint(self, name: str) -> ctypes.c_uint32:
        return ctypes.c_uint32.in_dll(self.loaded, name)

    def pointer(self, name: str) -> ctypes.c_void_p:
        return ctypes.c_void_p.in_dll(self.loaded, name)

    def test_zero_length_preserves_memory_and_destination_return(self) -> None:
        guarded = (ctypes.c_ubyte * 18)(*range(18))
        before = bytes(guarded)
        destination = ctypes.addressof(guarded) + 7
        self.reset()
        self.assertEqual(self.zero(destination, 0), destination)
        self.assertEqual(bytes(guarded), before)
        self.assertEqual(
            self.uint("open_cfw_test_runtime_memory_zero_calls").value,
            1,
        )
        self.assertEqual(
            self.pointer(
                "open_cfw_test_runtime_memory_zero_destination"
            ).value,
            destination,
        )
        self.assertEqual(
            self.uint("open_cfw_test_runtime_memory_zero_size").value,
            0,
        )

    def test_each_length_clears_only_the_requested_forward_span(self) -> None:
        for length in (1, 2, 3, 4, 7, 12, 20, 31, 64):
            guarded = (ctypes.c_ubyte * 80)(*[0xA5] * 80)
            destination = ctypes.addressof(guarded) + 8
            self.reset()
            with self.subTest(length=length):
                self.assertEqual(self.zero(destination, length), destination)
                self.assertEqual(bytes(guarded[:8]), bytes([0xA5] * 8))
                self.assertEqual(
                    bytes(guarded[8:8 + length]),
                    bytes(length),
                )
                self.assertEqual(
                    bytes(guarded[8 + length:]),
                    bytes([0xA5] * (72 - length)),
                )
                self.assertEqual(
                    self.uint(
                        "open_cfw_test_runtime_memory_zero_calls"
                    ).value,
                    1,
                )
                self.assertEqual(
                    self.uint(
                        "open_cfw_test_runtime_memory_zero_size"
                    ).value,
                    length,
                )

    def test_null_plus_zero_is_forwarded_and_returned(self) -> None:
        self.reset()
        self.assertIsNone(self.zero(None, 0))
        self.assertEqual(
            self.uint("open_cfw_test_runtime_memory_zero_calls").value,
            1,
        )
        self.assertIsNone(
            self.pointer(
                "open_cfw_test_runtime_memory_zero_destination"
            ).value
        )

    def test_stock_span_callers_dependency_and_adjacency_are_pinned(
        self,
    ) -> None:
        application = OFFICIAL.read_bytes()[32:]

        def span(start: int, end: int) -> bytes:
            return application[
                start - APPLICATION_BASE:end - APPLICATION_BASE
            ]

        stock = span(STOCK_START, STOCK_END)
        self.assertEqual(len(stock), 12)
        self.assertEqual(
            stock.hex(),
            "80b50a000021d2f720f801bd",
        )
        self.assertEqual(
            hashlib.sha256(stock).hexdigest(),
            "8ff986fa07383109f287b71ed376307b4"
            "e35fc4f7a01d5ab1ffdcc35daaff80b",
        )
        self.assertEqual(span(0x004826F8, STOCK_START).hex(), "30000000")
        self.assertEqual(
            span(STOCK_END, 0x00482716).hex(),
            "007aff2801d1012000e000207047",
        )

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
                    dependencies.append((address, target, encoded.hex()))

        self.assertEqual(
            callers,
            [
                (0x00482790, "fff7b4ff"),
                (0x004827AA, "fff7a7ff"),
                (0x0048295E, "fff7cdfe"),
            ],
        )
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(
            dependencies,
            [(0x00482702, 0x00454746, "d2f720f8")],
        )

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
            if value == STOCK_START + 1 or (
                STOCK_START + 1 < value < STOCK_END
                and value & 1
            ):
                stored.append(
                    (APPLICATION_BASE + offset, value, offset & 3)
                )

        self.assertEqual(narrow_entry, [])
        self.assertEqual(narrow_interior, [])
        self.assertEqual(stored, [])

    def test_source_and_fixture_are_bounded(self) -> None:
        text = SOURCE.read_text()
        self.assertIn("open_cfw_runtime_memory_zero", text)
        self.assertIn("OPEN_CFW_RUNTIME_MEMORY_ZERO_FILL", text)
        self.assertNotIn("0x00454746", text)
        self.assertIn("runtime_memory_zero.c", FIXTURE.read_text())


if __name__ == "__main__":
    unittest.main()
