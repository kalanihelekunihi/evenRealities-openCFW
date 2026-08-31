import ctypes
import hashlib
import platform
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/kvdb_als_scale.c"
FIXTURE = ROOT / "tests/fixtures"
EXPECTED_SYMBOLS = {
    "open_cfw_kvdb_als_scale_default_initialize",
    "open_cfw_kvdb_als_scale_load_and_migrate",
    "open_cfw_kvdb_write_als_scale",
}
SOURCE_SHA256 = "0db26600540b8f3e8d244204329acb431ab2ad01a73da322f1f2f9d0fba548c2"


class KvdbAlsScaleCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        cls.library = Path(cls.temporary.name) / f"kvdb_als_scale{suffix}"
        subprocess.run(
            [
                "clang", "-std=c11", "-shared", "-fPIC", "-O1",
                "-include", str(FIXTURE / "kvdb_als_scale_host.h"),
                str(SOURCE), str(FIXTURE / "kvdb_als_scale_host.c"),
                "-o", str(cls.library),
            ],
            check=True,
            cwd=ROOT,
        )
        cls.loaded = ctypes.CDLL(str(cls.library))
        cls.loaded.open_cfw_kvdb_write_als_scale.argtypes = [ctypes.c_void_p]
        cls.loaded.open_cfw_test_kvdb_als_scale_set_read.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
        ]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.loaded.open_cfw_test_kvdb_als_scale_reset()

    def byte_array(self, name: str) -> bytes:
        return bytes((ctypes.c_ubyte * 12).in_dll(self.loaded, name))

    def uint(self, name: str) -> int:
        return ctypes.c_uint.in_dll(self.loaded, name).value

    def set_read(self, value: bytes, result: int) -> None:
        raw = (ctypes.c_ubyte * 12).from_buffer_copy(value)
        self.loaded.open_cfw_test_kvdb_als_scale_set_read(raw, result)

    def test_default_crc(self) -> None:
        self.assertEqual(self.loaded.open_cfw_kvdb_als_scale_default_initialize(), 0)
        self.assertEqual(
            self.byte_array("open_cfw_test_kvdb_als_scale_record"),
            bytes.fromhex("01000000000400002daa0000"),
        )

    def test_writer_replaces_record_and_forces_version_crc(self) -> None:
        value = bytes.fromhex("0901020304050607aaaabbcc")
        raw = (ctypes.c_ubyte * 12).from_buffer_copy(value)
        self.assertEqual(self.loaded.open_cfw_kvdb_write_als_scale(raw), 0)
        record = self.byte_array("open_cfw_test_kvdb_als_scale_record")
        self.assertEqual(record[:8], bytes.fromhex("0101020304050607"))
        self.assertEqual(record[8:10], struct.pack("<H", 0x505E))
        self.assertEqual(record[10:], b"\xbb\xcc")
        self.assertEqual(self.byte_array("open_cfw_test_kvdb_als_scale_written"), record)
        self.assertEqual(self.uint("open_cfw_test_kvdb_als_scale_write_count"), 1)

    def test_migration_never_imports_stored_record(self) -> None:
        self.loaded.open_cfw_kvdb_als_scale_default_initialize()
        current = self.byte_array("open_cfw_test_kvdb_als_scale_record")
        self.set_read(bytes(12), 0)
        self.loaded.open_cfw_kvdb_als_scale_load_and_migrate()
        self.assertEqual(self.byte_array("open_cfw_test_kvdb_als_scale_record"), current)
        self.assertEqual(self.uint("open_cfw_test_kvdb_als_scale_write_count"), 1)

        for version, expected_count in ((0, 1), (1, 0)):
            self.loaded.open_cfw_test_kvdb_als_scale_reset()
            self.loaded.open_cfw_kvdb_als_scale_default_initialize()
            current = self.byte_array("open_cfw_test_kvdb_als_scale_record")
            stored = bytearray(12)
            stored[0] = version
            stored[8:10] = b"\x34\x12"
            self.set_read(bytes(stored), 1)
            self.loaded.open_cfw_kvdb_als_scale_load_and_migrate()
            self.assertEqual(self.byte_array("open_cfw_test_kvdb_als_scale_record"), current)
            self.assertEqual(self.uint("open_cfw_test_kvdb_als_scale_write_count"), expected_count)

    def test_thumb_compile_has_exact_global_text_surface(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "kvdb_als_scale.o"
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
