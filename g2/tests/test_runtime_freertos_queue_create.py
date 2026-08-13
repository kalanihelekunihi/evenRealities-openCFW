from __future__ import annotations

import os

import ctypes
import hashlib
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
    / "runtime_freertos_queue_create.c"
)
FIXTURE = ROOT / "tests" / "fixtures" / "runtime_freertos_queue_create_host.c"
OFFICIAL = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
BASE = 0x00438000
FUNCTIONS = {
    "static": (
        0x004415CA,
        0x00441636,
        "2ea331756c835ac36e34e934a9cb807f2695aeae46d6c459dc3033a9879b51b6",
    ),
    "dynamic": (
        0x00441636,
        0x00441696,
        "2e2411839f0b813cc4356ae5a06eafa9e5ee125d200e3980d81e9757c73f0660",
    ),
    "initialise_new": (
        0x00441696,
        0x004416B8,
        "a95e0e593a7afb1fbc642b83c9bc54ab0dc6d994ad4e109bf14dc914d3c2add7",
    ),
    "initialise_mutex": (
        0x004416B8,
        0x004416D6,
        "b74cd4e549fb5b1420f880bbdd86c996f25322ecfd6875555923197d98a875e6",
    ),
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


class RuntimeFreeRTOSQueueCreateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        library = temporary / (
            "runtime_freertos_queue_create.dylib"
            if sys.platform == "darwin"
            else "runtime_freertos_queue_create.so"
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

        cls.reset = cls.loaded.open_cfw_test_queue_create_host_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.static_pointer = (
            cls.loaded.open_cfw_test_queue_create_static_pointer
        )
        cls.static_pointer.restype = ctypes.c_void_p
        cls.storage_pointer = (
            cls.loaded.open_cfw_test_queue_create_storage_pointer
        )
        cls.storage_pointer.restype = ctypes.c_void_p
        cls.allocation_pointer = (
            cls.loaded.open_cfw_test_queue_create_allocation_pointer
        )
        cls.allocation_pointer.restype = ctypes.c_void_p
        cls.control_size = cls.loaded.open_cfw_test_queue_create_control_size
        cls.control_size.restype = ctypes.c_uint

        cls.static_create = (
            cls.loaded.open_cfw_freertos_queue_generic_create_static
        )
        cls.static_create.argtypes = [
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_ubyte,
        ]
        cls.static_create.restype = ctypes.c_void_p
        cls.dynamic_create = (
            cls.loaded.open_cfw_freertos_queue_generic_create
        )
        cls.dynamic_create.argtypes = [
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_ubyte,
        ]
        cls.dynamic_create.restype = ctypes.c_void_p
        cls.initialise_mutex = (
            cls.loaded.open_cfw_freertos_queue_initialise_mutex
        )
        cls.initialise_mutex.argtypes = [ctypes.c_void_p]
        cls.initialise_mutex.restype = None
        cls.dynamic_asserting = (
            cls.loaded.open_cfw_test_queue_create_dynamic_asserting
        )
        cls.dynamic_asserting.argtypes = [ctypes.c_uint, ctypes.c_uint]
        cls.dynamic_asserting.restype = ctypes.c_int
        cls.static_asserting = (
            cls.loaded.open_cfw_test_queue_create_static_asserting
        )
        cls.static_asserting.argtypes = [
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_int,
            ctypes.c_int,
        ]
        cls.static_asserting.restype = ctypes.c_int

        for name in (
            "head",
            "mutex_holder",
        ):
            function = getattr(
                cls.loaded,
                f"open_cfw_test_queue_create_{name}",
            )
            function.argtypes = [ctypes.c_void_p]
            function.restype = ctypes.c_ulong
            setattr(cls, name, function)
        for name in (
            "length",
            "item_size",
            "static_marker",
            "type",
            "messages",
            "recursive_count",
        ):
            function = getattr(
                cls.loaded,
                f"open_cfw_test_queue_create_{name}",
            )
            function.argtypes = [ctypes.c_void_p]
            function.restype = ctypes.c_uint
            setattr(cls, name, function)

        cls.target_object = temporary / "queue_create.o"
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

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def uint(self, name: str) -> int:
        return ctypes.c_uint.in_dll(self.loaded, name).value

    def set_uint(self, name: str, value: int) -> None:
        ctypes.c_uint.in_dll(self.loaded, name).value = value

    def test_official_boundaries_and_hashes_are_pinned(self) -> None:
        for start, end, digest in FUNCTIONS.values():
            blob = self.application[start - BASE:end - BASE]
            self.assertEqual(hashlib.sha256(blob).hexdigest(), digest)
        cluster = self.application[
            FUNCTIONS["static"][0] - BASE:
            FUNCTIONS["initialise_mutex"][1] - BASE
        ]
        self.assertEqual(len(cluster), 268)
        self.assertEqual(
            hashlib.sha256(cluster).hexdigest(),
            "88026bc2cb8b45e5983a6e34072ff2be0767a06775930305310dfcdf28bd48ad",
        )

    def test_static_creation_initialises_recovered_fields(self) -> None:
        self.reset()
        queue = self.static_pointer()
        storage = self.storage_pointer()
        self.assertEqual(
            self.static_create(7, 3, storage, queue, 6),
            queue,
        )
        self.assertEqual(self.head(queue), storage)
        self.assertEqual(self.length(queue), 7)
        self.assertEqual(self.item_size(queue), 3)
        self.assertEqual(self.static_marker(queue), 1)
        self.assertEqual(self.type(queue), 6)
        self.assertEqual(self.uint("open_cfw_test_queue_create_reset_count"), 1)
        self.assertEqual(
            self.uint("open_cfw_test_queue_create_reset_new_queue"),
            1,
        )

    def test_zero_item_static_queue_uses_control_block_as_head(self) -> None:
        self.reset()
        queue = self.static_pointer()
        self.assertEqual(self.static_create(1, 0, None, queue, 4), queue)
        self.assertEqual(self.head(queue), queue)
        self.assertEqual(self.item_size(queue), 0)

    def test_dynamic_creation_allocates_control_plus_storage(self) -> None:
        self.reset()
        queue = self.dynamic_create(5, 4, 2)
        allocation = self.allocation_pointer()
        self.assertEqual(queue, allocation)
        self.assertEqual(
            self.uint("open_cfw_test_queue_create_malloc_size"),
            self.control_size() + 20,
        )
        self.assertEqual(self.head(queue), allocation + self.control_size())
        self.assertEqual(self.static_marker(queue), 0)
        self.assertEqual(self.length(queue), 5)
        self.assertEqual(self.item_size(queue), 4)
        self.assertEqual(self.type(queue), 2)

    def test_dynamic_allocation_failure_is_not_an_assertion(self) -> None:
        self.reset()
        self.set_uint("open_cfw_test_queue_create_malloc_success", 0)
        self.assertIsNone(self.dynamic_create(2, 8, 1))
        self.assertEqual(self.uint("open_cfw_test_queue_create_assert_count"), 0)
        self.assertEqual(self.uint("open_cfw_test_queue_create_reset_count"), 0)

    def test_mutex_initialisation_matches_released_algorithm(self) -> None:
        self.reset()
        queue = self.static_pointer()
        self.static_create(1, 0, None, queue, 4)
        self.initialise_mutex(queue)
        self.assertEqual(self.head(queue), 0)
        self.assertEqual(self.mutex_holder(queue), 0)
        self.assertEqual(self.recursive_count(queue), 0)
        self.assertEqual(self.messages(queue), 1)
        self.assertEqual(self.uint("open_cfw_test_queue_create_send_count"), 1)
        self.assertEqual(self.uint("open_cfw_test_queue_create_send_ticks"), 0)
        self.assertEqual(
            ctypes.c_int.in_dll(
                self.loaded,
                "open_cfw_test_queue_create_send_position",
            ).value,
            0,
        )
        self.initialise_mutex(None)
        self.assertEqual(self.uint("open_cfw_test_queue_create_send_count"), 1)

    def test_invalid_dimensions_follow_assertion_path(self) -> None:
        for length, item_size in (
            (0, 1),
            (2, 0x80000000),
            (1, 0xFFFFFFC0),
        ):
            self.reset()
            self.assertEqual(self.dynamic_asserting(length, item_size), 1)
            self.assertEqual(
                self.uint("open_cfw_test_queue_create_assert_count"),
                1,
            )
        for args in (
            (1, 0, 0, 0),
            (0, 0, 0, 1),
            (1, 4, 0, 1),
        ):
            self.reset()
            self.assertEqual(self.static_asserting(*args), 1)
            self.assertEqual(
                self.uint("open_cfw_test_queue_create_assert_count"),
                1,
            )

    def test_source_scope_and_target_compile_are_explicit(self) -> None:
        source = SOURCE.read_text()
        for token in (
            "FreeRTOS Kernel V10.5.1",
            "SPDX-License-Identifier: MIT",
            "def7d2df2b0506d3d249334974f51e427c17a41c",
            "sizeof(struct open_cfw_queue_create_control) == 0x50U",
            "0x00441517U",
            "0x00456111U",
            "0x005FA0A5U",
            "open_cfw_freertos_queue_generic_create_static(",
            "open_cfw_freertos_queue_generic_create(",
            "open_cfw_freertos_queue_initialise_new(",
            "open_cfw_freertos_queue_initialise_mutex(",
            "open_cfw_freertos_queue_generic_send(",
        ):
            self.assertIn(token, source)
        self.assertNotIn("#include <", source)
        self.assertGreater(self.target_object.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
