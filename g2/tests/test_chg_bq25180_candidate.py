import ctypes
import hashlib
import platform
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/chg_bq25180.c"
FIXTURE = ROOT / "tests/fixtures"
SOURCE_SHA256 = "0291aa058fd90a957b97fd0066e2d49bf16676b761662a32bdb5d717be74067b"
EXPECTED_SYMBOLS = {
    "open_cfw_bq25180_hardware_init",
    "open_cfw_bq25180_read_device_id",
    "open_cfw_bq25180_read_event",
    "open_cfw_bq25180_read_state",
    "open_cfw_bq25180_refresh_status",
    "open_cfw_bq25180_set_battery_overcurrent",
    "open_cfw_bq25180_set_battery_regulation_voltage",
    "open_cfw_bq25180_set_battery_undervoltage_lockout",
    "open_cfw_bq25180_set_charge_enabled",
    "open_cfw_bq25180_set_fastcharge_current",
    "open_cfw_bq25180_set_input_current_limit",
    "open_cfw_bq25180_set_precharge_ratio",
    "open_cfw_bq25180_set_precharge_threshold",
    "open_cfw_bq25180_set_safety_timer",
    "open_cfw_bq25180_set_system_mode",
    "open_cfw_bq25180_set_system_voltage",
    "open_cfw_bq25180_set_termination_percent",
    "open_cfw_bq25180_set_ts_auto_enabled",
    "open_cfw_bq25180_set_ts_enabled",
    "open_cfw_bq25180_set_vdppm_enabled",
    "open_cfw_bq25180_set_vindpm",
    "open_cfw_bq25180_set_watchdog",
}


