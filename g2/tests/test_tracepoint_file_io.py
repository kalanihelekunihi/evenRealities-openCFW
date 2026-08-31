from __future__ import annotations

import os

import ctypes
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
COMPONENT_ROOT = OPENCFW_ROOT / "components" / "apollo_main" / "core_overlay"
SOURCE = COMPONENT_ROOT / "tracepoint_file_io.c"
FIXTURE = OPENCFW_ROOT / "tests" / "fixtures" / "tracepoint_file_io_host.c"
UINT_MASK = (1 << 32) - 1


class TracepointFileIOTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "tracepoint_file_io.dylib"
            if sys.platform == "darwin"
            else "tracepoint_file_io.so"
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

        cls.reset_fixture = cls.loaded.open_cfw_test_tracepoint_io_reset
        cls.reset_fixture.argtypes = []
        cls.reset_fixture.restype = None
        cls.set_handle = cls.loaded.open_cfw_test_tracepoint_io_set_handle
        cls.set_handle.argtypes = [ctypes.c_uint]
        cls.set_handle.restype = None
        cls.has_handle = cls.loaded.open_cfw_test_tracepoint_io_has_handle
        cls.has_handle.argtypes = []
        cls.has_handle.restype = ctypes.c_uint

        cls.close = cls.loaded.open_cfw_tracepoint_active_close
        cls.close.argtypes = []
        cls.close.restype = None
        cls.close_callback = (
            cls.loaded.open_cfw_tracepoint_active_close_callback
        )
        cls.close_callback.argtypes = []
        cls.close_callback.restype = None
        cls.prune = cls.loaded.open_cfw_tracepoint_prune_files
        cls.prune.argtypes = []
        cls.prune.restype = ctypes.c_int
        cls.create = cls.loaded.open_cfw_tracepoint_active_create
        cls.create.argtypes = []
        cls.create.restype = ctypes.c_int
        cls.open_active = cls.loaded.open_cfw_tracepoint_active_open
        cls.open_active.argtypes = []
        cls.open_active.restype = ctypes.c_int
        cls.write = cls.loaded.open_cfw_tracepoint_write
        cls.write.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        cls.write.restype = ctypes.c_int
        cls.commit = cls.loaded.open_cfw_tracepoint_commit
        cls.commit.argtypes = []
        cls.commit.restype = ctypes.c_int
        cls.flush = cls.loaded.open_cfw_tracepoint_flush
        cls.flush.argtypes = []
        cls.flush.restype = ctypes.c_int

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset_fixture()

    @classmethod
    def word(cls, suffix: str) -> ctypes.c_uint:
        return ctypes.c_uint.in_dll(
            cls.loaded,
            f"open_cfw_test_tracepoint_io_{suffix}",
        )

    @classmethod
    def signed_word(cls, suffix: str) -> ctypes.c_int:
        return ctypes.c_int.in_dll(
            cls.loaded,
            f"open_cfw_test_tracepoint_io_{suffix}",
        )

    @classmethod
    def byte(cls, suffix: str) -> ctypes.c_ubyte:
        return ctypes.c_ubyte.in_dll(
            cls.loaded,
            f"open_cfw_test_tracepoint_io_{suffix}",
        )

    @classmethod
    def text(cls, suffix: str, capacity: int) -> str:
        value = (ctypes.c_char * capacity).in_dll(
            cls.loaded,
            f"open_cfw_test_tracepoint_io_{suffix}",
        )
        return bytes(value).split(b"\0", 1)[0].decode()

    @classmethod
    def events(cls) -> list[int]:
        count = cls.word("event_count").value
        values = (ctypes.c_uint * 64).in_dll(
            cls.loaded,
            "open_cfw_test_tracepoint_io_events",
        )
        return list(values[:count])

    @classmethod
    def removed_path(cls, slot: int) -> str:
        table = ((ctypes.c_char * 96) * 8).in_dll(
            cls.loaded,
            "open_cfw_test_tracepoint_io_removed_paths",
        )
        return bytes(table[slot]).split(b"\0", 1)[0].decode()

    @classmethod
    def write_sizes(cls) -> list[int]:
        count = cls.word("write_calls").value
        values = (ctypes.c_uint * 8).in_dll(
            cls.loaded,
            "open_cfw_test_tracepoint_io_write_sizes",
        )
        return list(values[:count])

    @classmethod
    def write_data(cls, slot: int, size: int) -> bytes:
        table = ((ctypes.c_ubyte * 128) * 8).in_dll(
            cls.loaded,
            "open_cfw_test_tracepoint_io_write_data",
        )
        return bytes(table[slot][:size])

    def test_close_and_callback_clear_only_a_live_handle(self) -> None:
        self.signed_word("close_result").value = -9
        self.close()
        self.assertEqual(self.word("close_calls").value, 0)

        self.set_handle(1)
        self.close()
        self.assertEqual(self.word("close_calls").value, 1)
        self.assertEqual(self.has_handle(), 0)

        self.close_callback()
        self.assertEqual(self.word("close_calls").value, 1)
        self.set_handle(1)
        self.close_callback()
        self.assertEqual(self.word("close_calls").value, 2)
        self.assertEqual(self.has_handle(), 0)

    def test_prune_rescans_and_removes_minimum_until_three_remain(
        self,
    ) -> None:
        self.word("scan_count").value = 5
        self.word("scan_minimum").value = 2
        self.word("scan_maximum").value = 9
        self.assertEqual(self.prune(), 0)
        self.assertEqual(self.word("scan_calls").value, 3)
        self.assertEqual(self.word("remove_calls").value, 2)
        self.assertEqual(
            (self.removed_path(0), self.removed_path(1)),
            ("/log/tp/tp_2.bin", "/log/tp/tp_3.bin"),
        )
        self.assertEqual(
            self.events(),
            [1, 2, 3, 1, 2, 3, 1],
        )

    def test_prune_preserves_scan_and_remove_error_policies(self) -> None:
        self.word("scan_count").value = UINT_MASK
        self.assertEqual(self.prune(), 0)
        self.assertEqual(self.word("remove_calls").value, 0)

        self.setUp()
        self.signed_word("scan_result").value = -7
        self.assertEqual(self.prune(), -7)
        self.assertEqual(self.word("format_calls").value, 0)

        self.setUp()
        self.word("scan_count").value = 4
        self.word("scan_minimum").value = 11
        self.signed_word("remove_result").value = -1
        self.assertEqual(self.prune(), -5)
        self.assertEqual(self.removed_path(0), "/log/tp/tp_11.bin")
        self.assertEqual(self.word("scan_calls").value, 1)

    def test_create_advances_persists_and_writes_exact_header(self) -> None:
        self.word("sequence").value = 0x11223344
        self.word("next_index").value = 7
        self.assertEqual(self.create(), 0)
        self.assertEqual(self.word("next_index").value, 8)
        self.assertEqual(self.word("persist_calls").value, 1)
        self.assertEqual(self.text("last_path", 96), "/log/tp/tp_7.bin")
        self.assertEqual(self.text("last_mode", 8), "wb")
        self.assertEqual(self.word("header_calls").value, 1)
        self.assertEqual(self.word("header_index").value, 7)
        self.assertEqual(self.word("header_sequence").value, 0x11223344)
        self.assertEqual(self.write_sizes(), [32])
        self.assertEqual(
            self.write_data(0, 32),
            bytes(range(0xA0, 0xC0)),
        )
        self.assertEqual(self.word("active_index").value, 7)
        self.assertEqual(self.word("active_size").value, 32)
        self.assertEqual(self.has_handle(), 1)
        self.assertEqual(self.events(), [1, 4, 2, 5, 6, 7])

    def test_create_failure_side_effects_match_stock_order(self) -> None:
        self.word("next_index").value = 4
        self.signed_word("scan_result").value = -8
        self.assertEqual(self.create(), -8)
        self.assertEqual(self.word("next_index").value, 4)
        self.assertEqual(self.word("persist_calls").value, 0)

        self.setUp()
        self.word("next_index").value = 4
        self.signed_word("persist_result").value = -6
        self.assertEqual(self.create(), -6)
        self.assertEqual(self.word("next_index").value, 5)
        self.assertEqual(self.word("open_calls").value, 0)

        self.setUp()
        self.word("next_index").value = 4
        self.word("open_fail").value = 1
        self.assertEqual(self.create(), -5)
        self.assertEqual(self.word("next_index").value, 5)
        self.assertEqual(self.word("header_calls").value, 0)
        self.assertEqual(self.has_handle(), 0)

        self.setUp()
        self.word("active_index").value = 0xA5A5A5A5
        self.word("active_size").value = 0x5A5A5A5A
        self.word("write_result_first").value = 31
        self.assertEqual(self.create(), -5)
        self.assertEqual(self.word("close_calls").value, 1)
        self.assertEqual(self.has_handle(), 0)
        self.assertEqual(self.word("active_index").value, 0xA5A5A5A5)
        self.assertEqual(self.word("active_size").value, 0x5A5A5A5A)

    def test_active_open_uses_saved_index_and_append_mode(self) -> None:
        self.word("active_index").value = 19
        self.assertEqual(self.open_active(), 0)
        self.assertEqual(self.text("last_path", 96), "/log/tp/tp_19.bin")
        self.assertEqual(self.text("last_mode", 8), "ab")
        self.assertEqual(self.has_handle(), 1)

        self.setUp()
        self.word("active_index").value = 20
        self.word("open_fail").value = 1
        self.assertEqual(self.open_active(), -5)
        self.assertEqual(self.has_handle(), 0)

    def test_write_reopens_existing_file_and_preserves_short_failure(
        self,
    ) -> None:
        payload = ctypes.create_string_buffer(b"xyz")
        self.word("active_index").value = 4
        self.word("active_size").value = 100
        self.assertEqual(self.write(payload, 3), 0)
        self.assertEqual(self.text("last_mode", 8), "ab")
        self.assertEqual(self.write_sizes(), [3])
        self.assertEqual(self.write_data(0, 3), b"xyz")
        self.assertEqual(self.word("active_size").value, 103)
        self.assertEqual(self.events(), [2, 5, 7])

        self.setUp()
        self.set_handle(1)
        self.word("active_index").value = 4
        self.word("active_size").value = 100
        self.word("write_result_first").value = 2
        self.assertEqual(self.write(payload, 3), -5)
        self.assertEqual(self.word("close_calls").value, 1)
        self.assertEqual(self.has_handle(), 0)
        self.assertEqual(self.word("active_index").value, 4)
        self.assertEqual(self.word("active_size").value, 100)

    def test_write_rotates_at_limit_and_uses_unsigned_wrap(self) -> None:
        payload = ctypes.create_string_buffer(b"abcde")
        self.set_handle(1)
        self.word("active_index").value = 4
        self.word("active_size").value = 0x8000
        self.word("next_index").value = 9
        self.word("sequence").value = 3
        self.assertEqual(self.write(payload, 5), 0)
        self.assertEqual(self.word("close_calls").value, 1)
        self.assertEqual(self.word("next_index").value, 10)
        self.assertEqual(self.word("active_index").value, 9)
        self.assertEqual(self.word("active_size").value, 37)
        self.assertEqual(self.write_sizes(), [32, 5])
        self.assertEqual(self.events(), [8, 1, 4, 2, 5, 6, 7, 7])

        self.setUp()
        self.set_handle(1)
        self.word("active_index").value = 4
        self.word("active_size").value = 0x7FFD
        self.assertEqual(self.write(payload, 3), 0)
        self.assertEqual(self.word("close_calls").value, 0)
        self.assertEqual(self.word("active_size").value, 0x8000)

        self.setUp()
        self.set_handle(1)
        self.word("active_index").value = 4
        self.word("active_size").value = UINT_MASK
        self.assertEqual(self.write(payload, 2), 0)
        self.assertEqual(self.word("close_calls").value, 0)
        self.assertEqual(self.word("active_size").value, 1)

    def test_write_requires_storage_initialization(self) -> None:
        payload = ctypes.create_string_buffer(b"x")
        self.byte("initialized").value = 0
        self.assertEqual(self.write(payload, 1), -2)
        self.assertEqual(self.events(), [])

    def test_commit_closes_only_nonempty_active_data_files(self) -> None:
        self.byte("initialized").value = 0
        self.word("active_index").value = 3
        self.word("active_size").value = 33
        self.set_handle(1)
        self.assertEqual(self.commit(), -2)
        self.assertEqual(self.has_handle(), 1)

        self.setUp()
        self.word("active_index").value = 0
        self.word("active_size").value = 99
        self.set_handle(1)
        self.assertEqual(self.commit(), 0)
        self.assertEqual(self.has_handle(), 1)

        self.word("active_index").value = 3
        self.word("active_size").value = 32
        self.assertEqual(self.commit(), 0)
        self.assertEqual(self.has_handle(), 1)

        self.word("active_size").value = 33
        self.assertEqual(self.commit(), 0)
        self.assertEqual(self.word("close_calls").value, 1)
        self.assertEqual(self.has_handle(), 0)
        self.assertEqual(self.word("active_index").value, 0)
        self.assertEqual(self.word("active_size").value, 0)

    def test_flush_is_noop_without_handle_and_propagates_result(self) -> None:
        self.signed_word("flush_result").value = -7
        self.assertEqual(self.flush(), 0)
        self.assertEqual(self.word("flush_calls").value, 0)

        self.set_handle(1)
        self.assertEqual(self.flush(), -7)
        self.assertEqual(self.word("flush_calls").value, 1)
        self.assertEqual(self.has_handle(), 1)

    def test_sources_are_review_pinned(self) -> None:
        expected = {
            SOURCE:
                "b0df208f0d6cb5b463695b319aaac0dc0b2a4500467a67ed94f5b78350a18cb7",
            FIXTURE:
                "432b33daeba71a157f5f1d46f1df73781256b4ad39661df24858b8788a8659bb",
        }
        for path, digest in expected.items():
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(),
                digest,
            )


if __name__ == "__main__":
    unittest.main()
