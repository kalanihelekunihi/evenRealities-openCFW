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
SOURCE = COMPONENT_ROOT / "runtime_linked_list_remove.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "runtime_linked_list_remove_host.c"
)
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
STOCK_START = 0x00482C0E
STOCK_END = 0x00482C9A
STORAGE_SIZE = 4096

EVENT_GET_HEAD = 1
EVENT_GET_TAIL = 2
EVENT_GET_PREVIOUS = 3
EVENT_GET_NEXT = 4
EVENT_SET_PREVIOUS = 5
EVENT_SET_NEXT = 6
EVENT_FAULT = 7

CALLERS = [
    (0x0044CA84, "36f0c3f8"),
    (0x0044CD64, "35f053ff"),
    (0x0044D444, "35f0e3fb"),
    (0x00450954, "32f05bf9"),
    (0x00450AD6, "32f09af8"),
    (0x00450B16, "32f07af8"),
    (0x00453918, "2ff079f9"),
    (0x004644FA, "1ef088fb"),
    (0x00482CC6, "fff7a2ff"),
    (0x00482D4E, "fff75eff"),
    (0x004B21D4, "d0f71bfd"),
    (0x005C307E, "bff6c6fd"),
    (0x005C314C, "bff65ffd"),
    (0x005C5BB8, "bdf629f8"),
    (0x005C5BDE, "bdf616f8"),
    (0x005C9CE0, "b8f695ff"),
    (0x005C9CF8, "b8f689ff"),
    (0x005C9F16, "b8f67afe"),
]