class Bq25180CandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        cls.library = Path(cls.temporary.name) / f"chg_bq25180{suffix}"
        subprocess.run([
            "clang", "-std=c11", "-shared", "-fPIC", "-O1",
            "-include", str(FIXTURE / "chg_bq25180_host.h"),
            str(SOURCE), str(FIXTURE / "chg_bq25180_host.c"),
            "-o", str(cls.library),
        ], check=True, cwd=ROOT)
        cls.loaded = ctypes.CDLL(str(cls.library))
        cls.loaded.open_cfw_bq25180_read_event.argtypes = [ctypes.POINTER(ctypes.c_ubyte)]
        cls.loaded.open_cfw_bq25180_read_event.restype = ctypes.c_int
        cls.loaded.open_cfw_bq25180_read_state.argtypes = [ctypes.POINTER(ctypes.c_ushort)]
        cls.loaded.open_cfw_bq25180_read_state.restype = ctypes.c_int
        cls.loaded.open_cfw_bq25180_set_battery_regulation_voltage.argtypes = [
            ctypes.c_ushort
        ]
        cls.loaded.open_cfw_bq25180_set_fastcharge_current.argtypes = [
            ctypes.c_ushort
        ]
        cls.loaded.open_cfw_bq25180_set_battery_undervoltage_lockout.argtypes = [
            ctypes.c_ushort
        ]
        cls.loaded.open_cfw_bq25180_set_input_current_limit.argtypes = [
            ctypes.c_ushort
        ]
        cls.loaded.open_cfw_bq25180_set_termination_percent.argtypes = [
            ctypes.c_ubyte
        ]
        cls.loaded.open_cfw_bq25180_hardware_init.restype = ctypes.c_int
        cls.loaded.open_cfw_bq25180_refresh_status.restype = ctypes.c_int

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.loaded.open_cfw_test_bq25180_reset()

    def registers(self):
        return (ctypes.c_ubyte * 13).in_dll(
            self.loaded, "open_cfw_test_bq25180_registers"
        )

    def uint(self, name: str) -> int:
        return ctypes.c_uint.in_dll(self.loaded, name).value

    def test_read_event_and_state_preserve_wire_layout(self) -> None:
        registers = self.registers()
        registers[2] = 0xa5
        registers[0] = 0x61
        registers[1] = 0x82
        event = ctypes.c_ubyte()
        state = ctypes.c_ushort()
        self.assertEqual(self.loaded.open_cfw_bq25180_read_event(ctypes.byref(event)), 1)
        self.assertEqual(self.loaded.open_cfw_bq25180_read_state(ctypes.byref(state)), 1)
        self.assertEqual(event.value, 0xa5)
        self.assertEqual(state.value, 0x8261)
        self.assertEqual(self.uint("open_cfw_test_bq25180_charge_state"), 3)
        self.assertEqual(self.uint("open_cfw_test_bq25180_read_count"), 3)
        self.assertEqual(ctypes.c_ubyte.in_dll(self.loaded, "open_cfw_test_bq25180_last_bus").value, 7)
        self.assertEqual(ctypes.c_ubyte.in_dll(self.loaded, "open_cfw_test_bq25180_last_address").value, 0x6a)

    def test_voltage_and_current_encodings(self) -> None:
        registers = self.registers()
        self.loaded.open_cfw_bq25180_set_battery_regulation_voltage(4400)
        self.assertEqual(registers[3], 90)
        for current, expected in ((5, 0), (35, 30), (36, 30), (91, 36), (1000, 127)):
            registers[4] = 0x80
            self.loaded.open_cfw_bq25180_set_fastcharge_current(current)
            self.assertEqual(registers[4], 0x80 | expected)

    def test_undervoltage_threshold_buckets(self) -> None:
        registers = self.registers()
        for voltage, expected in (
            (3000, 2), (2800, 3), (2600, 4), (2400, 5), (2200, 6), (2000, 7)
        ):
            registers[6] = 0x07
            self.loaded.open_cfw_bq25180_set_battery_undervoltage_lockout(voltage)
            self.assertEqual((registers[6] >> 3) & 7, expected)
            self.assertEqual(registers[6] & 7, 7)

    def test_input_limit_and_termination_thresholds(self) -> None:
        registers = self.registers()
        for current, expected in (
            (0, 0), (100, 1), (200, 2), (300, 3),
            (400, 4), (500, 5), (700, 6), (1100, 7),
        ):
            self.loaded.open_cfw_bq25180_set_input_current_limit(current)
            self.assertEqual(registers[8] & 7, expected)
        for percent, expected in ((0, 0), (5, 1), (10, 2), (20, 3)):
            self.loaded.open_cfw_bq25180_set_termination_percent(percent)
            self.assertEqual((registers[5] >> 4) & 3, expected)

    def test_hardware_init_matches_stock_default_register_image(self) -> None:
        registers = self.registers()
        self.assertEqual(self.loaded.open_cfw_bq25180_hardware_init(), 0)
        self.assertEqual(list(registers), [
            0x00, 0x00, 0x00, 0x5a, 0x24, 0x24, 0x1f,
            0x44, 0x06, 0x00, 0x21, 0x00, 0xf0,
        ])
        self.assertEqual(self.uint("open_cfw_test_bq25180_diagnostic_count"), 3)
        self.assertEqual(self.uint("open_cfw_test_bq25180_last_diagnostic"), 5)

    def test_hardware_init_rejects_nonzero_device_id(self) -> None:
        registers = self.registers()
        registers[12] = 0xc1
        self.assertEqual(self.loaded.open_cfw_bq25180_hardware_init(), -1)
        self.assertEqual(self.uint("open_cfw_test_bq25180_write_count"), 0)
        self.assertEqual(self.uint("open_cfw_test_bq25180_last_diagnostic"), 4)

    def test_refresh_updates_runtime_record(self) -> None:
        registers = self.registers()
        registers[0] = 0x40
        registers[1] = 0x12
        registers[2] = 0x34
        self.assertEqual(self.loaded.open_cfw_bq25180_refresh_status(), 0)
        runtime = (ctypes.c_ubyte * 24).in_dll(
            self.loaded, "open_cfw_test_bq25180_runtime"
        )
        self.assertEqual(runtime[0x14], 0x34)
        self.assertEqual(bytes(runtime[0x16:0x18]), b"\x40\x12")
        self.assertEqual(self.uint("open_cfw_test_bq25180_charge_state"), 2)

    def test_candidate_exports_are_explicit_and_source_is_pinned(self) -> None:
        output = subprocess.run(
            ["nm", "-g", str(self.library)], check=True,
            text=True, capture_output=True,
        ).stdout
        for symbol in EXPECTED_SYMBOLS:
            self.assertIn(symbol, output)
        self.assertNotIn("DRV_Bq25180", output)
        self.assertEqual(hashlib.sha256(SOURCE.read_bytes()).hexdigest(), SOURCE_SHA256)

    def test_thumb_compile_has_exact_global_text_surface(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "chg_bq25180.o"
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


if __name__ == "__main__":
    unittest.main()
