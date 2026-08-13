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
SOURCE = COMPONENT_ROOT / "runtime_linked_list_init.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "runtime_linked_list_init_host.c"
)
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
STOCK_START = 0x00482B00
STOCK_END = 0x00482B12


def _sign_extend(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return value - (1 << bits) if value & sign else value


class RuntimeLinkedList(ctypes.Structure):
    _fields_ = [
        ("node_size", ctypes.c_uint32),
        ("head", ctypes.c_uint32),
        ("tail", ctypes.c_uint32),
    ]


class RuntimeLinkedListInitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "runtime_linked_list_init.dylib"
            if sys.platform == "darwin"
            else "runtime_linked_list_init.so"
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
        cls.initialize = cls.loaded.open_cfw_runtime_linked_list_init
        cls.initialize.argtypes = [
            ctypes.POINTER(RuntimeLinkedList),
            ctypes.c_uint32,
        ]
        cls.initialize.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def span(cls, start: int, end: int) -> bytes:
        return cls.application[
            start - APPLICATION_BASE:end - APPLICATION_BASE
        ]

    def initialize_value(self, node_size: int) -> RuntimeLinkedList:
        linked_list = RuntimeLinkedList(
            0xA1B2C3D4,
            0x11223344,
            0x55667788,
        )
        self.initialize(ctypes.byref(linked_list), node_size)
        return linked_list

    def test_representative_sizes_round_up_to_four_bytes(self) -> None:
        for node_size in range(0, 1025):
            linked_list = self.initialize_value(node_size)
            expected = (node_size + 3) & ~3
            with self.subTest(node_size=node_size):
                self.assertEqual(linked_list.node_size, expected)
                self.assertEqual(linked_list.head, 0)
                self.assertEqual(linked_list.tail, 0)

    def test_rounding_uses_exact_32_bit_wrap_semantics(self) -> None:
        cases = {
            0x7FFFFFFD: 0x80000000,
            0x7FFFFFFF: 0x80000000,
            0xFFFFFFF8: 0xFFFFFFF8,
            0xFFFFFFF9: 0xFFFFFFFC,
            0xFFFFFFFC: 0xFFFFFFFC,
            0xFFFFFFFD: 0,
            0xFFFFFFFE: 0,
            0xFFFFFFFF: 0,
        }
        for node_size, expected in cases.items():
            with self.subTest(node_size=f"{node_size:#010x}"):
                linked_list = self.initialize_value(node_size)
                self.assertEqual(linked_list.node_size, expected)
                self.assertEqual(linked_list.head, 0)
                self.assertEqual(linked_list.tail, 0)

    def test_stock_body_and_adjacent_boundaries_are_exact(self) -> None:
        stock = self.span(STOCK_START, STOCK_END)
        self.assertEqual(len(stock), 18)
        self.assertEqual(
            stock.hex(),
            "0022426000228260c91c8908890001607047",
        )
        self.assertEqual(
            hashlib.sha256(stock).hexdigest(),
            "e8bd7819a54b5fdf15e0c8404e14d9f"
            "43f0ec417fecffe139d45c0d3bf75799c",
        )

        previous = self.span(0x00482AB2, STOCK_START)
        self.assertEqual(len(previous), 78)
        self.assertEqual(
            hashlib.sha256(previous).hexdigest(),
            "4189f9073fb8b1348be4112fb54b869"
            "ce0be29aed96084b5817d906e65421207",
        )

        following = self.span(STOCK_END, 0x00482B56)
        self.assertEqual(len(following), 68)
        self.assertEqual(
            hashlib.sha256(following).hexdigest(),
            "576df2aaf1e74eff0a6c8cc0375747bf"
            "2264c66d964267f8ab25ecbc331f7cb4",
        )

    def test_all_sixteen_direct_callers_are_exact(self) -> None:
        expected = [
            (0x0044B914, "37f0f4f8"),
            (0x0044D334, "35f0e4fb"),
            (0x0044F8E8, "33f00af9"),
            (0x004503B0, "32f0a6fb"),
            (0x00464338, "1ef0e2fb"),
            (0x0047351C, "0ff0f0fa"),
            (0x00473526, "0ff0ebfa"),
            (0x00488F58, "f9f7d2fd"),
            (0x004B1C56, "d0f753ff"),
            (0x004C6D94, "bbf7b4fe"),
            (0x005C2D20, "bff6eefe"),
            (0x005C2DFC, "bff680fe"),
            (0x005C5B1A, "bcf6f1ff"),
            (0x005C5B24, "bcf6ecff"),
            (0x005C99D0, "b9f696f8"),
            (0x005C9E9E, "b8f62ffe"),
        ]

        sys.path.insert(0, str(OPENCFW_ROOT / "tools")); sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
        import apollo_overlay

        observed = []
        for offset in range(0, len(self.application) - 3, 2):
            address = APPLICATION_BASE + offset
            encoded = self.application[offset:offset + 4]
            try:
                target = apollo_overlay.decode_thumb_branch(
                    address,
                    encoded,
                    link=True,
                )
            except apollo_overlay.BuildError:
                continue
            if target == STOCK_START:
                observed.append((address, encoded.hex()))

        self.assertEqual(observed, expected)
        digest = hashlib.sha256(
            b"".join(
                struct.pack("<I", address)
                for address, _encoded in observed
            )
        ).hexdigest()
        self.assertEqual(
            digest,
            "e02600f755391df52af98001a989a579"
            "9ebe7ceb661574c0589aeeee1e5c8f8b",
        )

        argument_contexts = {
            0x0044B914: self.span(0x0044B90E, 0x0044B918).hex(),
            0x0044D334: self.span(0x0044D32E, 0x0044D338).hex(),
            0x004503B0: self.span(0x004503AA, 0x004503B4).hex(),
            0x0047351C: self.span(0x00473516, 0x00473520).hex(),
            0x00473526: self.span(0x00473520, 0x0047352A).hex(),
            0x005C5B1A: self.span(0x005C5B14, 0x005C5B1E).hex(),
            0x005C5B24: self.span(0x005C5B1E, 0x005C5B28).hex(),
            0x005C9E9E: self.span(0x005C9E98, 0x005C9EA2).hex(),
        }
        self.assertEqual(
            argument_contexts,
            {
                0x0044B914: "1421dff83c0837f0f4f8",
                0x0044D334: "2021dff8840235f0e4fb",
                0x004503B0: "602114f1ac0032f0a6fb",
                0x0047351C: "4ff44771201d0ff0f0fa",
                0x00473526: "dc2114f144000ff0ebfa",
                0x005C5B1A: "142114f12c00bcf6f1ff",
                0x005C5B24: "182114f13800bcf6ecff",
                0x005C9E9E: "382115f12c00b8f62ffe",
            },
        )

    def test_no_dependency_or_alternate_entry_topology_exists(self) -> None:
        sys.path.insert(0, str(OPENCFW_ROOT / "tools")); sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
        import apollo_overlay

        jumps = []
        interior = []
        dependencies = []
        for offset in range(0, len(self.application) - 3, 2):
            address = APPLICATION_BASE + offset
            encoded = self.application[offset:offset + 4]
            for link in (True, False):
                try:
                    target = apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=link,
                    )
                except apollo_overlay.BuildError:
                    continue
                if not link and target == STOCK_START:
                    jumps.append((address, encoded.hex()))
                if (
                    STOCK_START < target < STOCK_END
                    and not STOCK_START <= address < STOCK_END
                ):
                    interior.append((address, target, link))
                if link and STOCK_START <= address < STOCK_END:
                    dependencies.append(
                        (address, target, encoded.hex())
                    )

        narrow_entry = []
        narrow_interior = []
        for offset in range(0, len(self.application) - 1, 2):
            address = APPLICATION_BASE + offset
            halfword = struct.unpack_from(
                "<H",
                self.application,
                offset,
            )[0]
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
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from(
                "<I",
                self.application,
                offset,
            )[0]
            target = value & ~1
            if value & 1 and STOCK_START <= target < STOCK_END:
                stored.append((APPLICATION_BASE + offset, target))

        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(dependencies, [])
        self.assertEqual(narrow_entry, [])
        self.assertEqual(narrow_interior, [])
        self.assertEqual(stored, [])

    def test_source_and_fixture_are_bounded(self) -> None:
        source = SOURCE.read_text()
        for token in (
            "struct open_cfw_runtime_linked_list",
            "open_cfw_runtime_linked_list_init(",
            "list->head = 0U;",
            "list->tail = 0U;",
            "list->node_size = (node_size + 3U) & ~3U;",
        ):
            self.assertIn(token, source)
        self.assertNotIn("#include <", source)
        self.assertIn("runtime_linked_list_init.c", FIXTURE.read_text())


if __name__ == "__main__":
    unittest.main()
