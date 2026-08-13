import ctypes
import hashlib
import platform
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/kvdb_module_configure.c"
FIXTURE = ROOT / "tests/fixtures"
EXPECTED_SYMBOLS = {
    "open_cfw_kvdb_read_language",
    "open_cfw_kvdb_write_language",
    "open_cfw_kvdb_read_dashboard_auto_close",
    "open_cfw_kvdb_write_dashboard_auto_close",
    "open_cfw_kvdb_read_menu_configuration",
    "open_cfw_kvdb_write_menu_configuration",
}
SOURCE_SHA256 = "9eb84180d0b211f168b64d8aaa5acc762e815236c17b7955ce432b94447ab1db"
MAGIC = 0x5555AAAA


class KvdbModuleConfigureCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        cls.library = Path(cls.temporary.name) / f"kvdb_module_configure{suffix}"
        subprocess.run(
            [
                "clang", "-std=c11", "-shared", "-fPIC", "-O1",
                "-include", str(FIXTURE / "kvdb_module_configure_host.h"),
                str(SOURCE), str(FIXTURE / "kvdb_module_configure_host.c"),
                "-o", str(cls.library),
            ],
            check=True,
            cwd=ROOT,
        )
        cls.loaded = ctypes.CDLL(str(cls.library))
        cls.loaded.open_cfw_kvdb_write_language.argtypes = [ctypes.c_ubyte]
        cls.loaded.open_cfw_kvdb_write_dashboard_auto_close.argtypes = [ctypes.c_uint]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.loaded.open_cfw_test_module_reset()

    def uint(self, name: str) -> int:
        return ctypes.c_uint.in_dll(self.loaded, name).value

    def integer(self, name: str) -> int:
        return ctypes.c_int.in_dll(self.loaded, name).value

    def bytes_symbol(self, name: str, length: int) -> bytes:
        return bytes((ctypes.c_ubyte * length).in_dll(self.loaded, name))

    def set_uint(self, name: str, value: int) -> None:
        ctypes.c_uint.in_dll(self.loaded, name).value = value

    def set_db(self, value: bytes, result: int = 1) -> None:
        target = (ctypes.c_ubyte * 888).in_dll(
            self.loaded, "open_cfw_test_module_db_value"
        )
        target[:len(value)] = value
        ctypes.c_int.in_dll(
            self.loaded, "open_cfw_test_module_read_result"
        ).value = result

    @staticmethod
    def record(items: list[tuple[int, int, bytes, int]]) -> bytes:
        output = bytearray(888)
        struct.pack_into("<I", output, 0, MAGIC)
        output[4] = len(items)
        for index, (icon, app_type, text, app_id) in enumerate(items):
            offset = 8 + index * 44
            output[offset] = icon
            struct.pack_into("<I", output, offset + 4, app_type)
            output[offset + 8:offset + 8 + len(text)] = text
            struct.pack_into("<I", output, offset + 40, app_id)
        return bytes(output)

    def test_language_load_valid_invalid_and_missing(self) -> None:
        for stored, result, expected in ((7, 1, 7), (8, 1, 0), (3, 0, 0)):
            self.loaded.open_cfw_test_module_reset()
            self.set_db(bytes([stored]), result)
            self.assertEqual(self.loaded.open_cfw_kvdb_read_language(), 0)
            self.assertEqual(self.uint("open_cfw_test_module_language"), expected)
            self.assertEqual(self.uint("open_cfw_test_module_read_count"), 1)
            self.assertEqual(self.uint("open_cfw_test_module_last_length"), 1)

    def test_scalar_writers_preserve_width_and_ignore_backend_result(self) -> None:
        ctypes.c_int.in_dll(
            self.loaded, "open_cfw_test_module_write_result"
        ).value = -7
        self.loaded.open_cfw_kvdb_write_language(0xAB)
        self.assertEqual(self.bytes_symbol("open_cfw_test_module_written", 4)[0], 0xAB)
        self.assertEqual(self.uint("open_cfw_test_module_last_length"), 1)
        self.loaded.open_cfw_kvdb_write_dashboard_auto_close(0x12345678)
        self.assertEqual(
            self.bytes_symbol("open_cfw_test_module_written", 4),
            struct.pack("<I", 0x12345678),
        )
        self.assertEqual(self.uint("open_cfw_test_module_last_length"), 4)

    def test_dashboard_mode_two_skips_read_and_mutation(self) -> None:
        ctypes.c_int.in_dll(
            self.loaded, "open_cfw_test_module_dashboard_mode"
        ).value = 2
        self.set_db(struct.pack("<I", 123), 1)
        self.assertEqual(self.loaded.open_cfw_kvdb_read_dashboard_auto_close(), 0)
        self.assertEqual(self.uint("open_cfw_test_module_dashboard"), 99)
        self.assertEqual(self.uint("open_cfw_test_module_read_count"), 0)

    def test_dashboard_loads_word_or_defaults_to_ten(self) -> None:
        self.set_db(struct.pack("<I", 123), 1)
        self.loaded.open_cfw_kvdb_read_dashboard_auto_close()
        self.assertEqual(self.uint("open_cfw_test_module_dashboard"), 123)
        self.loaded.open_cfw_test_module_reset()
        self.set_db(struct.pack("<I", 456), 0)
        self.loaded.open_cfw_kvdb_read_dashboard_auto_close()
        self.assertEqual(self.uint("open_cfw_test_module_dashboard"), 10)

    def test_menu_missing_or_bad_magic_leaves_selection_globals_alone(self) -> None:
        self.set_uint("open_cfw_test_module_use_external", 9)
        self.set_uint("open_cfw_test_module_external_count", 11)
        self.set_db(b"\0" * 888, 1)
        self.assertEqual(self.loaded.open_cfw_kvdb_read_menu_configuration(), 0)
        self.assertEqual(self.uint("open_cfw_test_module_use_external"), 9)
        self.assertEqual(self.uint("open_cfw_test_module_external_count"), 11)
        self.assertEqual(self.bytes_symbol("open_cfw_test_module_record", 888), b"\0" * 888)

    def test_menu_reader_imports_builtin_and_custom_items(self) -> None:
        value = self.record([
            (0, 0x1111, b"ignored\0", 0xAABBCCDD),
            (9, 0x2222, b"custom\0", 0x01020304),
        ])
        runtime = (ctypes.c_ubyte * (52 * 20)).in_dll(
            self.loaded, "open_cfw_test_module_runtime"
        )
        runtime[52 + 4:52 + 4 + 16] = b"Z" * 16
        self.set_db(value)
        self.assertEqual(self.loaded.open_cfw_kvdb_read_menu_configuration(), 0)
        raw = bytes(runtime)
        self.assertEqual(self.uint("open_cfw_test_module_lookup_id"), 0xAABBCCDD)
        self.assertEqual(raw[4:12], b"builtin\0")
        self.assertEqual(struct.unpack_from("<I", raw, 36)[0], 0x1234)
        self.assertEqual(raw[40], 7)
        self.assertEqual(struct.unpack_from("<I", raw, 48)[0], 0xAABBCCDD)
        self.assertEqual(raw[52 + 4:52 + 10], b"custom")
        self.assertEqual(raw[52 + 10], ord("Z"))
        self.assertEqual(struct.unpack_from("<I", raw, 52 + 36)[0], 0xFFE)
        self.assertEqual(raw[52 + 40], 1)
        self.assertEqual(struct.unpack_from("<I", raw, 52 + 48)[0], 0x01020304)
        self.assertEqual(self.uint("open_cfw_test_module_use_external"), 1)
        self.assertEqual(self.uint("open_cfw_test_module_external_count"), 2)

    def test_menu_lookup_failure_returns_minus_one_without_committing_globals(self) -> None:
        self.set_db(self.record([(0, 0, b"\0", 42)]))
        ctypes.c_int.in_dll(
            self.loaded, "open_cfw_test_module_lookup_result"
        ).value = -5
        self.assertEqual(self.loaded.open_cfw_kvdb_read_menu_configuration(), -1)
        self.assertEqual(self.uint("open_cfw_test_module_use_external"), 0)
        self.assertEqual(self.uint("open_cfw_test_module_external_count"), 0)

    def test_menu_writer_rejects_unready_state(self) -> None:
        self.assertEqual(self.loaded.open_cfw_kvdb_write_menu_configuration(), -1)
        self.assertEqual(self.uint("open_cfw_test_module_read_count"), 0)
        self.assertEqual(self.uint("open_cfw_test_module_write_count"), 0)

    def test_menu_writer_skips_identical_stored_record(self) -> None:
        value = self.record([(3, 0x11223344, b"same\0", 0x55667788)])
        runtime = (ctypes.c_ubyte * (52 * 20)).in_dll(
            self.loaded, "open_cfw_test_module_runtime"
        )
        runtime[4:9] = b"same\0"
        runtime[40] = 3
        struct.pack_into("<I", runtime, 44, 0x11223344)
        struct.pack_into("<I", runtime, 48, 0x55667788)
        self.set_uint("open_cfw_test_module_use_external", 1)
        self.set_uint("open_cfw_test_module_external_count", 1)
        self.set_db(value)
        self.assertEqual(self.loaded.open_cfw_kvdb_write_menu_configuration(), 0)
        self.assertEqual(self.uint("open_cfw_test_module_write_count"), 0)
        self.assertEqual(self.uint("open_cfw_test_module_begin_count"), 0)

    def test_menu_writer_rebuilds_record_under_snapshot_and_returns_backend(self) -> None:
        runtime = (ctypes.c_ubyte * (52 * 20)).in_dll(
            self.loaded, "open_cfw_test_module_runtime"
        )
        runtime[4:10] = b"fresh\0"
        runtime[40] = 4
        struct.pack_into("<I", runtime, 44, 0x10203040)
        struct.pack_into("<I", runtime, 48, 0x50607080)
        self.set_uint("open_cfw_test_module_use_external", 1)
        self.set_uint("open_cfw_test_module_external_count", 1)
        self.set_db(b"\0" * 888, 0)
        ctypes.c_int.in_dll(
            self.loaded, "open_cfw_test_module_write_result"
        ).value = -12
        self.assertEqual(self.loaded.open_cfw_kvdb_write_menu_configuration(), -12)
        written = self.bytes_symbol("open_cfw_test_module_written", 888)
        self.assertEqual(struct.unpack_from("<I", written, 0)[0], MAGIC)
        self.assertEqual(written[4], 1)
        self.assertEqual(written[8], 4)
        self.assertEqual(struct.unpack_from("<I", written, 12)[0], 0x10203040)
        self.assertEqual(written[16:22], b"fresh\0")
        self.assertEqual(struct.unpack_from("<I", written, 48)[0], 0x50607080)
        self.assertEqual(self.uint("open_cfw_test_module_begin_count"), 1)
        self.assertEqual(self.uint("open_cfw_test_module_end_count"), 1)
        self.assertEqual(self.uint("open_cfw_test_module_write_count"), 1)
        self.assertEqual(self.uint("open_cfw_test_module_last_length"), 888)

    def test_thumb_compile_has_exact_global_text_surface(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "kvdb_module_configure.o"
            subprocess.run(
                [
                    "clang", "-target", "thumbv7em-none-eabi", "-mthumb", "-O2",
                    "-ffreestanding", "-fno-jump-tables", "-fomit-frame-pointer",
                    "-fno-builtin", "-mno-unaligned-access", "-fno-unwind-tables",
                    "-fno-asynchronous-unwind-tables", "-fropi", "-Wall", "-Wextra",
                    "-Werror", "-c", str(SOURCE), "-o", str(target),
                ],
                check=True,
                cwd=ROOT,
            )
            symbols = subprocess.run(
                ["nm", str(target)], check=True, capture_output=True, text=True
            ).stdout
            observed = {
                fields[2]
                for line in symbols.splitlines()
                if len(fields := line.split()) == 3 and fields[1] == "T"
            }
            self.assertEqual(observed, EXPECTED_SYMBOLS)

    def test_source_hash(self) -> None:
        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(), SOURCE_SHA256)


if __name__ == "__main__":
    unittest.main()
