import ctypes
import hashlib
import platform
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/nvdb_sys_dt.c"
FIXTURE = ROOT / "tests/fixtures"
FACTORY_RECORD = bytes.fromhex(
    "02533230304c4442453231303030310053323030455642544c4e323530363330"
    "3131313131000000693401000c0a0f0000000000000000000000000000000000"
    "0000000000000000000000000000000000000000000000000000000000000000"
    "0000000000000000000000000000000000000000000000000000000000000000"
    "0000000000000000000000000000000000000000000000000000000000000000"
    "000000000000000000000000"
)
EXPECTED_SYMBOLS = {
    "open_cfw_nvdb_sys_dt_default_initialize",
    "open_cfw_nvdb_sys_dt_load_and_migrate",
    "open_cfw_nvdb_sys_dt_write",
    "open_cfw_nvdb_sys_dt_get",
    "open_cfw_nvdb_sys_dt_read",
    "open_cfw_nvdb_sys_dt_parse_psn",
    "open_cfw_nvdb_sys_dt_manufacturer_name",
    "open_cfw_nvdb_sys_dt_year",
    "open_cfw_nvdb_sys_dt_month",
    "open_cfw_nvdb_sys_dt_reset_aging",
    "open_cfw_nvdb_sys_dt_mark_legacy_psn",
    "open_cfw_nvdb_sys_dt_read_psn_from_otp",
    "open_cfw_nvdb_sys_dt_write_psn_to_otp",
}
SOURCE_SHA256 = "a18152b8a7e769142bb21795cb724ef29df2c8ea18176050d12d8606189516c7"


class NvdbSysDtCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        cls.library = Path(cls.temporary.name) / f"nvdb_sys_dt{suffix}"
        subprocess.run(
            [
                "clang", "-std=c11", "-shared", "-fPIC", "-O1",
                "-include", str(FIXTURE / "nvdb_sys_dt_host.h"),
                str(SOURCE), str(FIXTURE / "nvdb_sys_dt_host.c"),
                "-o", str(cls.library),
            ],
            check=True,
            cwd=ROOT,
        )
        cls.loaded = ctypes.CDLL(str(cls.library))
        cls.loaded.open_cfw_nvdb_sys_dt_write.argtypes = [
            ctypes.c_ubyte, ctypes.c_void_p,
        ]
        cls.loaded.open_cfw_nvdb_sys_dt_get.argtypes = [ctypes.c_ubyte]
        cls.loaded.open_cfw_nvdb_sys_dt_get.restype = ctypes.c_void_p
        cls.loaded.open_cfw_nvdb_sys_dt_read.argtypes = [ctypes.c_ubyte]
        cls.loaded.open_cfw_nvdb_sys_dt_read.restype = ctypes.c_void_p
        cls.loaded.open_cfw_nvdb_sys_dt_parse_psn.argtypes = [ctypes.c_char_p]
        cls.loaded.open_cfw_nvdb_sys_dt_manufacturer_name.argtypes = [ctypes.c_char]
        cls.loaded.open_cfw_nvdb_sys_dt_manufacturer_name.restype = ctypes.c_char_p
        cls.loaded.open_cfw_nvdb_sys_dt_year.argtypes = [ctypes.c_char]
        cls.loaded.open_cfw_nvdb_sys_dt_year.restype = ctypes.c_uint
        cls.loaded.open_cfw_nvdb_sys_dt_month.argtypes = [ctypes.c_char]
        cls.loaded.open_cfw_nvdb_sys_dt_month.restype = ctypes.c_char_p
        cls.loaded.open_cfw_nvdb_sys_dt_read_psn_from_otp.argtypes = [
            ctypes.c_char_p, ctypes.POINTER(ctypes.c_int),
        ]
        cls.loaded.open_cfw_nvdb_sys_dt_write_psn_to_otp.argtypes = [
            ctypes.c_char_p,
        ]
        cls.loaded.open_cfw_test_nvdb_sys_dt_set_read.argtypes = [
            ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
        ]
        cls.loaded.open_cfw_test_nvdb_sys_dt_set_otp_slot.argtypes = [
            ctypes.c_uint, ctypes.POINTER(ctypes.c_ubyte),
        ]
        cls.loaded.open_cfw_test_nvdb_sys_dt_set_otp_read_failure.argtypes = [
            ctypes.c_uint, ctypes.c_uint, ctypes.c_int,
        ]
        cls.loaded.open_cfw_test_nvdb_sys_dt_set_otp_write_failure.argtypes = [
            ctypes.c_uint, ctypes.c_int,
        ]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.loaded.open_cfw_test_nvdb_sys_dt_reset()

    def bytes_array(self, name: str, size: int) -> bytes:
        return bytes((ctypes.c_ubyte * size).in_dll(self.loaded, name))

    def uint(self, name: str) -> int:
        return ctypes.c_uint.in_dll(self.loaded, name).value

    def byte(self, name: str) -> int:
        return ctypes.c_ubyte.in_dll(self.loaded, name).value

    @staticmethod
    def crc16(data: bytes) -> int:
        crc = 0xFFFF
        for value in data:
            crc ^= value << 8
            for _ in range(8):
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
        return crc

    @staticmethod
    def array(value: bytes):
        return (ctypes.c_ubyte * len(value)).from_buffer_copy(value)

    def set_read(self, value: bytes, result: int) -> None:
        raw = self.array(value)
        self.loaded.open_cfw_test_nvdb_sys_dt_set_read(raw, result)

    def set_slot(self, slot: int, serial: bytes) -> None:
        value = serial[:14].ljust(16, b"\0")
        raw = self.array(value)
        self.loaded.open_cfw_test_nvdb_sys_dt_set_otp_slot(slot, raw)

    def test_factory_layout_and_default_crc(self) -> None:
        self.assertEqual(len(FACTORY_RECORD), 172)
        self.assertEqual(self.bytes_array("open_cfw_test_nvdb_sys_dt_record", 172), FACTORY_RECORD)
        self.assertEqual(self.loaded.open_cfw_nvdb_sys_dt_default_initialize(), 0)
        record = self.bytes_array("open_cfw_test_nvdb_sys_dt_record", 172)
        self.assertEqual(record[:38], FACTORY_RECORD[:38])
        self.assertEqual(struct.unpack_from("<H", record, 38)[0], 0x1DC7)
        self.assertEqual(struct.unpack_from("<I", record, 40)[0], 78953)
        self.assertEqual(record[44:47], bytes((12, 10, 15)))

    def test_write_switch_layout_crc_and_full_record(self) -> None:
        long_psn = ctypes.create_string_buffer(b"S200LABI270028-extra")
        self.assertEqual(self.loaded.open_cfw_nvdb_sys_dt_write(0, long_psn), 0)
        record = self.bytes_array("open_cfw_test_nvdb_sys_dt_record", 172)
        self.assertEqual(record[1:16], b"S200LABI270028\0")
        self.assertEqual(record[0], 2)
        self.assertEqual(struct.unpack_from("<H", record, 38)[0], self.crc16(record[:38]))

        board = ctypes.create_string_buffer(b"S200EVBTLN250630123456789")
        self.loaded.open_cfw_nvdb_sys_dt_write(1, board)
        lux = ctypes.c_uint(123456)
        self.loaded.open_cfw_nvdb_sys_dt_write(2, ctypes.byref(lux))
        for index, value in ((3, 7), (4, 8), (5, 9), (9, 10), (10, 11), (11, 12), (12, 13)):
            byte = ctypes.c_ubyte(value)
            self.loaded.open_cfw_nvdb_sys_dt_write(index, ctypes.byref(byte))
        for index, start in ((6, 0), (7, 40), (8, 80)):
            payload = (ctypes.c_ubyte * 40)(*range(start, start + 40))
            self.loaded.open_cfw_nvdb_sys_dt_write(index, payload)
        record = self.bytes_array("open_cfw_test_nvdb_sys_dt_record", 172)
        self.assertEqual(record[16:38], b"S200EVBTLN25063012345\0")
        self.assertEqual(struct.unpack_from("<I", record, 40)[0], 123456)
        self.assertEqual(record[44:47], bytes((7, 8, 9)))
        self.assertEqual(record[48:88], bytes(range(40)))
        self.assertEqual(record[88:128], bytes(range(40, 80)))
        self.assertEqual(record[128:168], bytes(range(80, 120)))
        self.assertEqual(record[168:172], bytes((10, 11, 12, 13)))
        self.assertEqual(self.uint("open_cfw_test_nvdb_sys_dt_last_write_length"), 172)

        before = self.uint("open_cfw_test_nvdb_sys_dt_write_count")
        self.assertEqual(self.loaded.open_cfw_nvdb_sys_dt_write(14, None), 0)
        self.assertEqual(self.uint("open_cfw_test_nvdb_sys_dt_write_count"), before)
        replacement = bytearray(172)
        replacement[1:5] = b"TEST"
        raw = self.array(bytes(replacement))
        self.loaded.open_cfw_nvdb_sys_dt_write(13, raw)
        record = self.bytes_array("open_cfw_test_nvdb_sys_dt_record", 172)
        self.assertEqual(record[0], 2)
        self.assertEqual(record[1:5], b"TEST")
        self.assertEqual(struct.unpack_from("<H", record, 38)[0], self.crc16(record[:38]))

    def test_get_mapping_and_read_otp_override(self) -> None:
        base = ctypes.addressof((ctypes.c_ubyte * 172).in_dll(
            self.loaded, "open_cfw_test_nvdb_sys_dt_record"
        ))
        offsets = [1, 16, 40, 44, 45, 46, 48, 88, 128, 168, 169, 170, 171]
        for index, offset in enumerate(offsets):
            self.assertEqual(self.loaded.open_cfw_nvdb_sys_dt_get(index), base + offset)
        self.assertEqual(self.loaded.open_cfw_nvdb_sys_dt_get(13), base)
        self.assertEqual(self.loaded.open_cfw_nvdb_sys_dt_get(255), base)

        stored = bytearray(FACTORY_RECORD)
        stored[1:16] = b"S200LABI270028\0"
        stored[40:44] = struct.pack("<I", 777)
        self.set_read(bytes(stored), 1)
        self.set_slot(3, b"S200LCBI200010")
        self.assertEqual(self.loaded.open_cfw_nvdb_sys_dt_read(2), base + 40)
        record = self.bytes_array("open_cfw_test_nvdb_sys_dt_record", 172)
        self.assertEqual(record[1:16], b"S200LCBI200010\0")
        self.assertEqual(struct.unpack_from("<I", record, 40)[0], 777)
        self.assertEqual(self.byte("open_cfw_test_nvdb_sys_dt_legacy_psn_flag"), 1)

    def test_migration_keeps_live_record_and_rewrites_only_old_or_missing(self) -> None:
        self.loaded.open_cfw_nvdb_sys_dt_default_initialize()
        current = self.bytes_array("open_cfw_test_nvdb_sys_dt_record", 172)
        stale = bytearray(FACTORY_RECORD)
        stale[0] = 0
        struct.pack_into("<H", stale, 38, 0)
        self.set_read(bytes(stale), 1)
        self.set_slot(2, b"S200LCBI190025")
        self.assertEqual(self.loaded.open_cfw_nvdb_sys_dt_load_and_migrate(), 0)
        record = self.bytes_array("open_cfw_test_nvdb_sys_dt_record", 172)
        self.assertEqual(record[1:16], b"S200LCBI190025\0")
        self.assertEqual(record[40:], current[40:])
        self.assertEqual(self.uint("open_cfw_test_nvdb_sys_dt_write_count"), 1)
        self.assertEqual(self.uint("open_cfw_test_nvdb_sys_dt_parse_count"), 1)

        self.loaded.open_cfw_test_nvdb_sys_dt_reset()
        self.loaded.open_cfw_nvdb_sys_dt_default_initialize()
        current = self.bytes_array("open_cfw_test_nvdb_sys_dt_record", 172)
        newer = bytearray(FACTORY_RECORD)
        newer[0] = 2
        struct.pack_into("<H", newer, 38, 0)
        self.set_read(bytes(newer), 1)
        self.loaded.open_cfw_nvdb_sys_dt_load_and_migrate()
        self.assertEqual(self.bytes_array("open_cfw_test_nvdb_sys_dt_record", 172), current)
        self.assertEqual(self.uint("open_cfw_test_nvdb_sys_dt_write_count"), 0)

        self.loaded.open_cfw_test_nvdb_sys_dt_reset()
        self.loaded.open_cfw_nvdb_sys_dt_default_initialize()
        self.set_read(bytes(172), 0)
        self.loaded.open_cfw_nvdb_sys_dt_load_and_migrate()
        self.assertEqual(self.uint("open_cfw_test_nvdb_sys_dt_write_count"), 1)

    def test_parser_mappings_and_legacy_flag(self) -> None:
        self.loaded.open_cfw_nvdb_sys_dt_parse_psn(b"S200LDBE210001")
        self.assertEqual(self.uint("open_cfw_test_nvdb_sys_dt_parse_count"), 1)
        self.assertEqual(self.bytes_array("open_cfw_test_nvdb_sys_dt_parsed_project", 5), b"S200\0")
        self.assertEqual(self.bytes_array("open_cfw_test_nvdb_sys_dt_parsed_manufacturer", 20).split(b"\0")[0], b"LianHeGuangDian")
        self.assertEqual(self.uint("open_cfw_test_nvdb_sys_dt_parsed_year"), 2025)
        self.assertEqual(self.bytes_array("open_cfw_test_nvdb_sys_dt_parsed_month", 4).split(b"\0")[0], b"5")
        self.assertEqual(self.bytes_array("open_cfw_test_nvdb_sys_dt_parsed_day", 3), b"21\0")
        self.assertEqual(self.bytes_array("open_cfw_test_nvdb_sys_dt_parsed_serial", 5), b"0001\0")
        self.assertEqual(self.loaded.open_cfw_nvdb_sys_dt_manufacturer_name(b"X"), b"unknow")
        self.assertEqual(self.loaded.open_cfw_nvdb_sys_dt_year(b"A"), 2024)
        self.assertEqual(self.loaded.open_cfw_nvdb_sys_dt_year(b"0"), 0)
        self.assertEqual(self.loaded.open_cfw_nvdb_sys_dt_month(b"L"), b"12")
        self.assertEqual(self.loaded.open_cfw_nvdb_sys_dt_month(b"0"), b"unknow")

        record = (ctypes.c_ubyte * 172).in_dll(
            self.loaded, "open_cfw_test_nvdb_sys_dt_record"
        )
        record[1:16] = b"S200LABI270028\0"
        self.loaded.open_cfw_nvdb_sys_dt_mark_legacy_psn()
        self.assertEqual(self.byte("open_cfw_test_nvdb_sys_dt_legacy_psn_flag"), 1)
        record[1:16] = b"S200LDBE210001\0"
        self.loaded.open_cfw_nvdb_sys_dt_mark_legacy_psn()
        self.assertEqual(self.byte("open_cfw_test_nvdb_sys_dt_legacy_psn_flag"), 1)

    def test_reset_aging_preserves_total_count_and_persists(self) -> None:
        record = (ctypes.c_ubyte * 172).in_dll(
            self.loaded, "open_cfw_test_nvdb_sys_dt_record"
        )
        for index in range(48, 172):
            record[index] = 0xAA
        self.loaded.open_cfw_nvdb_sys_dt_reset_aging()
        raw = bytes(record)
        self.assertEqual(raw[48:168], bytes(120))
        self.assertEqual(raw[168:170], b"\0\0")
        self.assertEqual(raw[170], 0xAA)
        self.assertEqual(raw[171], 0)
        self.assertEqual(self.uint("open_cfw_test_nvdb_sys_dt_write_count"), 1)

    def test_otp_read_uses_last_valid_slot_and_stops_on_read_failure(self) -> None:
        self.set_slot(1, b"S200LABI270028")
        self.set_slot(5, b"S200LCBI200010")
        output = ctypes.create_string_buffer(15)
        index = ctypes.c_int(-1)
        self.assertEqual(self.loaded.open_cfw_nvdb_sys_dt_read_psn_from_otp(output, ctypes.byref(index)), 0)
        self.assertEqual(output.value, b"S200LCBI200010")
        self.assertEqual(index.value, 5)
        self.assertEqual(self.uint("open_cfw_test_nvdb_sys_dt_otp_begin_count"), 1)
        self.assertEqual(self.uint("open_cfw_test_nvdb_sys_dt_otp_end_count"), 1)

        self.loaded.open_cfw_test_nvdb_sys_dt_reset()
        self.set_slot(1, b"S200LABI270028")
        self.set_slot(6, b"S200LCBI200010")
        self.loaded.open_cfw_test_nvdb_sys_dt_set_otp_read_failure(4, 2, 7)
        output = ctypes.create_string_buffer(15)
        index = ctypes.c_int(-1)
        self.assertEqual(self.loaded.open_cfw_nvdb_sys_dt_read_psn_from_otp(output, ctypes.byref(index)), 0)
        self.assertEqual(output.value, b"S200LABI270028")
        self.assertEqual(index.value, 1)

    def test_otp_write_validates_deduplicates_appends_and_handles_failure(self) -> None:
        self.assertEqual(self.loaded.open_cfw_nvdb_sys_dt_write_psn_to_otp(None), -1)
        self.assertEqual(self.loaded.open_cfw_nvdb_sys_dt_write_psn_to_otp(b"bad"), -1)
        self.assertEqual(self.loaded.open_cfw_nvdb_sys_dt_write_psn_to_otp(b"S200LABI270028"), 0)
        otp = self.bytes_array("open_cfw_test_nvdb_sys_dt_otp", 128)
        self.assertEqual(otp[:16], b"S200LABI270028\0\0")
        self.assertEqual(self.uint("open_cfw_test_nvdb_sys_dt_otp_write_count"), 4)
        self.assertEqual(self.loaded.open_cfw_nvdb_sys_dt_write_psn_to_otp(b"S200LABI270028"), 0)
        self.assertEqual(self.uint("open_cfw_test_nvdb_sys_dt_otp_write_count"), 4)
        self.assertEqual(self.loaded.open_cfw_nvdb_sys_dt_write_psn_to_otp(b"S200LCBI200010"), 0)
        otp = self.bytes_array("open_cfw_test_nvdb_sys_dt_otp", 128)
        self.assertEqual(otp[16:32], b"S200LCBI200010\0\0")

        self.loaded.open_cfw_test_nvdb_sys_dt_reset()
        self.loaded.open_cfw_test_nvdb_sys_dt_set_otp_write_failure(2, 9)
        self.assertEqual(self.loaded.open_cfw_nvdb_sys_dt_write_psn_to_otp(b"S200LABI270028"), -1)
        self.assertEqual(self.uint("open_cfw_test_nvdb_sys_dt_otp_begin_count"), 2)
        self.assertEqual(self.uint("open_cfw_test_nvdb_sys_dt_otp_end_count"), 2)
        self.assertEqual(self.uint("open_cfw_test_nvdb_sys_dt_otp_write_count"), 2)

    def test_thumb_compile_has_exact_global_text_surface(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "nvdb_sys_dt.o"
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
            SOURCE_SHA256,
        )


if __name__ == "__main__":
    unittest.main()
