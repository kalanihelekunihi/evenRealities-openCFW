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
    / "runtime_heap_coordinator.c"
)
FIXTURE = (
    ROOT / "tests" / "fixtures" / "runtime_heap_coordinator_host.c"
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
    "initialize": (0x0048413C, 0x00484180),
    "allocate": (0x00484180, 0x004841D8),
    "memalign": (0x004841D8, 0x00484234),
    "reallocate": (0x00484234, 0x0048429E),
    "free": (0x0048429E, 0x004842E6),
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

EVENT_TLSF_CREATE = 1
EVENT_MUTEX_CREATE = 2
EVENT_DIAGNOSTIC = 3
EVENT_FATAL = 4
EVENT_MUTEX_ACQUIRE = 5
EVENT_MUTEX_RELEASE = 6
EVENT_TLSF_ALLOCATE = 7
EVENT_TLSF_MEMALIGN = 8
EVENT_TLSF_BLOCK_SIZE = 9
EVENT_TLSF_REALLOCATE = 10
EVENT_TLSF_FREE = 11
WAIT_FOREVER = 0xFFFFFFFF


_APPLE_ONLY = unittest.skipUnless(
    (os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") or "apple-clang") == "apple-clang",
    "byte-exact / toolchain-specific Apple-clang assertion; Linux byte "
    "reproduction is verified end-to-end by tests/test_toolchain_profiles.py",
)


class HeapDescriptor(ctypes.Structure):
    _fields_ = [
        ("mutex", ctypes.c_uint32),
        ("allocator", ctypes.c_uint32),
        ("current_bytes", ctypes.c_uint32),
        ("peak_bytes", ctypes.c_uint32),
        ("arena_size", ctypes.c_uint32),
        ("arena", ctypes.c_uint32),
        ("policy", ctypes.c_uint8),
        ("reserved", ctypes.c_uint8 * 3),
    ]


def _sign_extend(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return value - (1 << bits) if value & sign else value


class RuntimeHeapCoordinatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        library = temporary / (
            "runtime_heap_coordinator.dylib"
            if sys.platform == "darwin"
            else "runtime_heap_coordinator.so"
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
        cls.reset = (
            cls.loaded.open_cfw_test_runtime_heap_coordinator_reset
        )
        cls.reset.argtypes = [ctypes.c_uint32] * 6
        cls.reset.restype = None
        cls.set_block_sizes = (
            cls.loaded
            .open_cfw_test_runtime_heap_coordinator_set_block_sizes
        )
        cls.set_block_sizes.argtypes = [
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_uint32,
        ]
        cls.set_block_sizes.restype = None
        cls.initialize = (
            cls.loaded.open_cfw_test_runtime_heap_coordinator_initialize
        )
        cls.initialize.argtypes = [
            ctypes.POINTER(HeapDescriptor),
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.initialize.restype = ctypes.c_int
        cls.allocate = (
            cls.loaded.open_cfw_runtime_heap_generic_allocate
        )
        cls.allocate.argtypes = [
            ctypes.POINTER(HeapDescriptor),
            ctypes.c_uint32,
        ]
        cls.allocate.restype = ctypes.c_uint32
        cls.memalign = (
            cls.loaded.open_cfw_runtime_heap_generic_memalign
        )
        cls.memalign.argtypes = [
            ctypes.POINTER(HeapDescriptor),
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.memalign.restype = ctypes.c_uint32
        cls.reallocate = (
            cls.loaded.open_cfw_runtime_heap_generic_reallocate
        )
        cls.reallocate.argtypes = [
            ctypes.POINTER(HeapDescriptor),
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.reallocate.restype = ctypes.c_uint32
        cls.free = cls.loaded.open_cfw_runtime_heap_generic_free
        cls.free.argtypes = [
            ctypes.POINTER(HeapDescriptor),
            ctypes.c_uint32,
        ]
        cls.free.restype = None

        cls.target_object = temporary / "runtime_heap_coordinator.o"
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

    def descriptor(self) -> HeapDescriptor:
        descriptor = HeapDescriptor()
        descriptor.mutex = 0x11111111
        descriptor.allocator = 0x22222222
        descriptor.current_bytes = 0x33333333
        descriptor.peak_bytes = 0x44444444
        descriptor.arena_size = 0x55555555
        descriptor.arena = 0x66666666
        descriptor.policy = 0x77
        descriptor.reserved[:] = (0x88, 0x99, 0xAA)
        return descriptor

    def configure(
        self,
        *,
        tlsf_create: int = 0xC001C001,
        mutex_create: int = 0xABCD1234,
        mutex_acquire: int = 1,
        allocate: int = 0x10001000,
        memalign: int = 0x20002000,
        reallocate: int = 0x30003000,
        block_sizes: tuple[int, ...] = (),
    ) -> None:
        self.reset(
            tlsf_create,
            mutex_create,
            mutex_acquire,
            allocate,
            memalign,
            reallocate,
        )
        if block_sizes:
            values = (ctypes.c_uint32 * len(block_sizes))(*block_sizes)
            self.set_block_sizes(values, len(block_sizes))

    def uint(self, name: str) -> int:
        return ctypes.c_uint32.in_dll(self.loaded, name).value

    def events(self) -> list[tuple[int, int, int, int, int]]:
        count = self.uint(
            "open_cfw_test_runtime_heap_coordinator_event_count"
        )
        self.assertLessEqual(count, 64)
        arrays = []
        for suffix in (
            "event_codes",
            "event_argument0",
            "event_argument1",
            "event_argument2",
            "event_argument3",
        ):
            arrays.append(
                (ctypes.c_uint32 * 64).in_dll(
                    self.loaded,
                    "open_cfw_test_runtime_heap_coordinator_" + suffix,
                )
            )
        return [
            tuple(int(array[index]) for array in arrays)
            for index in range(count)
        ]

    def span(self, start: int, end: int) -> bytes:
        return self.application[start - BASE:end - BASE]

    def test_descriptor_layout_is_exactly_twenty_eight_bytes(self) -> None:
        self.assertEqual(ctypes.sizeof(HeapDescriptor), 28)
        self.assertEqual(
            {
                name: getattr(HeapDescriptor, name).offset
                for name, _field_type in HeapDescriptor._fields_
            },
            {
                "mutex": 0,
                "allocator": 4,
                "current_bytes": 8,
                "peak_bytes": 12,
                "arena_size": 16,
                "arena": 20,
                "policy": 24,
                "reserved": 25,
            },
        )

    def test_initialize_success_preserves_policy_tail(self) -> None:
        descriptor = self.descriptor()
        self.configure(tlsf_create=0x12345678, mutex_create=0x89ABCDEF)

        self.assertEqual(
            self.initialize(
                ctypes.byref(descriptor),
                0x20001000,
                0xFFFFF123,
            ),
            0,
        )
        self.assertEqual(
            (
                descriptor.mutex,
                descriptor.allocator,
                descriptor.current_bytes,
                descriptor.peak_bytes,
                descriptor.arena_size,
                descriptor.arena,
                descriptor.policy,
                tuple(descriptor.reserved),
            ),
            (
                0x89ABCDEF,
                0x12345678,
                0,
                0,
                0xFFFFF123,
                0x20001000,
                0x77,
                (0x88, 0x99, 0xAA),
            ),
        )
        self.assertEqual(
            self.events(),
            [
                (EVENT_TLSF_CREATE, 0x20001000, 0xFFFFF123, 0, 0),
                (EVENT_MUTEX_CREATE, 1, 0, 0, 0),
            ],
        )

    def test_initialize_pool_failure_logs_then_fails_safely(self) -> None:
        descriptor = self.descriptor()
        before = bytes(descriptor)
        self.configure(tlsf_create=0)

        self.assertEqual(
            self.initialize(ctypes.byref(descriptor), 0x20002000, 0x4000),
            1,
        )
        expected = bytearray(before)
        expected[4:8] = b"\0\0\0\0"
        self.assertEqual(bytes(descriptor), bytes(expected))
        self.assertEqual(
            self.events(),
            [
                (EVENT_TLSF_CREATE, 0x20002000, 0x4000, 0, 0),
                (EVENT_DIAGNOSTIC, 1, 0, 0, 0),
                (EVENT_FATAL, 0, 0, 0, 0),
            ],
        )
        message = ctypes.c_char_p.in_dll(
            self.loaded,
            "open_cfw_test_runtime_heap_coordinator_diagnostic_message",
        ).value
        self.assertEqual(message, b"TLSF memory pool creation failed!\n")

    def test_initialize_mutex_failure_logs_then_fails_safely(self) -> None:
        descriptor = self.descriptor()
        before = bytes(descriptor)
        self.configure(tlsf_create=0x87654321, mutex_create=0)

        self.assertEqual(
            self.initialize(ctypes.byref(descriptor), 0x20003000, 0x8000),
            1,
        )
        expected = bytearray(before)
        expected[0:4] = b"\0\0\0\0"
        expected[4:8] = struct.pack("<I", 0x87654321)
        self.assertEqual(bytes(descriptor), bytes(expected))
        self.assertEqual(
            self.events(),
            [
                (EVENT_TLSF_CREATE, 0x20003000, 0x8000, 0, 0),
                (EVENT_MUTEX_CREATE, 1, 0, 0, 0),
                (EVENT_DIAGNOSTIC, 2, 0, 0, 0),
                (EVENT_FATAL, 0, 0, 0, 0),
            ],
        )
        message = ctypes.c_char_p.in_dll(
            self.loaded,
            "open_cfw_test_runtime_heap_coordinator_diagnostic_message",
        ).value
        self.assertEqual(message, b"TLSF mutex creation failed!\n")

    def test_allocate_zero_and_lock_failures_have_no_side_effects(
        self,
    ) -> None:
        for size, lock_result, expected_events in (
            (0, 1, []),
            (
                1,
                0,
                [
                    (
                        EVENT_MUTEX_ACQUIRE,
                        0x11111111,
                        WAIT_FOREVER,
                        0,
                        0,
                    )
                ],
            ),
            (
                0xFFFFFFFF,
                2,
                [
                    (
                        EVENT_MUTEX_ACQUIRE,
                        0x11111111,
                        WAIT_FOREVER,
                        0,
                        0,
                    )
                ],
            ),
        ):
            descriptor = self.descriptor()
            before = bytes(descriptor)
            self.configure(mutex_acquire=lock_result)
            with self.subTest(size=size, lock_result=lock_result):
                self.assertEqual(
                    self.allocate(ctypes.byref(descriptor), size),
                    0,
                )
                self.assertEqual(bytes(descriptor), before)
                self.assertEqual(self.events(), expected_events)

    def test_allocate_failure_releases_without_accounting(self) -> None:
        descriptor = self.descriptor()
        before = bytes(descriptor)
        self.configure(allocate=0, block_sizes=(0x100,))

        self.assertEqual(
            self.allocate(ctypes.byref(descriptor), 0xFEDCBA98),
            0,
        )
        self.assertEqual(bytes(descriptor), before)
        self.assertEqual(
            self.events(),
            [
                (
                    EVENT_MUTEX_ACQUIRE,
                    descriptor.mutex,
                    WAIT_FOREVER,
                    0,
                    0,
                ),
                (
                    EVENT_TLSF_ALLOCATE,
                    descriptor.allocator,
                    0xFEDCBA98,
                    0,
                    0,
                ),
                (EVENT_MUTEX_RELEASE, descriptor.mutex, 0, 0, 0),
            ],
        )
        self.assertEqual(
            self.uint(
                "open_cfw_test_runtime_heap_coordinator_block_size_index"
            ),
            0,
        )

    def test_allocate_accounts_with_unsigned_wrap_and_peak_policy(
        self,
    ) -> None:
        cases = (
            (10, 20, 7, 17, 20),
            (0xFFFFFFF0, 0x10, 0x30, 0x20, 0x20),
            (
                0xFFFFFFF0,
                0xFFFFFFF5,
                0x30,
                0x20,
                0xFFFFFFF5,
            ),
        )
        for current, peak, block_size, expected_current, expected_peak in cases:
            descriptor = self.descriptor()
            descriptor.current_bytes = current
            descriptor.peak_bytes = peak
            self.configure(allocate=0xDEADBEEF, block_sizes=(block_size,))
            with self.subTest(current=current, peak=peak):
                self.assertEqual(
                    self.allocate(ctypes.byref(descriptor), 0x1234),
                    0xDEADBEEF,
                )
                self.assertEqual(
                    (descriptor.current_bytes, descriptor.peak_bytes),
                    (expected_current, expected_peak),
                )
                self.assertEqual(
                    self.events(),
                    [
                        (
                            EVENT_MUTEX_ACQUIRE,
                            descriptor.mutex,
                            WAIT_FOREVER,
                            0,
                            0,
                        ),
                        (
                            EVENT_TLSF_ALLOCATE,
                            descriptor.allocator,
                            0x1234,
                            0,
                            0,
                        ),
                        (
                            EVENT_TLSF_BLOCK_SIZE,
                            0xDEADBEEF,
                            0,
                            0,
                            0,
                        ),
                        (
                            EVENT_MUTEX_RELEASE,
                            descriptor.mutex,
                            0,
                            0,
                            0,
                        ),
                    ],
                )

    def test_memalign_argument_order_and_accounting_are_exact(self) -> None:
        descriptor = self.descriptor()
        descriptor.current_bytes = 100
        descriptor.peak_bytes = 110
        self.configure(memalign=0xCAFEBABE, block_sizes=(16,))

        self.assertEqual(
            self.memalign(
                ctypes.byref(descriptor),
                0x12345678,
                0x80000000,
            ),
            0xCAFEBABE,
        )
        self.assertEqual(
            (descriptor.current_bytes, descriptor.peak_bytes),
            (116, 116),
        )
        self.assertEqual(
            self.events(),
            [
                (
                    EVENT_MUTEX_ACQUIRE,
                    descriptor.mutex,
                    WAIT_FOREVER,
                    0,
                    0,
                ),
                (
                    EVENT_TLSF_MEMALIGN,
                    descriptor.allocator,
                    0x80000000,
                    0x12345678,
                    0,
                ),
                (EVENT_TLSF_BLOCK_SIZE, 0xCAFEBABE, 0, 0, 0),
                (EVENT_MUTEX_RELEASE, descriptor.mutex, 0, 0, 0),
            ],
        )

        descriptor = self.descriptor()
        before = bytes(descriptor)
        self.configure()
        self.assertEqual(
            self.memalign(ctypes.byref(descriptor), 0, 0x20),
            0,
        )
        self.assertEqual(bytes(descriptor), before)
        self.assertEqual(self.events(), [])

    def test_reallocate_lock_failure_does_not_query_old_size(self) -> None:
        descriptor = self.descriptor()
        before = bytes(descriptor)
        self.configure(mutex_acquire=0, block_sizes=(0x55,))

        self.assertEqual(
            self.reallocate(
                ctypes.byref(descriptor),
                0x11112222,
                0x33334444,
            ),
            0,
        )
        self.assertEqual(bytes(descriptor), before)
        self.assertEqual(
            self.events(),
            [
                (
                    EVENT_MUTEX_ACQUIRE,
                    descriptor.mutex,
                    WAIT_FOREVER,
                    0,
                    0,
                )
            ],
        )
        self.assertEqual(
            self.uint(
                "open_cfw_test_runtime_heap_coordinator_block_size_index"
            ),
            0,
        )

    def test_reallocate_success_uses_fifo_sizes_and_unsigned_math(
        self,
    ) -> None:
        cases = (
            (100, 120, 40, 70, 130, 130),
            (5, 10, 9, 2, 0xFFFFFFFE, 0xFFFFFFFE),
        )
        for (
            current,
            peak,
            old_size,
            new_size,
            expected_current,
            expected_peak,
        ) in cases:
            descriptor = self.descriptor()
            descriptor.current_bytes = current
            descriptor.peak_bytes = peak
            self.configure(
                reallocate=0x55667788,
                block_sizes=(old_size, new_size),
            )
            with self.subTest(current=current, old_size=old_size):
                self.assertEqual(
                    self.reallocate(
                        ctypes.byref(descriptor),
                        0x11223344,
                        0x99AABBCC,
                    ),
                    0x55667788,
                )
                self.assertEqual(
                    (descriptor.current_bytes, descriptor.peak_bytes),
                    (expected_current, expected_peak),
                )
                self.assertEqual(
                    self.events(),
                    [
                        (
                            EVENT_MUTEX_ACQUIRE,
                            descriptor.mutex,
                            WAIT_FOREVER,
                            0,
                            0,
                        ),
                        (
                            EVENT_TLSF_BLOCK_SIZE,
                            0x11223344,
                            0,
                            0,
                            0,
                        ),
                        (
                            EVENT_TLSF_REALLOCATE,
                            descriptor.allocator,
                            0x11223344,
                            0x99AABBCC,
                            0,
                        ),
                        (
                            EVENT_TLSF_BLOCK_SIZE,
                            0x55667788,
                            0,
                            0,
                            0,
                        ),
                        (
                            EVENT_MUTEX_RELEASE,
                            descriptor.mutex,
                            0,
                            0,
                            0,
                        ),
                    ],
                )

    def test_reallocate_size_zero_preserves_stock_stale_accounting_bug(
        self,
    ) -> None:
        descriptor = self.descriptor()
        descriptor.current_bytes = 0x12345678
        descriptor.peak_bytes = 0x87654321
        self.configure(reallocate=0, block_sizes=(0x1000, 0x2000))

        self.assertEqual(
            self.reallocate(ctypes.byref(descriptor), 0xAABBCCDD, 0),
            0,
        )
        self.assertEqual(
            (descriptor.current_bytes, descriptor.peak_bytes),
            (0x12345678, 0x87654321),
        )
        self.assertEqual(
            self.events(),
            [
                (
                    EVENT_MUTEX_ACQUIRE,
                    descriptor.mutex,
                    WAIT_FOREVER,
                    0,
                    0,
                ),
                (EVENT_TLSF_BLOCK_SIZE, 0xAABBCCDD, 0, 0, 0),
                (
                    EVENT_TLSF_REALLOCATE,
                    descriptor.allocator,
                    0xAABBCCDD,
                    0,
                    0,
                ),
                (EVENT_MUTEX_RELEASE, descriptor.mutex, 0, 0, 0),
            ],
        )
        self.assertEqual(
            self.uint(
                "open_cfw_test_runtime_heap_coordinator_block_size_index"
            ),
            1,
        )

    def test_free_null_and_lock_failure_are_no_ops(self) -> None:
        for allocation, lock_result, expected_events in (
            (0, 1, []),
            (
                0xFFFFFFFF,
                0,
                [
                    (
                        EVENT_MUTEX_ACQUIRE,
                        0x11111111,
                        WAIT_FOREVER,
                        0,
                        0,
                    )
                ],
            ),
            (
                0x12345678,
                2,
                [
                    (
                        EVENT_MUTEX_ACQUIRE,
                        0x11111111,
                        WAIT_FOREVER,
                        0,
                        0,
                    )
                ],
            ),
        ):
            descriptor = self.descriptor()
            before = bytes(descriptor)
            self.configure(mutex_acquire=lock_result, block_sizes=(99,))
            with self.subTest(allocation=allocation, lock_result=lock_result):
                self.free(ctypes.byref(descriptor), allocation)
                self.assertEqual(bytes(descriptor), before)
                self.assertEqual(self.events(), expected_events)

    def test_free_saturates_accounting_after_backend_free(self) -> None:
        for current, block_size, expected_current in (
            (100, 40, 60),
            (100, 100, 0),
            (100, 101, 0),
            (0, 0xFFFFFFFF, 0),
        ):
            descriptor = self.descriptor()
            descriptor.current_bytes = current
            descriptor.peak_bytes = 0xABCDEF01
            self.configure(block_sizes=(block_size,))
            with self.subTest(current=current, block_size=block_size):
                self.free(ctypes.byref(descriptor), 0x13579BDF)
                self.assertEqual(descriptor.current_bytes, expected_current)
                self.assertEqual(descriptor.peak_bytes, 0xABCDEF01)
                self.assertEqual(
                    self.events(),
                    [
                        (
                            EVENT_MUTEX_ACQUIRE,
                            descriptor.mutex,
                            WAIT_FOREVER,
                            0,
                            0,
                        ),
                        (
                            EVENT_TLSF_BLOCK_SIZE,
                            0x13579BDF,
                            0,
                            0,
                            0,
                        ),
                        (
                            EVENT_TLSF_FREE,
                            descriptor.allocator,
                            0x13579BDF,
                            0,
                            0,
                        ),
                        (
                            EVENT_MUTEX_RELEASE,
                            descriptor.mutex,
                            0,
                            0,
                            0,
                        ),
                    ],
                )

    def test_stock_spans_hashes_and_combined_boundary_are_exact(
        self,
    ) -> None:
        expected = {
            "initialize": (
                68,
                "151bc5509260a8d535b286753eb8b5ba"
                "99fc179049f9fbc1191e36a59c6ad35b",
            ),
            "allocate": (
                88,
                "5c8eae7744e9bcd8bcfe6ed1ebaf678c"
                "faf80ebcb4b1d9a74178f991bf163084",
            ),
            "memalign": (
                92,
                "a098f7aca0ad496ce3ccd16fa3a61aa90"
                "68e663ad265ab1a00aa14eb223713f6",
            ),
            "reallocate": (
                106,
                "470c32d27721f6932431a553868f6e5e4"
                "34d56bb1c8a0818e42e42b45882828e",
            ),
            "free": (
                72,
                "26fffcabeaafc258cfa459b415b1eefe"
                "672cc859c9bc23a19bd5834c6072886e",
            ),
        }
        for name, (length, digest) in expected.items():
            start, end = FUNCTIONS[name]
            body = self.span(start, end)
            with self.subTest(name=name):
                self.assertEqual(len(body), length)
                self.assertEqual(hashlib.sha256(body).hexdigest(), digest)
        combined = self.span(0x0048413C, 0x004842E6)
        self.assertEqual(len(combined), 426)
        self.assertEqual(
            hashlib.sha256(combined).hexdigest(),
            "7416a9e1f11c680ae3684dc26bdf5520"
            "71d5b932ebc67579ef0fc309244b2fd0",
        )

    def test_wide_callers_dependencies_and_interiors_are_exact(
        self,
    ) -> None:
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        callers = {name: [] for name in FUNCTIONS}
        jumps = {name: [] for name in FUNCTIONS}
        interiors = {name: [] for name in FUNCTIONS}
        dependencies = {name: [] for name in FUNCTIONS}
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
                    if link and start <= address < end:
                        dependencies[name].append(
                            (address, target, encoded.hex())
                        )

        self.assertEqual(
            callers,
            {
                "initialize": [
                    (0x004842F0, "fff724ff"),
                    (0x004842FE, "fff71dff"),
                    (0x0048430C, "fff716ff"),
                ],
                "allocate": [
                    (0x00484324, "fff72cff"),
                    (0x005140AE, "70f767f8"),
                    (0x00514172, "70f705f8"),
                    (0x00567652, "1cf795fd"),
                    (0x005676A6, "1cf76bfd"),
                    (0x005676D8, "1cf752fd"),
                ],
                "memalign": [
                    (0x00514090, "70f7a2f8"),
                    (0x005140A6, "70f797f8"),
                ],
                "reallocate": [
                    (0x00484332, "fff77fff"),
                    (0x005676E6, "1cf7a5fd"),
                ],
                "free": [
                    (0x0048433E, "fff7aeff"),
                    (0x005140D2, "70f7e4f8"),
                    (0x0051417E, "70f78ef8"),
                    (0x005676CC, "1cf7e7fd"),
                    (0x005676F0, "1cf7d5fd"),
                    (0x00567708, "1cf7c9fd"),
                ],
            },
        )
        self.assertEqual(jumps, {name: [] for name in FUNCTIONS})
        self.assertEqual(interiors, {name: [] for name in FUNCTIONS})
        self.assertEqual(
            dependencies,
            {
                "initialize": [
                    (0x00484148, 0x004D06EC, "4cf0d0fa"),
                    (0x00484156, 0x004733EE, "eff74af9"),
                    (0x0048415E, 0x004416D6, "bdf7bafa"),
                    (0x0048416C, 0x004733EE, "eff73ff9"),
                ],
                "allocate": [
                    (0x00484196, 0x00441C44, "bdf755fd"),
                    (0x004841A2, 0x004D0722, "4cf0befa"),
                    (0x004841AE, 0x004D05E4, "4cf019fa"),
                    (0x004841D0, 0x004417EE, "bdf70dfb"),
                ],
                "memalign": [
                    (0x004841F0, 0x00441C44, "bdf728fd"),
                    (0x004841FE, 0x004D0744, "4cf0a1fa"),
                    (0x0048420A, 0x004D05E4, "4cf0ebf9"),
                    (0x0048422C, 0x004417EE, "bdf7dffa"),
                ],
                "reallocate": [
                    (0x00484246, 0x00441C44, "bdf7fdfc"),
                    (0x00484250, 0x004D05E4, "4cf0c8f9"),
                    (0x0048425C, 0x004D0868, "4cf004fb"),
                    (0x00484272, 0x004D05E4, "4cf0b7f9"),
                    (0x00484294, 0x004417EE, "bdf7abfa"),
                ],
                "free": [
                    (0x004842AE, 0x00441C44, "bdf7c9fc"),
                    (0x004842B8, 0x004D05E4, "4cf094f9"),
                    (0x004842C2, 0x004D0808, "4cf0a1fa"),
                    (0x004842E0, 0x004417EE, "bdf785fa"),
                ],
            },
        )

    def test_no_external_narrow_entries_and_stored_candidates_are_bounded(
        self,
    ) -> None:
        narrow_entries = {name: [] for name in FUNCTIONS}
        narrow_interiors = {name: [] for name in FUNCTIONS}
        for offset in range(0, len(self.application) - 1, 2):
            address = BASE + offset
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
                if start in candidates and not start <= address < end:
                    narrow_entries[name].append((address, halfword))
                for target in candidates:
                    if (
                        start < target < end
                        and not start <= address < end
                    ):
                        narrow_interiors[name].append(
                            (address, target, halfword)
                        )

        stored = {name: [] for name in FUNCTIONS}
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            target = value & ~1
            if value & 1:
                for name, (start, end) in FUNCTIONS.items():
                    if start <= target < end:
                        stored[name].append(
                            (BASE + offset, target, value)
                        )

        self.assertEqual(
            narrow_entries,
            {name: [] for name in FUNCTIONS},
        )
        self.assertEqual(
            narrow_interiors,
            {name: [] for name in FUNCTIONS},
        )
        self.assertEqual(
            stored,
            {
                "initialize": [
                    (0x0046D561, 0x00484148, 0x00484149),
                ],
                "allocate": [
                    (0x00583CED, 0x004841B4, 0x004841B5),
                ],
                "memalign": [],
                "reallocate": [],
                "free": [
                    (0x0044CFC3, 0x004842D0, 0x004842D1),
                ],
            },
        )
        self.assertTrue(
            all(
                address & 1
                for candidates in stored.values()
                for address, _target, _value in candidates
            )
        )

    @_APPLE_ONLY
    def test_target_text_symbols_and_dependencies_are_exact(self) -> None:
        self.assertEqual(len(self.target_text), 498)
        self.assertEqual(
            hashlib.sha256(self.target_text).hexdigest(),
            "9d3d1d4bd34f8cd47baa89c7466da494"
            "33c7604e16468e8c9f1f9bcdc77d2909",
        )
        expected_symbols = {
            "open_cfw_runtime_heap_generic_initialize": (0, 86),
            "open_cfw_runtime_heap_generic_allocate": (88, 94),
            "open_cfw_runtime_heap_generic_memalign": (184, 102),
            "open_cfw_runtime_heap_generic_reallocate": (288, 114),
            "open_cfw_runtime_heap_generic_free": (404, 94),
        }
        for name, expected in expected_symbols.items():
            fields = self.symbols[name]
            with self.subTest(name=name):
                self.assertEqual((fields[1] & ~1, fields[2]), expected)
        self.assertEqual(
            self.text_relocations,
            [
                (54, 49, ".L.str"),
                (58, 50, ".L.str"),
                (64, 10, "open_cfw_log_format_dispatch"),
                (70, 49, ".L.str.1"),
                (74, 50, ".L.str.1"),
                (80, 10, "open_cfw_log_format_dispatch"),
            ],
        )
        self.assertEqual(
            sorted(
                name
                for name, fields in self.symbols.items()
                if fields[5] == 0
            ),
            ["open_cfw_log_format_dispatch"],
        )

    def test_source_scope_and_eleven_seams_are_explicit(self) -> None:
        source = SOURCE.read_text()
        for token in (
            "sizeof(struct open_cfw_runtime_heap_descriptor) == 28U",
            "open_cfw_runtime_heap_generic_initialize(",
            "open_cfw_runtime_heap_generic_allocate(",
            "open_cfw_runtime_heap_generic_memalign(",
            "open_cfw_runtime_heap_generic_reallocate(",
            "open_cfw_runtime_heap_generic_free(",
            "OPEN_CFW_RUNTIME_HEAP_DIAGNOSTIC(",
            "OPEN_CFW_RUNTIME_HEAP_FATAL()",
            "OPEN_CFW_RUNTIME_HEAP_MUTEX_CREATE(",
            "OPEN_CFW_RUNTIME_HEAP_MUTEX_ACQUIRE(",
            "OPEN_CFW_RUNTIME_HEAP_MUTEX_RELEASE(",
            "OPEN_CFW_RUNTIME_HEAP_TLSF_CREATE_WITH_POOL(",
            "OPEN_CFW_RUNTIME_HEAP_TLSF_BLOCK_SIZE(",
            "OPEN_CFW_RUNTIME_HEAP_TLSF_ALLOCATE(",
            "OPEN_CFW_RUNTIME_HEAP_TLSF_MEMALIGN(",
            "OPEN_CFW_RUNTIME_HEAP_TLSF_REALLOCATE(",
            "OPEN_CFW_RUNTIME_HEAP_TLSF_FREE(",
        ):
            self.assertIn(token, source)
        self.assertNotIn("#include <", source)
        fixture = FIXTURE.read_text()
        self.assertIn("setjmp(", fixture)
        self.assertIn("longjmp(", fixture)
        self.assertIn("runtime_heap_coordinator.c", fixture)


if __name__ == "__main__":
    unittest.main()
