import ctypes
import hashlib
import platform
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/kvdb_ring.c"
FIXTURE = ROOT / "tests/fixtures"
EXPECTED_SYMBOLS = {
    "open_cfw_kvdb_ring_default_initialize",
    "open_cfw_kvdb_ring_load_and_migrate",
    "open_cfw_kvdb_write_ring",
}
SOURCE_SHA256 = "470ce433f52d117d76638f7ca39c257429cbb1bb4e52a12f1421de986ba84269"


class KvdbRingCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        cls.library = Path(cls.temporary.name) / f"kvdb_ring{suffix}"
        subprocess.run(
            [
                "clang", "-std=c11", "-shared", "-fPIC", "-O1",
                "-include", str(FIXTURE / "kvdb_ring_host.h"),
                str(SOURCE), str(FIXTURE / "kvdb_ring_host.c"),
                "-o", str(cls.library),
            ],
            check=True,
            cwd=ROOT,
        )
        cls.loaded = ctypes.CDLL(str(cls.library))
        cls.loaded.open_cfw_kvdb_write_ring.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte), ctypes.c_char_p,
        ]
        cls.loaded.open_cfw_test_kvdb_ring_set_read.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
        ]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.loaded.open_cfw_test_kvdb_ring_reset()

    def record(self) -> bytes:
        return bytes((ctypes.c_ubyte * 24).in_dll(
            self.loaded, "open_cfw_test_kvdb_ring_record"
        ))

    def uint(self, name: str) -> int:
        return ctypes.c_uint.in_dll(self.loaded, name).value

    def set_read(self, value: bytes, result: int) -> None:
        raw = (ctypes.c_ubyte * 24).from_buffer_copy(value)
        self.loaded.open_cfw_test_kvdb_ring_set_read(raw, result)

    def test_default_crc(self) -> None:
        self.assertEqual(self.loaded.open_cfw_kvdb_ring_default_initialize(), 0)
        self.assertEqual(self.record()[22:24], struct.pack("<H", 0x06D4))

    def test_writer_sets_mac_truncates_name_and_preserves_reserved(self) -> None:
        raw_mac = (ctypes.c_ubyte * 6)(1, 2, 3, 4, 5, 6)
        self.loaded.open_cfw_kvdb_write_ring(raw_mac, b"abcdefghijklmnop")
        record = self.record()
        self.assertEqual(record[0], 1)
        self.assertEqual(record[1:7], bytes(range(1, 7)))
        self.assertEqual(record[7:21], b"abcdefghijklm\0")
        self.assertEqual(record[21], 0)
        self.assertEqual(record[22:24], struct.pack("<H", 0xFC20))
        written = bytes((ctypes.c_ubyte * 24).in_dll(
            self.loaded, "open_cfw_test_kvdb_ring_written"
        ))
        self.assertEqual(written, record)
        self.assertEqual(self.uint("open_cfw_test_kvdb_ring_write_count"), 1)

    def test_null_writer_fills_mac_and_all_fourteen_name_bytes(self) -> None:
        self.loaded.open_cfw_kvdb_write_ring(None, None)
        record = self.record()
        self.assertEqual(record[1:7], b"\xff" * 6)
        self.assertEqual(record[7:21], b"\xff" * 14)
        self.assertEqual(record[21], 0)
        self.assertEqual(record[22:24], struct.pack("<H", 0x37D4))

    def test_missing_migration_rewrites_current_without_importing(self) -> None:
        self.loaded.open_cfw_kvdb_ring_default_initialize()
        stored = bytes.fromhex("00") + b"\x11" * 23
        self.set_read(stored, 0)
        self.loaded.open_cfw_kvdb_ring_load_and_migrate()
        record = self.record()
        self.assertEqual(record[:20], bytes.fromhex(
            "01ffffffffffff4556454e2052315f4646464646"
        ))
        self.assertEqual(record[20:22], b"\0\0")
        self.assertEqual(record[22:24], struct.pack("<H", 0xA1BE))
        self.assertNotEqual(record, stored)
        self.assertEqual(self.uint("open_cfw_test_kvdb_ring_write_count"), 1)

    def test_migration_only_rewrites_mismatched_v0(self) -> None:
        for version, crc, expected_writes in ((0, 0x1234, 1), (1, 0x1234, 0), (0, 0x06D4, 0)):
            self.loaded.open_cfw_test_kvdb_ring_reset()
            self.loaded.open_cfw_kvdb_ring_default_initialize()
            stored = bytearray(24)
            stored[0] = version
            stored[22:24] = struct.pack("<H", crc)
            self.set_read(bytes(stored), 1)
            self.loaded.open_cfw_kvdb_ring_load_and_migrate()
            self.assertEqual(
                self.uint("open_cfw_test_kvdb_ring_write_count"), expected_writes
            )
            self.assertNotEqual(self.record(), bytes(stored))

    def test_thumb_compile_has_exact_global_text_surface(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "kvdb_ring.o"
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
