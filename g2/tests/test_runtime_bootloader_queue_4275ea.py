# SPDX-License-Identifier: MIT
from __future__ import annotations

import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_queue_4275ea.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_queue_4275ea_host.c"


class Queue(ctypes.Structure):
    _fields_ = [
        ("write_index", ctypes.c_uint32),
        ("read_index", ctypes.c_uint32),
        ("length", ctypes.c_uint32),
        ("capacity", ctypes.c_uint32),
        ("item_size", ctypes.c_uint32),
        ("data", ctypes.POINTER(ctypes.c_uint8)),
    ]


class BootloaderQueueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        library = Path(cls.temp.name) / "queue.so"
        subprocess.run(
            ["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-shared",
             "-fPIC", str(FIXTURE), "-o", str(library)],
            cwd=ROOT, check=True,
        )
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_bootloader_queue_init_4275ea.argtypes = [
            ctypes.POINTER(Queue), ctypes.c_void_p,
            ctypes.c_uint32, ctypes.c_uint32,
        ]
        cls.lib.open_cfw_bootloader_queue_item_add_427602.argtypes = [
            ctypes.POINTER(Queue), ctypes.c_void_p, ctypes.c_uint32,
        ]
        cls.lib.open_cfw_bootloader_queue_item_add_427602.restype = ctypes.c_bool
        cls.lib.open_cfw_bootloader_queue_item_get_427660.argtypes = [
            ctypes.POINTER(Queue), ctypes.c_void_p, ctypes.c_uint32,
        ]
        cls.lib.open_cfw_bootloader_queue_item_get_427660.restype = ctypes.c_bool
        cls.lib.open_cfw_queue_host_reset.argtypes = [ctypes.c_uint32]
        for name in (
            "open_cfw_queue_host_save_calls",
            "open_cfw_queue_host_restore_calls",
            "open_cfw_queue_host_restored_token",
            "open_cfw_queue_host_order",
        ):
            getattr(cls.lib, name).restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def new_queue(self, capacity: int = 8, item_size: int = 1):
        storage = (ctypes.c_uint8 * capacity)()
        queue = Queue()
        self.lib.open_cfw_bootloader_queue_init_4275ea(
            ctypes.byref(queue), storage, item_size, capacity,
        )
        return queue, storage

    def assert_critical_pair(self, token: int) -> None:
        self.assertEqual(self.lib.open_cfw_queue_host_save_calls(), 1)
        self.assertEqual(self.lib.open_cfw_queue_host_restore_calls(), 1)
        self.assertEqual(self.lib.open_cfw_queue_host_restored_token(), token)
        self.assertEqual(self.lib.open_cfw_queue_host_order(), 12)

    def test_init_sets_the_exact_six_word_ambiq_abi(self) -> None:
        queue, storage = self.new_queue(capacity=13, item_size=4)
        self.assertEqual(len(Queue._fields_), 6)
        self.assertEqual(
            (queue.write_index, queue.read_index, queue.length,
             queue.capacity, queue.item_size),
            (0, 0, 0, 13, 4),
        )
        self.assertEqual(
            ctypes.addressof(queue.data.contents), ctypes.addressof(storage))

    def test_add_and_get_preserve_fifo_order_across_wrap(self) -> None:
        queue, storage = self.new_queue(capacity=8, item_size=2)
        first = (ctypes.c_uint8 * 6)(10, 11, 12, 13, 14, 15)
        self.lib.open_cfw_queue_host_reset(0xA5A5A5A5)
        self.assertTrue(self.lib.open_cfw_bootloader_queue_item_add_427602(
            ctypes.byref(queue), first, 3))
        self.assertEqual((queue.write_index, queue.length), (6, 6))
        self.assert_critical_pair(0xA5A5A5A5)

        prefix = (ctypes.c_uint8 * 4)()
        self.lib.open_cfw_queue_host_reset(7)
        self.assertTrue(self.lib.open_cfw_bootloader_queue_item_get_427660(
            ctypes.byref(queue), prefix, 2))
        self.assertEqual(list(prefix), [10, 11, 12, 13])
        self.assertEqual((queue.read_index, queue.length), (4, 2))
        self.assert_critical_pair(7)

        wrapped = (ctypes.c_uint8 * 6)(20, 21, 22, 23, 24, 25)
        self.lib.open_cfw_queue_host_reset(8)
        self.assertTrue(self.lib.open_cfw_bootloader_queue_item_add_427602(
            ctypes.byref(queue), wrapped, 3))
        self.assertEqual((queue.write_index, queue.length), (4, 8))
        self.assertEqual(list(storage), [22, 23, 24, 25, 14, 15, 20, 21])

        output = (ctypes.c_uint8 * 8)()
        self.lib.open_cfw_queue_host_reset(9)
        self.assertTrue(self.lib.open_cfw_bootloader_queue_item_get_427660(
            ctypes.byref(queue), output, 4))
        self.assertEqual(list(output), [14, 15, 20, 21, 22, 23, 24, 25])
        self.assertEqual((queue.read_index, queue.length), (4, 0))

    def test_capacity_and_length_failures_are_atomic(self) -> None:
        queue, storage = self.new_queue(capacity=4)
        queue.write_index = 3
        queue.read_index = 2
        queue.length = 3
        storage[:] = (1, 2, 3, 4)
        queue_size = ctypes.sizeof(Queue)
        before = (bytes(ctypes.string_at(ctypes.byref(queue), queue_size)),
                  bytes(storage))
        source = (ctypes.c_uint8 * 2)(8, 9)
        self.lib.open_cfw_queue_host_reset(0x12345678)
        self.assertFalse(self.lib.open_cfw_bootloader_queue_item_add_427602(
            ctypes.byref(queue), source, 2))
        self.assertEqual(
            (bytes(ctypes.string_at(ctypes.byref(queue), queue_size)),
             bytes(storage)),
            before,
        )
        self.assert_critical_pair(0x12345678)

        destination = (ctypes.c_uint8 * 4)(9, 9, 9, 9)
        self.lib.open_cfw_queue_host_reset(0x87654321)
        self.assertFalse(self.lib.open_cfw_bootloader_queue_item_get_427660(
            ctypes.byref(queue), destination, 4))
        self.assertEqual(list(destination), [9, 9, 9, 9])
        self.assertEqual((queue.write_index, queue.read_index, queue.length),
                         (3, 2, 3))
        self.assert_critical_pair(0x87654321)

    def test_null_buffers_advance_queue_without_copying(self) -> None:
        queue, storage = self.new_queue(capacity=5)
        storage[:] = (1, 2, 3, 4, 5)
        self.lib.open_cfw_queue_host_reset(1)
        self.assertTrue(self.lib.open_cfw_bootloader_queue_item_add_427602(
            ctypes.byref(queue), None, 3))
        self.assertEqual(list(storage), [1, 2, 3, 4, 5])
        self.assertEqual((queue.write_index, queue.length), (3, 3))
        self.lib.open_cfw_queue_host_reset(2)
        self.assertTrue(self.lib.open_cfw_bootloader_queue_item_get_427660(
            ctypes.byref(queue), None, 2))
        self.assertEqual((queue.read_index, queue.length), (2, 1))

    def test_source_is_bounded_reviewable_ambiq_c(self) -> None:
        text = SOURCE.read_text()
        for token in (
            "Copyright (c) 2025, Ambiq Micro, Inc.",
            "queue->capacity - queue->length",
            "queue->write_index = (queue->write_index + 1U) % queue->capacity",
            "queue->read_index = (queue->read_index + 1U) % queue->capacity",
            "open_cfw_bootloader_critical_save_41b8ec",
            '"msr primask, %0"',
        ):
            self.assertIn(token, text)
        self.assertNotIn(".byte", text)
        self.assertNotIn(".inst", text)


if __name__ == "__main__":
    unittest.main()
