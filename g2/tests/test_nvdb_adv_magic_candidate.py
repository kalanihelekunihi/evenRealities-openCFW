import ctypes
import hashlib
import platform
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/nvdb_adv_magic.c"
FIXTURE = ROOT / "tests/fixtures"
EXPECTED_SYMBOLS = {
    "open_cfw_nvdb_adv_magic_default_crc_initialize",
    "open_cfw_nvdb_adv_magic_load_and_migrate",
    "open_cfw_nvdb_adv_magic_update",
}


class NvdbAdvMagicCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        cls.library = Path(cls.temporary.name) / f"nvdb_adv_magic{suffix}"
        subprocess.run(
            [
                "clang", "-std=c11", "-shared", "-fPIC", "-O1",
                "-include", str(FIXTURE / "nvdb_adv_magic_host.h"),
                str(SOURCE), str(FIXTURE / "nvdb_adv_magic_host.c"),
                "-o", str(cls.library),
            ],
            check=True,
            cwd=ROOT,
        )
        cls.loaded = ctypes.CDLL(str(cls.library))
        cls.loaded.open_cfw_nvdb_adv_magic_update.argtypes = [ctypes.c_ubyte]
        cls.loaded.open_cfw_test_nvdb_adv_magic_set_read_record.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int
        ]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.loaded.open_cfw_test_nvdb_adv_magic_reset()

    def byte_array(self, name: str):
        return (ctypes.c_ubyte * 4).in_dll(self.loaded, name)

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
        value = (ctypes.c_ubyte * 4).from_buffer_copy(data)
        self.loaded.open_cfw_test_nvdb_adv_magic_set_read_record(value, result)

    def initialize(self) -> bytes:
        self.assertEqual(self.loaded.open_cfw_nvdb_adv_magic_default_crc_initialize(), 0)
        return bytes(self.byte_array("open_cfw_test_nvdb_adv_magic_record"))

    def test_default_crc(self) -> None:
        self.assertEqual(self.initialize(), bytes.fromhex("01205c0a"))

    def test_update_sets_version_crc_and_persists_four_bytes(self) -> None:
        self.loaded.open_cfw_nvdb_adv_magic_update(0x42)
        record = bytes(self.byte_array("open_cfw_test_nvdb_adv_magic_record"))
        self.assertEqual(record[:2], bytes((1, 0x42)))
        self.assertEqual(struct.unpack_from("<H", record, 2)[0], self.crc(record[:2]))
        self.assertEqual(bytes(self.byte_array("open_cfw_test_nvdb_adv_magic_written_record")), record)
        self.assertEqual(self.word("open_cfw_test_nvdb_adv_magic_write_count"), 1)
        self.assertEqual(self.word("open_cfw_test_nvdb_adv_magic_last_write_length"), 4)

    def test_missing_and_v0_mismatch_rewrite_current_magic(self) -> None:
        current = self.initialize()
        self.set_read(bytes(4), 0)
        self.loaded.open_cfw_nvdb_adv_magic_load_and_migrate()
        self.assertEqual(bytes(self.byte_array("open_cfw_test_nvdb_adv_magic_written_record")), current)

        self.loaded.open_cfw_test_nvdb_adv_magic_reset()
        current = self.initialize()
        stale = bytearray(current)
        stale[0] = 0
        stale[2:4] = b"\x00\x00"
        self.set_read(bytes(stale))
        self.loaded.open_cfw_nvdb_adv_magic_load_and_migrate()
        self.assertEqual(bytes(self.byte_array("open_cfw_test_nvdb_adv_magic_written_record")), current)

    def test_equal_crc_or_v1_mismatch_does_not_write_or_import(self) -> None:
        current = self.initialize()
        equal_crc = bytearray(4)
        equal_crc[2:4] = current[2:4]
        self.set_read(bytes(equal_crc))
        self.loaded.open_cfw_nvdb_adv_magic_load_and_migrate()
        self.assertEqual(self.word("open_cfw_test_nvdb_adv_magic_write_count"), 0)
        self.assertEqual(bytes(self.byte_array("open_cfw_test_nvdb_adv_magic_record")), current)

        stale = bytearray(current)
        stale[0] = 1
        stale[1] ^= 1
        stale[2:4] = b"\x00\x00"
        self.set_read(bytes(stale))
        self.loaded.open_cfw_nvdb_adv_magic_load_and_migrate()
        self.assertEqual(self.word("open_cfw_test_nvdb_adv_magic_write_count"), 0)
        self.assertEqual(bytes(self.byte_array("open_cfw_test_nvdb_adv_magic_record")), current)

    def test_thumb_compile_has_exact_global_text_surface(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "nvdb_adv_magic.o"
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
            "6385cb384472a5789331ed22cc0068f20272c0c689ab241b90d589c13a692c21",
        )


if __name__ == "__main__":
    unittest.main()
