import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/sensor_hub.c"
FIXTURE = ROOT / "tests/fixtures/sensor_hub_host.c"
HEADER = ROOT / "tests/fixtures/sensor_hub_host.h"


class Record(ctypes.Structure):
    _fields_ = [
        ("id", ctypes.c_uint16),
        ("reserved", ctypes.c_uint16),
        ("argument", ctypes.c_uint32),
    ]


class SensorHubCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.output = Path(cls.temp.name) / "sensor-hub.so"
        subprocess.run([
            "/usr/bin/clang", "-std=c11", "-shared", "-fPIC", "-O2",
            "-Wall", "-Wextra", "-Werror", "-include", str(HEADER),
            str(SOURCE), str(FIXTURE), "-o", str(cls.output),
        ], check=True)
        cls.lib = ctypes.CDLL(str(cls.output))
        cls.lib.open_cfw_sensor_hub_send.argtypes = [ctypes.c_void_p]
        cls.lib.open_cfw_sensor_hub_message_process.argtypes = [ctypes.c_void_p]
        cls.lib.open_cfw_sensor_hub_collection_handler.argtypes = [ctypes.c_void_p]
        cls.lib.open_cfw_sensor_hub_set_mode_handler.argtypes = [ctypes.c_void_p]
        cls.lib.open_cfw_sensor_hub_function_open_handler.argtypes = [ctypes.c_void_p]
        cls.lib.open_cfw_sensor_hub_function_close_handler.argtypes = [ctypes.c_void_p]
        cls.lib.open_cfw_sensor_hub_parameter_config.argtypes = [
            ctypes.c_uint8, ctypes.POINTER(ctypes.c_uint32)]
        cls.lib.open_cfw_sensor_hub_open.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_sensor_hub_close.argtypes = [ctypes.c_uint32]
        cls.lib.host_sensor_hub_register_capture.argtypes = [ctypes.c_uint16]

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def scalar(self, ctype, name):
        return ctype.in_dll(self.lib, name)

    def array(self, ctype, name):
        return ctype.in_dll(self.lib, name)

    def setUp(self):
        self.lib.host_sensor_hub_reset()

    def test_resource_thread_timer_and_role_lifecycle(self):
        self.lib.open_cfw_sensor_hub_thread_init()
        self.lib.open_cfw_sensor_hub_resource_init()
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_sensor_hub_thread_new_count").value, 1)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_sensor_hub_queue_depth").value, 50)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_sensor_hub_queue_item_size").value, 8)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_sensor_hub_timer_new_type").value, 1)
        self.lib.open_cfw_sensor_hub_state_enter()
        self.lib.open_cfw_sensor_hub_state_exit()
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_sensor_hub_active_index").value, 5)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_sensor_hub_exit_index").value, 5)
        self.scalar(ctypes.c_uint32,
                    "host_sensor_hub_role_getter_value").value = 1
        self.lib.open_cfw_sensor_hub_role_init()
        self.assertEqual(self.scalar(ctypes.c_uint16,
                                     "host_sensor_hub_role").value, 3)
        self.lib.open_cfw_sensor_hub_thread_terminate()
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_sensor_hub_thread_terminate_count").value, 1)

    def test_bounded_queue_send_and_dispatch(self):
        record = Record(7, 0, 99)
        self.assertEqual(self.lib.open_cfw_sensor_hub_send(ctypes.byref(record)), -1)
        self.lib.open_cfw_sensor_hub_resource_init()
        self.assertEqual(self.lib.open_cfw_sensor_hub_send(ctypes.byref(record)), 0)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_sensor_hub_queue_count").value, 1)
        self.lib.host_sensor_hub_register_capture(7)
        self.lib.open_cfw_sensor_hub_message_process(ctypes.byref(record))
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_sensor_hub_dispatch_count").value, 1)
        dispatched = Record.in_dll(self.lib, "host_sensor_hub_dispatched")
        self.assertEqual((dispatched.id, dispatched.argument), (7, 99))
        unknown = Record(9, 0, 2)
        self.lib.open_cfw_sensor_hub_message_process(ctypes.byref(unknown))
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_sensor_hub_dispatch_count").value, 1)

    def test_timer_ota_gate_and_collection_modes(self):
        self.lib.open_cfw_sensor_hub_resource_init()
        self.scalar(ctypes.c_uint32,
                    "host_sensor_hub_timer_enabled").value = 1
        self.lib.open_cfw_sensor_hub_als_timer_callback(None)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_sensor_hub_last_tick").value, 1234)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_sensor_hub_queue_count").value, 1)
        self.scalar(ctypes.c_uint32,
                    "host_sensor_hub_ota_active_value").value = 1
        self.lib.open_cfw_sensor_hub_als_timer_callback(None)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_sensor_hub_queue_count").value, 1)
        start = Record(0, 0, 1)
        stop = Record(0, 0, 0)
        self.lib.open_cfw_sensor_hub_collection_handler(ctypes.byref(start))
        self.lib.open_cfw_sensor_hub_collection_handler(ctypes.byref(stop))
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_sensor_hub_imu_start_count").value, 1)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_sensor_hub_imu_stop_count").value, 1)

    def test_work_mode_mutual_exclusion_and_close_restore(self):
        self.lib.open_cfw_sensor_hub_resource_init()
        open_one = Record(5, 0, 1)
        self.lib.open_cfw_sensor_hub_function_open_handler(ctypes.byref(open_one))
        self.assertEqual(self.array(ctypes.c_uint8 * 4,
                                    "host_sensor_hub_states")[0], 1)
        queued = (Record * 64).in_dll(self.lib, "host_sensor_hub_queue")
        self.assertEqual((queued[0].id, queued[0].argument), (1, 0))
        self.array(ctypes.c_uint8 * 4,
                   "host_sensor_hub_states")[2] = 1
        before = self.scalar(ctypes.c_uint32,
                             "host_sensor_hub_queue_count").value
        open_two = Record(5, 0, 2)
        self.lib.open_cfw_sensor_hub_function_open_handler(ctypes.byref(open_two))
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_sensor_hub_queue_count").value, before)
        close_three = Record(6, 0, 3)
        self.lib.open_cfw_sensor_hub_function_close_handler(ctypes.byref(close_three))
        self.assertEqual(queued[before].argument, 2)

    def test_public_role_policy_and_parameter_dispatch(self):
        self.lib.open_cfw_sensor_hub_resource_init()
        self.scalar(ctypes.c_uint16, "host_sensor_hub_role").value = 2
        self.assertEqual(self.lib.open_cfw_sensor_hub_open(1), -1)
        values = (ctypes.c_uint32 * 2)(17, 23)
        self.assertEqual(self.lib.open_cfw_sensor_hub_parameter_config(1, values), -1)
        self.scalar(ctypes.c_uint16, "host_sensor_hub_role").value = 3
        self.assertEqual(self.lib.open_cfw_sensor_hub_open(4), 0)
        self.assertEqual(self.lib.open_cfw_sensor_hub_close(4), 0)
        self.assertEqual(self.lib.open_cfw_sensor_hub_parameter_config(1, values), 0)
        self.assertEqual(self.lib.open_cfw_sensor_hub_parameter_config(2, values), 0)
        self.assertEqual(self.lib.open_cfw_sensor_hub_parameter_config(5, values), 0)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_sensor_hub_threshold").value, 17)
        self.assertEqual(list(self.array(ctypes.c_uint32 * 2,
                                         "host_sensor_hub_period")), [17, 23])
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_sensor_hub_accel").value, 17)

    def test_calibration_and_display_contract(self):
        self.lib.open_cfw_sensor_hub_calibration_init()
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_sensor_hub_calibration_load_count").value, 1)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_sensor_hub_calibration_apply_count").value, 1)
        self.lib.open_cfw_sensor_hub_calibration_display_update(None)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_sensor_hub_screen_count").value, 1)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_sensor_hub_label_count").value, 2)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_sensor_hub_text_count").value, 2)
        self.lib.open_cfw_sensor_hub_calibration_success_display()
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_sensor_hub_screen_count").value, 1)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_sensor_hub_text_count").value, 4)

    def test_all_target_selectors_compile_strictly(self):
        for selector in range(1, 32):
            output = Path(self.temp.name) / f"selector-{selector}.o"
            subprocess.run([
                "/usr/bin/clang", "-std=c11", "-Os", "-ffreestanding",
                "-fno-builtin", "-fno-unwind-tables",
                "-fno-asynchronous-unwind-tables", "--target=arm-none-eabi",
                "-mcpu=cortex-m55", "-mthumb", "-Wall", "-Wextra", "-Werror",
                f"-DOPEN_CFW_SENSOR_HUB_SELECTOR={selector}",
                "-c", str(SOURCE), "-o", str(output),
            ], check=True)


if __name__ == "__main__":
    unittest.main()
