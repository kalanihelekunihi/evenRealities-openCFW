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
SOURCE = COMPONENT_ROOT / "runtime_linked_list_insertions.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "runtime_linked_list_insertions_host.c"
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
    "head": (0x00482B12, 0x00482B56),
    "before": (0x00482B56, 0x00482BCA),
    "tail": (0x00482BCA, 0x00482C0E),
}
STORAGE_SIZE = 4096
EVENT_CAPACITY = 32

EVENT_ALLOCATE = 1
EVENT_GET_HEAD = 2
EVENT_GET_PREVIOUS = 3
EVENT_SET_PREVIOUS = 4
EVENT_SET_NEXT = 5
EVENT_INSERT_HEAD = 6

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


class RuntimeLinkedListInsertDescriptor(ctypes.Structure):
    _fields_ = [
        ("node_size", ctypes.c_uint32),
        ("head", ctypes.c_uint32),
        ("tail", ctypes.c_uint32),
    ]


class RuntimeLinkedListInsertionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "runtime_linked_list_insertions.dylib"
            if sys.platform == "darwin"
            else "runtime_linked_list_insertions.so"
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
        cls.reset = cls.loaded.open_cfw_test_runtime_linked_list_insert_reset
        cls.reset.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.reset.restype = None
        cls.set_links = (
            cls.loaded.open_cfw_test_runtime_linked_list_insert_set_links
        )
        cls.set_links.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.set_links.restype = None
        cls.previous = (
            cls.loaded.open_cfw_test_runtime_linked_list_insert_previous
        )
        cls.previous.argtypes = [ctypes.c_uint32]
        cls.previous.restype = ctypes.c_uint32
        cls.next = cls.loaded.open_cfw_test_runtime_linked_list_insert_next
        cls.next.argtypes = [ctypes.c_uint32]
        cls.next.restype = ctypes.c_uint32
        cls.execute_head = (
            cls.loaded.open_cfw_test_runtime_linked_list_insert_execute_head
        )
        cls.execute_head.argtypes = []
        cls.execute_head.restype = ctypes.c_uint32
        cls.execute_before = (
            cls.loaded.open_cfw_test_runtime_linked_list_insert_execute_before
        )
        cls.execute_before.argtypes = [ctypes.c_uint32]
        cls.execute_before.restype = ctypes.c_uint32
        cls.execute_tail = (
            cls.loaded.open_cfw_test_runtime_linked_list_insert_execute_tail
        )
        cls.execute_tail.argtypes = []
        cls.execute_tail.restype = ctypes.c_uint32
        cls.execute_before_null = (
            cls.loaded
            .open_cfw_test_runtime_linked_list_insert_execute_before_null_list
        )
        cls.execute_before_null.argtypes = [ctypes.c_uint32]
        cls.execute_before_null.restype = ctypes.c_uint32

        cls.list = RuntimeLinkedListInsertDescriptor.in_dll(
            cls.loaded,
            "open_cfw_test_runtime_linked_list_insert_descriptor",
        )
        cls.storage = (ctypes.c_ubyte * STORAGE_SIZE).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_linked_list_insert_storage",
        )
        cls.event_kind = (ctypes.c_uint32 * EVENT_CAPACITY).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_linked_list_insert_event_kind",
        )
        cls.event_node = (ctypes.c_uint32 * EVENT_CAPACITY).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_linked_list_insert_event_node",
        )
        cls.event_link = (ctypes.c_uint32 * EVENT_CAPACITY).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_linked_list_insert_event_link",
        )
        cls.event_head = (ctypes.c_uint32 * EVENT_CAPACITY).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_linked_list_insert_event_head",
        )
        cls.event_tail = (ctypes.c_uint32 * EVENT_CAPACITY).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_linked_list_insert_event_tail",
        )

        target_object = Path(cls.temporary.name) / "insertions.o"
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

    def uint(self, name: str) -> ctypes.c_uint32:
        return ctypes.c_uint32.in_dll(self.loaded, name)

    def events(self) -> list[tuple[int, int, int, int, int]]:
        count = self.uint(
            "open_cfw_test_runtime_linked_list_insert_event_count"
        ).value
        self.assertLessEqual(count, EVENT_CAPACITY)
        return [
            (
                self.event_kind[index],
                self.event_node[index],
                self.event_link[index],
                self.event_head[index],
                self.event_tail[index],
            )
            for index in range(count)
        ]

    def test_head_insertion_mutates_links_before_descriptor(self) -> None:
        node_size = 16
        old_head = 256
        old_tail = 512
        new_node = 768
        self.reset(node_size, old_head, old_tail, new_node)
        self.set_links(old_head, 0, old_tail)
        self.set_links(old_tail, old_head, 0)

        self.assertEqual(self.execute_head(), new_node)
        self.assertEqual(
            self.events(),
            [
                (EVENT_ALLOCATE, 24, new_node, old_head, old_tail),
                (
                    EVENT_SET_PREVIOUS,
                    new_node,
                    0,
                    old_head,
                    old_tail,
                ),
                (
                    EVENT_SET_NEXT,
                    new_node,
                    old_head,
                    old_head,
                    old_tail,
                ),
                (
                    EVENT_SET_PREVIOUS,
                    old_head,
                    new_node,
                    old_head,
                    old_tail,
                ),
            ],
        )
        self.assertEqual((self.list.head, self.list.tail), (new_node, old_tail))
        self.assertEqual(
            (self.previous(new_node), self.next(new_node)),
            (0, old_head),
        )
        self.assertEqual(self.previous(old_head), new_node)

        self.reset(node_size, 0, 0, new_node)
        self.assertEqual(self.execute_head(), new_node)
        self.assertEqual((self.list.head, self.list.tail), (new_node, new_node))
        self.assertEqual(
            [event[:3] for event in self.events()],
            [
                (EVENT_ALLOCATE, 24, new_node),
                (EVENT_SET_PREVIOUS, new_node, 0),
                (EVENT_SET_NEXT, new_node, 0),
            ],
        )

    def test_tail_insertion_mutates_links_before_descriptor(self) -> None:
        node_size = 20
        old_head = 128
        old_tail = 384
        new_node = 896
        self.reset(node_size, old_head, old_tail, new_node)
        self.set_links(old_head, 0, old_tail)
        self.set_links(old_tail, old_head, 0)

        self.assertEqual(self.execute_tail(), new_node)
        self.assertEqual(
            self.events(),
            [
                (EVENT_ALLOCATE, 28, new_node, old_head, old_tail),
                (
                    EVENT_SET_NEXT,
                    new_node,
                    0,
                    old_head,
                    old_tail,
                ),
                (
                    EVENT_SET_PREVIOUS,
                    new_node,
                    old_tail,
                    old_head,
                    old_tail,
                ),
                (
                    EVENT_SET_NEXT,
                    old_tail,
                    new_node,
                    old_head,
                    old_tail,
                ),
            ],
        )
        self.assertEqual((self.list.head, self.list.tail), (old_head, new_node))
        self.assertEqual(
            (self.previous(new_node), self.next(new_node)),
            (old_tail, 0),
        )
        self.assertEqual(self.next(old_tail), new_node)

        self.reset(node_size, 0, 0, new_node)
        self.assertEqual(self.execute_tail(), new_node)
        self.assertEqual((self.list.head, self.list.tail), (new_node, new_node))

    def test_insert_before_middle_and_head_paths_are_exact(self) -> None:
        node_size = 12
        head = 128
        previous = 256
        active = 384
        tail = 512
        new_node = 768
        self.reset(node_size, head, tail, new_node)
        self.set_links(head, 0, previous)
        self.set_links(previous, head, active)
        self.set_links(active, previous, tail)
        self.set_links(tail, active, 0)

        self.assertEqual(self.execute_before(active), new_node)
        self.assertEqual(
            [event[:3] for event in self.events()],
            [
                (EVENT_GET_HEAD, 0, head),
                (EVENT_ALLOCATE, 20, new_node),
                (EVENT_GET_PREVIOUS, active, previous),
                (EVENT_SET_NEXT, previous, new_node),
                (EVENT_SET_PREVIOUS, new_node, previous),
                (EVENT_SET_PREVIOUS, active, new_node),
                (EVENT_SET_NEXT, new_node, active),
            ],
        )
        self.assertEqual((self.list.head, self.list.tail), (head, tail))
        self.assertEqual(self.next(previous), new_node)
        self.assertEqual(
            (self.previous(new_node), self.next(new_node)),
            (previous, active),
        )
        self.assertEqual(self.previous(active), new_node)
        self.assertTrue(
            all(
                event[3:] == (head, tail)
                for event in self.events()
            )
        )

        self.reset(node_size, head, tail, new_node)
        self.set_links(head, 0, tail)
        self.set_links(tail, head, 0)
        self.assertEqual(self.execute_before(head), new_node)
        self.assertEqual(
            [event[:3] for event in self.events()],
            [
                (EVENT_GET_HEAD, 0, head),
                (EVENT_INSERT_HEAD, 0, 0),
                (EVENT_ALLOCATE, 20, new_node),
                (EVENT_SET_PREVIOUS, new_node, 0),
                (EVENT_SET_NEXT, new_node, head),
                (EVENT_SET_PREVIOUS, head, new_node),
            ],
        )
        self.assertEqual((self.list.head, self.list.tail), (new_node, tail))

    def test_invalid_previous_null_preserves_stock_orphan_quirk(self) -> None:
        node_size = 8
        head = 128
        active = 384
        tail = 512
        new_node = 768
        self.reset(node_size, head, tail, new_node)
        self.set_links(head, 0, tail)
        self.set_links(active, 0, tail)
        self.set_links(tail, head, 0)

        self.assertEqual(self.execute_before(active), new_node)
        self.assertEqual(
            [event[:3] for event in self.events()],
            [
                (EVENT_GET_HEAD, 0, head),
                (EVENT_ALLOCATE, 16, new_node),
                (EVENT_GET_PREVIOUS, active, 0),
                (EVENT_SET_NEXT, 0, new_node),
                (EVENT_SET_PREVIOUS, new_node, 0),
                (EVENT_SET_PREVIOUS, active, new_node),
                (EVENT_SET_NEXT, new_node, active),
            ],
        )
        self.assertEqual((self.list.head, self.list.tail), (head, tail))
        self.assertEqual(self.next(head), tail)
        self.assertEqual(
            (self.previous(new_node), self.next(new_node)),
            (0, active),
        )
        self.assertEqual(self.previous(active), new_node)

    def test_null_guards_failures_and_size_wrap_are_exact(self) -> None:
        self.reset(16, 128, 512, 768)
        before_descriptor = bytes(ctypes.string_at(ctypes.byref(self.list), 12))
        before_storage = bytes(self.storage)
        self.assertEqual(self.execute_before(0), 0)
        self.assertEqual(self.execute_before_null(384), 0)
        self.assertEqual(self.events(), [])
        self.assertEqual(
            bytes(ctypes.string_at(ctypes.byref(self.list), 12)),
            before_descriptor,
        )
        self.assertEqual(bytes(self.storage), before_storage)

        for operation in (self.execute_head, self.execute_tail):
            self.reset(0xFFFFFFFC, 128, 512, 0)
            before_descriptor = bytes(
                ctypes.string_at(ctypes.byref(self.list), 12)
            )
            before_storage = bytes(self.storage)
            self.assertEqual(operation(), 0)
            with self.subTest(operation=operation.__name__):
                self.assertEqual(
                    self.uint(
                        "open_cfw_test_runtime_linked_list_insert_"
                        "allocation_size"
                    ).value,
                    4,
                )
                self.assertEqual(
                    bytes(ctypes.string_at(ctypes.byref(self.list), 12)),
                    before_descriptor,
                )
                self.assertEqual(bytes(self.storage), before_storage)
                self.assertEqual(
                    [event[:3] for event in self.events()],
                    [(EVENT_ALLOCATE, 4, 0)],
                )

        self.reset(16, 128, 512, 0)
        self.assertEqual(self.execute_before(384), 0)
        self.assertEqual(
            [event[:3] for event in self.events()],
            [
                (EVENT_GET_HEAD, 0, 128),
                (EVENT_ALLOCATE, 24, 0),
            ],
        )

    def test_head_and_tail_null_list_dereferences_fault(self) -> None:
        probe = Path(self.temporary.name) / "null_probe"
        subprocess.run(
            [
                os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                "-O2",
                "-Wall",
                "-Wextra",
                "-Werror",
                "-DOPEN_CFW_TEST_RUNTIME_LINKED_LIST_INSERT_NULL_PROBE",
                str(FIXTURE),
                "-o",
                str(probe),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        for mode in ("head", "tail"):
            completed = subprocess.run(
                [str(probe), mode],
                capture_output=True,
                text=True,
            )
            with self.subTest(mode=mode):
                self.assertNotEqual(completed.returncode, 0)

    def test_stock_function_and_adjacent_spans_are_exact(self) -> None:
        expected = {
            "head": (
                68,
                "576df2aaf1e74eff0a6c8cc0375747bf"
                "2264c66d964267f8ab25ecbc331f7cb4",
            ),
            "before": (
                116,
                "cf3af22fd95b08760465aea0fd071292"
                "d08221e269ad91163cf575264ce4dd08",
            ),
            "tail": (
                68,
                "e4d96faa3751ad6a63d9b0fcebfb75d4"
                "6f1b4628fac1723b5826602c1a0f1274",
            ),
        }
        for name, (start, end) in FUNCTIONS.items():
            body = self.span(start, end)
            size, digest = expected[name]
            with self.subTest(name=name):
                self.assertEqual(len(body), size)
                self.assertEqual(hashlib.sha256(body).hexdigest(), digest)

        combined = self.span(0x00482B12, 0x00482C0E)
        self.assertEqual(len(combined), 252)
        self.assertEqual(
            hashlib.sha256(combined).hexdigest(),
            "baaea6576a01385d49632243ed2a0059"
            "2793cbcaa75bceb0494444f1fcedc03e",
        )
        self.assertEqual(
            hashlib.sha256(
                self.span(0x00482B00, 0x00482B12)
            ).hexdigest(),
            "e8bd7819a54b5fdf15e0c8404e14d9f"
            "43f0ec417fecffe139d45c0d3bf75799c",
        )
        self.assertEqual(
            hashlib.sha256(
                self.span(0x00482C0E, 0x00482C9A)
            ).hexdigest(),
            "f78c4e1dc9dedefcfde77a8e2911a89e"
            "b7d1436e8cac0736174cb5445e8a2131",
        )

    def test_all_callers_dependencies_and_wide_topology_are_exact(
        self,
    ) -> None:
        expected_callers = {
            "head": [
                (0x0044C09E, "36f038fd"),
                (0x0044F7CC, "33f0a1f9"),
                (0x00450434, "32f06dfb"),
                (0x0046447A, "1ef04afb"),
                (0x00482B74, "fff7cdff"),
                (0x004890CE, "f9f720fd"),
                (0x004C7076, "bbf74cfd"),
                (0x005C2BA0, "bff6b7ff"),
                (0x005C976E, "b9f6d0f9"),
            ],
            "before": [(0x004538EC, "2ff033f9")],
            "tail": [
                (0x0044D364, "35f031fc"),
                (0x00453722, "2ff052fa"),
                (0x004B2136, "d0f748fd"),
            ],
        }
        expected_digests = {
            "head": "bed7d5fdf1629d95846ee44543e4765d"
                    "e8198e74a60d68867bc6043185cd1c4f",
            "before": "b0b7ce061af8028a5a9bbf65b6d39283"
                      "dc83b4fea4a66ea2b94e9b57b5e016bc",
            "tail": "68c9ff86e45f862c42675e3416e38028"
                    "564befe2fc1f22e512a8cdb64dfd272b",
        }
        expected_dependencies = {
            "head": [
                (0x00482B1A, 0x0044F718, "ccf7fdfd"),
                (0x00482B2A, 0x00482DAE, "00f040f9"),
                (0x00482B34, 0x00482DC2, "00f045f9"),
                (0x00482B44, 0x00482DAE, "00f033f9"),
            ],
            "before": [
                (0x00482B6A, 0x00482CD8, "00f0b5f8"),
                (0x00482B74, 0x00482B12, "fff7cdff"),
                (0x00482B86, 0x0044F718, "ccf7c7fd"),
                (0x00482B98, 0x00482CFA, "00f0aff8"),
                (0x00482BA4, 0x00482DC2, "00f00df9"),
                (0x00482BAE, 0x00482DAE, "00f0fef8"),
                (0x00482BB8, 0x00482DAE, "00f0f9f8"),
                (0x00482BC2, 0x00482DC2, "00f0fef8"),
            ],
            "tail": [
                (0x00482BD2, 0x0044F718, "ccf7a1fd"),
                (0x00482BE2, 0x00482DC2, "00f0eef8"),
                (0x00482BEC, 0x00482DAE, "00f0dff8"),
                (0x00482BFC, 0x00482DC2, "00f0e1f8"),
            ],
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
                self.assertEqual(
                    dependencies[name],
                    expected_dependencies[name],
                )

    def test_no_narrow_entries_and_stored_candidates_are_unaligned(
        self,
    ) -> None:
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
        for name, (start, end) in FUNCTIONS.items():
            for target in range(start, end, 2):
                needle = struct.pack("<I", target | 1)
                position = self.application.find(needle)
                while position >= 0:
                    stored[name].append(
                        (APPLICATION_BASE + position, target)
                    )
                    position = self.application.find(
                        needle,
                        position + 1,
                    )

        self.assertEqual(narrow_entry, {name: [] for name in FUNCTIONS})
        self.assertEqual(narrow_interior, {name: [] for name in FUNCTIONS})
        self.assertEqual(
            stored,
            {
                "head": [(0x00492BCD, 0x00482B48)],
                "before": [(0x0054AA89, 0x00482BA8)],
                "tail": [],
            },
        )
        self.assertTrue(
            all(
                address & 1
                for candidates in stored.values()
                for address, _target in candidates
            )
        )

    def test_reviewed_target_clang_output_is_exact(self) -> None:
        self.assertEqual(
            self.target_functions,
            {
                "open_cfw_runtime_linked_list_insert_head": {
                    "offset": 0,
                    "size": 74,
                },
                "open_cfw_runtime_linked_list_insert_before": {
                    "offset": 76,
                    "size": 134,
                },
                "open_cfw_runtime_linked_list_insert_tail": {
                    "offset": 212,
                    "size": 74,
                },
            },
        )
        self.assertEqual(self.target_report["text_size"], 286)
        self.assertEqual(self.target_report["rodata_size"], 0)
        self.assertEqual(self.target_report["rodata_sections"], [])
        self.assertEqual(
            self.target_report["resolved_relocation_count"],
            1,
        )
        self.assertEqual(
            self.target_report["resolved_relocations"],
            [
                {
                    "section": ".rel.text",
                    "site": 124,
                    "symbol": "open_cfw_runtime_linked_list_insert_head",
                    "type": 30,
                }
            ],
        )
        self.assertEqual(
            hashlib.sha256(self.target_text).hexdigest(),
            "ac9c87672e502d874b46f3dea807388a"
            "6112d66eb31668980b7714e73be27f61",
        )
        expected_bodies = {
            "open_cfw_runtime_linked_list_insert_head":
                "6496ec2e89dc21ea27c6596fdf9c770f"
                "4124db73f3887de223f8e630c8dbd878",
            "open_cfw_runtime_linked_list_insert_before":
                "f2cd9eed89630b708bed29562439fb2de"
                "298a06c29d8217a7b41f871a8c1127f",
            "open_cfw_runtime_linked_list_insert_tail":
                "a7a24f9c3e084ba21ea3149ffff23553"
                "2e2396b450b87dc8eac9443b5fb57e13",
        }
        for name, expected in expected_bodies.items():
            info = self.target_functions[name]
            body = self.target_text[
                info["offset"]:info["offset"] + info["size"]
            ]
            self.assertEqual(hashlib.sha256(body).hexdigest(), expected)

    def test_combined_linked_list_translation_unit_is_compatible(
        self,
    ) -> None:
        sources = [
            "runtime_linked_list_init.c",
            "runtime_linked_list_accessors.c",
            "runtime_linked_list_pointer_setters.c",
            "runtime_linked_list_move_before.c",
            "runtime_linked_list_insertions.c",
        ]
        translation_unit = "\n".join(
            f'#include "{COMPONENT_ROOT / source}"'
            for source in sources
        ) + "\n"
        combined_object = Path(self.temporary.name) / "linked_list_all.o"
        subprocess.run(
            [
                os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                *TARGET_FLAGS,
                "-x",
                "c",
                "-c",
                "-",
                "-o",
                str(combined_object),
            ],
            input=translation_unit,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertGreater(combined_object.stat().st_size, 0)

    def test_source_and_fixture_are_bounded(self) -> None:
        source = SOURCE.read_text()
        for token in (
            "open_cfw_runtime_linked_list_insert_head(",
            "open_cfw_runtime_linked_list_insert_before(",
            "open_cfw_runtime_linked_list_insert_tail(",
            "list->node_size + 8U",
            "0x0044F719U",
            "0x00482CD9U",
            "0x00482CFBU",
            "0x00482DAFU",
            "0x00482DC3U",
        ):
            self.assertIn(token, source)
        self.assertNotIn("#include <", source)
        self.assertIn(
            "runtime_linked_list_insertions.c",
            FIXTURE.read_text(),
        )


if __name__ == "__main__":
    unittest.main()
