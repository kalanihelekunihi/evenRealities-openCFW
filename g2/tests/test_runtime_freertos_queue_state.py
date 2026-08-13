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


ROOT = Path(__file__).resolve().parent.parent
SOURCE = (
    ROOT
    / "components"
    / "apollo_main"
    / "core_overlay"
    / "runtime_freertos_queue_state.c"
)
FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_freertos_queue_state_host.c"
)
OFFICIAL = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
BASE = 0x00438000
FUNCTIONS = {
    "is_empty": (0x00441FF6, 0x00442012),
    "is_full": (0x00442012, 0x00442030),
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


class QueueList32(ctypes.Structure):
    _fields_ = [
        ("item_count", ctypes.c_uint32),
        ("remainder", ctypes.c_uint8 * 16),
    ]


class QueueValue32(ctypes.Union):
    _fields_ = [
        ("words", ctypes.c_uint32 * 2),
        ("bytes", ctypes.c_uint8 * 8),
    ]


class QueueControl32(ctypes.Structure):
    _fields_ = [
        ("head", ctypes.c_uint32),
        ("write_to", ctypes.c_uint32),
        ("value", QueueValue32),
        ("tasks_waiting_to_send", QueueList32),
        ("tasks_waiting_to_receive", QueueList32),
        ("messages_waiting", ctypes.c_uint32),
        ("length", ctypes.c_uint32),
        ("item_size", ctypes.c_uint32),
        ("receive_lock", ctypes.c_int8),
        ("transmit_lock", ctypes.c_int8),
        ("statically_allocated", ctypes.c_uint8),
        ("allocation_padding", ctypes.c_uint8),
        ("queue_number", ctypes.c_uint32),
        ("queue_type", ctypes.c_uint8),
        ("trace_padding", ctypes.c_uint8 * 3),
    ]


class RuntimeFreeRTOSQueueStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        library = temporary / (
            "runtime_freertos_queue_state.dylib"
            if sys.platform == "darwin"
            else "runtime_freertos_queue_state.so"
        )
        host_command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(FIXTURE),
        ]
        if sys.platform == "darwin":
            host_command.extend(["-dynamiclib", "-o", str(library)])
        else:
            host_command.extend(["-shared", "-fPIC", "-o", str(library)])
        subprocess.run(
            host_command,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.loaded = ctypes.CDLL(str(library))
        cls.reset = cls.loaded.open_cfw_test_queue_state_reset
        cls.reset.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.reset.restype = None
        cls.set_enter_mutation = (
            cls.loaded.open_cfw_test_queue_state_set_enter_mutation
        )
        cls.set_enter_mutation.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.set_enter_mutation.restype = None
        cls.queue_pointer = (
            cls.loaded.open_cfw_test_queue_state_pointer
        )
        cls.queue_pointer.argtypes = []
        cls.queue_pointer.restype = ctypes.c_void_p
        cls.is_empty = cls.loaded.open_cfw_freertos_queue_is_empty
        cls.is_empty.argtypes = [ctypes.c_void_p]
        cls.is_empty.restype = ctypes.c_int
        cls.is_full = cls.loaded.open_cfw_freertos_queue_is_full
        cls.is_full.argtypes = [ctypes.c_void_p]
        cls.is_full.restype = ctypes.c_int

        cls.target_object = (
            temporary / "runtime_freertos_queue_state.o"
        )
        subprocess.run(
            [
                os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                *TARGET_FLAGS,
                "-c",
                str(SOURCE),
                "-o",
                str(cls.target_object),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        data, sections = apollo_overlay.parse_elf32(cls.target_object)
        text = apollo_overlay.section_named(sections, ".text")
        cls.target_text = data[
            int(text["offset"]):int(text["offset"]) + int(text["size"])
        ]
        symbol_table = apollo_overlay.section_named(
            sections,
            ".symtab",
        )
        string_table = sections[int(symbol_table["link"])]
        strings = data[
            int(string_table["offset"]):
            int(string_table["offset"]) + int(string_table["size"])
        ]
        cls.parsed_symbols = []
        for index in range(int(symbol_table["size"]) // 16):
            fields = struct.unpack_from(
                "<IIIBBH",
                data,
                int(symbol_table["offset"]) + index * 16,
            )
            name = apollo_overlay.elf_string(
                strings,
                fields[0],
                "symbol",
            )
            cls.parsed_symbols.append((name, fields))
        cls.symbols = {
            name: fields
            for name, fields in cls.parsed_symbols
            if name
        }
        cls.text_relocations = []
        for section in sections:
            if (
                int(section["type"]) == 9
                and int(section["info"]) == int(text["index"])
            ):
                for index in range(int(section["size"]) // 8):
                    offset, information = struct.unpack_from(
                        "<II",
                        data,
                        int(section["offset"]) + index * 8,
                    )
                    cls.text_relocations.append(
                        (
                            offset,
                            information & 0xFF,
                            cls.parsed_symbols[information >> 8][0],
                        )
                    )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def uint(self, name: str) -> int:
        return ctypes.c_uint32.in_dll(self.loaded, name).value

    def events(self) -> list[int]:
        count = self.uint("open_cfw_test_queue_state_event_count")
        events = (
            ctypes.c_uint32 * 8
        ).in_dll(self.loaded, "open_cfw_test_queue_state_events")
        self.assertLessEqual(count, 8)
        return list(events[:count])

    def span(self, start: int, end: int) -> bytes:
        return self.application[start - BASE:end - BASE]

    def test_target_queue_layout_and_symbols_are_exact(self) -> None:
        self.assertEqual(ctypes.sizeof(QueueList32), 20)
        self.assertEqual(ctypes.sizeof(QueueControl32), 0x50)
        self.assertEqual(QueueControl32.messages_waiting.offset, 0x38)
        self.assertEqual(QueueControl32.length.offset, 0x3C)

        functions = {
            "open_cfw_freertos_queue_is_empty": (0, 32),
            "open_cfw_freertos_queue_is_full": (32, 36),
        }
        self.assertEqual(
            {
                name: (self.symbols[name][1] & ~1, self.symbols[name][2])
                for name in functions
            },
            functions,
        )
        self.assertTrue(
            all(self.symbols[name][1] & 1 for name in functions)
        )
        self.assertEqual(len(self.target_text), 68)
        self.assertEqual(
            hashlib.sha256(self.target_text[:32]).hexdigest(),
            "51295be6a4a041e3530afbe3c44831c1"
            "1c12e157f5ec4d4244c85a9deded5113",
        )
        self.assertEqual(
            hashlib.sha256(self.target_text[32:]).hexdigest(),
            "89c57d336eb639671485028be4784739d"
            "ef9d22b96c03a68d3d8cb1711df4a60",
        )
        self.assertEqual(
            sorted(
                name
                for name, fields in self.symbols.items()
                if fields[5] == 0
            ),
            [],
        )

    def test_target_compiles_with_only_fixed_critical_seams(
        self,
    ) -> None:
        self.assertEqual(self.text_relocations, [])
        self.assertGreater(len(self.target_text), 0)
        source = SOURCE.read_text()
        for token in (
            "FreeRTOS Kernel V10.5.1",
            "SPDX-License-Identifier: MIT",
            "def7d2df2b0506d3d249334974f51e427c17a41c",
            "prvIsQueueEmpty()",
            "prvIsQueueFull()",
            "0x00441FF6",
            "0x00442012",
            "0x004420D1U",
            "0x004420E9U",
            "sizeof(struct open_cfw_queue_state_control) == 0x50U",
            "messages_waiting",
            "length",
        ):
            self.assertIn(token, source)
        self.assertNotIn("#include <", source)
        self.assertIn(
            "runtime_freertos_queue_state.c",
            FIXTURE.read_text(),
        )

    def test_empty_helper_matches_upstream_and_critical_order(self) -> None:
        for messages, expected in (
            (0, 1),
            (1, 0),
            (0xFFFFFFFF, 0),
        ):
            with self.subTest(messages=messages):
                self.reset(messages, 4)
                self.assertEqual(
                    self.is_empty(self.queue_pointer()),
                    expected,
                )
                self.assertEqual(self.events(), [1, 2])
                self.assertEqual(
                    self.uint(
                        "open_cfw_test_queue_state_critical_depth"
                    ),
                    0,
                )
                self.assertEqual(
                    self.uint(
                        "open_cfw_test_queue_state_max_critical_depth"
                    ),
                    1,
                )

    def test_full_helper_uses_equality_not_greater_than(self) -> None:
        for messages, length, expected in (
            (0, 4, 0),
            (3, 4, 0),
            (4, 4, 1),
            (5, 4, 0),
            (0xFFFFFFFF, 0xFFFFFFFF, 1),
        ):
            with self.subTest(messages=messages, length=length):
                self.reset(messages, length)
                self.assertEqual(
                    self.is_full(self.queue_pointer()),
                    expected,
                )
                self.assertEqual(self.events(), [1, 2])

    def test_state_is_sampled_after_entering_critical_section(self) -> None:
        self.reset(1, 4)
        self.set_enter_mutation(1, 0)
        self.assertEqual(self.is_empty(self.queue_pointer()), 1)
        self.assertEqual(self.events(), [1, 2])

        self.reset(0, 4)
        self.set_enter_mutation(1, 4)
        self.assertEqual(self.is_full(self.queue_pointer()), 1)
        self.assertEqual(self.events(), [1, 2])

    def test_stock_spans_hashes_callers_and_dependencies_are_exact(
        self,
    ) -> None:
        expected = {
            "is_empty": (
                28,
                "fb24b5bf27e2d16d89d87554fc4c93fd"
                "c8b94cd42bd72613b9e28336ef23932e",
                [
                    (0x00441BD4, "00f00ffa"),
                    (0x00441C38, "00f0ddf9"),
                    (0x00441D00, "00f079f9"),
                    (0x00441D7E, "00f03af9"),
                ],
            ),
            "is_full": (
                30,
                "bd4e5d3f3b08830ccc68d8f7e8f7b4fe"
                "930d111a7785ba40784ac2bfb0c73faf",
                [(0x004418CA, "00f0a2fb")],
            ),
        }
        for name, (start, end) in FUNCTIONS.items():
            stock = self.span(start, end)
            with self.subTest(name=name):
                self.assertEqual(len(stock), expected[name][0])
                self.assertEqual(
                    hashlib.sha256(stock).hexdigest(),
                    expected[name][1],
                )

        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        callers = {name: [] for name in FUNCTIONS}
        jumps = {name: [] for name in FUNCTIONS}
        interiors = {name: [] for name in FUNCTIONS}
        dependencies = {name: set() for name in FUNCTIONS}
        for offset in range(0, len(self.application) - 3, 2):
            address = BASE + offset
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
                        interiors[name].append(
                            (address, target, link, encoded.hex())
                        )
                    if start <= address < end and link:
                        dependencies[name].add(target)

        self.assertEqual(
            callers,
            {
                name: fields[2]
                for name, fields in expected.items()
            },
        )
        self.assertEqual(jumps, {name: [] for name in FUNCTIONS})
        self.assertEqual(interiors, {name: [] for name in FUNCTIONS})
        self.assertEqual(
            dependencies,
            {
                "is_empty": {0x004420D0, 0x004420E8},
                "is_full": {0x004420D0, 0x004420E8},
            },
        )

    def test_stock_field_loads_prove_recovered_configuration(self) -> None:
        empty = self.span(*FUNCTIONS["is_empty"])
        full = self.span(*FUNCTIONS["is_full"])
        self.assertEqual(
            empty.hex(),
            "10b5040000f069f8a06b002801d1012400e00024"
            "00f06df8200010bd",
        )
        self.assertEqual(
            full.hex(),
            "10b5040000f05bf8a06be16b884201d1012400e0"
            "002400f05ef8200010bd",
        )
        self.assertEqual(empty[8:10], bytes.fromhex("a06b"))
        self.assertEqual(full[8:12], bytes.fromhex("a06be16b"))


if __name__ == "__main__":
    unittest.main()
