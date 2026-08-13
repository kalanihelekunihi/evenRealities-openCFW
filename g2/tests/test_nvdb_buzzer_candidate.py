import ctypes
import hashlib
import platform
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/nvdb_buzzer.c"
FIXTURE = ROOT / "tests/fixtures"
EXPECTED_SYMBOLS = {
    "open_cfw_nvdb_buzzer_default_crc_initialize",
    "open_cfw_nvdb_buzzer_load_and_migrate",
    "open_cfw_nvdb_buzzer_frequency_get",
    "open_cfw_nvdb_buzzer_duty_get",
    "open_cfw_nvdb_buzzer_update",
}


class NvdbBuzzerCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        cls.library = Path(cls.temporary.name) / f"nvdb_buzzer{suffix}"
        subprocess.run(
            [
                "clang", "-std=c11", "-shared", "-fPIC", "-O1",
                "-include", str(FIXTURE / "nvdb_buzzer_host.h"),
                str(SOURCE), str(FIXTURE / "nvdb_buzzer_host.c"),
                "-o", str(cls.library),
            ],
            check=True,
            cwd=ROOT,
        )
        cls.loaded = ctypes.CDLL(str(cls.library))
        cls.loaded.open_cfw_nvdb_buzzer_frequency_get.restype = ctypes.c_uint32
        cls.loaded.open_cfw_nvdb_buzzer_duty_get.restype = ctypes.c_uint8
        cls.loaded.open_cfw_nvdb_buzzer_update.argtypes = [ctypes.c_uint32, ctypes.c_uint8]
        cls.loaded.open_cfw_test_nvdb_buzzer_set_read_record.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int
        ]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.loaded.open_cfw_test_nvdb_buzzer_reset()

    def byte_array(self, name: str):
        return (ctypes.c_ubyte * 12).in_dll(self.loaded, name)

    def word(self, name: str) -> int:
        return ctypes.c_uint.in_dll(self.loaded, name).value

    @staticmethod
    def crc(data: bytes) -> int:
        crc = 0xFFFF
        for value in data:
            crc ^= value << 8
            for _ in range(8):
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
        return crc

    def set_read(self, data: bytes, result: int = 1) -> None:
        value = (ctypes.c_ubyte * 12).from_buffer_copy(data)
        self.loaded.open_cfw_test_nvdb_buzzer_set_read_record(value, result)

    def initialize(self) -> bytes:
        self.assertEqual(self.loaded.open_cfw_nvdb_buzzer_default_crc_initialize(), 0)
        return bytes(self.byte_array("open_cfw_test_nvdb_buzzer_record"))

    def test_default_crc_and_accessors(self) -> None:
        record = self.initialize()
        self.assertEqual(record[:10], bytes.fromhex("02000000a00f00001e00"))
        self.assertEqual(struct.unpack_from("<H", record, 10)[0], 0x9B1E)
        self.assertEqual(self.loaded.open_cfw_nvdb_buzzer_frequency_get(), 4000)
        self.assertEqual(self.loaded.open_cfw_nvdb_buzzer_duty_get(), 30)

    def test_update_sets_version_crc_and_persists_all_twelve_bytes(self) -> None:
        self.loaded.open_cfw_nvdb_buzzer_update(5234, 44)
        record = bytes(self.byte_array("open_cfw_test_nvdb_buzzer_record"))
        self.assertEqual(record[0], 2)
        self.assertEqual(struct.unpack_from("<I", record, 4)[0], 5234)
        self.assertEqual(record[8], 44)
        self.assertEqual(struct.unpack_from("<H", record, 10)[0], self.crc(record[:10]))
        self.assertEqual(bytes(self.byte_array("open_cfw_test_nvdb_buzzer_written_record")), record)
        self.assertEqual(self.word("open_cfw_test_nvdb_buzzer_write_count"), 1)
        self.assertEqual(self.word("open_cfw_test_nvdb_buzzer_last_write_length"), 12)

    def test_missing_and_pre_v2_mismatch_rewrite_current_defaults(self) -> None:
        current = self.initialize()
        self.set_read(bytes(12), 0)
        self.loaded.open_cfw_nvdb_buzzer_load_and_migrate()
        self.assertEqual(self.word("open_cfw_test_nvdb_buzzer_write_count"), 1)
        self.assertEqual(bytes(self.byte_array("open_cfw_test_nvdb_buzzer_written_record")), current)

        self.loaded.open_cfw_test_nvdb_buzzer_reset()
        current = self.initialize()
        stale = bytearray(current)
        stale[0] = 1
        stale[10:12] = b"\x00\x00"
        self.set_read(bytes(stale))
        self.loaded.open_cfw_nvdb_buzzer_load_and_migrate()
        self.assertEqual(self.word("open_cfw_test_nvdb_buzzer_write_count"), 1)
        self.assertEqual(bytes(self.byte_array("open_cfw_test_nvdb_buzzer_written_record")), current)

    def test_equal_crc_or_v2_mismatch_does_not_write(self) -> None:
        current = self.initialize()
        equal_crc = bytearray(12)
        equal_crc[0] = 1
        equal_crc[10:12] = current[10:12]
        self.set_read(bytes(equal_crc))
        self.loaded.open_cfw_nvdb_buzzer_load_and_migrate()
        self.assertEqual(self.word("open_cfw_test_nvdb_buzzer_write_count"), 0)

        current_v2 = bytearray(current)
        current_v2[4] ^= 1
        current_v2[10:12] = b"\x00\x00"
        self.set_read(bytes(current_v2))
        self.loaded.open_cfw_nvdb_buzzer_load_and_migrate()
        self.assertEqual(self.word("open_cfw_test_nvdb_buzzer_write_count"), 0)
        self.assertEqual(self.word("open_cfw_test_nvdb_buzzer_diagnostic_count"), 2)

    def test_thumb_compile_has_exact_global_text_surface(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "nvdb_buzzer.o"
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
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "c4ed1b989c5e7ab019bd00fa9e57ee6ed166afe24caef7f1d37700efefe9656b",
        )


if __name__ == "__main__":
    unittest.main()
