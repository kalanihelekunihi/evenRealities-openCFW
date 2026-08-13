from __future__ import annotations

import ctypes
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/shared/nanopb/runtime_nanopb_field_decoder_cluster.c"
INCLUDE = SOURCE.parent
HARNESS = ROOT / "tests/fixtures/runtime_nanopb_field_decoder_cluster_host.c"
HEADER = INCLUDE / "runtime_nanopb_field_decoder_cluster.h"
ANALYZER = ROOT / "tools/analyze_g2_nanopb_field_decoder_cluster.py"
PINS = {
    SOURCE: (14_057, "6c34245f6d3c305499ffb6be2bae69508fe6c6f4c4b79e8306d3b998f84c9901"),
    HEADER: (888, "812560e152e879f3181bcb20a2b65b0a6c81673aa4bebe46ff3bb6c99de1a8ac"),
    HARNESS: (9_211, "c3fee7a4ff21332c33629d63fb003c45de8b37cdbb026dc2f8a78ea57d9d2682"),
}


class NanopbFieldDecoderClusterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library_path = Path(cls.temporary.name) / "field_decoder_cluster.so"
        subprocess.run(
            [
                os.environ.get("CC", "cc"), "-std=c11", "-shared", "-fPIC",
                "-O2", "-Wall", "-Wextra", "-Werror", f"-I{INCLUDE}",
                str(SOURCE), str(HARNESS), "-o", str(library_path),
            ],
            check=True,
            cwd=ROOT,
        )
        cls.library = ctypes.CDLL(str(library_path))
        cls.library.open_cfw_test_basic.argtypes = [ctypes.c_uint, ctypes.c_uint]
        cls.library.open_cfw_test_basic.restype = ctypes.c_bool
        cls.library.open_cfw_test_static_optional.restype = ctypes.c_bool
        cls.library.open_cfw_test_static_packed.argtypes = [ctypes.c_uint, ctypes.c_uint]
        cls.library.open_cfw_test_static_packed.restype = ctypes.c_bool
        cls.library.open_cfw_test_static_repeated.argtypes = [ctypes.c_uint, ctypes.c_uint]
        cls.library.open_cfw_test_static_repeated.restype = ctypes.c_bool
        cls.library.open_cfw_test_static_oneof.argtypes = [ctypes.c_uint]
        cls.library.open_cfw_test_static_oneof.restype = ctypes.c_bool
        cls.library.open_cfw_test_pointer.restype = ctypes.c_bool
        cls.library.open_cfw_test_callback.argtypes = [ctypes.c_uint, ctypes.c_uint]
        cls.library.open_cfw_test_callback.restype = ctypes.c_bool
        cls.library.open_cfw_test_fixed_length.argtypes = [ctypes.c_uint, ctypes.c_uint]
        cls.library.open_cfw_test_fixed_length.restype = ctypes.c_bool
        for name in (
            "called", "callback_calls", "skip_calls", "defaults_calls",
            "iterator_calls", "field_size", "stream_left",
        ):
            getattr(cls.library, f"open_cfw_test_{name}").restype = ctypes.c_uint
        cls.library.open_cfw_test_error.restype = ctypes.c_char_p
        cls.library.open_cfw_test_storage.restype = ctypes.POINTER(ctypes.c_uint8)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.library.open_cfw_test_reset()

    def storage(self, count: int = 8) -> bytes:
        return bytes(self.library.open_cfw_test_storage()[:count])

    def test_source_header_and_host_oracle_are_pinned(self) -> None:
        for path, expected in PINS.items():
            with self.subTest(path=path.name):
                data = path.read_bytes()
                self.assertEqual((len(data), hashlib.sha256(data).hexdigest()), expected)

    def test_basic_dispatch_routes_all_supported_logical_types(self) -> None:
        expected = {
            0: (0, 1),
            1: (0, 2),
            2: (0, 2),
            3: (0, 2),
            4: (5, 3),
            5: (1, 4),
            6: (2, 5),
            7: (2, 6),
            8: (2, 7),
            9: (2, 7),
        }
        for logical_type, (wire_type, called) in expected.items():
            with self.subTest(logical_type=logical_type):
                self.library.open_cfw_test_reset()
                self.assertTrue(self.library.open_cfw_test_basic(logical_type, wire_type))
                self.assertEqual(self.library.open_cfw_test_called(), called)
                self.assertEqual(self.library.open_cfw_test_stream_left(), 15)

    def test_basic_rejects_wrong_wire_and_unknown_logical_type(self) -> None:
        self.assertFalse(self.library.open_cfw_test_basic(4, 0))
        self.assertEqual(self.library.open_cfw_test_error(), b"wrong wire type")

        self.library.open_cfw_test_reset()
        self.assertFalse(self.library.open_cfw_test_basic(10, 0))
        self.assertEqual(self.library.open_cfw_test_error(), b"invalid field type")

    def test_optional_packed_and_repeated_static_paths(self) -> None:
        self.assertTrue(self.library.open_cfw_test_static_optional())
        self.assertEqual(self.library.open_cfw_test_called(), 1)

        self.library.open_cfw_test_reset()
        self.assertTrue(self.library.open_cfw_test_static_packed(3, 4))
        self.assertEqual(self.library.open_cfw_test_field_size(), 3)

        self.library.open_cfw_test_reset()
        self.assertFalse(self.library.open_cfw_test_static_packed(5, 4))
        self.assertEqual(self.library.open_cfw_test_field_size(), 4)
        self.assertEqual(self.library.open_cfw_test_error(), b"array overflow")

        self.library.open_cfw_test_reset()
        self.assertTrue(self.library.open_cfw_test_static_repeated(2, 4))
        self.assertEqual(self.library.open_cfw_test_field_size(), 3)

        self.library.open_cfw_test_reset()
        self.assertFalse(self.library.open_cfw_test_static_repeated(4, 4))
        self.assertEqual(self.library.open_cfw_test_field_size(), 5)
        self.assertEqual(self.library.open_cfw_test_error(), b"array overflow")

    def test_oneof_reinitializes_changed_submessage_and_propagates_failure(self) -> None:
        self.assertTrue(self.library.open_cfw_test_static_oneof(0))
        self.assertEqual(self.library.open_cfw_test_iterator_calls(), 1)
        self.assertEqual(self.library.open_cfw_test_defaults_calls(), 1)
        self.assertEqual(self.library.open_cfw_test_field_size(), 7)
        self.assertEqual(self.storage(4), b"\0\0\0\0")

        self.library.open_cfw_test_reset()
        self.assertFalse(self.library.open_cfw_test_static_oneof(5))
        self.assertEqual(self.library.open_cfw_test_error(), b"failed to set defaults")
        self.assertEqual(self.library.open_cfw_test_field_size(), 1)

    def test_no_malloc_pointer_path_is_fail_closed(self) -> None:
        self.assertFalse(self.library.open_cfw_test_pointer())
        self.assertEqual(self.library.open_cfw_test_error(), b"no malloc support")

    def test_callback_skip_progress_and_error_paths(self) -> None:
        self.assertTrue(self.library.open_cfw_test_callback(0, 0))
        self.assertEqual(self.library.open_cfw_test_skip_calls(), 1)

        self.library.open_cfw_test_reset()
        self.assertTrue(self.library.open_cfw_test_callback(1, 2))
        self.assertEqual(self.library.open_cfw_test_callback_calls(), 3)

        self.library.open_cfw_test_reset()
        self.assertTrue(self.library.open_cfw_test_callback(4, 2))
        self.assertEqual(self.library.open_cfw_test_callback_calls(), 1)

        self.library.open_cfw_test_reset()
        self.assertFalse(self.library.open_cfw_test_callback(2, 2))
        self.assertEqual(self.library.open_cfw_test_error(), b"callback detail")

        self.library.open_cfw_test_reset()
        self.assertFalse(self.library.open_cfw_test_callback(3, 2))
        self.assertEqual(self.library.open_cfw_test_error(), b"callback failed")

        self.library.open_cfw_test_reset()
        self.assertTrue(self.library.open_cfw_test_callback(1, 0))
        self.assertEqual(self.library.open_cfw_test_callback_calls(), 1)
        self.assertEqual(self.library.open_cfw_test_stream_left(), 0)

    def test_fixed_length_zero_exact_mismatch_and_overflow(self) -> None:
        self.assertTrue(self.library.open_cfw_test_fixed_length(0, 4))
        self.assertEqual(self.storage(8), b"\0\0\0\0\xA5\xA5\xA5\xA5")

        self.library.open_cfw_test_reset()
        self.assertTrue(self.library.open_cfw_test_fixed_length(4, 4))
        self.assertEqual(self.storage(6), b"\x01\x02\x03\x04\xA5\xA5")
        self.assertEqual(self.library.open_cfw_test_stream_left(), 28)

        self.library.open_cfw_test_reset()
        self.assertFalse(self.library.open_cfw_test_fixed_length(3, 4))
        self.assertEqual(
            self.library.open_cfw_test_error(),
            b"incorrect fixed length bytes size",
        )

        self.library.open_cfw_test_reset()
        self.assertFalse(self.library.open_cfw_test_fixed_length(65_536, 4))
        self.assertEqual(self.library.open_cfw_test_error(), b"bytes overflow")

    def test_target_selectors_have_closed_relocation_shapes(self) -> None:
        expected = {
            0: (
                "open_cfw_nanopb_dec_varint",
                "open_cfw_nanopb_dec_submessage",
                "open_cfw_nanopb_dec_string",
                "open_cfw_nanopb_decode_fixed64",
                "open_cfw_nanopb_dec_fixed_length_bytes",
                "open_cfw_nanopb_dec_bool",
                "open_cfw_nanopb_dec_bytes",
                "open_cfw_nanopb_decode_fixed32",
            ),
            1: (
                "open_cfw_nanopb_decode_basic_field",
                "open_cfw_nanopb_make_string_substream",
                "open_cfw_nanopb_decode_basic_field",
                "open_cfw_nanopb_close_string_substream",
                "open_cfw_nanopb_field_iter_begin",
                "open_cfw_nanopb_message_set_to_defaults",
                "open_cfw_nanopb_decode_basic_field",
            ),
            2: (),
            3: (
                "open_cfw_nanopb_make_string_substream",
                "open_cfw_nanopb_close_string_substream",
                "open_cfw_nanopb_skip_field",
                "open_cfw_nanopb_read_raw_value",
                "open_cfw_nanopb_istream_from_buffer",
            ),
            4: (
                "open_cfw_nanopb_decode_varint32",
                "open_cfw_nanopb_read",
            ),
        }
        with tempfile.TemporaryDirectory() as raw:
            directory = Path(raw)
            for selector, symbols in expected.items():
                with self.subTest(selector=selector):
                    object_path = directory / f"selector-{selector}.o"
                    completed = subprocess.run(
                        [
                            "/usr/bin/clang", "--target=thumbv7em-none-eabi",
                            "-mthumb", "-O2", "-ffreestanding", "-fno-jump-tables",
                            "-fomit-frame-pointer", "-fno-builtin",
                            "-mno-unaligned-access", "-fno-unwind-tables",
                            "-fno-asynchronous-unwind-tables", "-fropi",
                            "-ffunction-sections", "-fdata-sections", "-Wall",
                            "-Wextra", "-Werror", "-fno-ident",
                            f"-DOPEN_CFW_NANOPB_FIELD_DECODER_SELECTION={selector}",
                            f"-I{INCLUDE}", "-c", str(SOURCE), "-o", str(object_path),
                        ],
                        check=False,
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(completed.returncode, 0, completed.stderr)
                    relocations = subprocess.run(
                        ["/usr/bin/objdump", "-r", str(object_path)],
                        check=True,
                        capture_output=True,
                        text=True,
                    ).stdout
                    observed = tuple(
                        line.split()[-1]
                        for line in relocations.splitlines()
                        if "R_ARM_THM_CALL" in line or "R_ARM_THM_JUMP24" in line
                    )
                    self.assertEqual(observed, symbols)

    def test_analyzer_closes_all_entries_dependencies_and_collision_classes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(ANALYZER), "--json"],
            check=True,
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        report = json.loads(completed.stdout)
        self.assertEqual(
            [item["size"] for item in report["stock"]["segments"]],
            [372, 436, 20, 180, 108],
        )
        self.assertEqual(len(report["outgoing"]), 26)
        self.assertEqual(len(report["diagnostics"]), 8)
        self.assertEqual(len(report["dynamic_callbacks"]), 2)
        self.assertEqual(report["stored_patterns"]["count"], 47)
        self.assertEqual(report["decision"]["fixed_stock_seams_in_candidate"], 0)
        self.assertEqual(report["decision"]["stored_pointer_ingress"], 0)
        self.assertEqual(report["decision"]["alternate_executable_ingress"], 0)
        self.assertTrue(report["decision"]["production_candidate"])
        self.assertTrue(report["decision"]["production_integrated"])
        self.assertEqual(
            report["production_candidate"]["leaf_offsets"],
            [128_924, 129_144, 129_392, 129_840, 129_884],
        )


if __name__ == "__main__":
    unittest.main()
