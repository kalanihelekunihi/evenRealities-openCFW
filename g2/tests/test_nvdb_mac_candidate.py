import ctypes
import hashlib
import platform
import struct
import subprocess
import tempfile
import unittest
import zlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/nvdb_mac.c"
FIXTURE = ROOT / "tests/fixtures"
EXPECTED_SYMBOLS = {
    "open_cfw_nvdb_mac_default_initialize",
    "open_cfw_nvdb_mac_load_and_migrate",
    "open_cfw_nvdb_mac_update",
}


class NvdbMacCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        cls.library = Path(cls.temporary.name) / f"nvdb_mac{suffix}"
        subprocess.run(
            [
                "clang", "-std=c11", "-shared", "-fPIC", "-O1",
                "-include", str(FIXTURE / "nvdb_mac_host.h"),
                str(SOURCE), str(FIXTURE / "nvdb_mac_host.c"),
                "-o", str(cls.library),
            ],
            check=True,
            cwd=ROOT,
        )
        cls.loaded = ctypes.CDLL(str(cls.library))
        cls.loaded.open_cfw_nvdb_mac_update.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte)
        ]
        cls.loaded.open_cfw_test_nvdb_mac_set_read_record.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int
        ]
        cls.loaded.open_cfw_test_nvdb_mac_set_device_ids.argtypes = [
            ctypes.c_uint, ctypes.c_uint
        ]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.loaded.open_cfw_test_nvdb_mac_reset()

    def byte_array(self, name: str):
        return (ctypes.c_ubyte * 10).in_dll(self.loaded, name)

    def word(self, name: str) -> int:
        return ctypes.c_uint.in_dll(self.loaded, name).value

    @staticmethod
    def crc16(data: bytes) -> int:
        crc = 0xFFFF
        for value in data:
            crc ^= value << 8
            for _ in range(8):
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
        return crc

    def set_read(self, data: bytes, result: int = 1) -> None:
        value = (ctypes.c_ubyte * 10).from_buffer_copy(data)
        self.loaded.open_cfw_test_nvdb_mac_set_read_record(value, result)

    def initialize(self, chip_id0: int = 0x01234567, chip_id1: int = 0x89ABCDEF) -> bytes:
        self.loaded.open_cfw_test_nvdb_mac_set_device_ids(chip_id0, chip_id1)
        self.assertEqual(self.loaded.open_cfw_nvdb_mac_default_initialize(), 0)
        return bytes(self.byte_array("open_cfw_test_nvdb_mac_record"))

    def expected_record(self, chip_id0: int, chip_id1: int) -> bytes:
        serial = struct.pack("<II", chip_id1, chip_id0)
        fingerprint = zlib.crc32(serial) & 0xFFFFFFFF
        suffix = self.crc16(serial)
        address = bytearray(struct.pack("<I", fingerprint))
        address.extend((suffix >> 8, ((suffix & 0xFF) & 0xFC) | 0xC0))
        record = bytearray((1, *address, 0, 0, 0))
        struct.pack_into("<H", record, 8, self.crc16(record[:8]))
        return bytes(record)

    def test_default_derives_static_random_address_from_reversed_chip_ids(self) -> None:
        record = self.initialize()
        self.assertEqual(record, self.expected_record(0x01234567, 0x89ABCDEF))
        self.assertEqual(record[6] & 0xC0, 0xC0)
        self.assertEqual(record[6] & 0x03, 0)
        self.assertEqual(self.word("open_cfw_test_nvdb_mac_write_count"), 0)

    def test_chip_id_order_is_part_of_the_contract(self) -> None:
        normal = self.initialize(0x10203040, 0x50607080)
        self.loaded.open_cfw_test_nvdb_mac_reset()
        swapped = self.initialize(0x50607080, 0x10203040)
        self.assertNotEqual(normal[1:7], swapped[1:7])
        self.assertEqual(normal, self.expected_record(0x10203040, 0x50607080))

    def test_update_sets_version_crc_and_persists_ten_bytes(self) -> None:
        address = bytes.fromhex("1020304050c0")
        value = (ctypes.c_ubyte * 6).from_buffer_copy(address)
        self.loaded.open_cfw_nvdb_mac_update(value)
        record = bytes(self.byte_array("open_cfw_test_nvdb_mac_record"))
        self.assertEqual(record[0], 1)
        self.assertEqual(record[1:7], address)
        self.assertEqual(struct.unpack_from("<H", record, 8)[0], self.crc16(record[:8]))
        self.assertEqual(bytes(self.byte_array("open_cfw_test_nvdb_mac_written_record")), record)
        self.assertEqual(self.word("open_cfw_test_nvdb_mac_write_count"), 1)
        self.assertEqual(self.word("open_cfw_test_nvdb_mac_last_write_length"), 10)

    def test_missing_and_v0_mismatch_rewrite_current_derived_address(self) -> None:
        current = self.initialize()
        self.set_read(bytes(10), 0)
        self.loaded.open_cfw_nvdb_mac_load_and_migrate()
        self.assertEqual(bytes(self.byte_array("open_cfw_test_nvdb_mac_written_record")), current)

        self.loaded.open_cfw_test_nvdb_mac_reset()
        current = self.initialize()
        stale = bytearray(current)
        stale[0] = 0
        stale[8:10] = b"\x00\x00"
        self.set_read(bytes(stale))
        self.loaded.open_cfw_nvdb_mac_load_and_migrate()
        self.assertEqual(bytes(self.byte_array("open_cfw_test_nvdb_mac_written_record")), current)

    def test_equal_crc_or_v1_mismatch_does_not_write_or_import(self) -> None:
        current = self.initialize()
        equal_crc = bytearray(10)
        equal_crc[8:10] = current[8:10]
        self.set_read(bytes(equal_crc))
        self.loaded.open_cfw_nvdb_mac_load_and_migrate()
        self.assertEqual(self.word("open_cfw_test_nvdb_mac_write_count"), 0)
        self.assertEqual(bytes(self.byte_array("open_cfw_test_nvdb_mac_record")), current)

        stale = bytearray(current)
        stale[0] = 1
        stale[1] ^= 0xFF
        stale[8:10] = b"\x00\x00"
        self.set_read(bytes(stale))
        self.loaded.open_cfw_nvdb_mac_load_and_migrate()
        self.assertEqual(self.word("open_cfw_test_nvdb_mac_write_count"), 0)
        self.assertEqual(bytes(self.byte_array("open_cfw_test_nvdb_mac_record")), current)
        self.assertEqual(self.word("open_cfw_test_nvdb_mac_diagnostic_count"), 2)

    def test_thumb_compile_has_exact_global_text_surface(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "nvdb_mac.o"
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
            "038b882d360fc155dbccdb911e9910779cdabf97b244e53c9baaa38f196943ac",
        )


if __name__ == "__main__":
    unittest.main()
