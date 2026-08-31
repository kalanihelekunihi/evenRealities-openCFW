import ctypes
import hashlib
import platform
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/kvdb_setting.c"
FIXTURE = ROOT / "tests/fixtures"
EXPECTED_SYMBOLS = {
    "open_cfw_kvdb_setting_default_initialize",
    "open_cfw_kvdb_setting_load_and_migrate",
    "open_cfw_kvdb_write_setting",
}
SOURCE_SHA256 = "787036665e029143220ce2f541fd45a4f585842379b5fb26a058e5a57a44dbec"
FACTORY = bytes.fromhex("0164010000000000060101001e000000000000000000000000000000")


class KvdbSettingCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        cls.library = Path(cls.temporary.name) / f"kvdb_setting{suffix}"
        subprocess.run(
            [
                "clang", "-std=c11", "-shared", "-fPIC", "-O1",
                "-include", str(FIXTURE / "kvdb_setting_host.h"),
                str(SOURCE), str(FIXTURE / "kvdb_setting_host.c"),
                "-o", str(cls.library),
            ],
            check=True,
            cwd=ROOT,
        )
        cls.loaded = ctypes.CDLL(str(cls.library))
        cls.loaded.open_cfw_kvdb_write_setting.argtypes = [ctypes.c_void_p]
        cls.loaded.open_cfw_test_kvdb_setting_set_read.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
        ]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.loaded.open_cfw_test_kvdb_setting_reset()

    def byte_array(self, name: str) -> bytes:
        return bytes((ctypes.c_ubyte * 28).in_dll(self.loaded, name))

    def uint(self, name: str) -> int:
        return ctypes.c_uint.in_dll(self.loaded, name).value

    def set_read(self, value: bytes, result: int) -> None:
        raw = (ctypes.c_ubyte * 28).from_buffer_copy(value)
        self.loaded.open_cfw_test_kvdb_setting_set_read(raw, result)

    def test_default_crc(self) -> None:
        self.assertEqual(self.loaded.open_cfw_kvdb_setting_default_initialize(), 0)
        record = self.byte_array("open_cfw_test_kvdb_setting_record")
        self.assertEqual(record[:24], FACTORY[:24])
        self.assertEqual(record[24:26], struct.pack("<H", 0xA288))
        self.assertEqual(record[26:], FACTORY[26:])

    def test_writer_replaces_record_and_forces_version_crc(self) -> None:
        value = bytes(range(1, 29))
        raw = (ctypes.c_ubyte * 28).from_buffer_copy(value)
        self.assertEqual(self.loaded.open_cfw_kvdb_write_setting(raw), 0)
        record = self.byte_array("open_cfw_test_kvdb_setting_record")
        self.assertEqual(record[:24], bytes.fromhex("0402030405060708090a0b0c0d0e0f101112131415161718"))
        self.assertEqual(record[24:26], struct.pack("<H", 0x8BFC))
        self.assertEqual(record[26:], value[26:])
        self.assertEqual(self.byte_array("open_cfw_test_kvdb_setting_written"), record)
        self.assertEqual(self.uint("open_cfw_test_kvdb_setting_write_count"), 1)

    def test_migration_never_imports_stored_record(self) -> None:
        self.loaded.open_cfw_kvdb_setting_default_initialize()
        current = self.byte_array("open_cfw_test_kvdb_setting_record")
        self.set_read(bytes(28), 0)
        self.loaded.open_cfw_kvdb_setting_load_and_migrate()
        upgraded = bytearray(current)
        upgraded[0] = 4
        upgraded[24:26] = struct.pack("<H", 0x4987)
        self.assertEqual(
            self.byte_array("open_cfw_test_kvdb_setting_record"), bytes(upgraded)
        )
        self.assertEqual(self.uint("open_cfw_test_kvdb_setting_write_count"), 1)

        for version, expected_count in ((3, 1), (4, 0)):
            self.loaded.open_cfw_test_kvdb_setting_reset()
            self.loaded.open_cfw_kvdb_setting_default_initialize()
            current = self.byte_array("open_cfw_test_kvdb_setting_record")
            stored = bytearray(28)
            stored[0] = version
            stored[24:26] = b"\x34\x12"
            self.set_read(bytes(stored), 1)
            self.loaded.open_cfw_kvdb_setting_load_and_migrate()
            expected = current if expected_count == 0 else bytes(upgraded)
            self.assertEqual(self.byte_array("open_cfw_test_kvdb_setting_record"), expected)
            self.assertEqual(self.uint("open_cfw_test_kvdb_setting_write_count"), expected_count)

    def test_thumb_compile_has_exact_global_text_surface(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "kvdb_setting.o"
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
