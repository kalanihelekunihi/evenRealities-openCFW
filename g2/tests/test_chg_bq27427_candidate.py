import ctypes
import hashlib
import platform
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/chg_bq27427.c"
FIXTURE = ROOT / "tests/fixtures"
SOURCE_SHA256 = "2e8389a849a07af5a1d59467da0a3fa0a30dcb29c63be736a4f1db6a78412dc9"
EXPECTED_SYMBOLS = {
    "open_cfw_bq27427_apply_settings",
    "open_cfw_bq27427_change_chemistry_profile",
    "open_cfw_bq27427_checksum_dm_block",
    "open_cfw_bq27427_configure_from_params",
    "open_cfw_bq27427_execute_control_word",
    "open_cfw_bq27427_hardware_init",
    "open_cfw_bq27427_init_wrapper",
    "open_cfw_bq27427_read_ai",
    "open_cfw_bq27427_read_ap",
    "open_cfw_bq27427_read_avail_capacity",
    "open_cfw_bq27427_read_battery_voltage",
    "open_cfw_bq27427_read_charge",
    "open_cfw_bq27427_read_dm_block",
    "open_cfw_bq27427_read_flags",
    "open_cfw_bq27427_read_full_cap_fil",
    "open_cfw_bq27427_read_full_cap_unfl",
    "open_cfw_bq27427_read_full_capacity",
    "open_cfw_bq27427_read_int_temp",
    "open_cfw_bq27427_read_nom_capacity",
    "open_cfw_bq27427_read_rem_cap_fil",
    "open_cfw_bq27427_read_rem_cap_unfl",
    "open_cfw_bq27427_read_rem_capacity",
    "open_cfw_bq27427_read_soc",
    "open_cfw_bq27427_read_soc_unfl",
    "open_cfw_bq27427_read_temperature",
    "open_cfw_bq27427_seal",
    "open_cfw_bq27427_set_cfgupdate",
    "open_cfw_bq27427_settings_apply_defaults",
    "open_cfw_bq27427_soft_reset",
    "open_cfw_bq27427_status_update",
    "open_cfw_bq27427_unseal",
    "open_cfw_bq27427_update_dm_block",
    "open_cfw_bq27427_write_dm_block",
}


class DmBlock(ctypes.Structure):
    _fields_ = [
        ("subclass", ctypes.c_ubyte),
        ("block", ctypes.c_ubyte),
        ("data", ctypes.c_ubyte * 32),
        ("valid", ctypes.c_ubyte),
        ("dirty", ctypes.c_ubyte),
    ]


class Settings(ctypes.Structure):
    _fields_ = [
        ("energy_full_design", ctypes.c_uint32),
        ("charge_full_design", ctypes.c_uint32),
        ("voltage_min_design", ctypes.c_uint32),
    ]


class Runtime(ctypes.Structure):
    _fields_ = [
        ("reserved", ctypes.c_uint32),
        ("state_of_charge", ctypes.c_int32),
        ("voltage_mv", ctypes.c_int32),
        ("average_current_ma", ctypes.c_int32),
        ("temperature_centi_c", ctypes.c_int32),
    ]


