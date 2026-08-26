import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/service_box_detect.c"
FIXTURE = ROOT / "tests/fixtures/service_box_detect_host.c"
HEADER = ROOT / "tests/fixtures/service_box_detect_host.h"


class Event(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_uint16),
        ("length", ctypes.c_uint16),
        ("event", ctypes.c_uint8),
        ("reserved", ctypes.c_uint8 * 3),
    ]


class ServiceBoxDetectCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.library = Path(cls.temp.name) / "libservice_box_detect.so"
        subprocess.run(
            [
                "/usr/bin/clang", "-std=c11", "-shared", "-fPIC", "-O2",
                "-Wall", "-Wextra", "-Werror", "-include", str(HEADER),
                str(SOURCE), str(FIXTURE), "-o", str(cls.library),
            ],
            check=True,
        )
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.lib.host_box_reset()
        cls.lib.open_cfw_box_detect_process_case_state.argtypes = [ctypes.c_void_p]
        cls.lib.open_cfw_box_detect_common_data.argtypes = [
            ctypes.c_uint32, ctypes.c_void_p, ctypes.c_uint32
        ]
        cls.lib.open_cfw_box_detect_common_data.restype = ctypes.c_int
        cls.lib.open_cfw_box_detect_handle_event.argtypes = [ctypes.POINTER(Event)]

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.lib.host_box_reset()

    def u8(self, name):
        return ctypes.c_uint8.in_dll(self.lib, name)

    def u32(self, name):
        return ctypes.c_uint32.in_dll(self.lib, name).value

    def array(self, name, size):
        return (ctypes.c_uint8 * size).in_dll(self.lib, name)

    def test_timers_and_device_queue(self):
        self.lib.open_cfw_box_detect_timers_init()
        self.assertTrue(ctypes.c_void_p.in_dll(self.lib, "host_box_timer_force").value)
        self.lib.open_cfw_box_detect_force_timer_start()
        self.assertEqual(self.u32("host_box_timer_start_count"), 1)
        self.lib.open_cfw_box_detect_force_timer_expired()
        self.assertEqual(self.array("host_box_local", 4)[3], 1)
        self.assertEqual(self.u32("host_box_queue_count"), 0)
        self.lib.open_cfw_box_detect_timer_force_callback(None)
        self.assertEqual(self.u32("host_box_queue_count"), 1)
        self.lib.open_cfw_box_detect_timers_deinit()
        self.assertEqual(self.u32("host_box_timer_delete_count"), 2)

    def test_local_state_change_sync_and_force_policy(self):
        self.lib.open_cfw_box_detect_set_local_level(77)
        self.assertEqual(list(self.array("host_box_last_sync", 8)), [3, 4, 0, 1, 77, 0, 0, 0])
        self.assertEqual(self.u32("host_box_sync_count"), 1)
        self.lib.open_cfw_box_detect_set_force_out(1)
        self.assertEqual(self.u8("host_box_force").value, 1)
        self.assertEqual(self.u32("host_box_publish_count"), 1)
        self.assertEqual(self.u32("host_box_ring_change_count"), 1)
        self.assertEqual(self.u8("host_box_ring_reconnect").value, 1)
        self.lib.open_cfw_box_detect_clear_force_on_real_out()
        self.assertEqual(self.u8("host_box_force").value, 0)
        self.assertEqual(self.u32("host_box_notify_count"), 1)
        self.assertEqual(self.array("host_box_last_notify", 8)[7], 1)

    def test_case_state_intersection_and_outputs(self):
        local = self.array("host_box_local", 4)
        local[:] = (80, 1, 1, 1)
        message = (ctypes.c_uint8 * 8)(3, 4, 0, 1, 60, 1, 1, 1)
        self.lib.open_cfw_box_detect_process_case_state(message)
        self.assertEqual(list(self.array("host_box_case", 8)), [60, 1, 1, 1, 60, 1, 1, 1])
        self.assertEqual(self.u32("host_box_display_close_count"), 1)
        self.assertEqual(self.u32("host_box_input_out_count"), 1)
        self.assertEqual(self.u32("host_box_publish_count"), 1)
        self.assertEqual(self.u32("host_box_sync_count"), 1)
        self.assertEqual(self.array("host_box_last_sync", 8)[0], 2)

    def test_common_data_validation_and_dispatch(self):
        self.assertEqual(self.lib.open_cfw_box_detect_common_data(5, None, 8), -1)
        unknown = (ctypes.c_uint8 * 8)(9, 0, 0, 0, 0, 0, 0, 0)
        self.assertEqual(self.lib.open_cfw_box_detect_common_data(5, unknown, 8), -1)
        request = (ctypes.c_uint8 * 2)(1, 2)
        self.assertEqual(self.lib.open_cfw_box_detect_common_data(0, request, 2), 0)
        self.assertEqual(self.u32("host_box_case_request_count"), 1)
        sync_request = (ctypes.c_uint8 * 8)(1, 0, 0, 0, 0, 0, 0, 0)
        self.assertEqual(self.lib.open_cfw_box_detect_common_data(5, sync_request, 8), 0)
        self.assertEqual(self.array("host_box_last_sync", 8)[0], 2)

    def test_ring_event_lifecycle(self):
        self.u8("host_box_ring_reconnect").value = 1
        event = Event(type=3, length=1, event=3)
        self.lib.open_cfw_box_detect_handle_event(ctypes.byref(event))
        self.assertEqual(self.u8("host_box_ring_connected").value, 1)
        event.event = 4
        self.lib.open_cfw_box_detect_handle_event(ctypes.byref(event))
        self.assertEqual(self.u8("host_box_ring_connected").value, 0)
        self.assertEqual(self.u8("host_box_ring_reconnect").value, 0)
        self.u8("host_box_ring_reconnect").value = 1
        event.event = 7
        self.lib.open_cfw_box_detect_handle_event(ctypes.byref(event))
        self.assertEqual(self.u32("host_box_reconnect_count"), 1)

    def test_all_isolated_cortex_m55_entries_compile(self):
        with tempfile.TemporaryDirectory() as directory:
            for selector in range(1, 35):
                subprocess.run(
                    [
                        "/usr/bin/clang", "--target=thumbv7em-none-eabi",
                        "-mthumb", "-mcpu=cortex-m55", "-O2", "-ffreestanding",
                        "-fno-builtin", "-Wall", "-Wextra", "-Werror",
                        f"-DOPEN_CFW_BOX_DETECT_SELECTOR={selector}",
                        "-c", str(SOURCE), "-o", str(Path(directory) / f"{selector}.o"),
                    ],
                    check=True,
                )


if __name__ == "__main__":
    unittest.main()
