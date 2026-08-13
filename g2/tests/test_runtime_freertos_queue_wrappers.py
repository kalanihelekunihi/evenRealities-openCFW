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
    / "runtime_freertos_queue_wrappers.c"
)
FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_freertos_queue_wrappers_host.c"
)
UPSTREAM_QUEUE = ROOT / "third_party" / "freertos-kernel" / "queue.c"
OFFICIAL = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)

SOURCE_SHA256 = (
    "d70389a03826e97d8e5a5f2a97628764"
    "b9fabd07031dccc42a6b1b241e05fdad"
)
BASE = 0x00438000
STOCK_FUNCTIONS = {
    "mutex_static": (
        0x004416F0,
        0x00441710,
        "2977000da7aab5b87abce1270dca6518"
        "785de04a1e72d08082802713d478fd28",
    ),
    "counting_static": (
        0x00441790,
        0x004417C2,
        "a46100f23dd51b8276a4c2ebafa1ba96"
        "c6813114810ae0f5297764c20368eb62",
    ),
    "counting_dynamic": (
        0x004417C2,
        0x004417EE,
        "ed30ebca04b655b1ec31e60296d97738"
        "2d0712057db88f99b205a555b374120f",
    ),
}
TARGET_FUNCTIONS = {
    "open_cfw_freertos_queue_create_mutex_static": (
        32,
        "86078e5df86e099ad967604a8000b657"
        "8fa3da37a50afff200c32f7101dbf9a2",
    ),
    "open_cfw_freertos_queue_create_counting_semaphore_static": (
        62,
        "01d2ae17612d557af64c37865c4fda8b"
        "278ad8798f6cd4d192af21a38c0ad02c",
    ),
    "open_cfw_freertos_queue_create_counting_semaphore": (
        46,
        "9b3bc9e0c619ec725441ee2f84597071"
        "e0d2746a2f09e918917769b7950adfd8",
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


class RuntimeFreeRTOSQueueWrapperTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)

        library = temporary / (
            "runtime_freertos_queue_wrappers.dylib"
            if sys.platform == "darwin"
            else "runtime_freertos_queue_wrappers.so"
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

        cls.reset = cls.loaded.open_cfw_test_queue_wrapper_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.static_pointer = (
            cls.loaded.open_cfw_test_queue_wrapper_static_pointer
        )
        cls.static_pointer.argtypes = []
        cls.static_pointer.restype = ctypes.c_void_p
        cls.dynamic_pointer = (
            cls.loaded.open_cfw_test_queue_wrapper_dynamic_pointer
        )
        cls.dynamic_pointer.argtypes = []
        cls.dynamic_pointer.restype = ctypes.c_void_p
        cls.messages = cls.loaded.open_cfw_test_queue_wrapper_messages
        cls.messages.argtypes = [ctypes.c_void_p]
        cls.messages.restype = ctypes.c_uint

        cls.mutex_static = (
            cls.loaded.open_cfw_freertos_queue_create_mutex_static
        )
        cls.mutex_static.argtypes = [ctypes.c_uint, ctypes.c_void_p]
        cls.mutex_static.restype = ctypes.c_void_p
        cls.counting_static = (
            cls.loaded
            .open_cfw_freertos_queue_create_counting_semaphore_static
        )
        cls.counting_static.argtypes = [
            ctypes.c_uint,
            ctypes.c_uint,
            ctypes.c_void_p,
        ]
        cls.counting_static.restype = ctypes.c_void_p
        cls.counting_dynamic = (
            cls.loaded.open_cfw_freertos_queue_create_counting_semaphore
        )
        cls.counting_dynamic.argtypes = [ctypes.c_uint, ctypes.c_uint]
        cls.counting_dynamic.restype = ctypes.c_void_p

        cls.target_object = temporary / "queue_wrappers.o"
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
        cls.integration_object = temporary / "queue_wrappers_integrated.o"
        subprocess.run(
            [
                os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                *TARGET_FLAGS,
                "-include",
                str(
                    ROOT
                    / "components"
                    / "apollo_main"
                    / "core_overlay"
                    / "runtime_freertos_queue_create.c"
                ),
                "-c",
                str(SOURCE),
                "-o",
                str(cls.integration_object),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        data, sections = apollo_overlay.parse_elf32(cls.target_object)
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
            name = apollo_overlay.elf_string(strings, fields[0], "symbol")
            cls.parsed_symbols.append((name, fields))
        cls.symbols = {
            name: fields
            for name, fields in cls.parsed_symbols
            if name
        }
        cls.sections = sections
        cls.data = data
        cls.text = apollo_overlay.section_named(sections, ".text")
        cls.target_text = data[
            int(cls.text["offset"]):
            int(cls.text["offset"]) + int(cls.text["size"])
        ]
        cls.relocations = []
        for section in sections:
            if int(section["type"]) != 9:
                continue
            relocated = sections[int(section["info"])]
            for index in range(int(section["size"]) // 8):
                offset, information = struct.unpack_from(
                    "<II",
                    data,
                    int(section["offset"]) + index * 8,
                )
                cls.relocations.append(
                    {
                        "section": relocated["name"],
                        "offset": offset,
                        "type": information & 0xFF,
                        "symbol": cls.parsed_symbols[
                            information >> 8
                        ][0],
                    }
                )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def uint(self, name: str) -> int:
        return ctypes.c_uint.in_dll(self.loaded, name).value

    def ulong(self, name: str) -> int:
        return ctypes.c_ulong.in_dll(self.loaded, name).value

    def set_uint(self, name: str, value: int) -> None:
        ctypes.c_uint.in_dll(self.loaded, name).value = value

    def target_function_bytes(self, name: str) -> bytes:
        (
            _name_offset,
            value,
            size,
            _info,
            _other,
            section_index,
        ) = self.symbols[name]
        section = self.sections[section_index]
        offset = int(section["offset"]) + (value & ~1)
        return self.data[offset:offset + size]

    def test_source_and_official_bodies_are_authenticated(self) -> None:
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            SOURCE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(UPSTREAM_QUEUE.read_bytes()).hexdigest(),
            "5cdf4fa35fe059446effff5bf20deaf83"
            "ddffb08921bc198fda106b1d17dd894",
        )
        for start, end, digest in STOCK_FUNCTIONS.values():
            body = self.application[start - BASE:end - BASE]
            self.assertEqual(hashlib.sha256(body).hexdigest(), digest)
        concatenated = b"".join(
            self.application[start - BASE:end - BASE]
            for start, end, _digest in STOCK_FUNCTIONS.values()
        )
        self.assertEqual(len(concatenated), 126)
        self.assertEqual(
            hashlib.sha256(concatenated).hexdigest(),
            "1d305cd5e6313c35b3489f26b310b416"
            "1252543b882bc6c62e9c55d567523460",
        )

    def test_static_mutex_preserves_byte_type_and_failure_behavior(
        self,
    ) -> None:
        self.reset()
        queue = self.static_pointer()
        self.assertEqual(self.mutex_static(0xABCD0104, queue), queue)
        self.assertEqual(
            self.uint("open_cfw_test_queue_wrapper_static_create_calls"),
            1,
        )
        self.assertEqual(self.uint("open_cfw_test_queue_wrapper_length"), 1)
        self.assertEqual(
            self.uint("open_cfw_test_queue_wrapper_item_size"),
            0,
        )
        self.assertEqual(
            self.uint("open_cfw_test_queue_wrapper_queue_type"),
            4,
        )
        self.assertEqual(
            self.ulong("open_cfw_test_queue_wrapper_storage"),
            0,
        )
        self.assertEqual(
            self.ulong("open_cfw_test_queue_wrapper_static_buffer"),
            queue,
        )
        self.assertEqual(
            self.ulong("open_cfw_test_queue_wrapper_mutex_argument"),
            queue,
        )

        self.reset()
        self.set_uint("open_cfw_test_queue_wrapper_static_succeeds", 0)
        self.assertIsNone(self.mutex_static(1, queue))
        self.assertEqual(
            self.uint(
                "open_cfw_test_queue_wrapper_initialise_mutex_calls"
            ),
            1,
        )
        self.assertEqual(
            self.ulong("open_cfw_test_queue_wrapper_mutex_argument"),
            0,
        )
        self.assertEqual(
            self.uint("open_cfw_test_queue_wrapper_assert_calls"),
            0,
        )

    def test_counting_wrappers_create_and_store_only_after_success(
        self,
    ) -> None:
        self.reset()
        static_queue = self.static_pointer()
        self.assertEqual(
            self.counting_static(7, 5, static_queue),
            static_queue,
        )
        self.assertEqual(self.messages(static_queue), 5)
        self.assertEqual(self.uint("open_cfw_test_queue_wrapper_length"), 7)
        self.assertEqual(
            self.uint("open_cfw_test_queue_wrapper_item_size"),
            0,
        )
        self.assertEqual(
            self.uint("open_cfw_test_queue_wrapper_queue_type"),
            2,
        )

        self.reset()
        before = self.messages(static_queue)
        self.set_uint("open_cfw_test_queue_wrapper_static_succeeds", 0)
        self.assertIsNone(self.counting_static(7, 5, static_queue))
        self.assertEqual(self.messages(static_queue), before)

        self.reset()
        dynamic_queue = self.dynamic_pointer()
        self.assertEqual(
            self.counting_dynamic(9, 9),
            dynamic_queue,
        )
        self.assertEqual(self.messages(dynamic_queue), 9)
        self.assertEqual(
            self.uint("open_cfw_test_queue_wrapper_dynamic_create_calls"),
            1,
        )

        self.reset()
        self.set_uint("open_cfw_test_queue_wrapper_dynamic_succeeds", 0)
        self.assertIsNone(self.counting_dynamic(2, 1))
        self.assertEqual(
            self.uint("open_cfw_test_queue_wrapper_assert_calls"),
            0,
        )

    def test_unsigned_boundaries_and_invalid_dimensions(self) -> None:
        static_queue = self.static_pointer()
        dynamic_queue = self.dynamic_pointer()
        for maximum, initial in (
            (0x80000000, 0x7FFFFFFF),
            (0xFFFFFFFF, 0xFFFFFFFF),
        ):
            self.reset()
            self.assertEqual(
                self.counting_static(maximum, initial, static_queue),
                static_queue,
            )
            self.assertEqual(self.messages(static_queue), initial)
            self.reset()
            self.assertEqual(
                self.counting_dynamic(maximum, initial),
                dynamic_queue,
            )
            self.assertEqual(self.messages(dynamic_queue), initial)

        for maximum, initial in (
            (0, 0),
            (0, 1),
            (4, 5),
            (0x7FFFFFFF, 0x80000000),
        ):
            self.reset()
            self.assertIsNone(
                self.counting_static(maximum, initial, static_queue)
            )
            self.assertEqual(
                self.uint(
                    "open_cfw_test_queue_wrapper_static_create_calls"
                ),
                0,
            )
            self.assertEqual(
                self.uint("open_cfw_test_queue_wrapper_assert_calls"),
                1,
            )
            self.reset()
            self.assertIsNone(self.counting_dynamic(maximum, initial))
            self.assertEqual(
                self.uint(
                    "open_cfw_test_queue_wrapper_dynamic_create_calls"
                ),
                0,
            )
            self.assertEqual(
                self.uint("open_cfw_test_queue_wrapper_assert_calls"),
                1,
            )

    def test_target_output_and_relocations_are_pinned(self) -> None:
        self.assertEqual(len(self.target_text), 142)
        self.assertEqual(
            hashlib.sha256(self.target_text).hexdigest(),
            "d8e4cf8b063bde9cb06c10f1268ef4ad"
            "3a7b0f0f4023e6df19f55598600792c5",
        )
        for name, (expected_size, expected_digest) in (
            TARGET_FUNCTIONS.items()
        ):
            body = self.target_function_bytes(name)
            self.assertEqual(len(body), expected_size)
            self.assertEqual(
                hashlib.sha256(body).hexdigest(),
                expected_digest,
            )

        text_relocations = [
            relocation
            for relocation in self.relocations
            if relocation["section"] == ".text"
        ]
        self.assertEqual(
            [
                (
                    relocation["offset"],
                    relocation["type"],
                    relocation["symbol"],
                )
                for relocation in text_relocations
            ],
            [
                (
                    16,
                    10,
                    "open_cfw_freertos_queue_generic_create_static",
                ),
                (
                    22,
                    10,
                    "open_cfw_freertos_queue_initialise_mutex",
                ),
                (
                    58,
                    10,
                    "open_cfw_freertos_queue_generic_create_static",
                ),
                (
                    110,
                    10,
                    "open_cfw_freertos_queue_generic_create",
                ),
            ],
        )
        self.assertFalse([
            relocation
            for relocation in self.relocations
            if relocation["section"] not in {".text", ".ARM.exidx"}
        ])

        assertion_call = bytes.fromhex("4af2a500c0f25f008047")
        mutex = self.target_function_bytes(
            "open_cfw_freertos_queue_create_mutex_static"
        )
        self.assertIn(bytes.fromhex("c4b2"), mutex)
        self.assertNotIn(assertion_call, mutex)
        self.assertIn(
            assertion_call,
            self.target_function_bytes(
                "open_cfw_freertos_queue_create_counting_semaphore_static"
            ),
        )
        self.assertIn(
            assertion_call,
            self.target_function_bytes(
                "open_cfw_freertos_queue_create_counting_semaphore"
            ),
        )

    def test_source_scope_is_explicit(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        for token in (
            "FreeRTOS Kernel V10.5.1",
            "SPDX-License-Identifier: MIT",
            "def7d2df2b0506d3d249334974f51e427c17a41c",
            "messages_waiting) == 0x38U",
            "0x005FA0A5U",
            "open_cfw_freertos_queue_generic_create_static(",
            "open_cfw_freertos_queue_generic_create(",
            "open_cfw_freertos_queue_initialise_mutex(",
        ):
            self.assertIn(token, source)
        self.assertNotIn("#include <", source)
        self.assertGreater(self.integration_object.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
