from __future__ import annotations

import os

import ctypes
import hashlib
import itertools
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
COMPONENT_ROOT = OPENCFW_ROOT / "components" / "apollo_main" / "core_overlay"
SOURCE = COMPONENT_ROOT / "runtime_linked_list_move_before.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "runtime_linked_list_move_before_host.c"
)
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
STOCK_START = 0x00482D22
STOCK_END = 0x00482D88

EVENT_GET_TAIL = 1
EVENT_GET_PREVIOUS = 2
EVENT_REMOVE = 3
EVENT_SET_PREVIOUS = 4
EVENT_SET_NEXT = 5


def _sign_extend(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return value - (1 << bits) if value & sign else value


class RuntimeLinkedListMoveDescriptor(ctypes.Structure):
    _fields_ = [
        ("node_size", ctypes.c_uint32),
        ("head", ctypes.c_uint32),
        ("tail", ctypes.c_uint32),
    ]


class RuntimeLinkedListMoveBeforeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "runtime_linked_list_move_before.dylib"
            if sys.platform == "darwin"
            else "runtime_linked_list_move_before.so"
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
        cls.reset = cls.loaded.open_cfw_test_runtime_linked_list_move_reset
        cls.reset.argtypes = [ctypes.c_uint32]
        cls.reset.restype = None
        cls.node_at = (
            cls.loaded.open_cfw_test_runtime_linked_list_move_node_at
        )
        cls.node_at.argtypes = [ctypes.c_uint32]
        cls.node_at.restype = ctypes.c_uint32
        cls.previous_at = (
            cls.loaded.open_cfw_test_runtime_linked_list_move_previous_at
        )
        cls.previous_at.argtypes = [ctypes.c_uint32]
        cls.previous_at.restype = ctypes.c_uint32
        cls.next_at = cls.loaded.open_cfw_test_runtime_linked_list_move_next_at
        cls.next_at.argtypes = [ctypes.c_uint32]
        cls.next_at.restype = ctypes.c_uint32
        cls.set_links = (
            cls.loaded.open_cfw_test_runtime_linked_list_move_set_links
        )
        cls.set_links.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.set_links.restype = None
        cls.execute = cls.loaded.open_cfw_test_runtime_linked_list_move_execute
        cls.execute.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.execute.restype = None
        cls.execute_null = (
            cls.loaded.open_cfw_test_runtime_linked_list_move_execute_null_list
        )
        cls.execute_null.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.execute_null.restype = None
        cls.list = RuntimeLinkedListMoveDescriptor.in_dll(
            cls.loaded,
            "open_cfw_test_runtime_linked_list_move_descriptor",
        )
        cls.event_kinds = (ctypes.c_uint32 * 16).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_linked_list_move_event_kind",
        )
        cls.event_nodes = (ctypes.c_uint32 * 16).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_linked_list_move_event_node",
        )
        cls.event_links = (ctypes.c_uint32 * 16).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_linked_list_move_event_link",
        )
        cls.event_heads = (ctypes.c_uint32 * 16).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_linked_list_move_event_head",
        )
        cls.event_tails = (ctypes.c_uint32 * 16).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_linked_list_move_event_tail",
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def uint(self, name: str) -> ctypes.c_uint32:
        return ctypes.c_uint32.in_dll(self.loaded, name)

    def nodes(self, count: int) -> list[int]:
        return [self.node_at(index) for index in range(count)]

    def observed_order(self, count: int) -> list[int]:
        if count == 0:
            self.assertEqual(self.list.head, 0)
            self.assertEqual(self.list.tail, 0)
            return []
        order = []
        current = self.list.head
        previous = 0
        while current != 0:
            self.assertNotIn(current, order)
            self.assertEqual(self.previous_at(current), previous)
            order.append(current)
            previous = current
            current = self.next_at(current)
        self.assertEqual(previous, self.list.tail)
        self.assertEqual(len(order), count)
        return order

    def events(self) -> list[tuple[int, int, int]]:
        count = self.uint(
            "open_cfw_test_runtime_linked_list_move_event_count"
        ).value
        return [
            (
                self.event_kinds[index],
                self.event_nodes[index],
                self.event_links[index],
            )
            for index in range(count)
        ]

    def expected_order(
        self,
        nodes: list[int],
        moving_index: int,
        before_index: int | None,
    ) -> list[int]:
        moving = nodes[moving_index]
        before = 0 if before_index is None else nodes[before_index]
        if moving == before:
            return nodes
        previous = nodes[-1] if before == 0 else (
            0 if before_index == 0 else nodes[before_index - 1]
        )
        if moving == previous:
            return nodes
        result = [node for node in nodes if node != moving]
        if before == 0:
            result.append(moving)
        else:
            result.insert(result.index(before), moving)
        return result

    def test_all_valid_move_positions_match_list_oracle(self) -> None:
        for count in range(1, 9):
            for moving_index, before_index in itertools.product(
                range(count),
                [None, *range(count)],
            ):
                self.reset(count)
                nodes = self.nodes(count)
                before = (
                    0 if before_index is None else nodes[before_index]
                )
                self.execute(nodes[moving_index], before)
                with self.subTest(
                    count=count,
                    moving=moving_index,
                    before=before_index,
                ):
                    self.assertEqual(
                        self.observed_order(count),
                        self.expected_order(
                            nodes,
                            moving_index,
                            before_index,
                        ),
                    )

    def test_same_node_returns_without_reading_or_mutating(self) -> None:
        self.reset(4)
        nodes = self.nodes(4)
        before = (
            self.list.head,
            self.list.tail,
            [
                (self.previous_at(node), self.next_at(node))
                for node in nodes
            ],
        )
        self.execute(nodes[2], nodes[2])
        self.assertEqual(self.events(), [])
        self.assertEqual(
            (
                self.list.head,
                self.list.tail,
                [
                    (self.previous_at(node), self.next_at(node))
                    for node in nodes
                ],
            ),
            before,
        )

    def test_already_before_target_and_tail_to_end_are_noops(self) -> None:
        for moving_index, before_index in ((1, 2), (3, None)):
            self.reset(4)
            nodes = self.nodes(4)
            before = 0 if before_index is None else nodes[before_index]
            self.execute(nodes[moving_index], before)
            expected_lookup = (
                (EVENT_GET_TAIL, 0, nodes[-1])
                if before_index is None
                else (
                    EVENT_GET_PREVIOUS,
                    before,
                    nodes[moving_index],
                )
            )
            with self.subTest(before=before_index):
                self.assertEqual(self.events(), [expected_lookup])
                self.assertEqual(self.observed_order(4), nodes)

    def test_mutation_dependency_order_and_head_tail_timing_are_exact(
        self,
    ) -> None:
        self.reset(4)
        nodes = self.nodes(4)
        moving = nodes[3]
        before = nodes[0]
        self.execute(moving, before)
        self.assertEqual(
            self.events(),
            [
                (EVENT_GET_PREVIOUS, before, 0),
                (EVENT_REMOVE, moving, 0),
                (EVENT_SET_NEXT, 0, moving),
                (EVENT_SET_PREVIOUS, moving, 0),
                (EVENT_SET_PREVIOUS, before, moving),
                (EVENT_SET_NEXT, moving, before),
            ],
        )
        self.assertEqual(
            list(self.event_heads[:6]),
            [nodes[0], nodes[0], nodes[0], nodes[0], nodes[0], nodes[0]],
        )
        self.assertEqual(
            list(self.event_tails[:6]),
            [nodes[3], nodes[3], nodes[2], nodes[2], nodes[2], nodes[2]],
        )
        self.assertEqual(self.list.head, moving)
        self.assertEqual(self.list.tail, nodes[2])

    def test_null_before_moves_to_tail_and_updates_tail_after_links(
        self,
    ) -> None:
        self.reset(4)
        nodes = self.nodes(4)
        moving = nodes[0]
        self.execute(moving, 0)
        self.assertEqual(
            self.events(),
            [
                (EVENT_GET_TAIL, 0, nodes[3]),
                (EVENT_REMOVE, moving, 0),
                (EVENT_SET_NEXT, nodes[3], moving),
                (EVENT_SET_PREVIOUS, moving, nodes[3]),
                (EVENT_SET_PREVIOUS, 0, moving),
                (EVENT_SET_NEXT, moving, 0),
            ],
        )
        self.assertEqual(
            list(self.event_tails[:6]),
            [nodes[3]] * 6,
        )
        self.assertEqual(self.list.tail, moving)
        self.assertEqual(
            self.observed_order(4),
            [nodes[1], nodes[2], nodes[3], nodes[0]],
        )

    def test_detached_node_can_become_head_and_tail_of_empty_list(
        self,
    ) -> None:
        self.reset(0)
        moving = self.node_at(0)
        self.set_links(moving, 0, 0)
        self.execute(moving, 0)
        self.assertEqual(
            self.events(),
            [
                (EVENT_GET_TAIL, 0, 0),
                (EVENT_REMOVE, moving, 0),
                (EVENT_SET_NEXT, 0, moving),
                (EVENT_SET_PREVIOUS, moving, 0),
                (EVENT_SET_PREVIOUS, 0, moving),
                (EVENT_SET_NEXT, moving, 0),
            ],
        )
        self.assertEqual(self.list.head, moving)
        self.assertEqual(self.list.tail, moving)
        self.assertEqual(self.previous_at(moving), 0)
        self.assertEqual(self.next_at(moving), 0)

    def test_null_node_short_circuits_only_safe_head_cases(self) -> None:
        self.reset(3)
        nodes = self.nodes(3)
        self.execute(0, 0)
        self.assertEqual(self.events(), [])
        self.assertEqual(self.observed_order(3), nodes)

        self.reset(3)
        self.execute(0, nodes[0])
        self.assertEqual(
            self.events(),
            [(EVENT_GET_PREVIOUS, nodes[0], 0)],
        )
        self.assertEqual(self.observed_order(3), nodes)

    def test_null_list_is_safe_only_when_nodes_compare_equal(self) -> None:
        self.reset(0)
        self.execute_null(0, 0)
        self.execute_null(0x12345678, 0x12345678)
        self.assertEqual(self.events(), [])

    def test_reviewed_arm_toolchain_emits_relocation_free_body(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            object_path = (
                Path(directory) / "runtime_linked_list_move_before.o"
            )
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

            sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
            import apollo_overlay

            data, sections = apollo_overlay.parse_elf32(object_path)
            text_section = apollo_overlay.section_named(sections, ".text")
            start = int(text_section["offset"])
            end = start + int(text_section["size"])
            text = data[start:end]

        self.assertEqual(len(text), 120)
        self.assertEqual(
            hashlib.sha256(text).hexdigest(),
            "a08ca9c0269fa3d9a76b6b60f6e17c1a"
            "a642932c080dfc5c776ac7ad39312b31",
        )
        self.assertNotIn(
            ".rel.text",
            {str(section["name"]) for section in sections},
        )

    def test_stock_span_caller_dependencies_and_boundaries_are_pinned(
        self,
    ) -> None:
        application = OFFICIAL.read_bytes()[32:]

        def span(start: int, end: int) -> bytes:
            return application[
                start - APPLICATION_BASE:end - APPLICATION_BASE
            ]

        preceding = span(0x00482CD8, STOCK_START)
        self.assertEqual(len(preceding), 74)
        self.assertEqual(
            hashlib.sha256(preceding).hexdigest(),
            "cc8f5ff84820370ff107fa077310efdff"
            "abbbc503682303638cb0519144f48ed",
        )
        stock = span(STOCK_START, STOCK_END)
        self.assertEqual(len(stock), 102)
        self.assertEqual(
            hashlib.sha256(stock).hexdigest(),
            "723328d50c75adb0ac95e2bc70b3e934"
            "b1152c1176774f8cc2207761865b094e",
        )
        following = span(STOCK_END, 0x00482DB0)
        self.assertEqual(len(following), 40)
        self.assertEqual(
            hashlib.sha256(following).hexdigest(),
            "76cfcfd2aa288f0f79074afecd87749c"
            "65a249ee842557f890005ec01e4384c7",
        )
        dependency_spans = {
            (0x00482C0E, 0x00482C9A):
                "f78c4e1dc9dedefcfde77a8e2911a89e"
                "b7d1436e8cac0736174cb5445e8a2131",
            (0x00482CE4, 0x00482CF0):
                "6717bf57b1ac7ad781c851f7c28681c1"
                "78495a01508c9d99488d5d36ada09443",
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

        self.assertEqual(callers, [(0x005C2F1C, "bff601ff")])
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(
            dependencies,
            [
                (0x00482D36, 0x00482CFA, "fff7e0ff"),
                (0x00482D40, 0x00482CE4, "fff7d0ff"),
                (0x00482D4E, 0x00482C0E, "fff75eff"),
                (0x00482D58, 0x00482DC2, "00f033f8"),
                (0x00482D62, 0x00482DAE, "00f024f8"),
                (0x00482D6C, 0x00482DAE, "00f01ff8"),
                (0x00482D76, 0x00482DC2, "00f024f8"),
            ],
        )
        caller_context = span(0x005C2F08, 0x005C2F30)
        self.assertEqual(
            hashlib.sha256(caller_context).hexdigest(),
            "fe6545a490d4b837d02b666de4a58dbe"
            "31696c57b63f1ef97eab484f50a52689",
        )

    def test_no_alternate_entry_and_stored_false_positives_are_pinned(
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
                stored.append((APPLICATION_BASE + offset, target, value))

        self.assertEqual(narrow_entry, [])
        self.assertEqual(narrow_interior, [])
        self.assertEqual(
            stored,
            [
                (0x0055E16F, 0x00482D60, 0x00482D61),
                (0x0055E175, 0x00482D60, 0x00482D61),
            ],
        )

    def test_source_and_fixture_are_bounded(self) -> None:
        source = SOURCE.read_text()
        for token in (
            "open_cfw_runtime_linked_list_move_before(",
            "if (moving == before)",
            "if (moving == previous)",
            "OPEN_CFW_RUNTIME_LINKED_LIST_MOVE_REMOVE(list, moving);",
            "OPEN_CFW_RUNTIME_LINKED_LIST_MOVE_SET_NEXT(list, previous, moving)",
            "OPEN_CFW_RUNTIME_LINKED_LIST_MOVE_SET_PREVIOUS(list, before, moving)",
            "OPEN_CFW_RUNTIME_LINKED_LIST_MOVE_SET_NEXT(list, moving, before)",
            "list->tail = moving;",
            "list->head = moving;",
            "0x00482C0FU",
            "0x00482DAFU",
            "0x00482DC3U",
        ):
            self.assertIn(token, source)
        self.assertNotIn("#include <", source)
        self.assertIn(
            "runtime_linked_list_move_before.c",
            FIXTURE.read_text(),
        )


if __name__ == "__main__":
    unittest.main()
