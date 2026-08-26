import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/ring_service.c"
FIXTURE = ROOT / "tests/fixtures/ring_service_host.c"
HEADER = ROOT / "tests/fixtures/ring_service_host.h"


class RingServiceCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.output = Path(cls.temp.name) / "ring-service.so"
        subprocess.run([
            "/usr/bin/clang", "-std=c11", "-shared", "-fPIC", "-O2",
            "-Wall", "-Wextra", "-Werror", "-include", str(HEADER),
            str(SOURCE), str(FIXTURE), "-o", str(cls.output),
        ], check=True)
        cls.lib = ctypes.CDLL(str(cls.output))
        byte_pointer = ctypes.POINTER(ctypes.c_uint8)
        cls.lib.open_cfw_ring_service_cmd_touch_update.argtypes = [
            byte_pointer, ctypes.c_uint16]
        cls.lib.open_cfw_ring_service_cmd_battery_report.argtypes = [
            byte_pointer, ctypes.c_uint16]
        cls.lib.open_cfw_ring_service_cmd_wear_status.argtypes = [byte_pointer]
        cls.lib.open_cfw_ring_service_cmd_package_parse.argtypes = [
            byte_pointer, ctypes.c_uint16]
        cls.lib.open_cfw_ring_service_cmd_touch_update.restype = ctypes.c_int32
        cls.lib.open_cfw_ring_service_cmd_battery_report.restype = ctypes.c_int32

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def scalar(self, ctype, name):
        return ctype.in_dll(self.lib, name)

    def array(self, ctype, name):
        return ctype.in_dll(self.lib, name)

    def setUp(self):
        for name in (
            "host_ring_service_last_touch_tick", "host_ring_service_wear_started",
            "host_ring_service_battery_template", "host_ring_service_raw_count",
            "host_ring_service_message_event", "host_ring_service_message_count",
            "host_ring_service_posted_event", "host_ring_service_posted_event_count",
            "host_ring_service_input_count", "host_ring_service_battery_count",
            "host_ring_service_tick_value", "host_ring_service_wear_duration",
            "host_ring_service_wear_report_count", "host_ring_service_remove_count",
            "host_ring_service_push_count", "host_ring_service_owner",
            "host_ring_service_notify_value", "host_ring_service_notify_count",
            "host_ring_service_reconnect_count", "host_ring_service_reject_count",
        ):
            self.scalar(ctypes.c_uint32, name).value = 0
        for name in (
            "host_ring_service_wearing", "host_ring_service_owner_set",
            "host_ring_service_in_case_value", "host_ring_service_wear_status_value",
            "host_ring_service_imu_status_value", "host_ring_service_lcd_status_value",
        ):
            self.scalar(ctypes.c_uint8, name).value = 0
        for ctype, name in (
            (ctypes.c_uint8 * 16, "host_ring_service_raw"),
            (ctypes.c_uint8 * 16, "host_ring_service_message"),
            (ctypes.c_uint8 * 5, "host_ring_service_phy"),
            (ctypes.c_uint8 * 4, "host_ring_service_input"),
            (ctypes.c_uint32 * 2, "host_ring_service_battery"),
            (ctypes.c_uint8 * 6, "host_ring_service_mac"),
            (ctypes.c_uint8 * 6, "host_ring_service_rejected_mac"),
            (ctypes.c_uint32 * 8, "host_ring_service_delays"),
        ):
            ctypes.memset(ctypes.addressof(self.array(ctype, name)), 0,
                          ctypes.sizeof(ctype))

    @staticmethod
    def packet(*values):
        return (ctypes.c_uint8 * len(values))(*values)

    def test_outbound_frame_and_thread_message_contracts(self):
        self.lib.open_cfw_ring_service_heartbeat_process()
        raw = self.array(ctypes.c_uint8 * 16, "host_ring_service_raw")
        self.assertEqual(list(raw[:4]), [0, 0x1A, 0x94, 1])
        self.lib.open_cfw_ring_service_touch_report_time_process(0x1234)
        self.assertEqual(list(raw[:6]), [0, 0x1A, 0x8A, 1, 0x34, 0x12])
        self.lib.open_cfw_ring_service_send_touch_enable(0)
        self.assertEqual(list(raw[:8]), [0, 0x1A, 0x85, 1, 0xFF, 0xAA, 0xAA, 0xAA])
        self.lib.open_cfw_ring_service_send_status_bits(1, 1)
        self.assertEqual(list(raw[:8]), [0, 0x1A, 0x89, 1, 0xC0, 0, 0, 0])
        self.lib.open_cfw_ring_service_post_touch_report_time(0x4567)
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_ring_service_message_event").value,
                         0x1000)
        message = self.array(ctypes.c_uint8 * 16, "host_ring_service_message")
        self.assertEqual(list(message[:2]), [0x67, 0x45])

    def test_status_phy_and_callback_wrappers(self):
        self.scalar(ctypes.c_uint8, "host_ring_service_wear_status_value").value = 1
        self.scalar(ctypes.c_uint8, "host_ring_service_imu_status_value").value = 0
        self.lib.open_cfw_ring_service_send_glasses_status_event()
        message = self.array(ctypes.c_uint8 * 16, "host_ring_service_message")
        self.assertEqual(self.scalar(ctypes.c_uint32, "host_ring_service_message_event").value,
                         0x400)
        self.assertEqual(list(message[:2]), [1, 1])
        self.scalar(ctypes.c_uint8, "host_ring_service_in_case_value").value = 1
        self.lib.open_cfw_ring_service_send_glasses_status_event()
        self.assertEqual(list(message[:2]), [0, 0])
        self.lib.open_cfw_ring_service_set_phy_process(7)
        self.assertEqual(list(self.array(ctypes.c_uint8 * 5,
                                         "host_ring_service_phy")), [7, 0, 4, 1, 2])
        self.lib.open_cfw_ring_service_owner_connect_callback(0)
        self.assertEqual(self.scalar(ctypes.c_uint8, "host_ring_service_owner_set").value,
                         0)
        self.lib.open_cfw_ring_service_touch_error_callback(0)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_ring_service_posted_event").value, 0x800)
        self.lib.open_cfw_ring_service_post_disconnect_event()
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_ring_service_posted_event").value, 0x40)

    def test_touch_mapping_and_tick_deduplication(self):
        packet = self.packet(0, 0, 0x61, 0, 4, 0x12, 0x34, 100, 0, 0, 0)
        self.assertEqual(self.lib.open_cfw_ring_service_cmd_touch_update(packet, 11), 0)
        self.assertEqual(list(self.array(ctypes.c_uint8 * 4,
                                         "host_ring_service_input")),
                         [4, 5, 0x12, 0x34])
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_ring_service_last_touch_tick").value, 100)
        packet[4] = 5
        packet[7] = 150
        self.lib.open_cfw_ring_service_cmd_touch_update(packet, 11)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_ring_service_input_count").value, 1)
        packet[4] = 8
        self.lib.open_cfw_ring_service_cmd_touch_update(packet, 11)
        self.assertEqual(list(self.array(ctypes.c_uint8 * 4,
                                         "host_ring_service_input")), [4, 14, 0, 0])
        self.assertEqual(self.lib.open_cfw_ring_service_cmd_touch_update(None, 0), -1)

    def test_battery_and_wear_lifecycle(self):
        self.scalar(ctypes.c_uint32,
                    "host_ring_service_battery_template").value = 0xA5A50000
        battery = self.packet(0, 0, 0x8B, 0, 77, 1)
        self.assertEqual(self.lib.open_cfw_ring_service_cmd_battery_report(battery, 6), 0)
        self.assertEqual(list(self.array(ctypes.c_uint32 * 2,
                                         "host_ring_service_battery")),
                         [0x00020004, 0xA5A5014D])
        self.assertEqual(self.lib.open_cfw_ring_service_cmd_battery_report(battery, 5), -1)
        wear = self.packet(0, 0, 0x8C, 0, 1)
        self.scalar(ctypes.c_uint32, "host_ring_service_tick_value").value = 1000
        self.lib.open_cfw_ring_service_cmd_wear_status(wear)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_ring_service_wear_started").value, 1000)
        wear[4] = 0
        self.scalar(ctypes.c_uint32, "host_ring_service_tick_value").value = 1750
        self.lib.open_cfw_ring_service_cmd_wear_status(wear)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_ring_service_wear_duration").value, 750)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_ring_service_wear_report_count").value, 1)

    def test_dispatch_owner_heartbeat_and_invalid_mac_paths(self):
        enable = self.packet(0, 0, 0x85, 0, 1)
        self.lib.open_cfw_ring_service_cmd_package_parse(enable, 5)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_ring_service_remove_count").value, 2)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_ring_service_notify_count").value, 1)
        self.scalar(ctypes.c_uint32, "host_ring_service_owner").value = 1
        self.lib.open_cfw_ring_service_cmd_package_parse(enable, 5)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_ring_service_reconnect_count").value, 1)
        heartbeat = self.packet(0, 0, 0x94, 0, 0x20)
        self.lib.open_cfw_ring_service_cmd_package_parse(heartbeat, 5)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_ring_service_push_count").value, 2)
        self.assertEqual(list(self.array(ctypes.c_uint32 * 8,
                                         "host_ring_service_delays"))[:2], [100, 500])
        mac = self.array(ctypes.c_uint8 * 6, "host_ring_service_mac")
        for index in range(6):
            mac[index] = index + 1
        rejected = self.packet(0, 0, 0x96, 0, 0)
        self.lib.open_cfw_ring_service_cmd_package_parse(rejected, 5)
        self.assertEqual(list(self.array(ctypes.c_uint8 * 6,
                                         "host_ring_service_rejected_mac")),
                         [1, 2, 3, 4, 5, 6])

    def test_all_target_selectors_compile_strictly(self):
        for selector in range(1, 19):
            output = Path(self.temp.name) / f"selector-{selector}.o"
            subprocess.run([
                "/usr/bin/clang", "-std=c11", "-Os", "-ffreestanding",
                "-fno-builtin", "-fno-unwind-tables",
                "-fno-asynchronous-unwind-tables", "--target=arm-none-eabi",
                "-mcpu=cortex-m55", "-mthumb", "-Wall", "-Wextra", "-Werror",
                f"-DOPEN_CFW_RING_SERVICE_SELECTOR={selector}",
                "-c", str(SOURCE), "-o", str(output),
            ], check=True)


if __name__ == "__main__":
    unittest.main()
