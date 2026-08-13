import ctypes
import hashlib
import platform
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/kvdb_time.c"
FIXTURE = ROOT / "tests/fixtures"
EXPECTED_SYMBOLS = {
    "open_cfw_kvdb_time_default_initialize",
    "open_cfw_kvdb_time_load_and_migrate",
    "open_cfw_kvdb_write_time",
}
SOURCE_SHA256 = "1643ea64328e021ae2176b55513df76d79ab7c6e0f7eabaecf982b42a211d13c"


class KvdbTimeCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        cls.library = Path(cls.temporary.name) / f"kvdb_time{suffix}"
        subprocess.run(
            [
                "clang", "-std=c11", "-shared", "-fPIC", "-O1",
                "-include", str(FIXTURE / "kvdb_time_host.h"),
                str(SOURCE), str(FIXTURE / "kvdb_time_host.c"),
                "-o", str(cls.library),
            ],
            check=True,
            cwd=ROOT,
        )
        cls.loaded = ctypes.CDLL(str(cls.library))
        cls.loaded.open_cfw_kvdb_write_time.argtypes = [ctypes.c_uint32, ctypes.c_int8]
        cls.loaded.open_cfw_test_kvdb_time_set_read.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
        ]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.loaded.open_cfw_test_kvdb_time_reset()

    def record(self) -> bytes:
        return bytes((ctypes.c_ubyte * 12).in_dll(
            self.loaded, "open_cfw_test_kvdb_time_record"
        ))

    def uint(self, name: str) -> int:
        return ctypes.c_uint.in_dll(self.loaded, name).value

    def set_read(self, value: bytes, result: int) -> None:
        raw = (ctypes.c_ubyte * 12).from_buffer_copy(value)
        self.loaded.open_cfw_test_kvdb_time_set_read(raw, result)

    def test_default_crc(self) -> None:
        self.assertEqual(self.loaded.open_cfw_kvdb_time_default_initialize(), 0)
        record = self.record()
        self.assertEqual(record[:10], bytes.fromhex("010000002b2d37682000"))
        self.assertEqual(record[10:], struct.pack("<H", 0x18F0))

    def test_writer_updates_fields_preserves_reserved_and_forces_v3(self) -> None:
        self.loaded.open_cfw_kvdb_write_time(0x12345678, -5)
        record = self.record()
        self.assertEqual(record[:4], bytes.fromhex("03000000"))
        self.assertEqual(record[4:8], struct.pack("<I", 0x12345678))
        self.assertEqual(record[8:10], bytes.fromhex("fb00"))
        self.assertEqual(record[10:], struct.pack("<H", 0xC4BF))
        written = bytes((ctypes.c_ubyte * 12).in_dll(
            self.loaded, "open_cfw_test_kvdb_time_written"
        ))
        self.assertEqual(written, record)
        self.assertEqual(self.uint("open_cfw_test_kvdb_time_write_count"), 1)

    def test_migration_never_imports_stored_record(self) -> None:
        for version, read_result, expected_writes in ((0, 0, 1), (0, 1, 1), (3, 1, 0)):
            self.loaded.open_cfw_test_kvdb_time_reset()
            self.loaded.open_cfw_kvdb_time_default_initialize()
            current = self.record()
            stored = bytearray(12)
            stored[0] = version
            stored[10:12] = b"\x34\x12"
            self.set_read(bytes(stored), read_result)
            self.loaded.open_cfw_kvdb_time_load_and_migrate()
            expected = bytearray(current)
            if expected_writes:
                expected[0] = 3
                expected[10:12] = struct.pack("<H", 0xC67A)
            self.assertEqual(self.record(), bytes(expected))
            self.assertEqual(self.uint("open_cfw_test_kvdb_time_write_count"), expected_writes)

    def test_thumb_compile_has_exact_global_text_surface(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "kvdb_time.o"
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
