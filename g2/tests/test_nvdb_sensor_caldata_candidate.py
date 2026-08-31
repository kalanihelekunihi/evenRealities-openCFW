import ctypes
import hashlib
import platform
import struct
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/nvdb_sensor_caldata.c"
FIXTURE = ROOT / "tests/fixtures"
EXPECTED_SYMBOLS = {
    "open_cfw_nvdb_sensor_caldata_default_initialize",
    "open_cfw_nvdb_sensor_caldata_load_and_migrate",
    "open_cfw_nvdb_sensor_caldata_update",
    "open_cfw_nvdb_sensor_caldata_ag_default_initialize",
    "open_cfw_nvdb_sensor_caldata_ag_load_and_migrate",
    "open_cfw_nvdb_sensor_caldata_ag_update",
    "open_cfw_nvdb_sensor_caldata_ag_read",
    "open_cfw_nvdb_sensor_caldata_check",
}
DEFAULT_MATRIX = bytes.fromhex(
    "4bab51bf99d5bbbefd12d93ecb48e53eff0c8a3d02805f3f"
    "4ad1b2be88d66e3f849eed3d"
)


class NvdbSensorCaldataCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        cls.library = Path(cls.temporary.name) / f"nvdb_sensor_caldata{suffix}"
        subprocess.run(
            [
                "clang", "-std=c11", "-shared", "-fPIC", "-O1",
                "-include", str(FIXTURE / "nvdb_sensor_caldata_host.h"),
                str(SOURCE), str(FIXTURE / "nvdb_sensor_caldata_host.c"),
                "-o", str(cls.library),
            ],
            check=True,
            cwd=ROOT,
        )
        cls.loaded = ctypes.CDLL(str(cls.library))
        fptr = ctypes.POINTER(ctypes.c_float)
        cls.loaded.open_cfw_nvdb_sensor_caldata_update.argtypes = [
            fptr, fptr, fptr, ctypes.POINTER(ctypes.c_int32),
            ctypes.c_float, ctypes.POINTER(ctypes.c_ubyte),
        ]
        cls.loaded.open_cfw_nvdb_sensor_caldata_ag_update.argtypes = [fptr, fptr, fptr]
        cls.loaded.open_cfw_nvdb_sensor_caldata_ag_read.argtypes = [fptr, fptr, fptr]
        cls.loaded.open_cfw_test_nvdb_sensor_caldata_set_read.argtypes = [
            ctypes.c_char_p, ctypes.POINTER(ctypes.c_ubyte), ctypes.c_int,
        ]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.loaded.open_cfw_test_nvdb_sensor_caldata_reset()

    def bytes_array(self, name: str, size: int) -> bytes:
        return bytes((ctypes.c_ubyte * size).in_dll(self.loaded, name))

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

    def set_read(self, key: bytes, value: bytes, result: int) -> None:
        raw = (ctypes.c_ubyte * len(value)).from_buffer_copy(value)
        self.loaded.open_cfw_test_nvdb_sensor_caldata_set_read(key, raw, result)

    def test_default_initializers_only_fill_record_crc(self) -> None:
        primary_before = self.bytes_array("open_cfw_test_nvdb_sensor_caldata_record", 92)
        ag_before = self.bytes_array("open_cfw_test_nvdb_sensor_caldata_ag_record", 68)
        self.assertEqual(self.loaded.open_cfw_nvdb_sensor_caldata_default_initialize(), 0)
        self.assertEqual(self.loaded.open_cfw_nvdb_sensor_caldata_ag_default_initialize(), 0)
        primary = self.bytes_array("open_cfw_test_nvdb_sensor_caldata_record", 92)
        ag = self.bytes_array("open_cfw_test_nvdb_sensor_caldata_ag_record", 68)
        self.assertEqual(primary[:88], primary_before[:88])
        self.assertEqual(ag[:64], ag_before[:64])
        self.assertEqual(struct.unpack_from("<H", primary, 88)[0], 0xD886)
        self.assertEqual(struct.unpack_from("<H", ag, 64)[0], 0x82FC)
        self.assertEqual(primary[90:], b"\0\0")
        self.assertEqual(ag[66:], b"\0\0")

    def test_primary_update_preserves_exact_payload_layout_and_persists(self) -> None:
        a = (ctypes.c_float * 3)(1.0, 2.0, 3.0)
        b = (ctypes.c_float * 3)(4.0, 5.0, 6.0)
        c = (ctypes.c_float * 4)(7.0, 8.0, 9.0, 10.0)
        fixed = (ctypes.c_int32 * 4)(-1, 2, -3, 4)
        tail = (ctypes.c_ubyte * 24)(*range(24))
        self.loaded.open_cfw_nvdb_sensor_caldata_update(a, b, c, fixed, 1.5, tail)
        record = self.bytes_array("open_cfw_test_nvdb_sensor_caldata_record", 92)
        self.assertEqual(record[0], 1)
        self.assertEqual(struct.unpack_from("<3f", record, 4), (1.0, 2.0, 3.0))
        self.assertEqual(struct.unpack_from("<3f", record, 16), (4.0, 5.0, 6.0))
        self.assertEqual(struct.unpack_from("<4f", record, 28), (7.0, 8.0, 9.0, 10.0))
        self.assertEqual(struct.unpack_from("<4i", record, 44), (-1, 2, -3, 4))
        self.assertEqual(struct.unpack_from("<f", record, 60)[0], 1.5)
        self.assertEqual(record[64:88], bytes(range(24)))
        self.assertEqual(struct.unpack_from("<H", record, 88)[0], self.crc16(record[:88]))
        self.assertEqual(self.word("open_cfw_test_nvdb_sensor_caldata_last_write_length"), 92)
        self.assertEqual(self.bytes_array("open_cfw_test_nvdb_sensor_caldata_written", 92), record)

    def test_primary_migration_rewrites_current_defaults_without_importing(self) -> None:
        self.loaded.open_cfw_nvdb_sensor_caldata_default_initialize()
        current = self.bytes_array("open_cfw_test_nvdb_sensor_caldata_record", 92)
        stale = bytearray(92)
        stale[0] = 0
        self.set_read(b"nvSCald", bytes(stale), 1)
        self.loaded.open_cfw_nvdb_sensor_caldata_load_and_migrate()
        self.assertEqual(self.bytes_array("open_cfw_test_nvdb_sensor_caldata_record", 92), current)
        self.assertEqual(self.bytes_array("open_cfw_test_nvdb_sensor_caldata_written", 92), current)

        self.loaded.open_cfw_test_nvdb_sensor_caldata_reset()
        self.loaded.open_cfw_nvdb_sensor_caldata_default_initialize()
        current = self.bytes_array("open_cfw_test_nvdb_sensor_caldata_record", 92)
        stale[0] = 1
        self.set_read(b"nvSCald", bytes(stale), 1)
        self.loaded.open_cfw_nvdb_sensor_caldata_load_and_migrate()
        self.assertEqual(self.word("open_cfw_test_nvdb_sensor_caldata_write_count"), 0)
        self.assertEqual(self.bytes_array("open_cfw_test_nvdb_sensor_caldata_record", 92), current)

    def test_ag_update_allows_independent_partial_payload_updates(self) -> None:
        a = (ctypes.c_float * 3)(10.0, 11.0, 12.0)
        self.loaded.open_cfw_nvdb_sensor_caldata_ag_update(a, None, None)
        record = self.bytes_array("open_cfw_test_nvdb_sensor_caldata_ag_record", 68)
        self.assertEqual(struct.unpack_from("<3f", record, 4), (10.0, 11.0, 12.0))
        self.assertEqual(record[28:64], DEFAULT_MATRIX)
        self.assertEqual(struct.unpack_from("<H", record, 64)[0], self.crc16(record[:64]))
        self.assertEqual(self.word("open_cfw_test_nvdb_sensor_caldata_last_write_length"), 68)
        self.assertEqual(self.loaded.open_cfw_nvdb_sensor_caldata_ag_load_and_migrate(), 0)

    def test_ag_read_imports_flash_and_replaces_only_suspicious_pattern(self) -> None:
        stored = bytearray(self.bytes_array("open_cfw_test_nvdb_sensor_caldata_ag_record", 68))
        struct.pack_into("<3f", stored, 4, 1.0, 2.0, 3.0)
        struct.pack_into("<3f", stored, 16, 4.0, 5.0, 6.0)
        struct.pack_into("<f", stored, 28, 0.7)
        struct.pack_into("<f", stored, 48, -0.8)
        self.set_read(b"nvSCaldAG", bytes(stored), 7)
        a = (ctypes.c_float * 3)()
        b = (ctypes.c_float * 3)()
        matrix = (ctypes.c_float * 9)()
        self.assertEqual(self.loaded.open_cfw_nvdb_sensor_caldata_ag_read(a, b, matrix), 7)
        self.assertEqual(tuple(a), (1.0, 2.0, 3.0))
        self.assertEqual(tuple(b), (4.0, 5.0, 6.0))
        self.assertEqual(bytes(matrix), DEFAULT_MATRIX)
        self.assertEqual(self.word("open_cfw_test_nvdb_sensor_caldata_diagnostic_count"), 1)
        imported = self.bytes_array("open_cfw_test_nvdb_sensor_caldata_ag_record", 68)
        self.assertEqual(imported[28:64], DEFAULT_MATRIX)

    def test_pattern_gate_and_boundaries_are_exact(self) -> None:
        record = (ctypes.c_ubyte * 68).in_dll(
            self.loaded, "open_cfw_test_nvdb_sensor_caldata_ag_record"
        )
        struct.pack_into("<f", record, 28, 0.6)
        struct.pack_into("<f", record, 48, -0.8)
        self.assertEqual(self.loaded.open_cfw_nvdb_sensor_caldata_check(), 0)

        struct.pack_into("<f", record, 28, 0.7)
        self.loaded.open_cfw_test_nvdb_sensor_caldata_set_pattern_check(0)
        self.assertEqual(self.loaded.open_cfw_nvdb_sensor_caldata_check(), 0)
        self.loaded.open_cfw_test_nvdb_sensor_caldata_set_pattern_check(1)
        self.assertEqual(self.loaded.open_cfw_nvdb_sensor_caldata_check(), 1)

    def test_thumb_compile_has_exact_global_text_surface(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "nvdb_sensor_caldata.o"
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
            "519df61d63a85b6527c8093185431b3e877ef42cefbd1ca0ebdd33051434e2f0",
        )


if __name__ == "__main__":
    unittest.main()
