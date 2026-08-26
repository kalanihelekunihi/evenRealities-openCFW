import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/als.c"
FIXTURE = ROOT / "tests/fixtures/als_host.c"
HEADER = ROOT / "tests/fixtures/als_host.h"


class AlsCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.output = Path(cls.temp.name) / "als.so"
        subprocess.run([
            "/usr/bin/clang", "-std=c11", "-shared", "-fPIC", "-O2",
            "-Wall", "-Wextra", "-Werror", "-include", str(HEADER),
            str(SOURCE), str(FIXTURE), "-o", str(cls.output),
        ], check=True)
        cls.lib = ctypes.CDLL(str(cls.output))
        for name in (
            "open_cfw_als_clamp_brightness", "open_cfw_als_bucket_index",
            "open_cfw_als_bucket_brightness", "open_cfw_als_brightness_for_lux",
            "open_cfw_als_apply_scale", "open_cfw_als_target_for_bucket",
            "open_cfw_als_calculate_scale", "open_cfw_als_move_toward",
            "open_cfw_als_filter_value_by_pitch", "open_cfw_als_raw_latest",
            "open_cfw_als_raw_peak", "open_cfw_als_samples_vary",
            "open_cfw_als_extreme_dark_ready", "open_cfw_als_read_data",
            "open_cfw_als_can_fast_dim", "open_cfw_als_get_scale",
        ):
            getattr(cls.lib, name).restype = ctypes.c_uint32
        cls.lib.open_cfw_als_sync_handler.argtypes = [
            ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32]

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def scalar(self, ctype, name):
        return ctype.in_dll(self.lib, name)

    def array(self, ctype, name):
        return ctype.in_dll(self.lib, name)

    def setUp(self):
        self.lib.host_als_reset()

    def test_curve_clamp_scale_and_motion_contract(self):
        self.assertEqual(self.lib.open_cfw_als_clamp_brightness(0), 35)
        self.assertEqual(self.lib.open_cfw_als_clamp_brightness(101), 100)
        self.assertEqual(
            [self.lib.open_cfw_als_bucket_index(v)
             for v in (10, 11, 200, 201, 400, 401, 1301)],
            [0, 1, 1, 2, 2, 3, 5])
        self.assertEqual(
            [self.lib.open_cfw_als_bucket_brightness(i) for i in range(6)],
            [35, 50, 70, 70, 100, 100])
        self.assertEqual(self.lib.open_cfw_als_apply_scale(70, 1024), 70)
        self.assertEqual(self.lib.open_cfw_als_calculate_scale(70, 35), 614)
        self.assertEqual(self.lib.open_cfw_als_calculate_scale(70, 100), 1434)
        self.assertEqual(self.lib.open_cfw_als_move_toward(70, 50, 2), 52)
        self.assertEqual(self.lib.open_cfw_als_move_toward(35, 50, 5), 45)
        self.assertEqual(self.lib.open_cfw_als_move_toward(49, 50, 5), 49)

    def test_sample_windows_variance_and_extreme_dark(self):
        for value in (10, 20, 30, 400, 50):
            self.lib.open_cfw_als_raw_push(value)
        self.assertEqual(self.lib.open_cfw_als_raw_peak(), 400)
        self.assertEqual(self.lib.open_cfw_als_samples_vary(), 1)
        self.lib.open_cfw_als_raw_reset()
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_als_raw_count").value, 0)
        for _ in range(19):
            self.lib.open_cfw_als_dark_push(2)
        self.lib.open_cfw_als_dark_push(3)
        self.assertEqual(self.lib.open_cfw_als_extreme_dark_ready(), 1)
        self.lib.open_cfw_als_update_target_with_extreme_dark_mode(2)
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_als_extreme_dark").value, 1)
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_als_target_brightness").value, 15)
        self.lib.open_cfw_als_update_target_with_extreme_dark_mode(11)
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_als_extreme_dark").value, 0)

    def test_pitch_filter_and_opt3007_lux_conversion(self):
        self.scalar(ctypes.c_uint32, "host_als_raw_value").value = 77
        self.scalar(ctypes.c_float, "host_als_pitch").value = -31.0
        self.assertEqual(self.lib.open_cfw_als_filter_value_by_pitch(123), 77)
        self.scalar(ctypes.c_float, "host_als_pitch").value = -30.0
        self.assertEqual(self.lib.open_cfw_als_filter_value_by_pitch(123), 123)
        self.scalar(ctypes.c_uint32, "host_als_register_value").value = 0x100A
        self.assertEqual(self.lib.open_cfw_als_read_data(), 2)
        self.scalar(ctypes.c_uint32, "host_als_lux_base").value = 500000
        self.assertEqual(self.lib.open_cfw_als_read_data(), 10)

    def test_hardware_init_open_and_close_policy(self):
        self.assertEqual(self.lib.open_cfw_als_initialize(), 0)
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_als_power_sensor").value, 9)
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_als_power_enabled").value, 1)
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_als_delay_ticks").value, 5)
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_als_config_value").value, 3)
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_als_range_value").value, 0)
        self.scalar(ctypes.c_int32, "host_als_manufacturer").value = 0
        self.assertEqual(self.lib.open_cfw_als_initialize(), -1)
        self.scalar(ctypes.c_int32, "host_als_manufacturer").value = 0x5449
        self.assertEqual(self.lib.open_cfw_als_open(), 0)
        self.assertEqual(self.lib.open_cfw_als_open(), -1)
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_als_process_status").value, 1)
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_als_timer_ticks").value, 110)
        self.assertEqual(self.lib.open_cfw_als_close(), 0)
        self.assertEqual(self.lib.open_cfw_als_close(), -1)
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_als_power_enabled").value, 0)
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_als_timer_stop_count").value, 1)

    def test_target_and_learning_state(self):
        self.lib.open_cfw_als_update_target(300)
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_als_bucket").value, 2)
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_als_curve_brightness").value, 70)
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_als_target_brightness").value, 70)
        self.lib.open_cfw_als_learn_scale(100)
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_als_learn_count").value, 1)
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_als_scale").value, 1311)
        self.lib.open_cfw_als_set_scale(1)
        self.assertEqual(self.lib.open_cfw_als_get_scale(), 614)
        self.lib.open_cfw_als_set_scale(9999)
        self.assertEqual(self.lib.open_cfw_als_get_scale(), 1434)

    def test_timer_start_adjust_poll_and_manual_lock(self):
        self.scalar(ctypes.c_uint32, "host_als_register_value").value = 0x0064
        self.lib.open_cfw_als_timer_start()
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_als_process_status").value, 3)
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_als_timer_ticks").value, 1000)
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_als_sync_count").value, 1)
        self.scalar(ctypes.c_uint32, "host_als_target_brightness").value = 70
        self.scalar(ctypes.c_uint32, "host_als_brightness").value = 50
        self.lib.open_cfw_als_timer_adjust()
        sync = self.array(ctypes.c_uint8 * 2, "host_als_sync_record")
        self.assertEqual((sync[0], sync[1]), (52, 0))
        self.scalar(ctypes.c_uint32, "host_als_manual_lock_tick").value = 100
        self.scalar(ctypes.c_uint32, "host_als_tick").value = 200
        before = self.scalar(ctypes.c_uint32, "host_als_timer_start_count").value
        self.lib.open_cfw_als_timer_polling()
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_als_manual_lock_tick").value, 100)
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_als_timer_start_count").value, before)

    def test_sync_and_manual_brightness_contract(self):
        invalid = (ctypes.c_uint8 * 1)(20)
        self.assertEqual(self.lib.open_cfw_als_sync_handler(0, invalid, 1), -1)
        record = (ctypes.c_uint8 * 2)(64, 1)
        self.assertEqual(self.lib.open_cfw_als_sync_handler(0, record, 2), 0)
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_als_applied_brightness").value, 64)
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_als_display_brightness_value").value, 64)
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_als_notify_count").value, 1)
        self.assertEqual(self.lib.open_cfw_als_manual_set_brightness(51), 1)
        self.scalar(ctypes.c_uint32, "host_als_opened").value = 1
        self.scalar(ctypes.c_uint32, "host_als_raw_value").value = 300
        self.assertEqual(self.lib.open_cfw_als_manual_set_brightness(51), 0)
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_als_last_brightness").value, 50)
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_als_notify_application").value, 1)

    def test_all_target_selectors_compile_strictly(self):
        with tempfile.TemporaryDirectory() as directory:
            for selector in range(1, 39):
                output = Path(directory) / f"als-{selector}.o"
                subprocess.run([
                    "/usr/bin/clang", "--target=arm-none-eabi",
                    "-mcpu=cortex-m55", "-mthumb", "-mfloat-abi=hard",
                    "-mfpu=fpv5-d16", "-ffreestanding", "-fno-builtin",
                    "-fno-stack-protector", "-Oz", "-std=c11", "-Wall",
                    "-Wextra", "-Werror", f"-DOPEN_CFW_ALS_SELECTOR={selector}",
                    "-c", str(SOURCE), "-o", str(output),
                ], check=True)
                self.assertGreater(output.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