def _sign_extend(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return value - (1 << bits) if value & sign else value


class RuntimeLinkedListRemoveDescriptor(ctypes.Structure):
    _fields_ = [
        ("node_size", ctypes.c_uint32),
        ("head", ctypes.c_uint32),
        ("tail", ctypes.c_uint32),
    ]


class RuntimeLinkedListRemoveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "runtime_linked_list_remove.dylib"
            if sys.platform == "darwin"
            else "runtime_linked_list_remove.so"
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
        cls.reset = cls.loaded.open_cfw_test_runtime_linked_list_remove_reset
        cls.reset.argtypes = [ctypes.c_uint32]
        cls.reset.restype = None
        cls.node_at = cls.loaded.open_cfw_test_runtime_linked_list_remove_node_at
        cls.node_at.argtypes = [ctypes.c_uint32]
        cls.node_at.restype = ctypes.c_uint32
        cls.previous_at = (
            cls.loaded.open_cfw_test_runtime_linked_list_remove_previous_at
        )
        cls.previous_at.argtypes = [ctypes.c_uint32]
        cls.previous_at.restype = ctypes.c_uint32
        cls.next_at = cls.loaded.open_cfw_test_runtime_linked_list_remove_next_at
        cls.next_at.argtypes = [ctypes.c_uint32]
        cls.next_at.restype = ctypes.c_uint32
        cls.set_links = (
            cls.loaded.open_cfw_test_runtime_linked_list_remove_set_links
        )
        cls.set_links.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.set_links.restype = None
        cls.set_descriptor = (
            cls.loaded.open_cfw_test_runtime_linked_list_remove_set_descriptor
        )
        cls.set_descriptor.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.set_descriptor.restype = None
        cls.execute = cls.loaded.open_cfw_test_runtime_linked_list_remove_execute
        cls.execute.argtypes = [ctypes.c_uint32]
        cls.execute.restype = ctypes.c_uint32
        cls.execute_null = (
            cls.loaded.open_cfw_test_runtime_linked_list_remove_execute_null_list
        )
        cls.execute_null.argtypes = [ctypes.c_uint32]
        cls.execute_null.restype = ctypes.c_uint32
        cls.list = RuntimeLinkedListRemoveDescriptor.in_dll(
            cls.loaded,
            "open_cfw_test_runtime_linked_list_remove_descriptor",
        )
        cls.storage = (ctypes.c_ubyte * STORAGE_SIZE).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_linked_list_remove_storage",
        )
        cls.event_kinds = (ctypes.c_uint32 * 16).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_linked_list_remove_event_kind",
        )
        cls.event_nodes = (ctypes.c_uint32 * 16).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_linked_list_remove_event_node",
        )
        cls.event_links = (ctypes.c_uint32 * 16).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_linked_list_remove_event_link",
        )
        cls.event_heads = (ctypes.c_uint32 * 16).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_linked_list_remove_event_head",
        )
        cls.event_tails = (ctypes.c_uint32 * 16).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_linked_list_remove_event_tail",
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def uint(self, name: str) -> ctypes.c_uint32:
        return ctypes.c_uint32.in_dll(self.loaded, name)

    def nodes(self, count: int) -> list[int]:
        return [self.node_at(index) for index in range(count)]

    def events(self) -> list[tuple[int, int, int]]:
        count = self.uint(
            "open_cfw_test_runtime_linked_list_remove_event_count"
        ).value
        return [
            (
                self.event_kinds[index],
                self.event_nodes[index],
                self.event_links[index],
            )
            for index in range(count)
        ]

    def observed_order(self, expected_count: int) -> list[int]:
        if expected_count == 0:
            self.assertEqual(self.list.head, 0)
            self.assertEqual(self.list.tail, 0)
            return []
        order = []
        node = self.list.head
        previous = 0
        while node != 0:
            self.assertNotIn(node, order)
            self.assertEqual(self.previous_at(node), previous)
            order.append(node)
            previous = node
            node = self.next_at(node)
        self.assertEqual(previous, self.list.tail)
        self.assertEqual(len(order), expected_count)
        return order

    def test_every_valid_position_unlinks_without_clearing_node_links(
        self,
    ) -> None:
        for count in range(1, 9):
            for removed_index in range(count):
                self.reset(count)
                nodes = self.nodes(count)
                removed = nodes[removed_index]
                removed_links = (
                    self.previous_at(removed),
                    self.next_at(removed),
                )
                self.assertEqual(self.execute(removed), 0)
                with self.subTest(count=count, removed=removed_index):
                    self.assertEqual(
                        self.observed_order(count - 1),
                        nodes[:removed_index] + nodes[removed_index + 1:],
                    )
                    self.assertEqual(
                        (
                            self.previous_at(removed),
                            self.next_at(removed),
                        ),
                        removed_links,
                    )

    def test_head_removal_stores_head_before_clearing_previous(self) -> None:
        self.reset(4)
        nodes = self.nodes(4)
        self.assertEqual(self.execute(nodes[0]), 0)
        self.assertEqual(
            self.events(),
            [
                (EVENT_GET_HEAD, 0, nodes[0]),
                (EVENT_GET_NEXT, nodes[0], nodes[1]),
                (EVENT_SET_PREVIOUS, nodes[1], 0),
            ],
        )
        self.assertEqual(
            list(self.event_heads[:3]),
            [nodes[0], nodes[0], nodes[1]],
        )
        self.assertEqual(list(self.event_tails[:3]), [nodes[3]] * 3)

    def test_tail_removal_stores_tail_before_clearing_next(self) -> None:
        self.reset(4)
        nodes = self.nodes(4)
        self.assertEqual(self.execute(nodes[3]), 0)
        self.assertEqual(
            self.events(),
            [
                (EVENT_GET_HEAD, 0, nodes[0]),
                (EVENT_GET_TAIL, 0, nodes[3]),
                (EVENT_GET_PREVIOUS, nodes[3], nodes[2]),
                (EVENT_SET_NEXT, nodes[2], 0),
            ],
        )
        self.assertEqual(
            list(self.event_tails[:4]),
            [nodes[3], nodes[3], nodes[3], nodes[2]],
        )
        self.assertEqual(list(self.event_heads[:4]), [nodes[0]] * 4)

    def test_middle_removal_rewires_next_then_previous(self) -> None:
        self.reset(4)
        nodes = self.nodes(4)
        self.assertEqual(self.execute(nodes[2]), 0)
        self.assertEqual(
            self.events(),
            [
                (EVENT_GET_HEAD, 0, nodes[0]),
                (EVENT_GET_TAIL, 0, nodes[3]),
                (EVENT_GET_PREVIOUS, nodes[2], nodes[1]),
                (EVENT_GET_NEXT, nodes[2], nodes[3]),
                (EVENT_SET_NEXT, nodes[1], nodes[3]),
                (EVENT_SET_PREVIOUS, nodes[3], nodes[1]),
            ],
        )
        self.assertEqual(self.next_at(nodes[1]), nodes[3])
        self.assertEqual(self.previous_at(nodes[3]), nodes[1])

    def test_singleton_and_inconsistent_endpoint_zeroing_quirks(self) -> None:
        self.reset(1)
        node = self.node_at(0)
        self.assertEqual(self.execute(node), 0)
        self.assertEqual(self.events(), [
            (EVENT_GET_HEAD, 0, node),
            (EVENT_GET_NEXT, node, 0),
        ])
        self.assertEqual((self.list.head, self.list.tail), (0, 0))

        self.reset(2)
        nodes = self.nodes(2)
        external = self.node_at(5)
        self.set_links(external, 0, 0)
        self.set_descriptor(external, nodes[1])
        self.assertEqual(self.execute(external), 0)
        self.assertEqual((self.list.head, self.list.tail), (0, 0))

        self.reset(2)
        self.set_links(external, 0, 0)
        self.set_descriptor(nodes[0], external)
        self.assertEqual(self.execute(external), 0)
        self.assertEqual((self.list.head, self.list.tail), (0, 0))

    def test_nonmember_is_not_validated_and_can_corrupt_neighbors(self) -> None:
        self.reset(3)
        nodes = self.nodes(3)
        detached = self.node_at(5)
        self.set_links(detached, 0, 0)
        before = bytes(self.storage)
        self.assertEqual(self.execute(detached), 0)
        self.assertEqual(
            self.events(),
            [
                (EVENT_GET_HEAD, 0, nodes[0]),
                (EVENT_GET_TAIL, 0, nodes[2]),
                (EVENT_GET_PREVIOUS, detached, 0),
                (EVENT_GET_NEXT, detached, 0),
                (EVENT_SET_NEXT, 0, 0),
                (EVENT_SET_PREVIOUS, 0, 0),
            ],
        )
        self.assertEqual(bytes(self.storage), before)
        self.assertEqual(self.observed_order(3), nodes)

        self.reset(3)
        self.set_links(detached, nodes[0], nodes[2])
        self.assertEqual(self.execute(detached), 0)
        self.assertEqual(self.next_at(nodes[0]), nodes[2])
        self.assertEqual(self.previous_at(nodes[2]), nodes[0])
        self.assertEqual(self.next_at(nodes[1]), nodes[2])
        self.assertEqual(self.previous_at(nodes[1]), nodes[0])
        self.assertEqual(self.observed_order(2), [nodes[0], nodes[2]])

    def test_null_list_returns_but_null_node_faults_for_any_real_list(
        self,
    ) -> None:
        self.reset(3)
        self.assertEqual(self.execute_null(0), 0)
        self.assertEqual(self.execute_null(self.node_at(0)), 0)
        self.assertEqual(self.events(), [])

        self.reset(0)
        descriptor_before = (self.list.head, self.list.tail)
        storage_before = bytes(self.storage)
        self.assertEqual(self.execute(0), 1)
        self.assertEqual(
            self.events(),
            [
                (EVENT_GET_HEAD, 0, 0),
                (EVENT_FAULT, 0, EVENT_GET_NEXT),
            ],
        )
        self.assertEqual((self.list.head, self.list.tail), descriptor_before)
        self.assertEqual(bytes(self.storage), storage_before)

        self.reset(3)
        nodes = self.nodes(3)
        descriptor_before = (self.list.head, self.list.tail)
        storage_before = bytes(self.storage)
        self.assertEqual(self.execute(0), 1)
        self.assertEqual(
            self.events(),
            [
                (EVENT_GET_HEAD, 0, nodes[0]),
                (EVENT_GET_TAIL, 0, nodes[2]),
                (EVENT_FAULT, 0, EVENT_GET_PREVIOUS),
            ],
        )
        self.assertEqual((self.list.head, self.list.tail), descriptor_before)
        self.assertEqual(bytes(self.storage), storage_before)

    def test_reviewed_arm_text_rodata_and_relocations_are_pinned(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            object_path = Path(directory) / "runtime_linked_list_remove.o"
            command = [
                os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
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
                "-c",
                str(SOURCE),
                "-o",
                str(object_path),
            ]
            subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )

            sys.path.insert(0, str(OPENCFW_ROOT / "tools")); sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
            import apollo_overlay

            data, sections = apollo_overlay.parse_elf32(object_path)
            text_section = apollo_overlay.section_named(sections, ".text")
            start = int(text_section["offset"])
            end = start + int(text_section["size"])
            text = data[start:end]

        self.assertEqual(len(text), 146)
        self.assertEqual(
            hashlib.sha256(text).hexdigest(),
            "1d84514ca40ea7c2f7ee6600895d6405"
            "99d4f49c772d418c1a44d289d77d5a27",
        )
        section_names = {str(section["name"]) for section in sections}
        self.assertNotIn(".rodata", section_names)
        self.assertNotIn(".rel.text", section_names)

    def test_stock_boundaries_dependencies_callers_and_return_use_are_pinned(
        self,
    ) -> None:
        application = OFFICIAL.read_bytes()[32:]

        def span(start: int, end: int) -> bytes:
            return application[
                start - APPLICATION_BASE:end - APPLICATION_BASE
            ]

        preceding = span(0x00482BCA, STOCK_START)
        self.assertEqual(len(preceding), 68)
        self.assertEqual(
            hashlib.sha256(preceding).hexdigest(),
            "e4d96faa3751ad6a63d9b0fcebfb75d4"
            "6f1b4628fac1723b5826602c1a0f1274",
        )
        stock = span(STOCK_START, STOCK_END)
        self.assertEqual(len(stock), 140)
        self.assertEqual(
            hashlib.sha256(stock).hexdigest(),
            "f78c4e1dc9dedefcfde77a8e2911a89e"
            "b7d1436e8cac0736174cb5445e8a2131",
        )
        following = span(STOCK_END, 0x00482CD8)
        self.assertEqual(len(following), 62)
        self.assertEqual(
            hashlib.sha256(following).hexdigest(),
            "5587afeb5f0ce7bc1573dea6617ea0bc"
            "511688d6c95db261478eee5f68e7af04",
        )

        dependency_spans = {
            (0x00482CD8, 0x00482CE4):
                "52da3be9e77a64ae55928264f6f8b955"
                "294a7603e3dbcfaefab3b4150b2b52b3",
            (0x00482CE4, 0x00482CF0):
                "6717bf57b1ac7ad781c851f7c28681c1"
                "78495a01508c9d99488d5d36ada09443",
            (0x00482CF0, 0x00482CFA):
                "2a717b6780c837377f451d1c683fff0e"
                "6406c048fc28554a03203e6ef5e3a128",
            (0x00482CFA, 0x00482D02):
                "10abde261a5ab42b61c57befe77bb9a1"
                "b8131964b4e24b9036b74e93366ce666",
            (0x00482DAE, 0x00482DC2):
                "e002a79c9ecd548fe89a31781a02e11c"
                "f6e7a665f5371b134a525530d8efa5d3",
            (0x00482DC2, 0x00482DD8):
                "d8becca7ac8e719a4611d782de5c1689"
                "037be97fc221b0dcd63e3f6d6c70cd9a",
        }
        for (start, end), expected in dependency_spans.items():
            with self.subTest(dependency=f"{start:#010x}"):
                self.assertEqual(
                    hashlib.sha256(span(start, end)).hexdigest(),
                    expected,
                )

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

        self.assertEqual(callers, CALLERS)
        self.assertEqual(
            hashlib.sha256(
                b"".join(
                    struct.pack("<I", address)
                    for address, _ in callers
                )
            ).hexdigest(),
            "7857143175e40c79831e2e042379a5be"
            "125832653ff16ae2b93263e41834ca33",
        )
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(
            dependencies,
            [
                (0x00482C1A, 0x00482CD8, "00f05df8"),
                (0x00482C26, 0x00482CF0, "00f063f8"),
                (0x00482C3E, 0x00482DAE, "00f0b6f8"),
                (0x00482C46, 0x00482CE4, "00f04df8"),
                (0x00482C52, 0x00482CFA, "00f052f8"),
                (0x00482C6A, 0x00482DC2, "00f0aaf8"),
                (0x00482C74, 0x00482CFA, "00f041f8"),
                (0x00482C7E, 0x00482CF0, "00f037f8"),
                (0x00482C8A, 0x00482DC2, "00f09af8"),
                (0x00482C94, 0x00482DAE, "00f08bf8"),
            ],
        )

        next_instruction_bytes = {
            0x0044CA84: "2000",
            0x0044CD64: "3000",
            0x0044D444: "2000",
            0x00450954: "00f03ff8",
            0x00450AD6: "6069",
            0x00450B16: "6869",
            0x00453918: "2000",
            0x004644FA: "0120",
            0x00482CC6: "2000",
            0x00482D4E: "3a00",
            0x004B21D4: "2068",
            0x005C307E: "4046",
            0x005C314C: "3800",
            0x005C5BB8: "2000",
            0x005C5BDE: "2000",
            0x005C9CE0: "3800",
            0x005C9CF8: "95f86800",
            0x005C9F16: "2800",
        }
        for address, expected in next_instruction_bytes.items():
            observed = span(
                address + 4,
                address + 4 + len(bytes.fromhex(expected)),
            )
            with self.subTest(caller=f"{address:#010x}"):
                self.assertEqual(observed.hex(), expected)
        self.assertEqual(
            span(0x004509DA, 0x004509E0).hex(),
            "10b5544c0120",
        )

    def test_wide_narrow_and_stored_pointer_topology_is_complete(self) -> None:
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
            "open_cfw_runtime_linked_list_remove(",
            "list->head = OPEN_CFW_RUNTIME_LINKED_LIST_REMOVE_GET_NEXT(",
            "list->tail = OPEN_CFW_RUNTIME_LINKED_LIST_REMOVE_GET_PREVIOUS(",
            "OPEN_CFW_RUNTIME_LINKED_LIST_REMOVE_SET_NEXT(list, previous, next)",
            "OPEN_CFW_RUNTIME_LINKED_LIST_REMOVE_SET_PREVIOUS(",
            "0x00482CD9U",
            "0x00482CE5U",
            "0x00482CF1U",
            "0x00482CFBU",
            "0x00482DAFU",
            "0x00482DC3U",
        ):
            self.assertIn(token, source)
        self.assertNotIn("#include <", source)
        self.assertIn(
            "runtime_linked_list_remove.c",
            FIXTURE.read_text(),
        )


if __name__ == "__main__":
    unittest.main()
