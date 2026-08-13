#!/usr/bin/env python3
"""Differential behavior and target-build gates for the ring-buffer adapter."""

from __future__ import annotations

import ctypes
import os
import random
import subprocess
import sys
import tempfile
import unittest
from collections import deque
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/shared/ring_buffer/runtime_ring_buffer.c"
FIXTURE = ROOT / "tests/fixtures/runtime_ring_buffer_host.c"


class RingBuffer(ctypes.Structure):
    _fields_ = [
        ("buffer", ctypes.POINTER(ctypes.c_ubyte)),
        ("buffer_mask", ctypes.c_uint32),
        ("tail_index", ctypes.c_uint32),
        ("head_index", ctypes.c_uint32),
    ]


class RuntimeRingBufferTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory(prefix="opencfw-ring-runtime-")
        library = Path(cls.temporary.name) / (
            "ring_buffer.dylib" if sys.platform == "darwin" else "ring_buffer.so"
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
        subprocess.run(command, cwd=ROOT, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.initialize = cls.loaded.open_cfw_ring_buffer_init
        cls.empty = cls.loaded.open_cfw_ring_buffer_is_empty
        cls.full = cls.loaded.open_cfw_ring_buffer_is_full
        cls.queue = cls.loaded.open_cfw_ring_buffer_queue
        cls.queue_arr = cls.loaded.open_cfw_ring_buffer_queue_arr
        cls.dequeue = cls.loaded.open_cfw_ring_buffer_dequeue
        cls.dequeue_arr = cls.loaded.open_cfw_ring_buffer_dequeue_arr
        cls.get_assert_count = cls.loaded.open_cfw_test_ring_buffer_get_assert_count
        cls.reset_assert_count = cls.loaded.open_cfw_test_ring_buffer_reset_assert_count

        cls.initialize.argtypes = [ctypes.POINTER(RingBuffer), ctypes.POINTER(ctypes.c_ubyte), ctypes.c_uint32]
        cls.empty.argtypes = [ctypes.POINTER(RingBuffer)]
        cls.full.argtypes = [ctypes.POINTER(RingBuffer)]
        cls.queue.argtypes = [ctypes.POINTER(RingBuffer), ctypes.c_ubyte]
        cls.queue_arr.argtypes = [ctypes.POINTER(RingBuffer), ctypes.POINTER(ctypes.c_ubyte), ctypes.c_uint32]
        cls.dequeue.argtypes = [ctypes.POINTER(RingBuffer), ctypes.POINTER(ctypes.c_ubyte)]
        cls.dequeue_arr.argtypes = [ctypes.POINTER(RingBuffer), ctypes.POINTER(ctypes.c_ubyte), ctypes.c_uint32]
        cls.empty.restype = ctypes.c_ubyte
        cls.full.restype = ctypes.c_ubyte
        cls.dequeue.restype = ctypes.c_ubyte
        cls.dequeue_arr.restype = ctypes.c_uint32
        cls.get_assert_count.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_assert_count()

    def make_ring(self, size: int = 8) -> tuple[RingBuffer, ctypes.Array]:
        storage = (ctypes.c_ubyte * size)()
        ring = RingBuffer()
        self.initialize(ctypes.byref(ring), storage, size)
        return ring, storage

    def test_initialization_and_power_of_two_assertion(self) -> None:
        for size, assertions in ((0, 0), (1, 0), (2, 0), (8, 0), (3, 1), (7, 1)):
            with self.subTest(size=size):
                self.reset_assert_count()
                storage = (ctypes.c_ubyte * max(size, 1))()
                ring = RingBuffer()
                self.initialize(ctypes.byref(ring), storage, size)
                self.assertEqual(self.get_assert_count(), assertions)
                self.assertEqual(ring.buffer_mask, (size - 1) & 0xFFFFFFFF)
                self.assertEqual((ring.tail_index, ring.head_index), (0, 0))

    def test_overwrite_oldest_capacity_policy(self) -> None:
        ring, _storage = self.make_ring(8)
        for value in range(10):
            self.queue(ctypes.byref(ring), value)
        result = (ctypes.c_ubyte * 8)()
        count = self.dequeue_arr(ctypes.byref(ring), result, 8)
        self.assertEqual(count, 7)
        self.assertEqual(list(result)[:count], list(range(3, 10)))
        self.assertEqual(self.empty(ctypes.byref(ring)), 1)

    def test_array_zero_length_and_empty_behavior(self) -> None:
        ring, _storage = self.make_ring(4)
        source = (ctypes.c_ubyte * 1)(99)
        output = (ctypes.c_ubyte * 1)(0xA5)
        self.queue_arr(ctypes.byref(ring), source, 0)
        self.assertEqual(self.dequeue_arr(ctypes.byref(ring), output, 1), 0)
        self.assertEqual(output[0], 0xA5)
        self.queue(ctypes.byref(ring), 42)
        self.assertEqual(self.dequeue_arr(ctypes.byref(ring), output, 0), 0)
        self.assertEqual(self.empty(ctypes.byref(ring)), 0)

    def test_randomized_reference_model(self) -> None:
        rng = random.Random(0x598134)
        for size in (2, 4, 8, 16, 32):
            ring, _storage = self.make_ring(size)
            model: deque[int] = deque(maxlen=size - 1)
            for _ in range(2000):
                if rng.randrange(3) != 0:
                    value = rng.randrange(256)
                    self.queue(ctypes.byref(ring), value)
                    model.append(value)
                else:
                    output = ctypes.c_ubyte(0xA5)
                    status = self.dequeue(ctypes.byref(ring), ctypes.byref(output))
                    if model:
                        self.assertEqual(status, 1)
                        self.assertEqual(output.value, model.popleft())
                    else:
                        self.assertEqual(status, 0)
                        self.assertEqual(output.value, 0xA5)
                self.assertEqual(self.empty(ctypes.byref(ring)), int(not model))
                self.assertEqual(self.full(ctypes.byref(ring)), int(len(model) == size - 1))

    def test_source_keeps_seven_distinct_entries_and_fixed_assert_seam(self) -> None:
        text = SOURCE.read_text(encoding="utf-8")
        for name in (
            "is_empty", "is_full", "init", "queue", "queue_arr", "dequeue", "dequeue_arr"
        ):
            self.assertIn(f"open_cfw_ring_buffer_{name}", text)
        self.assertIn("0x004D09B5U", text)
        self.assertIn("0x0074D6ECU", text)
        self.assertIn("0x006FC92CU", text)


if __name__ == "__main__":
    unittest.main()
