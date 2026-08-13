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
SOURCE = COMPONENT_ROOT / "runtime_linked_list_pointer_setters.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "runtime_linked_list_pointer_setters_host.c"
)
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
FUNCTIONS = {
    "previous": (0x00482DAE, 0x00482DC2),
    "next": (0x00482DC2, 0x00482DD8),
}
TARGET_FLAGS = [
    "--target=thumbv7em-none-eabi",
    "-mthumb",
    "-O2",
    "-ffreestanding",
    "-fno-jump-tables",
    "-fomit-frame-pointer",
    "-fno-builtin",
    "-mno-unaligned-access",
    "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables",
    "-fropi",
    "-Wall",
    "-Wextra",
    "-Werror",
]


def _sign_extend(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return value - (1 << bits) if value & sign else value


class RuntimeLinkedList(ctypes.Structure):
    _fields_ = [
        ("node_size", ctypes.c_uint32),
        ("head", ctypes.c_uint32),
        ("tail", ctypes.c_uint32),
    ]


class RuntimeLinkedListPointerSetterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "runtime_linked_list_pointer_setters.dylib"
            if sys.platform == "darwin"
            else "runtime_linked_list_pointer_setters.so"
        )
        native_command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(FIXTURE),
        ]
        if sys.platform == "darwin":
            native_command.extend(["-dynamiclib", "-o", str(library)])
        else:
            native_command.extend(["-shared", "-fPIC", "-o", str(library)])
        subprocess.run(
            native_command,
            check=True,
            capture_output=True,
            text=True,
        )

        cls.loaded = ctypes.CDLL(str(library))
        cls.set_previous = (
            cls.loaded.open_cfw_runtime_linked_list_set_previous
        )
        cls.set_next = cls.loaded.open_cfw_runtime_linked_list_set_next
        cls.reset = (
            cls.loaded.open_cfw_test_runtime_linked_list_setter_reset
        )
        arguments = [
            ctypes.POINTER(RuntimeLinkedList),
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.set_previous.argtypes = arguments
        cls.set_next.argtypes = arguments
        cls.set_previous.restype = None
        cls.set_next.restype = None
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.storage = (ctypes.c_ubyte * 1024).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_linked_list_setter_storage",
        )
        cls.resolutions = ctypes.c_uint32.in_dll(
            cls.loaded,
            "open_cfw_test_runtime_linked_list_setter_resolutions",
        )

        target_object = Path(cls.temporary.name) / "setters.o"
        subprocess.run(
            [
                os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                *TARGET_FLAGS,
                "-c",
                str(SOURCE),
                "-o",
                str(target_object),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
        from apollo_overlay import extract_linked_overlay

        (
            cls.target_text,
            cls.target_functions,
            cls.target_report,
        ) = extract_linked_overlay(target_object)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def span(cls, start: int, end: int) -> bytes:
        return cls.application[
            start - APPLICATION_BASE:end - APPLICATION_BASE
        ]

    def setUp(self) -> None:
        self.reset()

    def test_previous_and_next_write_only_the_exact_metadata_word(
        self,
    ) -> None:
        for node_size in (0, 4, 12, 64, 128):
            node = 128
            linked_list = RuntimeLinkedList(
                node_size,
                0x11111111,
                0x22222222,
            )
            previous = 0x10203040 + node_size
            next_node = 0x50607080 + node_size

            before = bytes(self.storage)
            self.set_previous(
                ctypes.byref(linked_list),
                node,
                previous,
            )
            after_previous = bytes(self.storage)
            expected_previous = bytearray(before)
            struct.pack_into(
                "<I",
                expected_previous,
                node + node_size,
                previous,
            )
            with self.subTest(node_size=node_size, setter="previous"):
                self.assertEqual(after_previous, bytes(expected_previous))

            self.set_next(
                ctypes.byref(linked_list),
                node,
                next_node,
            )
            expected_next = bytearray(expected_previous)
            struct.pack_into(
                "<I",
                expected_next,
                node + node_size + 4,
                next_node,
            )
            with self.subTest(node_size=node_size, setter="next"):
                self.assertEqual(bytes(self.storage), bytes(expected_next))

        self.assertEqual(self.resolutions.value, 10)

    def test_null_node_returns_before_list_dereference_or_resolution(
        self,
    ) -> None:
        before = bytes(self.storage)
        self.set_previous(None, 0, 0x12345678)
        self.set_next(None, 0, 0x9ABCDEF0)
        self.assertEqual(bytes(self.storage), before)
        self.assertEqual(self.resolutions.value, 0)

    def test_full_width_pointer_values_are_preserved(self) -> None:
        linked_list = RuntimeLinkedList(20, 0, 0)
        node = 64
        self.set_previous(ctypes.byref(linked_list), node, 0xFFFFFFFF)
        self.set_next(ctypes.byref(linked_list), node, 0x80000000)
        self.assertEqual(
            struct.unpack_from("<I", self.storage, node + 20)[0],
            0xFFFFFFFF,
        )
        self.assertEqual(
            struct.unpack_from("<I", self.storage, node + 24)[0],
            0x80000000,
        )

    def test_stock_spans_and_adjacent_boundaries_are_exact(self) -> None:
        expected = {
            "previous": (
                "04b4002904d00068084469460968016001b07047",
                "e002a79c9ecd548fe89a31781a02e11c"
                "f6e7a665f5371b134a525530d8efa5d3",
            ),
            "next": (
                "04b4002905d000680844001d69460968016001b07047",
                "d8becca7ac8e719a4611d782de5c1689"
                "037be97fc221b0dcd63e3f6d6c70cd9a",
            ),
        }
        for name, (start, end) in FUNCTIONS.items():
            body = self.span(start, end)
            body_hex, digest = expected[name]
            with self.subTest(name=name):
                self.assertEqual(body.hex(), body_hex)
                self.assertEqual(hashlib.sha256(body).hexdigest(), digest)

        combined = self.span(0x00482DAE, 0x00482DD8)
        self.assertEqual(
            hashlib.sha256(combined).hexdigest(),
            "3565b5bf9a474304896e0a7acdcab630"
            "e492df488323a00845064736babb0463",
        )
        self.assertEqual(
            hashlib.sha256(
                self.span(0x00482DA4, 0x00482DAE)
            ).hexdigest(),
            "0528fed662ee528664a6631b0b85ff07"
            "979195a55d4543a0e175074974c6801d",
        )
        self.assertEqual(
            hashlib.sha256(
                self.span(0x00482DD8, 0x00482E4C)
            ).hexdigest(),
            "7f812480f5849e8396429428554c8f73"
            "c5511d9f3d476e945af364e85ced0017",
        )

    def test_callers_dependencies_and_alternate_entry_topology_are_exact(
        self,
    ) -> None:
        expected_callers = {
            "previous": [
                (0x00482B2A, "00f040f9"),
                (0x00482B44, "00f033f9"),
                (0x00482BAE, "00f0fef8"),
                (0x00482BB8, "00f0f9f8"),
                (0x00482BEC, "00f0dff8"),
                (0x00482C3E, "00f0b6f8"),
                (0x00482C94, "00f08bf8"),
                (0x00482D62, "00f024f8"),
                (0x00482D6C, "00f01ff8"),
            ],
            "next": [
                (0x00482B34, "00f045f9"),
                (0x00482BA4, "00f00df9"),
                (0x00482BC2, "00f0fef8"),
                (0x00482BE2, "00f0eef8"),
                (0x00482BFC, "00f0e1f8"),
                (0x00482C6A, "00f0aaf8"),
                (0x00482C8A, "00f09af8"),
                (0x00482D58, "00f033f8"),
                (0x00482D76, "00f024f8"),
            ],
        }
        expected_digests = {
            "previous": "1ae3756679260bf0505118a542fcf314"
                        "dc4ea6d7e2d3bf02cb148e33976b664a",
            "next": "eeee5a7a3f85c839000c99aed0cb02ed"
                    "c2608e8d58ab825f1d9356ee08cbebfd",
        }
        sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
        import apollo_overlay

        callers = {name: [] for name in FUNCTIONS}
        jumps = {name: [] for name in FUNCTIONS}
        interior = {name: [] for name in FUNCTIONS}
        dependencies = {name: [] for name in FUNCTIONS}
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
                for name, (start, end) in FUNCTIONS.items():
                    if target == start:
                        (callers if link else jumps)[name].append(
                            (address, encoded.hex())
                        )
                    if (
                        start < target < end
                        and not start <= address < end
                    ):
                        interior[name].append((address, target, link))
                    if link and start <= address < end:
                        dependencies[name].append(
                            (address, target, encoded.hex())
                        )

        for name in FUNCTIONS:
            digest = hashlib.sha256(
                b"".join(
                    struct.pack("<I", address)
                    for address, _encoded in callers[name]
                )
            ).hexdigest()
            with self.subTest(name=name):
                self.assertEqual(callers[name], expected_callers[name])
                self.assertEqual(digest, expected_digests[name])
                self.assertEqual(jumps[name], [])
                self.assertEqual(interior[name], [])
                self.assertEqual(dependencies[name], [])

    def test_no_narrow_or_stored_pointer_topology_exists(self) -> None:
        narrow_entry = {name: [] for name in FUNCTIONS}
        narrow_interior = {name: [] for name in FUNCTIONS}
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
            for name, (start, end) in FUNCTIONS.items():
                if start in candidates:
                    narrow_entry[name].append((address, halfword))
                for target in candidates:
                    if (
                        start < target < end
                        and not start <= address < end
                    ):
                        narrow_interior[name].append(
                            (address, target, halfword)
                        )

        stored = {name: [] for name in FUNCTIONS}
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from(
                "<I",
                self.application,
                offset,
            )[0]
            if not value & 1:
                continue
            target = value & ~1
            for name, (start, end) in FUNCTIONS.items():
                if start <= target < end:
                    stored[name].append(
                        (APPLICATION_BASE + offset, target)
                    )

        for name in FUNCTIONS:
            with self.subTest(name=name):
                self.assertEqual(narrow_entry[name], [])
                self.assertEqual(narrow_interior[name], [])
                self.assertEqual(stored[name], [])

    def test_reviewed_target_clang_output_is_exact(self) -> None:
        self.assertEqual(
            self.target_functions,
            {
                "open_cfw_runtime_linked_list_set_previous": {
                    "offset": 0,
                    "size": 10,
                },
                "open_cfw_runtime_linked_list_set_next": {
                    "offset": 12,
                    "size": 14,
                },
            },
        )
        self.assertEqual(self.target_report["text_size"], 26)
        self.assertEqual(self.target_report["rodata_size"], 0)
        self.assertEqual(self.target_report["rodata_sections"], [])
        self.assertEqual(
            self.target_report["resolved_relocation_count"],
            0,
        )
        self.assertEqual(self.target_report["resolved_relocations"], [])
        self.assertEqual(
            hashlib.sha256(self.target_text).hexdigest(),
            "076690d9797872e7ecdec6085918412b"
            "ec2158a595ab2661fb589c5c9bbdc1a9",
        )
        expected_bodies = {
            "open_cfw_runtime_linked_list_set_previous":
                "38c28420075b5e1887bd5bfb022240a7"
                "fb58960f956a59436c645782819217c8",
            "open_cfw_runtime_linked_list_set_next":
                "0c84a5b6c820c842e75c8054f6d668f5"
                "ddbaf3839cc19962946fd318d1785188",
        }
        for name, expected in expected_bodies.items():
            info = self.target_functions[name]
            body = self.target_text[
                info["offset"]:info["offset"] + info["size"]
            ]
            self.assertEqual(hashlib.sha256(body).hexdigest(), expected)

    def test_source_and_fixture_are_bounded(self) -> None:
        source = SOURCE.read_text()
        for token in (
            "open_cfw_runtime_linked_list_set_previous(",
            "open_cfw_runtime_linked_list_set_next(",
            "if (node == 0U)",
            "node_bytes + list->node_size",
            "node_bytes + list->node_size + 4U",
        ):
            self.assertIn(token, source)
        self.assertNotIn("#include <", source)
        self.assertIn(
            "runtime_linked_list_pointer_setters.c",
            FIXTURE.read_text(),
        )


if __name__ == "__main__":
    unittest.main()
