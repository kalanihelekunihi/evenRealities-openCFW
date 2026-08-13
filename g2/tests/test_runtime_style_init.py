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
SOURCE = COMPONENT_ROOT / "runtime_style_init.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "runtime_style_init_host.c"
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
STOCK_START = 0x0048278C
STOCK_END = 0x00482796


def _sign_extend(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return value - (1 << bits) if value & sign else value


class RuntimeStyleInitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "runtime_style_init.dylib"
            if sys.platform == "darwin"
            else "runtime_style_init.so"
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
        cls.reset = cls.loaded.open_cfw_test_runtime_style_init_reset
        cls.reset.argtypes = [ctypes.c_uint32]
        cls.reset.restype = None
        cls.execute = cls.loaded.open_cfw_test_runtime_style_init_execute
        cls.execute.argtypes = []
        cls.execute.restype = None
        cls.storage = (ctypes.c_ubyte * 20).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_style_init_storage",
        )
        cls.before = (ctypes.c_ubyte * 12).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_style_init_before",
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def uint(self, name: str) -> ctypes.c_uint32:
        return ctypes.c_uint32.in_dll(self.loaded, name)

    def pointer(self, name: str) -> ctypes.c_void_p:
        return ctypes.c_void_p.in_dll(self.loaded, name)

    def test_initializer_zeroes_exactly_the_twelve_byte_descriptor(
        self,
    ) -> None:
        for seed in range(256):
            self.reset(seed)
            expected = bytes(
                (seed + index * 29) & 0xFF for index in range(20)
            )
            self.execute()
            with self.subTest(seed=seed):
                self.assertEqual(bytes(self.before), expected[:12])
                self.assertEqual(bytes(self.storage[:12]), bytes(12))
                self.assertEqual(bytes(self.storage[12:]), expected[12:])
                self.assertEqual(
                    self.uint(
                        "open_cfw_test_runtime_style_init_zero_calls"
                    ).value,
                    1,
                )
                self.assertEqual(
                    self.uint(
                        "open_cfw_test_runtime_style_init_zero_size"
                    ).value,
                    12,
                )
                self.assertEqual(
                    self.pointer(
                        "open_cfw_test_runtime_style_init_zero_destination"
                    ).value,
                    ctypes.addressof(self.storage),
                )

    def test_stock_boundary_and_adjacent_functions_are_pinned(self) -> None:
        application = OFFICIAL.read_bytes()[32:]

        def span(start: int, end: int) -> bytes:
            return application[
                start - APPLICATION_BASE:end - APPLICATION_BASE
            ]

        previous = span(0x0048277E, STOCK_START)
        self.assertEqual(len(previous), 14)
        self.assertEqual(
            hashlib.sha256(previous).hexdigest(),
            "859ac3abf53bb7eae92a12e11c26682b"
            "6bd049ee5b4b0dfb8adb541e8f201910",
        )

        stock = span(STOCK_START, STOCK_END)
        self.assertEqual(stock.hex(), "80b50c21fff7b4ff01bd")
        self.assertEqual(
            hashlib.sha256(stock).hexdigest(),
            "32dde2f27cf8bbf895887f8ee6cb5b8a"
            "3c984cbd1c06e5c14187215bc9884e61",
        )

        following = span(STOCK_END, 0x004827B0)
        self.assertEqual(len(following), 26)
        self.assertEqual(
            hashlib.sha256(following).hexdigest(),
            "a6778c79bfe8434836675b4a11922ac8"
            "43309a8a5e08af876bf2a1e2007bb975",
        )

    def test_all_three_callers_and_ignored_return_contexts_are_pinned(
        self,
    ) -> None:
        application = OFFICIAL.read_bytes()[32:]
        contexts = {
            (0x0044C6E0, 0x0044C700):
                "41f6885bacb6b645aad4c30600faea26"
                "0fde656a54618aebd014fb46ced78bb5",
            (0x0044C7FE, 0x0044C81E):
                "ee6f907548b325f8f5a13633a30bf968"
                "5cc8193e0cf88c99e65a57393765d354",
            (0x0048819C, 0x004881B4):
                "c3e41069d4cd2d5adc525cc1e8e00163"
                "9a8d7a3f784988471630ad2256e9ad4a",
        }
        for (start, end), expected in contexts.items():
            context = application[
                start - APPLICATION_BASE:end - APPLICATION_BASE
            ]
            with self.subTest(start=f"{start:#010x}"):
                self.assertEqual(hashlib.sha256(context).hexdigest(), expected)

    def test_wide_call_and_dependency_topology_is_complete(self) -> None:
        application = OFFICIAL.read_bytes()[32:]
        sys.path.insert(0, str(OPENCFW_ROOT / "tools")); sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
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

        self.assertEqual(
            callers,
            [
                (0x0044C6F2, "36f04bf8"),
                (0x0044C80C, "35f0beff"),
                (0x004881AE, "faf7edfa"),
            ],
        )
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(
            dependencies,
            [(0x00482790, 0x004826FC, "fff7b4ff")],
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
            target = value & ~1
            if value & 1 and STOCK_START <= target < STOCK_END:
                stored.append((APPLICATION_BASE + offset, target))

        self.assertEqual(narrow_entry, [])
        self.assertEqual(narrow_interior, [])
        self.assertEqual(stored, [])

    def test_source_and_fixture_are_bounded(self) -> None:
        source = SOURCE.read_text()
        for token in (
            "void open_cfw_runtime_style_init(void *style)",
            "OPEN_CFW_RUNTIME_STYLE_INIT_MEMORY_ZERO(style, 12U);",
            "void *open_cfw_runtime_memory_zero(",
        ):
            self.assertIn(token, source)
        self.assertNotIn("#include <", source)
        self.assertIn("runtime_style_init.c", FIXTURE.read_text())


if __name__ == "__main__":
    unittest.main()