class Bq27427CandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        cls.library = Path(cls.temporary.name) / f"chg_bq27427{suffix}"
        subprocess.run([
            "clang", "-std=c11", "-shared", "-fPIC", "-O1",
            "-include", str(FIXTURE / "chg_bq27427_host.h"),
            str(SOURCE), str(FIXTURE / "chg_bq27427_host.c"),
            "-o", str(cls.library),
        ], check=True, cwd=ROOT)
        cls.loaded = ctypes.CDLL(str(cls.library))
        cls.loaded.open_cfw_bq27427_checksum_dm_block.argtypes = [
            ctypes.POINTER(DmBlock)
        ]
        cls.loaded.open_cfw_bq27427_checksum_dm_block.restype = ctypes.c_ubyte
        cls.loaded.open_cfw_bq27427_update_dm_block.argtypes = [
            ctypes.POINTER(DmBlock), ctypes.c_ubyte, ctypes.c_uint32
        ]
        cls.loaded.open_cfw_bq27427_apply_settings.argtypes = [
            ctypes.POINTER(Settings)
        ]
        cls.loaded.open_cfw_bq27427_status_update.restype = ctypes.c_int

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.loaded.open_cfw_test_bq27427_reset()

    def registers(self):
        return (ctypes.c_ubyte * 256).in_dll(
            self.loaded, "open_cfw_test_bq27427_registers"
        )

    def dm(self):
        return ((ctypes.c_ubyte * 32) * 256).in_dll(
            self.loaded, "open_cfw_test_bq27427_dm"
        )

    def test_register_reads_preserve_little_endian_and_signed_values(self) -> None:
        registers = self.registers()
        registers[0x1c], registers[0x1d] = 0x34, 0x12
        registers[0x10], registers[0x11] = 0x80, 0xff
        registers[0x18], registers[0x19] = 0x00, 0x80
        self.assertEqual(self.loaded.open_cfw_bq27427_read_soc(), 0x1234)
        self.assertEqual(self.loaded.open_cfw_bq27427_read_ai(), -128)
        self.assertEqual(self.loaded.open_cfw_bq27427_read_ap(), -32768)
        self.assertEqual(
            ctypes.c_ubyte.in_dll(
                self.loaded, "open_cfw_test_bq27427_last_bus"
            ).value,
            7,
        )
        self.assertEqual(
            ctypes.c_ubyte.in_dll(
                self.loaded, "open_cfw_test_bq27427_last_address"
            ).value,
            0x55,
        )

    def test_dm_checksum_and_big_endian_update(self) -> None:
        block = DmBlock()
        block.valid = 1
        block.data[0] = 1
        block.data[31] = 2
        self.assertEqual(
            self.loaded.open_cfw_bq27427_checksum_dm_block(
                ctypes.byref(block)
            ),
            0xfc,
        )
        self.loaded.open_cfw_bq27427_update_dm_block(
            ctypes.byref(block), 0, 0x1234
        )
        self.assertEqual(bytes(block.data[6:8]), b"\x12\x34")
        self.assertEqual(block.dirty, 1)

    def test_product_defaults_recreate_data_memory_updates(self) -> None:
        self.loaded.open_cfw_bq27427_settings_apply_defaults()
        dm = self.dm()
        self.assertEqual(bytes(dm[82][2:4]), b"\x03\x00")
        self.assertEqual(bytes(dm[82][6:8]), b"\x00\x50")
        self.assertEqual(bytes(dm[82][8:10]), b"\x00\xf0")
        self.assertEqual(bytes(dm[82][10:12]), b"\x0c\x1c")
        self.assertEqual(dm[64][4], 43)
        self.assertEqual(dm[105][5], 40)

    def test_invalid_settings_do_not_touch_the_bus(self) -> None:
        settings = Settings(37500, 80, 3100)
        self.loaded.open_cfw_bq27427_apply_settings(ctypes.byref(settings))
        self.assertEqual(
            ctypes.c_uint32.in_dll(
                self.loaded, "open_cfw_test_bq27427_write_count"
            ).value,
            0,
        )

    def test_status_update_populates_exact_runtime_offsets(self) -> None:
        registers = self.registers()
        registers[0x06] = 1
        registers[0x1c], registers[0x1d] = 75, 0
        registers[0x02], registers[0x03] = 0xa5, 0x0b  # 2981 -> 25.0 C
        registers[0x04], registers[0x05] = 0xe4, 0x0c  # 3300 mV
        registers[0x10], registers[0x11] = 0x85, 0xff  # -123 mA
        self.assertEqual(self.loaded.open_cfw_bq27427_status_update(), 0)
        runtime = Runtime.in_dll(self.loaded, "open_cfw_test_bq27427_runtime")
        self.assertEqual(runtime.state_of_charge, 75)
        self.assertEqual(runtime.voltage_mv, 3300)
        self.assertEqual(runtime.average_current_ma, -123)
        self.assertEqual(runtime.temperature_centi_c, 2500)

    def test_zero_or_ff_flags_fail_closed(self) -> None:
        registers = self.registers()
        registers[0x06] = 0
        self.assertEqual(self.loaded.open_cfw_bq27427_status_update(), -1)
        registers[0x06] = 0xff
        self.assertEqual(self.loaded.open_cfw_bq27427_status_update(), -1)

    def test_candidate_exports_and_source_are_pinned(self) -> None:
        output = subprocess.run(
            ["nm", "-g", str(self.library)], check=True,
            text=True, capture_output=True,
        ).stdout
        for symbol in EXPECTED_SYMBOLS:
            self.assertIn(symbol, output)
        self.assertNotIn("DRV_Bq27427", output)
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(), SOURCE_SHA256
        )

    def test_thumb_compile_has_exact_global_text_surface(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "chg_bq27427.o"
            subprocess.run([
                "clang", "-target", "thumbv7em-none-eabi", "-mthumb",
                "-std=c11", "-O2", "-ffreestanding", "-fno-jump-tables",
                "-fomit-frame-pointer", "-fno-builtin", "-mno-unaligned-access",
                "-fno-unwind-tables", "-fno-asynchronous-unwind-tables",
                "-fropi", "-Wall", "-Wextra", "-Werror", "-c",
                str(SOURCE), "-o", str(target),
            ], check=True, cwd=ROOT)
            symbols = subprocess.run(
                ["nm", str(target)], check=True, capture_output=True, text=True
            ).stdout
            observed = {
                fields[2]
                for line in symbols.splitlines()
                if len(fields := line.split()) == 3 and fields[1] == "T"
            }
            self.assertEqual(observed, EXPECTED_SYMBOLS)


if __name__ == "__main__":
    unittest.main()
