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
SOURCE = COMPONENT_ROOT / "runtime_linked_list_clear_custom.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "runtime_linked_list_clear_custom_host.c"
)
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
FUNCTION_START = 0x00482C9A
FUNCTION_END = 0x00482CD8
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

EVENT_HEAD = 1
EVENT_NEXT = 2
EVENT_CALLBACK = 3
EVENT_REMOVE = 4
EVENT_FREE = 5


def _sign_extend(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return value - (1 << bits) if value & sign else value


class RuntimeLinkedList(ctypes.Structure):
    _fields_ = [
        ("node_size", ctypes.c_uint32),
        ("head", ctypes.c_uint32),
        ("tail", ctypes.c_uint32),
    ]


class RuntimeLinkedListClearCustomTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        library = temporary / (
            "runtime_linked_list_clear_custom.dylib"
            if sys.platform == "darwin"
            else "runtime_linked_list_clear_custom.so"
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
        cls.clear_custom = (
            cls.loaded.open_cfw_runtime_linked_list_clear_custom
        )
        cls.reset = cls.loaded.open_cfw_test_clear_custom_reset
        cls.clear_custom.argtypes = [
            ctypes.POINTER(RuntimeLinkedList),
            ctypes.c_uint32,
        ]
        cls.clear_custom.restype = None
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.storage = (ctypes.c_ubyte * 1024).in_dll(
            cls.loaded,
            "open_cfw_test_clear_custom_storage",
        )
        cls.event_codes = (ctypes.c_uint32 * 64).in_dll(
            cls.loaded,
            "open_cfw_test_clear_custom_event_codes",
        )
        cls.event_nodes = (ctypes.c_uint32 * 64).in_dll(
            cls.loaded,
            "open_cfw_test_clear_custom_event_nodes",
        )
        cls.event_count = ctypes.c_uint32.in_dll(
            cls.loaded,
            "open_cfw_test_clear_custom_event_count",
        )
        cls.callback_handle = ctypes.c_uint32.in_dll(
            cls.loaded,
            "open_cfw_test_clear_custom_callback_handle",
        )
        cls.callback_mutates_next = ctypes.c_uint32.in_dll(
            cls.loaded,
            "open_cfw_test_clear_custom_callback_mutates_next",
        )

        target_object = temporary / "clear_custom.o"
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

        combined_source = temporary / "linked_list_combined.c"
        combined_source.write_text(
            "\n".join(
                f'#include "{path.as_posix()}"'
                for path in (
                    COMPONENT_ROOT / "runtime_linked_list_init.c",
                    COMPONENT_ROOT / "runtime_linked_list_accessors.c",
                    COMPONENT_ROOT
                    / "runtime_linked_list_pointer_setters.c",
                    SOURCE,
                )
            )
            + "\n"
        )
        combined_object = temporary / "linked_list_combined.o"
        subprocess.run(
            [
                os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                *TARGET_FLAGS,
                "-c",
                str(combined_source),
                "-o",
                str(combined_object),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        (
            cls.combined_text,
            cls.combined_functions,
            cls.combined_report,
        ) = extract_linked_overlay(combined_object)

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

    def store_pointer(self, offset: int, value: int) -> None:
        struct.pack_into("<I", self.storage, offset, value)

    def trace(self) -> list[tuple[int, int]]:
        return [
            (self.event_codes[index], self.event_nodes[index])
            for index in range(self.event_count.value)
        ]

    def test_null_and_empty_lists_only_query_the_head(self) -> None:
        for cleanup in (0, 0x00481001):
            self.clear_custom(None, cleanup)
            self.assertEqual(self.trace(), [(EVENT_HEAD, 0)])
            self.reset()

        linked_list = RuntimeLinkedList(16, 0, 0)
        for cleanup in (0, 0x00481001):
            self.clear_custom(ctypes.byref(linked_list), cleanup)
            self.assertEqual(self.trace(), [(EVENT_HEAD, 0)])
            self.reset()

    def test_callback_path_captures_next_before_callback(self) -> None:
        nodes = [64, 192]
        linked_list = RuntimeLinkedList(12, nodes[0], nodes[-1])
        self.store_pointer(nodes[0] + linked_list.node_size + 4, nodes[1])
        self.store_pointer(nodes[1] + linked_list.node_size + 4, 0)
        self.callback_mutates_next.value = 1

        self.clear_custom(ctypes.byref(linked_list), 0x00481001)

        self.assertEqual(
            self.trace(),
            [
                (EVENT_HEAD, 0),
                (EVENT_NEXT, nodes[0]),
                (EVENT_CALLBACK, nodes[0]),
                (EVENT_NEXT, nodes[1]),
                (EVENT_CALLBACK, nodes[1]),
            ],
        )
        self.assertEqual(self.callback_handle.value, 0x00481001)
        self.assertEqual(
            struct.unpack_from(
                "<I",
                self.storage,
                nodes[0] + linked_list.node_size + 4,
            )[0],
            0,
        )
        self.assertEqual(
            (linked_list.node_size, linked_list.head, linked_list.tail),
            (12, nodes[0], nodes[-1]),
        )

    def test_null_callback_removes_then_frees_each_current_node(self) -> None:
        nodes = [80, 176, 272]
        linked_list = RuntimeLinkedList(8, nodes[0], nodes[-1])
        for index, node in enumerate(nodes):
            next_node = nodes[index + 1] if index + 1 < len(nodes) else 0
            self.store_pointer(node + linked_list.node_size + 4, next_node)

        self.clear_custom(ctypes.byref(linked_list), 0)

        self.assertEqual(
            self.trace(),
            [(EVENT_HEAD, 0)]
            + [
                event
                for node in nodes
                for event in (
                    (EVENT_NEXT, node),
                    (EVENT_REMOVE, node),
                    (EVENT_FREE, node),
                )
            ],
        )
        self.assertEqual(self.callback_handle.value, 0)

    def test_stock_body_and_adjacent_routine_hashes_are_exact(self) -> None:
        body = self.span(FUNCTION_START, FUNCTION_END)
        self.assertEqual(len(body), 62)
        self.assertEqual(
            body.hex(),
            "f8b505000e00280000f019f80400002012e02000b0470ee02100"
            "280000f01bf8070030000028f4d121002800fff7a2ff2000ccf7"
            "44fd3c00002cedd1f1bd",
        )
        self.assertEqual(
            hashlib.sha256(body).hexdigest(),
            "5587afeb5f0ce7bc1573dea6617ea0bc"
            "511688d6c95db261478eee5f68e7af04",
        )

        adjacent = {
            (0x00482C0E, FUNCTION_START):
                "f78c4e1dc9dedefcfde77a8e2911a89"
                "eb7d1436e8cac0736174cb5445e8a2131",
            (FUNCTION_END, 0x00482D22):
                "cc8f5ff84820370ff107fa077310efdf"
                "fabbbc503682303638cb0519144f48ed",
            (FUNCTION_END, 0x00482CE4):
                "52da3be9e77a64ae55928264f6f8b955"
                "294a7603e3dbcfaefab3b4150b2b52b3",
            (0x00482DA4, 0x00482DAE):
                "0528fed662ee528664a6631b0b85ff07"
                "979195a55d4543a0e175074974c6801d",
        }
        for (start, end), digest in adjacent.items():
            with self.subTest(start=hex(start), end=hex(end)):
                self.assertEqual(
                    hashlib.sha256(self.span(start, end)).hexdigest(),
                    digest,
                )

    def test_wide_callers_dependencies_and_indirect_callback_are_exact(
        self,
    ) -> None:
        from apollo_overlay import BuildError, decode_thumb_branch

        callers = []
        jumps = []
        interior = []
        dependencies = []
        for offset in range(0, len(self.application) - 3, 2):
            address = APPLICATION_BASE + offset
            encoded = self.application[offset:offset + 4]
            for link in (True, False):
                try:
                    target = decode_thumb_branch(
                        address,
                        encoded,
                        link=link,
                    )
                except BuildError:
                    continue
                if target == FUNCTION_START:
                    (callers if link else jumps).append(address)
                if (
                    FUNCTION_START < target < FUNCTION_END
                    and not FUNCTION_START <= address < FUNCTION_END
                ):
                    interior.append((address, target, link))
                if link and FUNCTION_START <= address < FUNCTION_END:
                    dependencies.append((address, target, encoded.hex()))

        self.assertEqual(callers, [0x00482DA8])
        self.assertEqual(
            hashlib.sha256(
                b"".join(struct.pack("<I", address) for address in callers)
            ).hexdigest(),
            "a904ff515cdf46240e654f2f944dc562"
            "6b2b112bfe6c4736de610e27caaf97e5",
        )
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(
            dependencies,
            [
                (0x00482CA2, 0x00482CD8, "00f019f8"),
                (0x00482CB6, 0x00482CF0, "00f01bf8"),
                (0x00482CC6, 0x00482C0E, "fff7a2ff"),
                (0x00482CCC, 0x0044F758, "ccf744fd"),
            ],
        )
        self.assertEqual(self.span(0x00482CAE, 0x00482CB0), b"\xb0G")
        self.assertEqual(self.span(0x00482DA8, 0x00482DAC), b"\xff\xf7w\xff")

    def test_narrow_and_stored_pointer_topology_is_exact(self) -> None:
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
            if FUNCTION_START in candidates:
                narrow_entry.append((address, halfword))
            for target in candidates:
                if (
                    FUNCTION_START < target < FUNCTION_END
                    and not FUNCTION_START <= address < FUNCTION_END
                ):
                    narrow_interior.append((address, target, halfword))

        stored = []
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            if value & 1:
                target = value & ~1
                if FUNCTION_START <= target < FUNCTION_END:
                    stored.append((APPLICATION_BASE + offset, target))

        self.assertEqual(narrow_entry, [])
        self.assertEqual(narrow_interior, [])
        self.assertEqual(stored, [(0x004733B5, 0x00482CD0)])
        context = self.span(0x004733B0, 0x004733BC)
        self.assertEqual(context.hex(), "10f1020f01d12c4800e02c48")
        self.assertEqual(
            hashlib.sha256(context).hexdigest(),
            "2ff7af7da5d80317d391ed72e67a455"
            "459fa7b6bcb0aaf4b6d11be0ee926d8aa",
        )

    def test_void_abi_does_not_preserve_stock_incidental_r0(self) -> None:
        body = self.span(FUNCTION_START, FUNCTION_END)
        self.assertEqual(body[:2], b"\xf8\xb5")
        self.assertEqual(body[-2:], b"\xf1\xbd")
        source = SOURCE.read_text()
        self.assertIn(
            "void open_cfw_runtime_linked_list_clear_custom(",
            source,
        )
        self.assertNotIn(
            "return current",
            source,
        )

    def test_reviewed_target_clang_output_is_exact(self) -> None:
        self.assertEqual(
            self.target_functions,
            {
                "open_cfw_runtime_linked_list_clear_custom": {
                    "offset": 0,
                    "size": 84,
                },
            },
        )
        self.assertEqual(self.target_report["text_size"], 84)
        self.assertEqual(self.target_report["rodata_size"], 0)
        self.assertEqual(self.target_report["rodata_sections"], [])
        self.assertEqual(
            self.target_report["resolved_relocation_count"],
            0,
        )
        self.assertEqual(self.target_report["resolved_relocations"], [])
        self.assertEqual(
            hashlib.sha256(self.target_text).hexdigest(),
            "55e0889be483163981da25a515842db35"
            "eb92ed8adca00f89fc534c88de1bbcc",
        )

    def test_combined_linked_list_translation_unit_is_compatible(
        self,
    ) -> None:
        expected_symbols = {
            "open_cfw_runtime_linked_list_init",
            "open_cfw_runtime_linked_list_get_head",
            "open_cfw_runtime_linked_list_get_tail",
            "open_cfw_runtime_linked_list_get_next",
            "open_cfw_runtime_linked_list_get_previous",
            "open_cfw_runtime_linked_list_get_length",
            "open_cfw_runtime_linked_list_is_empty",
            "open_cfw_runtime_linked_list_clear",
            "open_cfw_runtime_linked_list_set_previous",
            "open_cfw_runtime_linked_list_set_next",
            "open_cfw_runtime_linked_list_clear_custom",
        }
        self.assertEqual(set(self.combined_functions), expected_symbols)
        self.assertEqual(self.combined_report["rodata_size"], 0)
        clear_info = self.combined_functions[
            "open_cfw_runtime_linked_list_clear_custom"
        ]
        clear_body = self.combined_text[
            clear_info["offset"]:clear_info["offset"] + clear_info["size"]
        ]
        self.assertEqual(clear_info["size"], 84)
        self.assertEqual(
            hashlib.sha256(clear_body).hexdigest(),
            "55e0889be483163981da25a515842db35"
            "eb92ed8adca00f89fc534c88de1bbcc",
        )

    def test_source_and_fixture_are_bounded(self) -> None:
        source = SOURCE.read_text()
        for token in (
            "open_cfw_runtime_linked_list_clear_custom(",
            "0x00482CD9U",
            "0x00482CF1U",
            "0x00482C0FU",
            "0x0044F759U",
        ):
            self.assertIn(token, source)
        self.assertNotIn("#include <", source)
        self.assertIn(
            "runtime_linked_list_clear_custom.c",
            FIXTURE.read_text(),
        )


if __name__ == "__main__":
    unittest.main()
