from __future__ import annotations

import os

import binascii
import ctypes
import hashlib
import random
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
COMPONENT_ROOT = OPENCFW_ROOT / "components" / "apollo_main" / "core_overlay"
SOURCE = COMPONENT_ROOT / "tracepoint_storage.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "tracepoint_storage_host.c"
UINT_MASK = (1 << 32) - 1


class DirectoryStats(ctypes.Structure):
    _fields_ = [
        ("count", ctypes.c_uint),
        ("minimum_index", ctypes.c_uint),
        ("maximum_index", ctypes.c_uint),
    ]


class TracepointStorageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "tracepoint_storage.dylib"
            if sys.platform == "darwin"
            else "tracepoint_storage.so"
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

        cls.reset_fixture = (
            cls.loaded.open_cfw_test_tracepoint_storage_reset
        )
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.set_entry = (
            cls.loaded.open_cfw_test_tracepoint_storage_set_entry
        )
        cls.set_entry.argtypes = [
            ctypes.c_uint,
            ctypes.c_char_p,
            ctypes.c_uint,
        ]
        cls.set_entry.restype = None

        cls.crc = cls.loaded.open_cfw_tracepoint_state_crc32
        cls.crc.argtypes = [ctypes.c_void_p]
        cls.crc.restype = ctypes.c_uint
        cls.path_format = cls.loaded.open_cfw_tracepoint_path_format
        cls.path_format.argtypes = [
            ctypes.c_char_p,
            ctypes.c_uint,
            ctypes.c_uint,
        ]
        cls.path_format.restype = None
        cls.path_parse = cls.loaded.open_cfw_tracepoint_path_parse
        cls.path_parse.argtypes = [
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_uint),
        ]
        cls.path_parse.restype = ctypes.c_uint
        cls.file_size = cls.loaded.open_cfw_tracepoint_file_size
        cls.file_size.argtypes = [ctypes.c_char_p]
        cls.file_size.restype = ctypes.c_int
        cls.directory_scan = (
            cls.loaded.open_cfw_tracepoint_directory_scan
        )
        cls.directory_scan.argtypes = [ctypes.POINTER(DirectoryStats)]
        cls.directory_scan.restype = ctypes.c_int
        cls.persist = cls.loaded.open_cfw_tracepoint_state_persist
        cls.persist.argtypes = []
        cls.persist.restype = ctypes.c_int
        cls.load = cls.loaded.open_cfw_tracepoint_state_load
        cls.load.argtypes = []
        cls.load.restype = None
        cls.initialize = (
            cls.loaded.open_cfw_tracepoint_storage_initialize
        )
        cls.initialize.argtypes = []
        cls.initialize.restype = ctypes.c_int

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def word(cls, suffix: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_tracepoint_storage_{suffix}",
        )

    @classmethod
    def signed_word(cls, suffix: str) -> ctypes.c_int:
        return ctypes.c_int.in_dll(
            cls.loaded,
            f"open_cfw_test_tracepoint_storage_{suffix}",
        )

    @classmethod
    def byte(cls, suffix: str) -> ctypes.c_ubyte:
        return ctypes.c_ubyte.in_dll(
            cls.loaded,
            f"open_cfw_test_tracepoint_storage_{suffix}",
        )

    @classmethod
    def state_bytes(cls) -> ctypes.Array[ctypes.c_ubyte]:
        return (ctypes.c_ubyte * 16).in_dll(
            cls.loaded,
            "open_cfw_test_tracepoint_storage_state",
        )

    @classmethod
    def text(cls, suffix: str, capacity: int = 96) -> str:
        value = (ctypes.c_char * capacity).in_dll(
            cls.loaded,
            f"open_cfw_test_tracepoint_storage_{suffix}",
        )
        return bytes(value).split(b"\0", 1)[0].decode()

    def set_state_record(
        self,
        *,
        magic: int = 0x31535054,
        sequence: int,
        next_index: int,
        checksum: int | None = None,
    ) -> None:
        first = struct.pack(
            "<III",
            magic & UINT_MASK,
            sequence & UINT_MASK,
            next_index & UINT_MASK,
        )
        if checksum is None:
            checksum = binascii.crc32(first) & UINT_MASK
        self.state_bytes()[:] = first + struct.pack("<I", checksum)
        self.word("state_exists").value = 1

    def test_crc32_matches_standard_reflected_model(self) -> None:
        rng = random.Random(0x47DDFE)
        for payload in (
            bytes(12),
            b"TPS1" + bytes(8),
            bytes(range(12)),
            *(
                bytes(rng.randrange(256) for _ in range(12))
                for _ in range(500)
            ),
        ):
            buffer = ctypes.create_string_buffer(payload)
            self.assertEqual(
                self.crc(buffer),
                binascii.crc32(payload) & UINT_MASK,
            )

    def test_path_format_and_parser_preserve_exact_filename_grammar(
        self,
    ) -> None:
        buffer = ctypes.create_string_buffer(64)
        self.path_format(buffer, len(buffer), 4294967295)
        self.assertEqual(
            buffer.value,
            b"/log/tp/tp_4294967295.bin",
        )

        for name, accepted, expected in (
            (b"tp_0.bin", 1, 0),
            (b"tp_42.bin", 1, 42),
            (b"tp_0007.bin", 1, 7),
            (b"tp_.bin", 0, 0),
            (b"xp_7.bin", 0, 0),
            (b"tp_7.dat", 0, 0),
            (b"tp_7.bin.extra", 0, 0),
            (b"tp_7x.bin", 0, 0),
        ):
            output = ctypes.c_uint(0xA5A5A5A5)
            self.assertEqual(
                self.path_parse(name, ctypes.byref(output)),
                accepted,
            )
            self.assertEqual(
                output.value,
                expected if accepted else 0xA5A5A5A5,
            )

    def test_file_size_closes_every_opened_path_and_normalizes_failures(
        self,
    ) -> None:
        self.word("active_open_fail").value = 1
        self.assertEqual(self.file_size(b"/log/tp/tp_1.bin"), 0)
        self.assertEqual(self.word("close_calls").value, 0)

        self.setUp()
        self.signed_word("seek_result").value = -1
        self.signed_word("tell_result").value = 99
        self.assertEqual(self.file_size(b"/log/tp/tp_1.bin"), 0)
        self.assertEqual(self.word("tell_calls").value, 0)
        self.assertEqual(self.word("close_calls").value, 1)

        for observed, expected in ((-1, 0), (0, 0), (1, 1), (32767, 32767)):
            self.setUp()
            self.signed_word("tell_result").value = observed
            self.assertEqual(
                self.file_size(b"/log/tp/tp_9.bin"),
                expected,
            )
            self.assertEqual(self.word("seek_calls").value, 1)
            self.assertEqual(self.word("tell_calls").value, 1)
            self.assertEqual(self.word("close_calls").value, 1)
            self.assertEqual(self.text("last_mode", 8), "rb")

    def test_directory_scan_filters_and_tracks_unsigned_extrema(
        self,
    ) -> None:
        for slot, name, entry_type in (
            (0, b"tp_9.bin", 8),
            (1, b"tp_2.bin", 8),
            (2, b"tp_99.dat", 8),
            (3, b"tp_1.bin", 4),
            (4, b"tp_15.bin", 8),
        ):
            self.set_entry(slot, name, entry_type)
        stats = DirectoryStats(99, 99, 99)
        self.assertEqual(self.directory_scan(ctypes.byref(stats)), 0)
        self.assertEqual(
            (stats.count, stats.minimum_index, stats.maximum_index),
            (3, 2, 15),
        )
        self.assertEqual(self.word("closedir_calls").value, 1)

        self.setUp()
        self.word("opendir_fail").value = 1
        stats = DirectoryStats(99, 99, 99)
        self.assertEqual(self.directory_scan(ctypes.byref(stats)), -5)
        self.assertEqual(
            (stats.count, stats.minimum_index, stats.maximum_index),
            (0, UINT_MASK, 0),
        )
        self.assertEqual(self.word("closedir_calls").value, 0)

    def test_state_persist_emits_exact_record_and_error_policy(self) -> None:
        self.word("sequence").value = 0x11223344
        self.word("next_index").value = 0x89ABCDEF
        self.assertEqual(self.persist(), 0)
        record = bytes(self.state_bytes())
        self.assertEqual(
            record[:12],
            struct.pack("<III", 0x31535054, 0x11223344, 0x89ABCDEF),
        )
        self.assertEqual(
            struct.unpack_from("<I", record, 12)[0],
            binascii.crc32(record[:12]) & UINT_MASK,
        )
        self.assertEqual(self.text("last_mode", 8), "wb")
        self.assertEqual(self.word("close_calls").value, 1)

        self.setUp()
        self.word("state_write_open_fail").value = 1
        self.assertEqual(self.persist(), -5)
        self.assertEqual(self.word("write_calls").value, 0)

        self.setUp()
        self.word("write_result").value = 15
        self.assertEqual(self.persist(), -5)
        self.assertEqual(self.word("close_calls").value, 1)

    def test_state_load_validates_then_normalizes_next_index(self) -> None:
        for stored, expected in ((0, 1), (1, 1), (2, 2), (99, 99)):
            self.setUp()
            self.word("sequence").value = 7
            self.word("next_index").value = 8
            self.set_state_record(sequence=0x55667788, next_index=stored)
            self.load()
            self.assertEqual(self.word("sequence").value, 0x55667788)
            self.assertEqual(self.word("next_index").value, expected)
            self.assertEqual(self.word("close_calls").value, 1)

        for mutation in ("short", "magic", "checksum"):
            self.setUp()
            self.word("sequence").value = 7
            self.word("next_index").value = 8
            self.set_state_record(sequence=99, next_index=100)
            if mutation == "short":
                self.word("read_result").value = 15
            elif mutation == "magic":
                self.state_bytes()[0] ^= 1
            else:
                self.state_bytes()[15] ^= 1
            self.load()
            self.assertEqual(self.word("sequence").value, 7)
            self.assertEqual(self.word("next_index").value, 8)

    def test_initialize_scans_advances_and_persists_state(self) -> None:
        self.word("sequence").value = 10
        self.word("next_index").value = 2
        self.signed_word("tell_result").value = 100
        self.set_entry(0, b"tp_3.bin", 8)
        self.set_entry(1, b"tp_7.bin", 8)
        self.set_entry(2, b"unrelated", 8)

        self.assertEqual(self.initialize(), 0)
        self.assertEqual(self.word("sequence").value, 11)
        self.assertEqual(self.word("next_index").value, 8)
        self.assertEqual(self.word("active_index").value, 7)
        self.assertEqual(self.word("active_size").value, 100)
        self.assertEqual(self.byte("initialized").value, 1)
        self.assertEqual(
            self.text("last_formatted_path"),
            "/log/tp/tp_7.bin",
        )
        record = bytes(self.state_bytes())
        self.assertEqual(
            struct.unpack_from("<III", record),
            (0x31535054, 11, 8),
        )

        prior_counts = (
            self.word("mkdir_calls").value,
            self.word("opendir_calls").value,
            self.word("write_calls").value,
        )
        self.assertEqual(self.initialize(), 0)
        self.assertEqual(
            (
                self.word("mkdir_calls").value,
                self.word("opendir_calls").value,
                self.word("write_calls").value,
            ),
            prior_counts,
        )

    def test_initialize_preserves_failure_and_active_size_boundaries(
        self,
    ) -> None:
        self.word("sequence").value = UINT_MASK
        self.word("opendir_fail").value = 1
        self.assertEqual(self.initialize(), -5)
        self.assertEqual(self.word("sequence").value, 0)
        self.assertEqual(self.byte("initialized").value, 0)
        self.assertEqual(self.word("write_calls").value, 0)

        for size, accepted in (
            (31, False),
            (32, True),
            (32767, True),
            (32768, False),
        ):
            self.setUp()
            self.word("active_index").value = 0xA5A5A5A5
            self.word("active_size").value = 0x5A5A5A5A
            self.signed_word("tell_result").value = size
            self.set_entry(0, b"tp_4.bin", 8)
            self.assertEqual(self.initialize(), 0)
            self.assertEqual(
                self.word("active_index").value,
                4 if accepted else 0xA5A5A5A5,
            )
            self.assertEqual(
                self.word("active_size").value,
                size if accepted else 0x5A5A5A5A,
            )

    def test_sources_are_review_pinned(self) -> None:
        expected = {
            SOURCE:
                "35a95dd68538fa456fc932cb9166614f"
                "303e6797ef4a328ee00463076cee9945",
            FIXTURE:
                "12a20358d9486cd5141c30fec443009a0"
                "22dc03265c4919114b6b595cf3cb1f0",
        }
        for path, digest in expected.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                digest,
            )


if __name__ == "__main__":
    unittest.main()
