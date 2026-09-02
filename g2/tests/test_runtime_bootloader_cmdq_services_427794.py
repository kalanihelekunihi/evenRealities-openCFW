#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from __future__ import annotations

import ctypes
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_cmdq_services_427794.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_cmdq_services_427794_host.c"

SUCCESS = 0
IN_USE = 3
OUT_OF_RANGE = 5
INVALID_ARG = 6
INVALID_OPERATION = 7
INVALID_HANDLE = 2
MAGIC_INITIALIZED = 0x01CDCDCD
ENABLED = 0x02000000


class Config(ctypes.Structure):
    _fields_ = [
        ("size", ctypes.c_uint32),
        ("buffer", ctypes.c_uint32),
        ("priority", ctypes.c_uint32),
    ]


class Entry(ctypes.Structure):
    _fields_ = [("address", ctypes.c_uint32), ("value", ctypes.c_uint32)]


class Status(ctypes.Structure):
    _fields_ = [
        ("last_processed", ctypes.c_uint32),
        ("last_posted", ctypes.c_uint32),
        ("last_allocated", ctypes.c_uint32),
        ("transaction_in_progress", ctypes.c_bool),
        ("paused", ctypes.c_bool),
        ("error", ctypes.c_bool),
    ]


class State(ctypes.Structure):
    _fields_ = [
        ("prefix", ctypes.c_uint32),
        ("buffer_start", ctypes.c_uint32),
        ("buffer_end", ctypes.c_uint32),
        ("head", ctypes.c_uint32),
        ("tail", ctypes.c_uint32),
        ("next_tail", ctypes.c_uint32),
        ("size", ctypes.c_uint32),
        ("current_index", ctypes.c_uint32),
        ("end_index", ctypes.c_uint32),
        ("registers", ctypes.c_void_p),
        ("raw_sequence_start", ctypes.c_uint32),
    ]


class BootloaderCmdqServicesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory(prefix="open-cfw-cmdq-services-")
        library = Path(cls.temporary.name) / "cmdq-services.so"
        subprocess.run(
            ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared",
             "-fPIC", str(FIXTURE), "-o", str(library)],
            cwd=ROOT, check=True,
        )
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_cmdq_services_host_state.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_cmdq_services_host_state.restype = ctypes.POINTER(State)
        cls.lib.open_cfw_cmdq_services_host_entry.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_cmdq_services_host_entry.restype = ctypes.POINTER(Entry)
        cls.lib.open_cfw_cmdq_services_host_set_register.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32,
        ]
        cls.lib.open_cfw_cmdq_services_host_get_register.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32,
        ]
        cls.lib.open_cfw_cmdq_services_host_get_register.restype = ctypes.c_uint32
        cls.lib.open_cfw_cmdq_services_host_register_token.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32,
        ]
        cls.lib.open_cfw_cmdq_services_host_register_token.restype = ctypes.c_uint32
        cls.lib.open_cfw_cmdq_services_host_buffer_base.restype = ctypes.c_uint32
        cls.lib.open_cfw_cmdq_services_host_dmb_calls.restype = ctypes.c_uint32
        cls.lib.open_cfw_cmdq_services_host_update_calls.restype = ctypes.c_uint32

        cls.init = cls.lib.open_cfw_bootloader_cmdq_init_427794
        cls.init.argtypes = [ctypes.c_uint32, ctypes.POINTER(Config),
                             ctypes.POINTER(ctypes.c_void_p)]
        cls.init.restype = ctypes.c_uint32
        for name in ("enable_427878", "disable_4278c8", "release_block_4279be",
                     "error_resume_427b38", "reset_427baa"):
            function = getattr(cls.lib, "open_cfw_bootloader_cmdq_" + name)
            function.argtypes = [ctypes.c_void_p]
            function.restype = ctypes.c_uint32
        cls.enable = cls.lib.open_cfw_bootloader_cmdq_enable_427878
        cls.disable = cls.lib.open_cfw_bootloader_cmdq_disable_4278c8
        cls.release = cls.lib.open_cfw_bootloader_cmdq_release_block_4279be
        cls.error_resume = cls.lib.open_cfw_bootloader_cmdq_error_resume_427b38
        cls.reset_queue = cls.lib.open_cfw_bootloader_cmdq_reset_427baa
        cls.alloc = cls.lib.open_cfw_bootloader_cmdq_alloc_block_42790a
        cls.alloc.argtypes = [ctypes.c_void_p, ctypes.c_uint32,
                              ctypes.POINTER(ctypes.POINTER(Entry)),
                              ctypes.POINTER(ctypes.c_uint32)]
        cls.alloc.restype = ctypes.c_uint32
        cls.post = cls.lib.open_cfw_bootloader_cmdq_post_block_4279f0
        cls.post.argtypes = [ctypes.c_void_p, ctypes.c_bool]
        cls.post.restype = ctypes.c_uint32
        cls.get_status = cls.lib.open_cfw_bootloader_cmdq_get_status_427a56
        cls.get_status.argtypes = [ctypes.c_void_p, ctypes.POINTER(Status)]
        cls.get_status.restype = ctypes.c_uint32
        cls.term = cls.lib.open_cfw_bootloader_cmdq_term_427ad6
        cls.term.argtypes = [ctypes.c_void_p, ctypes.c_bool]
        cls.term.restype = ctypes.c_uint32
        cls.post_loop = cls.lib.open_cfw_bootloader_cmdq_post_loop_block_427c12
        cls.post_loop.argtypes = [ctypes.c_void_p, ctypes.c_bool]
        cls.post_loop.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.lib.open_cfw_cmdq_services_host_reset()
        self.base = self.lib.open_cfw_cmdq_services_host_buffer_base()

    def initialize(self, interface: int = 0, size: int = 32,
                   buffer_offset: int = 0, priority: int = 1):
        config = Config(size, self.base + buffer_offset, priority)
        handle = ctypes.c_void_p()
        result = self.init(interface, ctypes.byref(config), ctypes.byref(handle))
        self.assertEqual(result, SUCCESS)
        return handle, self.lib.open_cfw_cmdq_services_host_state(interface).contents

    def set_register(self, register_index: int, value: int,
                     interface: int = 0) -> None:
        self.lib.open_cfw_cmdq_services_host_set_register(
            interface, register_index, value)

    def get_register(self, register_index: int, interface: int = 0) -> int:
        return self.lib.open_cfw_cmdq_services_host_get_register(
            interface, register_index)

    def token(self, register_index: int, interface: int = 0) -> int:
        return self.lib.open_cfw_cmdq_services_host_register_token(
            interface, register_index)

    def test_init_validates_inputs_and_initializes_exact_state_and_registers(self) -> None:
        handle = ctypes.c_void_p()
        valid = Config(8, self.base, 3)
        self.assertEqual(self.init(12, ctypes.byref(valid), ctypes.byref(handle)),
                         OUT_OF_RANGE)
        self.assertEqual(self.init(0, None, ctypes.byref(handle)), INVALID_ARG)
        for bad in (Config(8, 0, 0), Config(1, self.base, 0)):
            self.assertEqual(self.init(0, ctypes.byref(bad), ctypes.byref(handle)),
                             INVALID_ARG)
        self.assertEqual(self.init(0, ctypes.byref(valid), None), INVALID_ARG)

        self.assertEqual(self.init(0, ctypes.byref(valid), ctypes.byref(handle)),
                         SUCCESS)
        state = self.lib.open_cfw_cmdq_services_host_state(0).contents
        self.assertEqual(state.prefix, MAGIC_INITIALIZED)
        self.assertEqual((state.buffer_start, state.buffer_end, state.size),
                         (self.base, self.base + 64, 64))
        self.assertEqual((state.head, state.tail, state.next_tail),
                         (self.base, self.base, self.base))
        self.assertEqual((state.current_index, state.end_index), (0, 0))
        self.assertEqual(self.get_register(0), 2)
        self.assertEqual(self.get_register(1), self.base)
        self.assertEqual(self.get_register(2), 0)
        self.assertEqual(self.get_register(3), 0)
        self.assertEqual(self.get_register(4), 0x40)
        self.assertEqual(self.init(0, ctypes.byref(valid), ctypes.byref(handle)),
                         INVALID_OPERATION)

    def test_enable_disable_are_validated_idempotent_and_barrier_safe(self) -> None:
        self.assertEqual(self.enable(None), INVALID_HANDLE)
        handle, state = self.initialize()
        self.assertEqual(self.enable(handle), SUCCESS)
        self.assertEqual(state.prefix, MAGIC_INITIALIZED | ENABLED)
        self.assertEqual(self.get_register(0), 3)
        self.assertEqual(self.lib.open_cfw_cmdq_services_host_dmb_calls(), 0)
        self.assertEqual(self.enable(handle), SUCCESS)
        self.assertEqual(self.disable(handle), SUCCESS)
        self.assertEqual(state.prefix, MAGIC_INITIALIZED)
        self.assertEqual(self.get_register(0), 2)
        self.assertEqual(self.disable(handle), SUCCESS)

        state.buffer_end = 0x20080000
        self.assertEqual(self.enable(handle), SUCCESS)
        self.assertEqual(self.lib.open_cfw_cmdq_services_host_dmb_calls(), 1)

    def test_allocate_release_and_post_a_contiguous_block(self) -> None:
        handle, state = self.initialize(size=16)
        block = ctypes.POINTER(Entry)()
        index = ctypes.c_uint32()
        self.assertEqual(self.alloc(handle, 2, ctypes.byref(block),
                                    ctypes.byref(index)), SUCCESS)
        self.assertEqual(index.value, 1)
        self.assertEqual(ctypes.addressof(block.contents),
                         ctypes.addressof(self.lib.open_cfw_cmdq_services_host_entry(0).contents))
        self.assertEqual((state.end_index, state.next_tail), (1, self.base + 16))
        self.assertEqual(self.alloc(handle, 1, ctypes.byref(block),
                                    ctypes.byref(index)), INVALID_OPERATION)
        self.assertEqual(self.release(handle), SUCCESS)
        self.assertEqual((state.end_index, state.next_tail), (0, self.base))
        self.assertEqual(self.release(handle), INVALID_OPERATION)

        self.assertEqual(self.alloc(handle, 2, ctypes.byref(block),
                                    ctypes.byref(index)), SUCCESS)
        self.assertEqual(self.post(handle, True), SUCCESS)
        update = self.lib.open_cfw_cmdq_services_host_entry(2).contents
        self.assertEqual(update.address, self.token(2) | 1)
        self.assertEqual(update.value, 1)
        self.assertEqual((state.tail, state.next_tail),
                         (self.base + 24, self.base + 24))
        self.assertEqual(self.get_register(3), 1)
        self.assertEqual(self.post(handle, False), INVALID_OPERATION)

    def test_allocate_wraps_with_a_hardware_queue_address_entry(self) -> None:
        handle, state = self.initialize(size=16)
        state.tail = self.base + 120
        state.next_tail = state.tail
        self.set_register(1, self.base + 64)
        block = ctypes.POINTER(Entry)()
        index = ctypes.c_uint32()
        self.assertEqual(self.alloc(handle, 2, ctypes.byref(block),
                                    ctypes.byref(index)), SUCCESS)
        wrap = self.lib.open_cfw_cmdq_services_host_entry(15).contents
        self.assertEqual((wrap.address, wrap.value), (self.token(1), self.base))
        self.assertEqual(ctypes.addressof(block.contents),
                         ctypes.addressof(self.lib.open_cfw_cmdq_services_host_entry(0).contents))
        self.assertEqual(state.next_tail, self.base + 16)

    def test_allocate_enforces_index_and_memory_capacity(self) -> None:
        handle, state = self.initialize(size=4)
        block = ctypes.POINTER(Entry)()
        index = ctypes.c_uint32()
        state.end_index = 255
        self.set_register(2, 0)
        self.assertEqual(self.alloc(handle, 1, ctypes.byref(block),
                                    ctypes.byref(index)), OUT_OF_RANGE)
        state.end_index = 0
        state.tail = self.base + 24
        state.next_tail = state.tail
        self.set_register(1, self.base)
        self.assertEqual(self.alloc(handle, 1, ctypes.byref(block),
                                    ctypes.byref(index)), OUT_OF_RANGE)
        self.assertEqual(self.alloc(handle, 1, None, ctypes.byref(index)),
                         INVALID_ARG)

    def test_status_reports_epoch_indices_pending_allocation_and_flags(self) -> None:
        handle, state = self.initialize()
        state.end_index = 0x210
        state.tail = self.base + 24
        state.next_tail = self.base + 32
        self.set_register(1, self.base + 8)
        self.set_register(2, 0xF0)
        self.set_register(6, 0x7)
        result = Status()
        self.assertEqual(self.get_status(handle, ctypes.byref(result)), SUCCESS)
        self.assertEqual((result.last_processed, result.last_posted,
                          result.last_allocated), (0x1F0, 0x20F, 0x210))
        self.assertTrue(result.transaction_in_progress)
        self.assertTrue(result.paused)
        self.assertTrue(result.error)
        self.assertEqual(state.head, self.base + 8)
        self.assertEqual(self.lib.open_cfw_cmdq_services_host_update_calls(), 1)
        self.assertEqual(self.get_status(handle, None), INVALID_ARG)

    def test_termination_refuses_in_use_queue_unless_forced(self) -> None:
        handle, state = self.initialize()
        state.end_index = 3
        self.set_register(2, 2)
        self.assertEqual(self.term(handle, False), IN_USE)
        self.assertEqual(state.prefix, MAGIC_INITIALIZED)
        self.assertEqual(self.term(handle, True), SUCCESS)
        self.assertEqual(state.prefix & 0x01000000, 0)
        self.assertEqual(self.get_register(0) & 1, 0)
        self.assertEqual(self.get_register(4) & 0x40, 0)
        self.assertEqual(self.term(handle, True), INVALID_HANDLE)

    def test_error_resume_follows_wrap_and_clears_update_interrupt(self) -> None:
        handle, state = self.initialize()
        self.assertEqual(self.enable(handle), SUCCESS)
        self.lib.open_cfw_cmdq_services_host_entry(0).contents.address = 0x60000000
        wrap = self.lib.open_cfw_cmdq_services_host_entry(1).contents
        wrap.address = self.token(1)
        wrap.value = self.base + 32
        self.lib.open_cfw_cmdq_services_host_entry(4).contents.address = 0x60000004
        update = self.lib.open_cfw_cmdq_services_host_entry(5).contents
        update.address = self.token(2) | 1
        update.value = 9
        self.set_register(1, self.base)

        self.assertEqual(self.error_resume(handle), SUCCESS)
        self.assertEqual(update.address, self.token(2))
        self.assertEqual(self.get_register(1), self.base + 40)
        self.assertEqual(self.get_register(0) & 1, 0)
        self.assertEqual(state.prefix, MAGIC_INITIALIZED)
        self.assertEqual(self.error_resume(handle), SUCCESS)

    def test_reset_requires_disabled_queue_and_restores_initial_indices(self) -> None:
        handle, state = self.initialize()
        self.assertEqual(self.enable(handle), SUCCESS)
        self.assertEqual(self.reset_queue(handle), INVALID_OPERATION)
        self.assertEqual(self.disable(handle), SUCCESS)
        state.head = self.base + 8
        state.tail = self.base + 16
        state.next_tail = self.base + 24
        state.current_index = 7
        state.end_index = 9
        self.set_register(1, self.base + 16)
        self.set_register(2, 7)
        self.set_register(3, 9)
        self.assertEqual(self.reset_queue(handle), SUCCESS)
        self.assertEqual((state.head, state.tail, state.next_tail),
                         (self.base, self.base, self.base))
        self.assertEqual((state.current_index, state.end_index), (0, 0))
        self.assertEqual((self.get_register(1), self.get_register(2),
                          self.get_register(3)), (self.base, 0, 0))

    def test_loop_post_writes_index_reset_and_loopback_entries(self) -> None:
        handle, state = self.initialize()
        state.next_tail = self.base + 16
        state.end_index = 0x123
        state.buffer_end = 0x20080000
        self.assertEqual(self.post_loop(handle, True), SUCCESS)
        reset_entry = self.lib.open_cfw_cmdq_services_host_entry(2).contents
        loop_entry = self.lib.open_cfw_cmdq_services_host_entry(3).contents
        self.assertEqual((reset_entry.address, reset_entry.value),
                         (self.token(2), 0))
        self.assertEqual((loop_entry.address, loop_entry.value),
                         (self.token(1) | 1, self.base))
        self.assertEqual((state.tail, state.next_tail),
                         (self.base + 32, self.base + 32))
        self.assertEqual(self.get_register(3), 0x23)
        self.assertEqual(self.lib.open_cfw_cmdq_services_host_dmb_calls(), 1)

    def test_source_is_reviewable_compilable_c_without_encoded_instructions(self) -> None:
        text = SOURCE.read_text()
        for token in (
            "open_cfw_bootloader_cmdq_init_427794",
            "open_cfw_bootloader_cmdq_alloc_block_42790a",
            "open_cfw_bootloader_cmdq_error_resume_427b38",
            "open_cfw_bootloader_cmdq_post_loop_block_427c12",
            "open_cfw_bootloader_cmdq_update_indices_427754(queue)",
            "OPEN_CFW_CMDQ_SSRAM_BASE",
            "dmb sy",
        ):
            self.assertIn(token, text)
        for token in (".byte", ".short", ".word", ".inst"):
            self.assertNotIn(token, text)


if __name__ == "__main__":
    unittest.main()
