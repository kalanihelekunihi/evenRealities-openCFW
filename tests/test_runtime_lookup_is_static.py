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
SOURCE = COMPONENT_ROOT / "runtime_lookup_is_static.c"
FIXTURE = (
    OPENCFW_ROOT / "tests" / "fixtures" / "runtime_lookup_is_static_host.c"
)
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
ZERO_WRAPPER_START = 0x004826FC
ZERO_WRAPPER_END = 0x00482708
STOCK_START = 0x00482708
STOCK_END = 0x00482716


def _sign_extend(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return value - (1 << bits) if value & sign else value


class RuntimeLookupIsStaticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "runtime_lookup_is_static.dylib"
            if sys.platform == "darwin"
            else "runtime_lookup_is_static.so"
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
        cls.predicate = cls.loaded.open_cfw_runtime_lookup_is_static
        cls.predicate.argtypes = [ctypes.c_void_p]
        cls.predicate.restype = ctypes.c_int

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_all_byte_values_match_the_exact_sentinel_oracle(self) -> None:
        for value in range(256):
            context = (ctypes.c_ubyte * 17)(
                *(((index * 29) + value) & 0xFF for index in range(17))
            )
            context[8] = value
            before = bytes(context)
            with self.subTest(value=value):
                self.assertEqual(self.predicate(context), int(value == 0xFF))
                self.assertEqual(bytes(context), before)

    def test_surrounding_context_bytes_do_not_affect_the_result(self) -> None:
        generator = random.Random(STOCK_START)
        for index in range(256):
            context = (ctypes.c_ubyte * 64)(
                *(generator.randrange(256) for _ in range(64))
            )
            sentinel = bool(index & 1)
            context[8] = 0xFF if sentinel else generator.randrange(0xFF)
            with self.subTest(index=index, sentinel=sentinel):
                self.assertEqual(self.predicate(context), int(sentinel))

    def test_stock_boundaries_and_adjacent_spans_are_pinned(self) -> None:
        application = OFFICIAL.read_bytes()[32:]

        def span(start: int, end: int) -> bytes:
            return application[
                start - APPLICATION_BASE:end - APPLICATION_BASE
            ]

        previous = span(0x00482684, 0x004826B2)
        self.assertEqual(len(previous), 46)
        self.assertEqual(
            hashlib.sha256(previous).hexdigest(),
            "584f21e8f8b4cc13f7994f623e309f95"
            "22edb33e3b5d9fa5036650fb429532dc",
        )

        retained_gap = span(0x004826B2, ZERO_WRAPPER_START)
        self.assertEqual(len(retained_gap), 74)
        self.assertEqual(
            hashlib.sha256(retained_gap).hexdigest(),
            "c6c3d975e48a8c70ee95aff430c79357"
            "728201a4e219b4f4095e1d5089c37090",
        )

        zero_wrapper = span(ZERO_WRAPPER_START, ZERO_WRAPPER_END)
        self.assertEqual(
            zero_wrapper.hex(),
            "80b50a000021d2f720f801bd",
        )
        self.assertEqual(
            hashlib.sha256(zero_wrapper).hexdigest(),
            "8ff986fa07383109f287b71ed376307b4"
            "e35fc4f7a01d5ab1ffdcc35daaff80b",
        )

        stock = span(STOCK_START, STOCK_END)
        self.assertEqual(len(stock), 14)
        self.assertEqual(
            stock.hex(),
            "007aff2801d1012000e000207047",
        )
        self.assertEqual(
            hashlib.sha256(stock).hexdigest(),
            "5f4d8578d1c93ca71614bc46df4d853"
            "223c3b8e389efde4fef5231c6cde6f999",
        )

        following = span(STOCK_END, 0x0048277E)
        self.assertEqual(len(following), 104)
        self.assertEqual(
            hashlib.sha256(following).hexdigest(),
            "094798629ce86c61f6c7e0aee2be6867"
            "6cb8e7629dba07c4d0a2959a63dabcce",
        )

    def test_wide_call_and_dependency_topology_is_complete(self) -> None:
        application = OFFICIAL.read_bytes()[32:]
        sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
        import apollo_overlay

        expected = {
            (ZERO_WRAPPER_START, ZERO_WRAPPER_END): {
                "callers": [
                    (0x00482790, "fff7b4ff"),
                    (0x004827AA, "fff7a7ff"),
                    (0x0048295E, "fff7cdfe"),
                ],
                "dependencies": [
                    (0x00482702, 0x00454746, "d2f720f8"),
                ],
            },
            (STOCK_START, STOCK_END): {
                "callers": [
                    (0x00482720, "fff7f2ff"),
                    (0x004827B8, "fff7a6ff"),
                    (0x00482872, "fff749ff"),
                ],
                "dependencies": [],
            },
        }

        for (start, end), topology in expected.items():
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
                    if target == start:
                        observed.append((address, encoded.hex()))
                    if (
                        start < target < end
                        and not start <= address < end
                    ):
                        interior.append((address, target, link))
                    if link and start <= address < end:
                        dependencies.append(
                            (address, target, encoded.hex())
                        )

            with self.subTest(start=f"{start:#010x}"):
                self.assertEqual(callers, topology["callers"])
                self.assertEqual(jumps, [])
                self.assertEqual(interior, [])
                self.assertEqual(
                    dependencies,
                    topology["dependencies"],
                )

    def test_no_narrow_entry_interior_or_stored_pointer_exists(self) -> None:
        application = OFFICIAL.read_bytes()[32:]
        for start, end in (
            (ZERO_WRAPPER_START, ZERO_WRAPPER_END),
            (STOCK_START, STOCK_END),
        ):
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
                if start in candidates:
                    narrow_entry.append((address, halfword))
                for target in candidates:
                    if (
                        start < target < end
                        and not start <= address < end
                    ):
                        narrow_interior.append(
                            (address, target, halfword)
                        )

            stored = []
            for offset in range(0, len(application) - 3):
                value = struct.unpack_from("<I", application, offset)[0]
                target = value & ~1
                if value & 1 and start <= target < end:
                    stored.append((APPLICATION_BASE + offset, target))

            with self.subTest(start=f"{start:#010x}"):
                self.assertEqual(narrow_entry, [])
                self.assertEqual(narrow_interior, [])
                self.assertEqual(stored, [])

    def test_source_is_bounded_and_records_the_abi_sensitive_skip(self) -> None:
        source = SOURCE.read_text()
        for token in (
            "int open_cfw_runtime_lookup_is_static(const void *context)",
            "return bytes[8] == 0xFFU;",
            "0x004826FC deliberately remains",
            "compiler-artifact-sensitive",
        ):
            self.assertIn(token, source)
        self.assertNotIn("#include <", source)
        self.assertIn("runtime_lookup_is_static.c", FIXTURE.read_text())


if __name__ == "__main__":
    unittest.main()
