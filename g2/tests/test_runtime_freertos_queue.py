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
    / "runtime_freertos_queue.c"
)
FIXTURE = ROOT / "tests" / "fixtures" / "runtime_freertos_queue_host.c"
OFFICIAL = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
BASE = 0x00438000
FUNCTIONS = {
    "create_mutex": (0x004416D6, 0x004416F0),
    "give_mutex_recursive": (0x00441710, 0x00441750),
    "take_mutex_recursive": (0x00441750, 0x00441790),
    "generic_send": (0x004417EE, 0x00441952),
    "semaphore_take": (0x00441C44, 0x00441DA6),
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

EVENT_GENERIC_CREATE = 1
EVENT_INITIALISE_MUTEX = 2
EVENT_ENTER_CRITICAL = 3
EVENT_EXIT_CRITICAL = 4
EVENT_COPY_DATA = 5
EVENT_REMOVE_EVENT = 6
EVENT_YIELD = 7
EVENT_SET_TIMEOUT = 8
EVENT_SUSPEND_ALL = 9
EVENT_CHECK_TIMEOUT = 10
EVENT_PLACE_ON_EVENT = 11
EVENT_UNLOCK = 12
EVENT_RESUME_ALL = 13
EVENT_INCREMENT_MUTEX_HELD = 14
EVENT_PRIORITY_INHERIT = 15
EVENT_DISINHERIT_PRIORITY = 16
EVENT_DISINHERIT_AFTER_TIMEOUT = 17
EVENT_ASSERT = 18
EVENT_CURRENT_TASK = 19


_APPLE_ONLY = unittest.skipUnless(
    (os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") or "apple-clang") == "apple-clang",
    "byte-exact / toolchain-specific Apple-clang assertion; Linux byte "
    "reproduction is verified end-to-end by tests/test_toolchain_profiles.py",
)


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


class RuntimeFreeRTOSQueueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        library = temporary / (
            "runtime_freertos_queue.dylib"
            if sys.platform == "darwin"
            else "runtime_freertos_queue.so"
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
        cls.reset = cls.loaded.open_cfw_test_queue_reset
        cls.reset.argtypes = [ctypes.c_uint32] * 4
        cls.reset.restype = None
        cls.queue_pointer = cls.loaded.open_cfw_test_queue_pointer
        cls.queue_pointer.argtypes = []
        cls.queue_pointer.restype = ctypes.c_void_p
        cls.set_waiters = cls.loaded.open_cfw_test_queue_set_waiters
        cls.set_waiters.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.set_waiters.restype = None
        cls.set_mutex_state = (
            cls.loaded.open_cfw_test_queue_set_mutex_state
        )
        cls.set_mutex_state.argtypes = [ctypes.c_ulong, ctypes.c_uint32]
        cls.set_mutex_state.restype = None
        cls.messages_waiting = (
            cls.loaded.open_cfw_test_queue_messages_waiting
        )
        cls.messages_waiting.argtypes = []
        cls.messages_waiting.restype = ctypes.c_uint32
        cls.send_waiters = cls.loaded.open_cfw_test_queue_send_waiters
        cls.send_waiters.argtypes = []
        cls.send_waiters.restype = ctypes.c_uint32
        cls.receive_waiters = (
            cls.loaded.open_cfw_test_queue_receive_waiters
        )
        cls.receive_waiters.argtypes = []
        cls.receive_waiters.restype = ctypes.c_uint32
        cls.mutex_holder = cls.loaded.open_cfw_test_queue_mutex_holder
        cls.mutex_holder.argtypes = []
        cls.mutex_holder.restype = ctypes.c_ulong
        cls.recursive_count = (
            cls.loaded.open_cfw_test_queue_recursive_count
        )
        cls.recursive_count.argtypes = []
        cls.recursive_count.restype = ctypes.c_uint32
        cls.queue_type = cls.loaded.open_cfw_test_queue_type
        cls.queue_type.argtypes = []
        cls.queue_type.restype = ctypes.c_uint32
        cls.write_offset = cls.loaded.open_cfw_test_queue_write_offset
        cls.write_offset.argtypes = []
        cls.write_offset.restype = ctypes.c_int
        cls.read_offset = cls.loaded.open_cfw_test_queue_read_offset
        cls.read_offset.argtypes = []
        cls.read_offset.restype = ctypes.c_int
        cls.storage_byte = cls.loaded.open_cfw_test_queue_storage_byte
        cls.storage_byte.argtypes = [ctypes.c_uint32]
        cls.storage_byte.restype = ctypes.c_ubyte

        cls.create_mutex = (
            cls.loaded.open_cfw_freertos_queue_create_mutex
        )
        cls.create_mutex.argtypes = [ctypes.c_ubyte]
        cls.create_mutex.restype = ctypes.c_void_p
        cls.generic_send = (
            cls.loaded.open_cfw_freertos_queue_generic_send
        )
        cls.generic_send.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_int,
        ]
        cls.generic_send.restype = ctypes.c_int
        cls.semaphore_take = (
            cls.loaded.open_cfw_freertos_queue_semaphore_take
        )
        cls.semaphore_take.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        cls.semaphore_take.restype = ctypes.c_int
        cls.give_mutex_recursive = (
            cls.loaded.open_cfw_freertos_queue_give_mutex_recursive
        )
        cls.give_mutex_recursive.argtypes = [ctypes.c_void_p]
        cls.give_mutex_recursive.restype = ctypes.c_int
        cls.take_mutex_recursive = (
            cls.loaded.open_cfw_freertos_queue_take_mutex_recursive
        )
        cls.take_mutex_recursive.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
        ]
        cls.take_mutex_recursive.restype = ctypes.c_int
        cls.send_asserting = (
            cls.loaded.open_cfw_test_queue_send_asserting
        )
        cls.send_asserting.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_int,
        ]
        cls.send_asserting.restype = ctypes.c_int
        cls.take_asserting = (
            cls.loaded.open_cfw_test_queue_take_asserting
        )
        cls.take_asserting.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        cls.take_asserting.restype = ctypes.c_int
        cls.give_recursive_asserting = (
            cls.loaded.open_cfw_test_queue_give_recursive_asserting
        )
        cls.give_recursive_asserting.argtypes = [ctypes.c_void_p]
        cls.give_recursive_asserting.restype = ctypes.c_int
        cls.take_recursive_asserting = (
            cls.loaded.open_cfw_test_queue_take_recursive_asserting
        )
        cls.take_recursive_asserting.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
        ]
        cls.take_recursive_asserting.restype = ctypes.c_int

        cls.target_object = temporary / "runtime_freertos_queue.o"
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

        sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        data, sections = apollo_overlay.parse_elf32(cls.target_object)
        text = apollo_overlay.section_named(sections, ".text")
        cls.target_text = data[
            int(text["offset"]):int(text["offset"]) + int(text["size"])
        ]
        symbol_table = apollo_overlay.section_named(sections, ".symtab")
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

    def set_uint(self, name: str, value: int) -> None:
        ctypes.c_uint32.in_dll(self.loaded, name).value = value

    def ulong(self, name: str) -> int:
        return ctypes.c_ulong.in_dll(self.loaded, name).value

    def set_ulong(self, name: str, value: int) -> None:
        ctypes.c_ulong.in_dll(self.loaded, name).value = value

    def events(self) -> list[tuple[int, int, int]]:
        count = self.uint("open_cfw_test_queue_event_count")
        events = (
            ctypes.c_uint32 * 128
        ).in_dll(self.loaded, "open_cfw_test_queue_events")
        arguments0 = (
            ctypes.c_uint32 * 128
        ).in_dll(self.loaded, "open_cfw_test_queue_arguments0")
        arguments1 = (
            ctypes.c_uint32 * 128
        ).in_dll(self.loaded, "open_cfw_test_queue_arguments1")
        self.assertLessEqual(count, 128)
        return [
            (events[index], arguments0[index], arguments1[index])
            for index in range(count)
        ]

    def span(self, start: int, end: int) -> bytes:
        return self.application[start - BASE:end - BASE]

    @_APPLE_ONLY
    def test_target_queue_layout_and_public_symbols_are_exact(self) -> None:
        self.assertEqual(ctypes.sizeof(QueueList32), 20)
        self.assertEqual(ctypes.sizeof(QueueControl32), 0x50)
        expected_offsets = {
            "head": 0x00,
            "write_to": 0x04,
            "value": 0x08,
            "tasks_waiting_to_send": 0x10,
            "tasks_waiting_to_receive": 0x24,
            "messages_waiting": 0x38,
            "length": 0x3C,
            "item_size": 0x40,
            "receive_lock": 0x44,
            "transmit_lock": 0x45,
            "statically_allocated": 0x46,
            "queue_number": 0x48,
            "queue_type": 0x4C,
        }
        self.assertEqual(
            {
                name: getattr(QueueControl32, name).offset
                for name in expected_offsets
            },
            expected_offsets,
        )

        public = {
            "open_cfw_freertos_queue_create_mutex": (0, 30),
            "open_cfw_freertos_queue_generic_send": (32, 556),
            "open_cfw_freertos_queue_give_mutex_recursive": (588, 74),
            "open_cfw_freertos_queue_take_mutex_recursive": (664, 76),
        }
        self.assertEqual(
            {
                name: (self.symbols[name][1] & ~1, self.symbols[name][2])
                for name in public
            },
            public,
        )
        self.assertTrue(
            all(self.symbols[name][1] & 1 for name in public)
        )
        self.assertNotIn(
            "open_cfw_freertos_queue_semaphore_take", self.symbols
        )
        self.assertEqual(len(self.target_text), 740)
        self.assertEqual(
            self.text_relocations,
            [
                (312, 10, "open_cfw_freertos_queue_is_full"),
                (532, 10, "open_cfw_freertos_queue_is_full"),
                (
                    654,
                    10,
                    "open_cfw_freertos_queue_generic_send",
                ),
            ],
        )
        self.assertEqual(
            sorted(
                name
                for name, fields in self.symbols.items()
                if fields[5] == 0
            ),
            [
                "open_cfw_freertos_queue_is_full",
            ],
        )

    def test_fixed_stock_seams_and_source_scope_are_explicit(self) -> None:
        source = SOURCE.read_text()
        for address in (
            "0x005FA0A5U",
            "0x00441637U",
            "0x004416B9U",
            "0x004558A5U",
            "0x0045589DU",
            "0x004420D1U",
            "0x004420E9U",
            "0x00441ED9U",
            "0x00455371U",
            "0x004420BDU",
            "0x00455557U",
            "0x00454D7DU",
            "0x00455567U",
            "0x00455283U",
            "0x00441F89U",
            "0x00454DCDU",
            "0x00455AE1U",
            "0x004558CDU",
            "0x00441EC5U",
            "0x00455A1DU",
        ):
            self.assertIn(address, source)
        for token in (
            "FreeRTOS Kernel V10.5.1",
            "SPDX-License-Identifier: MIT",
            "def7d2df2b0506d3d249334974f51e427c17a41c",
            "struct open_cfw_queue_control",
            "sizeof(struct open_cfw_queue_control) == 0x50U",
            "open_cfw_freertos_queue_create_mutex(",
            "open_cfw_freertos_queue_give_mutex_recursive(",
            "open_cfw_freertos_queue_take_mutex_recursive(",
            "open_cfw_freertos_queue_generic_send(",
            "open_cfw_freertos_queue_semaphore_take(",
            "open_cfw_freertos_queue_is_empty(",
            "open_cfw_freertos_queue_is_full(",
            "OPEN_CFW_FREERTOS_QUEUE_ASSERT(queue != 0)",
            "0xFFFFFFFFU",
        ):
            self.assertIn(token, source)
        self.assertNotIn("0x00441FF7U", source)
        self.assertNotIn("0x00442013U", source)
        self.assertNotIn("#include <", source)
        self.assertIn("runtime_freertos_queue.c", FIXTURE.read_text())

    def test_create_mutex_success_and_failure_match_upstream(self) -> None:
        self.reset(1, 0, 0, 0)
        queue = self.queue_pointer()
        self.assertEqual(self.create_mutex(4), queue)
        self.assertEqual(self.queue_type(), 4)
        self.assertEqual(self.messages_waiting(), 1)
        self.assertEqual(self.mutex_holder(), 0)
        self.assertEqual(self.recursive_count(), 0)
        self.assertEqual(
            [event for event, _arg0, _arg1 in self.events()],
            [
                EVENT_GENERIC_CREATE,
                EVENT_INITIALISE_MUTEX,
                EVENT_ENTER_CRITICAL,
                EVENT_COPY_DATA,
                EVENT_EXIT_CRITICAL,
            ],
        )
        self.assertEqual(self.events()[0], (EVENT_GENERIC_CREATE, 1, 0))
        self.assertEqual(self.events()[1], (EVENT_INITIALISE_MUTEX, 1, 0))
        self.assertEqual(self.events()[3], (EVENT_COPY_DATA, 0, 0))

        self.reset(1, 0, 0, 0)
        self.set_uint("open_cfw_test_queue_generic_create_success", 0)
        self.assertIsNone(self.create_mutex(1))
        self.assertEqual(
            self.events(),
            [
                (EVENT_GENERIC_CREATE, 1, 0),
                (EVENT_INITIALISE_MUTEX, 0, 0),
            ],
        )

    def test_generic_send_back_front_and_overwrite_copy_exactly(
        self,
    ) -> None:
        item = (ctypes.c_ubyte * 2)(0xA5, 0x5A)

        self.reset(3, 2, 0, 0)
        self.assertEqual(
            self.generic_send(self.queue_pointer(), item, 0, 0),
            1,
        )
        self.assertEqual(self.messages_waiting(), 1)
        self.assertEqual(self.write_offset(), 2)
        self.assertEqual(
            [self.storage_byte(index) for index in range(2)],
            [0xA5, 0x5A],
        )
        self.assertIn((EVENT_COPY_DATA, 0, 2), self.events())

        self.reset(3, 2, 0, 0)
        self.assertEqual(
            self.generic_send(self.queue_pointer(), item, 0, 1),
            1,
        )
        self.assertEqual(self.messages_waiting(), 1)
        self.assertEqual(self.read_offset(), 2)
        self.assertEqual(
            [self.storage_byte(index) for index in range(4, 6)],
            [0xA5, 0x5A],
        )
        self.assertIn((EVENT_COPY_DATA, 1, 2), self.events())

        self.reset(1, 2, 1, 0)
        self.assertEqual(
            self.generic_send(self.queue_pointer(), item, 0, 2),
            1,
        )
        self.assertEqual(self.messages_waiting(), 1)
        self.assertEqual(self.read_offset(), 0)
        self.assertEqual(
            [self.storage_byte(index) for index in range(2)],
            [0xA5, 0x5A],
        )
        self.assertIn((EVENT_COPY_DATA, 2, 2), self.events())

    def test_semaphore_and_mutex_send_have_zero_item_semantics(self) -> None:
        self.reset(3, 0, 0, 0)
        self.assertEqual(
            self.generic_send(self.queue_pointer(), None, 0, 0),
            1,
        )
        self.assertEqual(self.messages_waiting(), 1)
        self.assertIn((EVENT_COPY_DATA, 0, 0), self.events())

        self.reset(1, 0, 0, 1)
        self.assertEqual(self.mutex_holder(), 0x87654321)
        self.assertEqual(
            self.generic_send(self.queue_pointer(), None, 0, 0),
            1,
        )
        self.assertEqual(self.messages_waiting(), 1)
        self.assertEqual(self.mutex_holder(), 0)

    def test_send_full_no_wait_returns_without_copying(self) -> None:
        item = ctypes.c_uint32(0xA5A55A5A)
        self.reset(2, 4, 2, 0)
        self.assertEqual(
            self.generic_send(
                self.queue_pointer(),
                ctypes.byref(item),
                0,
                0,
            ),
            0,
        )
        self.assertEqual(self.messages_waiting(), 2)
        self.assertEqual(
            self.events(),
            [
                (EVENT_ENTER_CRITICAL, 0, 0),
                (EVENT_EXIT_CRITICAL, 0, 0),
            ],
        )

    def test_send_timeout_and_retry_paths_unlock_and_resume(self) -> None:
        item = ctypes.c_uint32(0x11223344)

        self.reset(2, 4, 2, 0)
        self.set_uint("open_cfw_test_queue_check_timeout_result", 1)
        self.assertEqual(
            self.generic_send(
                self.queue_pointer(),
                ctypes.byref(item),
                9,
                0,
            ),
            0,
        )
        self.assertEqual(
            [event for event, _arg0, _arg1 in self.events()],
            [
                EVENT_ENTER_CRITICAL,
                EVENT_SET_TIMEOUT,
                EVENT_EXIT_CRITICAL,
                EVENT_SUSPEND_ALL,
                EVENT_ENTER_CRITICAL,
                EVENT_EXIT_CRITICAL,
                EVENT_CHECK_TIMEOUT,
                EVENT_UNLOCK,
                EVENT_RESUME_ALL,
            ],
        )

        self.reset(2, 4, 2, 0)
        self.set_uint("open_cfw_test_queue_check_timeout_result", 0)
        self.set_uint("open_cfw_test_queue_check_timeout_mutation", 1)
        self.assertEqual(
            self.generic_send(
                self.queue_pointer(),
                ctypes.byref(item),
                7,
                0,
            ),
            1,
        )
        self.assertEqual(self.messages_waiting(), 2)
        self.assertEqual(
            [event for event, _arg0, _arg1 in self.events()].count(
                EVENT_SET_TIMEOUT
            ),
            1,
        )
        self.assertIn((EVENT_CHECK_TIMEOUT, 7, 0), self.events())
        self.assertIn((EVENT_COPY_DATA, 0, 4), self.events())

    def test_send_blocks_yields_then_retries_or_times_out(self) -> None:
        item = ctypes.c_uint32(0xAABBCCDD)

        self.reset(1, 4, 1, 0)
        self.set_uint("open_cfw_test_queue_check_timeout_result", 0)
        self.set_uint(
            "open_cfw_test_queue_check_timeout_result_after_first",
            1,
        )
        self.set_uint("open_cfw_test_queue_resume_all_result", 0)
        self.assertEqual(
            self.generic_send(
                self.queue_pointer(),
                ctypes.byref(item),
                17,
                0,
            ),
            0,
        )
        self.assertEqual(
            self.uint("open_cfw_test_queue_check_timeout_calls"),
            2,
        )
        self.assertIn((EVENT_PLACE_ON_EVENT, 17, 1), self.events())
        self.assertEqual(self.send_waiters(), 1)
        self.assertEqual(
            [event for event, _arg0, _arg1 in self.events()].count(
                EVENT_YIELD
            ),
            1,
        )
        self.assertEqual(
            [event for event, _arg0, _arg1 in self.events()].count(
                EVENT_UNLOCK
            ),
            2,
        )

        self.reset(1, 4, 1, 0)
        self.set_uint("open_cfw_test_queue_check_timeout_result", 0)
        self.set_uint(
            "open_cfw_test_queue_check_timeout_result_after_first",
            0,
        )
        self.set_uint(
            "open_cfw_test_queue_check_timeout_mutation_after_first",
            1,
        )
        self.assertEqual(
            self.generic_send(
                self.queue_pointer(),
                ctypes.byref(item),
                19,
                0,
            ),
            1,
        )
        self.assertEqual(
            self.uint("open_cfw_test_queue_check_timeout_calls"),
            2,
        )
        self.assertIn((EVENT_PLACE_ON_EVENT, 19, 1), self.events())
        self.assertIn((EVENT_COPY_DATA, 0, 4), self.events())
        self.assertEqual(self.messages_waiting(), 1)

    def test_send_wakes_receivers_and_yields_for_both_reasons(self) -> None:
        item = ctypes.c_uint32(0x01020304)
        self.reset(2, 4, 0, 0)
        self.set_waiters(0, 2)
        self.set_uint("open_cfw_test_queue_remove_event_result", 1)
        self.assertEqual(
            self.generic_send(
                self.queue_pointer(),
                ctypes.byref(item),
                0,
                0,
            ),
            1,
        )
        self.assertEqual(self.receive_waiters(), 1)
        self.assertIn((EVENT_REMOVE_EVENT, 2, 1), self.events())
        self.assertEqual(
            [event for event, _arg0, _arg1 in self.events()].count(
                EVENT_YIELD
            ),
            1,
        )

        self.reset(2, 4, 0, 0)
        self.set_uint("open_cfw_test_queue_copy_yield", 1)
        self.assertEqual(
            self.generic_send(
                self.queue_pointer(),
                ctypes.byref(item),
                0,
                0,
            ),
            1,
        )
        self.assertNotIn(
            EVENT_REMOVE_EVENT,
            [event for event, _arg0, _arg1 in self.events()],
        )
        self.assertIn((EVENT_YIELD, 0, 0), self.events())

    def test_semaphore_take_immediate_paths_update_count_and_holder(
        self,
    ) -> None:
        self.reset(3, 0, 2, 0)
        self.set_waiters(2, 0)
        self.set_uint("open_cfw_test_queue_remove_event_result", 1)
        self.assertEqual(
            self.semaphore_take(self.queue_pointer(), 0),
            1,
        )
        self.assertEqual(self.messages_waiting(), 1)
        self.assertEqual(self.send_waiters(), 1)
        self.assertIn((EVENT_REMOVE_EVENT, 2, 1), self.events())
        self.assertIn((EVENT_YIELD, 0, 0), self.events())
        self.assertNotIn(
            EVENT_INCREMENT_MUTEX_HELD,
            [event for event, _arg0, _arg1 in self.events()],
        )

        self.reset(1, 0, 1, 1)
        self.set_ulong(
            "open_cfw_test_queue_mutex_holder_value",
            0x12345678,
        )
        self.assertEqual(
            self.semaphore_take(self.queue_pointer(), 0),
            1,
        )
        self.assertEqual(self.messages_waiting(), 0)
        self.assertEqual(self.mutex_holder(), 0x12345678)
        self.assertIn(
            (EVENT_INCREMENT_MUTEX_HELD, 0, 0),
            self.events(),
        )

        self.reset(1, 0, 0, 0)
        self.assertEqual(
            self.semaphore_take(self.queue_pointer(), 0),
            0,
        )
        self.assertEqual(
            self.events(),
            [
                (EVENT_ENTER_CRITICAL, 0, 0),
                (EVENT_EXIT_CRITICAL, 0, 0),
            ],
        )

    def test_semaphore_take_timeout_and_retry_paths_are_exact(self) -> None:
        self.reset(1, 0, 0, 0)
        self.set_uint("open_cfw_test_queue_check_timeout_result", 1)
        self.assertEqual(
            self.semaphore_take(self.queue_pointer(), 11),
            0,
        )
        self.assertEqual(
            [event for event, _arg0, _arg1 in self.events()],
            [
                EVENT_ENTER_CRITICAL,
                EVENT_SET_TIMEOUT,
                EVENT_EXIT_CRITICAL,
                EVENT_SUSPEND_ALL,
                EVENT_ENTER_CRITICAL,
                EVENT_EXIT_CRITICAL,
                EVENT_CHECK_TIMEOUT,
                EVENT_UNLOCK,
                EVENT_RESUME_ALL,
            ],
        )

        self.reset(1, 0, 0, 0)
        self.set_uint("open_cfw_test_queue_check_timeout_result", 0)
        self.set_uint("open_cfw_test_queue_check_timeout_mutation", 2)
        self.assertEqual(
            self.semaphore_take(self.queue_pointer(), 13),
            1,
        )
        self.assertEqual(self.messages_waiting(), 0)
        self.assertIn((EVENT_CHECK_TIMEOUT, 13, 0), self.events())
        self.assertNotIn(
            EVENT_INCREMENT_MUTEX_HELD,
            [event for event, _arg0, _arg1 in self.events()],
        )
        self.assertEqual(
            [event for event, _arg0, _arg1 in self.events()].count(
                EVENT_SET_TIMEOUT
            ),
            1,
        )

    def test_take_blocks_retries_and_inherits_then_disinherits(self) -> None:
        self.reset(1, 0, 0, 0)
        self.set_uint("open_cfw_test_queue_check_timeout_result", 0)
        self.set_uint(
            "open_cfw_test_queue_check_timeout_result_after_first",
            0,
        )
        self.set_uint(
            "open_cfw_test_queue_check_timeout_mutation_after_first",
            2,
        )
        self.set_uint("open_cfw_test_queue_resume_all_result", 0)
        self.assertEqual(
            self.semaphore_take(self.queue_pointer(), 23),
            1,
        )
        self.assertEqual(
            self.uint("open_cfw_test_queue_check_timeout_calls"),
            2,
        )
        self.assertIn((EVENT_PLACE_ON_EVENT, 23, 1), self.events())
        self.assertEqual(self.receive_waiters(), 1)
        self.assertIn((EVENT_YIELD, 0, 0), self.events())
        self.assertNotIn(
            EVENT_PRIORITY_INHERIT,
            [event for event, _arg0, _arg1 in self.events()],
        )

        self.reset(1, 0, 0, 1)
        original_holder = self.mutex_holder()
        self.set_uint("open_cfw_test_queue_check_timeout_result", 0)
        self.set_uint(
            "open_cfw_test_queue_check_timeout_result_after_first",
            1,
        )
        self.set_uint("open_cfw_test_queue_priority_inherit_result", 1)
        self.set_uint(
            "open_cfw_test_queue_highest_waiting_priority",
            6,
        )
        self.assertEqual(
            self.semaphore_take(self.queue_pointer(), 29),
            0,
        )
        self.assertEqual(
            self.uint("open_cfw_test_queue_check_timeout_calls"),
            2,
        )
        self.assertIn((EVENT_PRIORITY_INHERIT, 1, 1), self.events())
        self.assertIn(
            (EVENT_DISINHERIT_PRIORITY, 6, 0),
            self.events(),
        )
        self.assertIn(
            (EVENT_DISINHERIT_AFTER_TIMEOUT, 6, 0),
            self.events(),
        )
        self.assertEqual(
            self.ulong("open_cfw_test_queue_disinherit_holder"),
            original_holder,
        )
        self.assertEqual(
            self.uint(
                "open_cfw_test_queue_disinherit_priority_value"
            ),
            6,
        )
        event_ids = [
            event for event, _arg0, _arg1 in self.events()
        ]
        self.assertLess(
            event_ids.index(EVENT_PRIORITY_INHERIT),
            event_ids.index(EVENT_PLACE_ON_EVENT),
        )
        self.assertLess(
            event_ids.index(EVENT_DISINHERIT_PRIORITY),
            event_ids.index(EVENT_DISINHERIT_AFTER_TIMEOUT),
        )

    def test_recursive_give_unwinds_only_for_the_current_owner(self) -> None:
        self.reset(1, 0, 0, 1)
        self.set_mutex_state(0x12345678, 2)
        self.assertEqual(
            self.give_mutex_recursive(self.queue_pointer()),
            1,
        )
        self.assertEqual(self.recursive_count(), 1)
        self.assertEqual(self.messages_waiting(), 0)
        self.assertEqual(self.mutex_holder(), 0x12345678)
        self.assertEqual(
            self.events(),
            [(EVENT_CURRENT_TASK, 0x12345678, 0)],
        )

        self.reset(1, 0, 0, 1)
        self.set_mutex_state(0x12345678, 1)
        self.set_waiters(0, 1)
        self.set_uint("open_cfw_test_queue_remove_event_result", 1)
        self.assertEqual(
            self.give_mutex_recursive(self.queue_pointer()),
            1,
        )
        self.assertEqual(self.recursive_count(), 0)
        self.assertEqual(self.messages_waiting(), 1)
        self.assertEqual(self.mutex_holder(), 0)
        self.assertEqual(self.receive_waiters(), 0)
        self.assertEqual(
            [event for event, _arg0, _arg1 in self.events()],
            [
                EVENT_CURRENT_TASK,
                EVENT_ENTER_CRITICAL,
                EVENT_COPY_DATA,
                EVENT_REMOVE_EVENT,
                EVENT_YIELD,
                EVENT_EXIT_CRITICAL,
            ],
        )

        self.reset(1, 0, 0, 1)
        self.set_mutex_state(0x87654321, 3)
        self.assertEqual(
            self.give_mutex_recursive(self.queue_pointer()),
            0,
        )
        self.assertEqual(self.recursive_count(), 3)
        self.assertEqual(self.messages_waiting(), 0)
        self.assertEqual(self.mutex_holder(), 0x87654321)
        self.assertEqual(
            self.events(),
            [(EVENT_CURRENT_TASK, 0x12345678, 0)],
        )

    def test_recursive_take_reenters_or_delegates_to_semaphore_take(
        self,
    ) -> None:
        self.reset(1, 0, 0, 1)
        self.set_mutex_state(0x12345678, 4)
        self.assertEqual(
            self.take_mutex_recursive(self.queue_pointer(), 27),
            1,
        )
        self.assertEqual(self.recursive_count(), 5)
        self.assertEqual(self.messages_waiting(), 0)
        self.assertEqual(
            self.events(),
            [(EVENT_CURRENT_TASK, 0x12345678, 0)],
        )

        self.reset(1, 0, 1, 1)
        self.set_mutex_state(0, 0)
        self.set_ulong(
            "open_cfw_test_queue_current_task_value",
            0x12345678,
        )
        self.set_ulong(
            "open_cfw_test_queue_mutex_holder_value",
            0x12345678,
        )
        self.assertEqual(
            self.take_mutex_recursive(self.queue_pointer(), 0),
            1,
        )
        self.assertEqual(self.recursive_count(), 1)
        self.assertEqual(self.messages_waiting(), 0)
        self.assertEqual(self.mutex_holder(), 0x12345678)
        self.assertEqual(
            [event for event, _arg0, _arg1 in self.events()],
            [
                EVENT_CURRENT_TASK,
                EVENT_ENTER_CRITICAL,
                EVENT_INCREMENT_MUTEX_HELD,
                EVENT_EXIT_CRITICAL,
            ],
        )

        self.reset(1, 0, 0, 1)
        self.set_mutex_state(0x87654321, 0)
        self.assertEqual(
            self.take_mutex_recursive(self.queue_pointer(), 0),
            0,
        )
        self.assertEqual(self.recursive_count(), 0)
        self.assertEqual(self.messages_waiting(), 0)
        self.assertEqual(self.mutex_holder(), 0x87654321)
        self.assertEqual(
            [event for event, _arg0, _arg1 in self.events()],
            [
                EVENT_CURRENT_TASK,
                EVENT_ENTER_CRITICAL,
                EVENT_EXIT_CRITICAL,
            ],
        )

    def test_assert_gates_reject_invalid_send_and_take_calls(self) -> None:
        item = ctypes.c_uint32(0x12345678)
        send_cases = (
            (2, 4, 0, 0, None, ctypes.byref(item), 0, 0),
            (2, 4, 0, 0, "queue", None, 0, 0),
            (2, 4, 0, 0, "queue", ctypes.byref(item), 0, 2),
            (2, 4, 0, 0, "queue", ctypes.byref(item), 5, 0),
        )
        for (
            length,
            item_size,
            messages,
            mutex,
            queue_kind,
            item_pointer,
            ticks,
            position,
        ) in send_cases:
            with self.subTest(
                api="send",
                queue=queue_kind,
                ticks=ticks,
                position=position,
            ):
                self.reset(length, item_size, messages, mutex)
                if ticks:
                    self.set_uint(
                        "open_cfw_test_queue_scheduler_state_value",
                        0,
                    )
                queue = (
                    self.queue_pointer()
                    if queue_kind == "queue"
                    else None
                )
                self.assertEqual(
                    self.send_asserting(
                        queue,
                        item_pointer,
                        ticks,
                        position,
                    ),
                    -100,
                )
                self.assertEqual(
                    self.uint("open_cfw_test_queue_assert_count"),
                    1,
                )
                self.assertEqual(self.events()[-1], (EVENT_ASSERT, 0, 0))

        take_cases = (
            (1, 0, 0, None, 0),
            (1, 4, 0, "queue", 0),
            (1, 0, 0, "queue", 5),
        )
        for length, item_size, messages, queue_kind, ticks in take_cases:
            with self.subTest(
                api="take",
                queue=queue_kind,
                ticks=ticks,
            ):
                self.reset(length, item_size, messages, 0)
                if ticks:
                    self.set_uint(
                        "open_cfw_test_queue_scheduler_state_value",
                        0,
                    )
                queue = (
                    self.queue_pointer()
                    if queue_kind == "queue"
                    else None
                )
                self.assertEqual(
                    self.take_asserting(queue, ticks),
                    -100,
                )
                self.assertEqual(
                    self.uint("open_cfw_test_queue_assert_count"),
                    1,
                )
                self.assertEqual(self.events()[-1], (EVENT_ASSERT, 0, 0))

        for api, call in (
            (
                "give_recursive",
                lambda: self.give_recursive_asserting(None),
            ),
            (
                "take_recursive",
                lambda: self.take_recursive_asserting(None, 0),
            ),
        ):
            with self.subTest(api=api):
                self.reset(1, 0, 0, 1)
                self.assertEqual(call(), -100)
                self.assertEqual(
                    self.uint("open_cfw_test_queue_assert_count"),
                    1,
                )
                self.assertEqual(self.events(), [(EVENT_ASSERT, 0, 0)])

    def test_stock_spans_hashes_and_callers_are_exact(self) -> None:
        expected = {
            "create_mutex": (
                26,
                "fd3801ca9d39f700a0c4dc5598707c4d"
                "d9c6efd75ec8c25d432e7ef29c15eddf",
            ),
            "give_mutex_recursive": (
                64,
                "ba48b7e573af0899510fa67e97d7127b"
                "06f55015f5aeb951fb834f94d44ec1c9",
            ),
            "take_mutex_recursive": (
                64,
                "08842b983b428e0e38c484385f62d27b"
                "6c50719ce1028019a36c343b4ccdc726",
            ),
            "generic_send": (
                356,
                "d8a463345ca0e7754eb0808ebf3a725a"
                "3ca66541b6e85220b6d5459166aac11d",
            ),
            "semaphore_take": (
                354,
                "4d112cee107085a6606d4704c6f9edb4"
                "83264086cc9f954991ac76818c08b34c",
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

        sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        callers = {name: [] for name in FUNCTIONS}
        jumps = {name: [] for name in FUNCTIONS}
        interiors = {name: [] for name in FUNCTIONS}
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

        self.assertEqual(
            callers,
            {
                "create_mutex": [
                    (0x00449796, "f7f79eff"),
                    (0x004497A0, "f7f799ff"),
                    (0x0048415E, "bdf7bafa"),
                    (0x004D4780, "6cf7a9ff"),
                ],
                "give_mutex_recursive": [
                    (0x0043C842, "04f065ff"),
                    (0x0043C868, "04f052ff"),
                    (0x0043C8C8, "04f022ff"),
                    (0x0043CB5A, "04f0d9fd"),
                    (0x0043CEF4, "04f00cfc"),
                    (0x00449848, "f7f762ff"),
                    (0x004D46A2, "6df735f8"),
                ],
                "take_mutex_recursive": [
                    (0x0043C826, "04f093ff"),
                    (0x0043CA84, "04f064fe"),
                    (0x0043CEDE, "04f037fc"),
                    (0x004497E6, "f7f7b3ff"),
                    (0x004D4676, "6df76bf8"),
                ],
                "generic_send": [
                    (0x004416D0, "00f08df8"),
                    (0x00441744, "00f053f8"),
                    (0x0044985E, "f7f7c6ff"),
                    (0x0044991C, "f7f767ff"),
                    (0x004499FE, "f7f7f6fe"),
                    (0x00449B22, "f7f764fe"),
                    (0x00449E86, "f7f7b2fc"),
                    (0x004738A2, "cdf7a4ff"),
                    (0x004738D8, "cdf789ff"),
                    (0x0047E7EE, "c2f7feff"),
                    (0x0047E7FC, "c2f7f7ff"),
                    (0x004841D0, "bdf70dfb"),
                    (0x0048422C, "bdf7dffa"),
                    (0x00484294, "bdf7abfa"),
                    (0x004842E0, "bdf785fa"),
                ],
                "semaphore_take": [
                    (0x00441780, "00f060fa"),
                    (0x00449802, "f8f71ffa"),
                    (0x0044999E, "f8f751f9"),
                    (0x00449DA0, "f7f750ff"),
                    (0x00473842, "cef7fff9"),
                    (0x00484196, "bdf755fd"),
                    (0x004841F0, "bdf728fd"),
                    (0x00484246, "bdf7fdfc"),
                    (0x004842AE, "bdf7c9fc"),
                    (0x00514014, "2df716fe"),
                ],
            },
        )
        self.assertEqual(jumps, {name: [] for name in FUNCTIONS})
        self.assertEqual(interiors, {name: [] for name in FUNCTIONS})

    def test_stock_internal_dependencies_match_recovered_seams(
        self,
    ) -> None:
        sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        targets = {name: set() for name in FUNCTIONS}
        for name, (start, end) in FUNCTIONS.items():
            for address in range(start, end, 2):
                encoded = self.span(address, address + 4)
                try:
                    target = apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=True,
                    )
                except apollo_overlay.BuildError:
                    continue
                targets[name].add(target)

        self.assertEqual(
            targets["create_mutex"],
            {0x00441636, 0x004416B8},
        )
        self.assertEqual(
            targets["give_mutex_recursive"],
            {0x005FA0A4, 0x0045589C, 0x004417EE},
        )
        self.assertEqual(
            targets["take_mutex_recursive"],
            {0x005FA0A4, 0x0045589C, 0x00441C44},
        )
        self.assertTrue(
            {
                0x005FA0A4,
                0x004558A4,
                0x004420D0,
                0x004420E8,
                0x00441ED8,
                0x00455370,
                0x004420BC,
                0x00455556,
                0x00454D7C,
                0x00455566,
                0x00442012,
                0x00455282,
                0x00441F88,
                0x00454DCC,
            }.issubset(targets["generic_send"])
        )
        self.assertTrue(
            {
                0x005FA0A4,
                0x004558A4,
                0x004420D0,
                0x004420E8,
                0x004558CC,
                0x00455370,
                0x004420BC,
                0x00455556,
                0x00454D7C,
                0x00455566,
                0x00441FF6,
                0x00455AE0,
                0x00455282,
                0x00441F88,
                0x00454DCC,
                0x00441EC4,
                0x00455A1C,
            }.issubset(targets["semaphore_take"])
        )


if __name__ == "__main__":
    unittest.main()
