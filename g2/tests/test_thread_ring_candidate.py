import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/thread_ring.c"
FIXTURE = ROOT / "tests/fixtures/thread_ring_host.c"
HEADER = ROOT / "tests/fixtures/thread_ring_host.h"


class ThreadRingCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.output = Path(cls.temp.name) / "thread-ring.so"
        subprocess.run([
            "/usr/bin/clang", "-std=c11", "-shared", "-fPIC", "-O2",
            "-Wall", "-Wextra", "-Werror", "-include", str(HEADER),
            str(SOURCE), str(FIXTURE), "-o", str(cls.output),
        ], check=True)
        cls.lib = ctypes.CDLL(str(cls.output))
        cls.lib.open_cfw_thread_ring_record_send.argtypes = [
            ctypes.c_uint32, ctypes.c_void_p, ctypes.c_uint16]
        cls.lib.open_cfw_thread_ring_send_message.argtypes = [
            ctypes.c_void_p, ctypes.c_uint16]
        cls.lib.open_cfw_thread_ring_event_handler.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_thread_ring_enable_touch.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_thread_ring_disable_touch.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_thread_ring_enable_pair.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_thread_ring_record_send.restype = ctypes.c_int32
        cls.lib.open_cfw_thread_ring_send_message.restype = ctypes.c_int32
        cls.lib.host_thread_ring_reset()

    @classmethod
    def tearDownClass(cls):
        cls.lib.host_thread_ring_reset()
        cls.temp.cleanup()

    def scalar(self, ctype, name):
        return ctype.in_dll(self.lib, name)

    def array(self, ctype, name):
        return ctype.in_dll(self.lib, name)

    def setUp(self):
        self.lib.host_thread_ring_reset()

    @staticmethod
    def payload(*values):
        return (ctypes.c_uint8 * len(values))(*values)

    def test_lifecycle_queue_and_exit_contract(self):
        self.lib.open_cfw_thread_ring_state_enter()
        self.lib.open_cfw_thread_ring_state_ready()
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_thread_ring_active_index").value, 6)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_thread_ring_ready_index").value, 6)
        self.lib.open_cfw_thread_ring_queue_init()
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_thread_ring_queue_depth").value, 3)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_thread_ring_queue_item_size").value, 4)
        self.lib.open_cfw_thread_ring_create()
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_thread_ring_thread_new_count").value, 1)
        self.lib.open_cfw_thread_ring_terminate()
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_thread_ring_thread_terminate_count").value, 1)
        self.lib.open_cfw_thread_ring_exit()
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_thread_ring_exit_index").value, 6)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_thread_ring_queue_delete_count").value, 1)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_thread_ring_exit_wait_count").value, 1)

    def test_record_send_validation_queue_and_failure_cleanup(self):
        data = self.payload(1, 2, 3)
        self.assertEqual(
            self.lib.open_cfw_thread_ring_record_send(2, data, 3), -1)
        self.lib.open_cfw_thread_ring_queue_init()
        self.assertEqual(
            self.lib.open_cfw_thread_ring_record_send(2, None, 1), -1)
        self.assertEqual(
            self.lib.open_cfw_thread_ring_record_send(2, data, 3), 0)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_thread_ring_queue_count").value, 1)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_thread_ring_flags").value, 0x400000)
        self.scalar(ctypes.c_uint32,
                    "host_thread_ring_queue_put_fail").value = 1
        self.assertEqual(
            self.lib.open_cfw_thread_ring_record_send(2, data, 3), -1)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_thread_ring_free_count").value, 1)
        self.scalar(ctypes.c_uint32,
                    "host_thread_ring_alloc_fail").value = 1
        self.assertEqual(
            self.lib.open_cfw_thread_ring_record_send(2, data, 3), -1)

    def test_message_dispatch_and_bounded_status_record(self):
        self.lib.open_cfw_thread_ring_queue_init()
        protocol = self.payload(0x11, 0x22, 0x33)
        touch = self.payload(1)
        status = self.payload(1, 0)
        short_status = self.payload(1)
        ticks = self.payload(0x34, 0x12)
        for message_id, data in (
            (2, protocol), (0x80, touch), (0x400, status),
            (0x400, short_status), (0x1000, ticks),
        ):
            self.assertEqual(self.lib.open_cfw_thread_ring_record_send(
                message_id, data, len(data)), 0)
        self.lib.open_cfw_thread_ring_message_handler()
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_thread_ring_parse_count").value, 1)
        self.assertEqual(list(self.array(ctypes.c_uint8 * 3,
                                         "host_thread_ring_parse_data")),
                         [0x11, 0x22, 0x33])
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_thread_ring_touch_enable_count").value, 1)
        self.assertEqual(self.scalar(ctypes.c_uint8,
                                     "host_thread_ring_touch_enable_value").value, 1)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_thread_ring_status_count").value, 1)
        self.assertEqual(list(self.array(ctypes.c_uint8 * 2,
                                         "host_thread_ring_status_values")),
                         [1, 0])
        self.assertEqual(self.scalar(ctypes.c_uint16,
                                     "host_thread_ring_touch_time_value").value,
                         0x1234)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_thread_ring_free_count").value, 5)

    def test_touch_callbacks_and_advertising_policy(self):
        self.lib.open_cfw_thread_ring_enable_touch(99)
        self.assertEqual(self.scalar(ctypes.c_uint8,
                                     "host_thread_ring_post_touch_value").value, 1)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_thread_ring_push_count").value, 1)
        self.assertEqual(self.array(ctypes.c_uint32 * 16,
                                    "host_thread_ring_push_delays")[0], 500)
        self.scalar(ctypes.c_uint8,
                    "host_thread_ring_connection_state").value = 1
        self.lib.open_cfw_thread_ring_enable_touch(0)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_thread_ring_push_count").value, 1)
        self.lib.open_cfw_thread_ring_disable_touch(0)
        self.assertEqual(self.scalar(ctypes.c_uint8,
                                     "host_thread_ring_post_touch_value").value, 0)
        self.lib.open_cfw_thread_ring_enable_pair(0)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_thread_ring_disconnect_count").value, 1)

    def test_event_dispatch_policy(self):
        self.lib.open_cfw_thread_ring_event_handler(0x04 | 0x20 | 0x40)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_thread_ring_heartbeat_count").value, 1)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_thread_ring_pair_count").value, 1)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_thread_ring_push_count").value, 5)
        self.assertEqual(list(self.array(ctypes.c_uint32 * 16,
                                         "host_thread_ring_push_delays"))[:5],
                         [200, 500, 3000, 500, 700])
        self.scalar(ctypes.c_uint32,
                    "host_thread_ring_phone_role_value").value = 0
        self.lib.open_cfw_thread_ring_event_handler(0x10)
        self.assertEqual(self.scalar(ctypes.c_uint32,
                                     "host_thread_ring_glasses_status_count").value, 1)
        self.assertEqual(self.scalar(ctypes.c_uint16,
                                     "host_thread_ring_touch_time_value").value, 1000)
        self.scalar(ctypes.c_uint32,
                    "host_thread_ring_phone_role_value").value = 1
        self.lib.open_cfw_thread_ring_event_handler(0x800)
        self.assertEqual(self.scalar(ctypes.c_uint16,
                                     "host_thread_ring_touch_time_value").value, 500)

    def test_all_target_selectors_compile_strictly(self):
        for selector in range(1, 18):
            output = Path(self.temp.name) / f"selector-{selector}.o"
            subprocess.run([
                "/usr/bin/clang", "-std=c11", "-Os", "-ffreestanding",
                "-fno-builtin", "-fno-unwind-tables",
                "-fno-asynchronous-unwind-tables", "--target=arm-none-eabi",
                "-mcpu=cortex-m55", "-mthumb", "-Wall", "-Wextra", "-Werror",
                f"-DOPEN_CFW_THREAD_RING_SELECTOR={selector}",
                "-c", str(SOURCE), "-o", str(output),
            ], check=True)


if __name__ == "__main__":
    unittest.main()
