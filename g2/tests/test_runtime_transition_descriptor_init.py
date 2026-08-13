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
SOURCE = COMPONENT_ROOT / "runtime_transition_descriptor_init.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "runtime_transition_descriptor_init_host.c"
)
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
STOCK_START = 0x00482950
STOCK_END = 0x0048297C
DEFAULT_LINEAR_PATH = 0x00450635


def _sign_extend(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return value - (1 << bits) if value & sign else value


class RuntimeTransitionDescriptor(ctypes.Structure):
    _fields_ = [
        ("properties", ctypes.c_uint32),
        ("user_data", ctypes.c_uint32),
        ("path_callback", ctypes.c_uint32),
        ("duration", ctypes.c_uint32),
        ("delay", ctypes.c_uint32),
    ]


class RuntimeTransitionDescriptorInitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "runtime_transition_descriptor_init.dylib"
            if sys.platform == "darwin"
            else "runtime_transition_descriptor_init.so"
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
        cls.reset = cls.loaded.open_cfw_test_runtime_transition_reset
        cls.reset.argtypes = [ctypes.c_uint32]
        cls.reset.restype = None
        cls.execute = cls.loaded.open_cfw_test_runtime_transition_execute
        cls.execute.argtypes = [ctypes.c_uint32] * 5
        cls.execute.restype = ctypes.c_uint32
        cls.descriptor = RuntimeTransitionDescriptor.in_dll(
            cls.loaded,
            "open_cfw_test_runtime_transition_descriptor",
        )
        cls.zero_before = (ctypes.c_ubyte * 20).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_transition_memory_zero_before",
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def uint(self, name: str) -> ctypes.c_uint32:
        return ctypes.c_uint32.in_dll(self.loaded, name)

    def pointer(self, name: str) -> ctypes.c_void_p:
        return ctypes.c_void_p.in_dll(self.loaded, name)

    @staticmethod
    def poison(seed: int) -> bytes:
        return bytes((seed + index * 29) & 0xFF for index in range(20))

    def assert_zero_call(self, seed: int) -> None:
        self.assertEqual(
            self.uint(
                "open_cfw_test_runtime_transition_memory_zero_calls"
            ).value,
            1,
        )
        self.assertEqual(
            self.uint(
                "open_cfw_test_runtime_transition_memory_zero_size"
            ).value,
            20,
        )
        self.assertEqual(
            self.pointer(
                "open_cfw_test_runtime_transition_memory_zero_destination"
            ).value,
            ctypes.addressof(self.descriptor),
        )
        self.assertEqual(bytes(self.zero_before), self.poison(seed))

    def test_custom_path_maps_all_six_abi_arguments(self) -> None:
        seed = 0xA7
        self.reset(seed)
        observed = self.execute(
            0x11223344,
            0x55667789,
            0x89ABCDEF,
            0x10203040,
            0x50607080,
        )
        self.assertEqual(observed, 0x89ABCDEF)
        self.assertEqual(self.descriptor.properties, 0x11223344)
        self.assertEqual(self.descriptor.user_data, 0x50607080)
        self.assertEqual(self.descriptor.path_callback, 0x55667789)
        self.assertEqual(self.descriptor.duration, 0x89ABCDEF)
        self.assertEqual(self.descriptor.delay, 0x10203040)
        self.assert_zero_call(seed)

    def test_null_path_selects_the_retained_linear_callback(self) -> None:
        seed = 0x31
        self.reset(seed)
        observed = self.execute(
            0x01020304,
            0,
            80,
            70,
            0,
        )
        self.assertEqual(observed, 80)
        self.assertEqual(self.descriptor.properties, 0x01020304)
        self.assertEqual(self.descriptor.user_data, 0)
        self.assertEqual(
            self.descriptor.path_callback,
            DEFAULT_LINEAR_PATH,
        )
        self.assertEqual(self.descriptor.duration, 80)
        self.assertEqual(self.descriptor.delay, 70)
        self.assert_zero_call(seed)

    def test_randomized_descriptors_match_the_stock_model(self) -> None:
        generator = random.Random(STOCK_START)
        for index in range(512):
            seed = generator.randrange(256)
            properties = generator.getrandbits(32)
            requested_path = (
                0 if index % 7 == 0 else generator.getrandbits(32)
            )
            duration = generator.getrandbits(32)
            delay = generator.getrandbits(32)
            user_data = generator.getrandbits(32)
            self.reset(seed)
            observed = self.execute(
                properties,
                requested_path,
                duration,
                delay,
                user_data,
            )
            with self.subTest(index=index):
                self.assertEqual(observed, duration)
                self.assertEqual(
                    bytes(self.descriptor),
                    struct.pack(
                        "<IIIII",
                        properties,
                        user_data,
                        requested_path or DEFAULT_LINEAR_PATH,
                        duration,
                        delay,
                    ),
                )
                self.assert_zero_call(seed)

    def test_stock_span_literal_and_adjacent_boundaries_are_pinned(
        self,
    ) -> None:
        application = OFFICIAL.read_bytes()[32:]

        def span(start: int, end: int) -> bytes:
            return application[
                start - APPLICATION_BASE:end - APPLICATION_BASE
            ]

        preceding = span(0x00482946, STOCK_START)
        self.assertEqual(preceding.hex(), "80b5c9b2fff7e4fe02bd")
        self.assertEqual(
            hashlib.sha256(preceding).hexdigest(),
            "152db6bc74bffc0424ceeb1dc3eeaffa"
            "bef107ac09a125bfbfc4c0093ccfb7af",
        )

        stock = span(STOCK_START, STOCK_END)
        self.assertEqual(len(stock), 44)
        self.assertEqual(
            stock.hex(),
            "f8b504000d0016001f0014212000fff7cdfe256030000028"
            "01d15a4effe707990698a660e76020616160f1bd",
        )
        self.assertEqual(
            hashlib.sha256(stock).hexdigest(),
            "fabbb1b5b1efc42178859412578c1d81"
            "4e2d03d28032144c156e8125460b70f2",
        )

        following = span(STOCK_END, 0x00482A5A)
        self.assertEqual(len(following), 222)
        self.assertEqual(
            hashlib.sha256(following).hexdigest(),
            "ff9eb32171697c70cbd592801924eb4e"
            "e1b7279a0378f9d0c04c6941e7beff96",
        )

        literal = struct.unpack_from(
            "<I",
            application,
            0x00482AD4 - APPLICATION_BASE,
        )[0]
        self.assertEqual(literal, DEFAULT_LINEAR_PATH)

    def test_wide_caller_dependency_and_interior_topology_is_complete(
        self,
    ) -> None:
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

        self.assertEqual(
            callers,
            [
                (0x00484B6A, "fdf7f1fe"),
                (0x00484B80, "fdf7e6fe"),
            ],
        )
        self.assertEqual(
            hashlib.sha256(
                b"".join(
                    struct.pack("<I", address) + bytes.fromhex(encoded)
                    for address, encoded in callers
                )
            ).hexdigest(),
            "ba487ada9fd6c2a7026e198c272d4e97"
            "32db59fc4fe4cedba7567313614f6aed",
        )
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(
            dependencies,
            [(0x0048295E, 0x004826FC, "fff7cdfe")],
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
                stored.append((APPLICATION_BASE + offset, target, value))

        self.assertEqual(narrow_entry, [])
        self.assertEqual(narrow_interior, [])
        self.assertEqual(stored, [])

    def test_source_and_fixture_are_bounded(self) -> None:
        source = SOURCE.read_text()
        for token in (
            "struct open_cfw_runtime_transition_descriptor",
            "open_cfw_runtime_transition_descriptor_init(",
            "OPEN_CFW_RUNTIME_TRANSITION_MEMORY_ZERO(",
            "OPEN_CFW_RUNTIME_TRANSITION_LINEAR_PATH 0x00450635U",
            "descriptor->properties = properties;",
            "descriptor->user_data = user_data;",
            "return duration;",
        ):
            self.assertIn(token, source)
        self.assertNotIn("#include <", source)
        self.assertIn(
            "runtime_transition_descriptor_init.c",
            FIXTURE.read_text(),
        )


if __name__ == "__main__":
    unittest.main()
