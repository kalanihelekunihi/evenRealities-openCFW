import ctypes
import hashlib
import platform
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/at_core_sensor.c"
FIXTURE = ROOT / "tests/fixtures"
EXPECTED_SYMBOLS = {
    "open_cfw_at_info_handler",
    "open_cfw_at_reset_handler",
    "open_cfw_at_psn_handler",
    "open_cfw_at_imu_rawdata_handler",
    "open_cfw_at_imu_euler_handler",
    "open_cfw_at_screen_x_handler",
    "open_cfw_at_screen_y_handler",
    "open_cfw_at_als_read_handler",
    "open_cfw_at_als_handler",
    "open_cfw_at_brightness_handler",
    "open_cfw_at_als_scale_read_handler",
    "open_cfw_at_brightness_read_handler",
}
SOURCE_SHA256 = "2be0e0f81c74d3ec60f2a44fbcac8f7aff6c3f80e155d66c3c130a698ac285b3"


class AtCoreSensorCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        cls.library = Path(cls.temporary.name) / f"at_core_sensor{suffix}"
        subprocess.run(
            [
                "clang", "-std=c11", "-shared", "-fPIC", "-O1",
                "-include", str(FIXTURE / "at_core_sensor_host.h"),
                str(SOURCE), str(FIXTURE / "at_core_sensor_host.c"),
                "-o", str(cls.library),
            ],
            check=True,
            cwd=ROOT,
        )
        cls.loaded = ctypes.CDLL(str(cls.library))
        for name in (
            "open_cfw_at_psn_handler",
            "open_cfw_at_imu_rawdata_handler",
            "open_cfw_at_screen_y_handler",
            "open_cfw_at_als_handler",
            "open_cfw_at_brightness_handler",
        ):
            getattr(cls.loaded, name).argtypes = [ctypes.c_char_p]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.loaded.open_cfw_test_reset()

    def uint(self, name: str) -> int:
        return ctypes.c_uint.in_dll(self.loaded, name).value

    def int_array(self, name: str, count: int) -> list[int]:
        values = (ctypes.c_int * 8).in_dll(self.loaded, name)
        return [values[index] for index in range(count)]

    def output_log(self) -> bytes:
        return ctypes.string_at(
            ctypes.addressof(
                (ctypes.c_char * 4096).in_dll(
                    self.loaded, "open_cfw_test_output_log"
                )
            )
        )

    def test_info_reports_identity_block_and_returns_one(self) -> None:
        self.assertEqual(self.loaded.open_cfw_at_info_handler(), 1)
        self.assertEqual(
            self.output_log(),
            b"Product name:     [S200]\r\n"
            b"Hardware version: [1.0.0.0]\r\n"
            b"Software version: [2.2.6.10]\r\n"
            b"Codec version:    [2.0.0.0]\r\n"
            b"Touch version:    [3.0.0.0]\r\n"
            b"Compile time:     [Jul  6 2026 21:37:47]\r\n"
            b"Product SN:       [12345678901234]\r\n"
            b"BLE NAME:         [G2]\r\n"
            b"BLE ADDR:         [33:22:11:CC:BB:AA]\r\n"
            b"INFO+OK\r\n",
        )
        self.assertEqual(self.uint("open_cfw_test_output_count"), 10)
        self.assertEqual(self.uint("open_cfw_test_psn_read_count"), 1)
        self.assertEqual(
            self.int_array("open_cfw_test_psn_read_slots", 1), [0]
        )

    def test_reset_acknowledges_then_invokes_provider(self) -> None:
        self.assertEqual(self.loaded.open_cfw_at_reset_handler(), 1)
        self.assertEqual(self.output_log(), b"RESET+OK\r\n")
        self.assertEqual(self.uint("open_cfw_test_reset_count"), 1)

    def test_psn_accepts_exactly_fourteen_bytes(self) -> None:
        self.assertEqual(
            self.loaded.open_cfw_at_psn_handler(b"ABCDEFGHIJKLMN"), 1
        )
        self.assertEqual(self.output_log(), b"ABCDEFGHIJKLMNPSN+OK\r\n")
        self.assertEqual(self.uint("open_cfw_test_psn_write_count"), 1)
        self.assertEqual(
            ctypes.c_int.in_dll(
                self.loaded, "open_cfw_test_psn_write_slot"
            ).value,
            0,
        )
        self.assertEqual(
            ctypes.string_at(
                ctypes.addressof(
                    (ctypes.c_char * 32).in_dll(
                        self.loaded, "open_cfw_test_psn_write_value"
                    )
                )
            ),
            b"ABCDEFGHIJKLMN",
        )

    def test_psn_rejects_other_lengths_but_still_acknowledges(self) -> None:
        for rejected in (b"", b"ABCDEFGHIJKLM", b"ABCDEFGHIJKLMNO"):
            self.loaded.open_cfw_test_reset()
            self.assertEqual(self.loaded.open_cfw_at_psn_handler(rejected), 1)
            self.assertEqual(
                self.output_log(),
                b"AT^PSN: set PSN: The parameter is incorrect. Please enter "
                b"the correct command (len 14)\r\nPSN+OK\r\n",
            )
            self.assertEqual(self.uint("open_cfw_test_psn_write_count"), 0)

    def test_imu_rawdata_starts_and_stops(self) -> None:
        self.assertEqual(self.loaded.open_cfw_at_imu_rawdata_handler(b"1"), 1)
        self.assertEqual(
            self.output_log(), b"AT^IMU_RAWDATA+OK:type=1\r\n"
        )
        self.assertEqual(
            self.int_array(
                "open_cfw_test_imu_rawdata_values",
                self.uint("open_cfw_test_imu_rawdata_count"),
            ),
            [1],
        )
        self.loaded.open_cfw_test_reset()
        self.assertEqual(self.loaded.open_cfw_at_imu_rawdata_handler(b"0"), 1)
        self.assertEqual(
            self.output_log(), b"AT^IMU_RAWDATA+OK:type=0\r\n"
        )
        self.assertEqual(
            self.int_array(
                "open_cfw_test_imu_rawdata_values",
                self.uint("open_cfw_test_imu_rawdata_count"),
            ),
            [0],
        )

    def test_imu_rawdata_rejects_other_values_and_returns_zero(self) -> None:
        for rejected in (b"2", b"-1", b"17"):
            self.loaded.open_cfw_test_reset()
            self.assertEqual(
                self.loaded.open_cfw_at_imu_rawdata_handler(rejected), 0
            )
            self.assertEqual(
                self.output_log(),
                b"AT^IMU_RAWDATA+ERROR: invalid parameter, use 1 to start "
                b"or 0 to stop\r\n",
            )
            self.assertEqual(self.uint("open_cfw_test_imu_rawdata_count"), 0)

    def test_imu_euler_promotes_three_floats(self) -> None:
        self.assertEqual(self.loaded.open_cfw_at_imu_euler_handler(), 1)
        self.assertEqual(
            self.output_log(),
            b"AT^IMU_EULER+OK:roll=1.50,pitch=-2.25,yaw=3.00\r\n",
        )

    def test_screen_x_is_a_stub_acknowledgement(self) -> None:
        self.assertEqual(self.loaded.open_cfw_at_screen_x_handler(), 1)
        self.assertEqual(self.output_log(), b"AT^SCRN_X+OK\r\n")
        self.assertEqual(self.uint("open_cfw_test_screen_height_count"), 0)

    def test_screen_y_accepts_zero_through_192(self) -> None:
        for accepted in (b"0", b"1", b"96", b"192"):
            self.loaded.open_cfw_test_reset()
            self.assertEqual(
                self.loaded.open_cfw_at_screen_y_handler(accepted), 1
            )
            self.assertEqual(self.output_log(), b"AT^SCRN_Y+OK\r\n")
            self.assertEqual(
                self.int_array(
                    "open_cfw_test_screen_height_values",
                    self.uint("open_cfw_test_screen_height_count"),
                ),
                [int(accepted)],
            )

    def test_screen_y_rejects_193_and_above_and_negatives(self) -> None:
        for rejected in (b"193", b"200", b"65535", b"-1"):
            self.loaded.open_cfw_test_reset()
            self.assertEqual(
                self.loaded.open_cfw_at_screen_y_handler(rejected), 1
            )
            self.assertEqual(
                self.output_log(),
                b"AT^SCRN_Y Error,height value must be 1 - 192.\r\n",
            )
            self.assertEqual(self.uint("open_cfw_test_screen_height_count"), 0)

    def test_als_read_formats_through_bounded_buffer(self) -> None:
        self.assertEqual(self.loaded.open_cfw_at_als_read_handler(), 1)
        self.assertEqual(
            self.output_log(),
            "AT^ALS_READ+OK:ALS值=1234, LUX_BASE=-77\r\n".encode("utf-8"),
        )
        self.assertEqual(self.uint("open_cfw_test_snprintf_count"), 1)

    def test_als_enables_disables_and_acknowledges_every_value(self) -> None:
        self.assertEqual(self.loaded.open_cfw_at_als_handler(b"1"), 1)
        self.assertEqual(self.output_log(), b"AT^ALS+OK:enable=1\r\n")
        self.assertEqual(
            self.int_array(
                "open_cfw_test_als_enable_values",
                self.uint("open_cfw_test_als_enable_count"),
            ),
            [1],
        )
        self.assertEqual(self.uint("open_cfw_test_als_disable_count"), 0)
        self.loaded.open_cfw_test_reset()
        self.assertEqual(self.loaded.open_cfw_at_als_handler(b"0"), 1)
        self.assertEqual(
            self.int_array(
                "open_cfw_test_als_disable_values",
                self.uint("open_cfw_test_als_disable_count"),
            ),
            [0],
        )
        self.assertEqual(self.uint("open_cfw_test_als_enable_count"), 0)
        self.loaded.open_cfw_test_reset()
        self.assertEqual(self.loaded.open_cfw_at_als_handler(b"7"), 1)
        self.assertEqual(self.output_log(), b"AT^ALS+OK:enable=7\r\n")
        self.assertEqual(self.uint("open_cfw_test_als_enable_count"), 0)
        self.assertEqual(self.uint("open_cfw_test_als_disable_count"), 0)

    def test_brightness_forwards_without_local_validation(self) -> None:
        for forwarded in (b"0", b"42", b"255", b"-5"):
            self.loaded.open_cfw_test_reset()
            self.assertEqual(
                self.loaded.open_cfw_at_brightness_handler(forwarded), 1
            )
            value = int(forwarded)
            self.assertEqual(
                self.output_log(),
                f"AT^BRIGHTNESS+OK:brightness={value}\r\n".encode("ascii"),
            )
            self.assertEqual(
                self.int_array(
                    "open_cfw_test_brightness_write_values",
                    self.uint("open_cfw_test_brightness_write_count"),
                ),
                [value],
            )

    def test_als_scale_read_reports_provider_value(self) -> None:
        self.assertEqual(self.loaded.open_cfw_at_als_scale_read_handler(), 1)
        self.assertEqual(
            self.output_log(), b"AT^ALS_SCALE_READ+OK:scale_q10=1024\r\n"
        )

    def test_brightness_read_reports_provider_value(self) -> None:
        self.assertEqual(self.loaded.open_cfw_at_brightness_read_handler(), 1)
        self.assertEqual(
            self.output_log(), b"AT^BRIGHTNESS_READ+OK:brightness=55\r\n"
        )

    def test_thumb_compile_has_exact_global_text_surface(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "at_core_sensor.o"
            subprocess.run(
                [
                    "clang", "-target", "thumbv7em-none-eabi", "-mthumb", "-O2",
                    "-ffreestanding", "-fno-jump-tables", "-fomit-frame-pointer",
                    "-fno-builtin", "-mno-unaligned-access", "-fno-unwind-tables",
                    "-fno-asynchronous-unwind-tables", "-fropi", "-Wall",
                    "-Wextra", "-Werror", "-c", str(SOURCE), "-o", str(target),
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
