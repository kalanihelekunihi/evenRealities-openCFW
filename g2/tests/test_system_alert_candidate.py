from __future__ import annotations

import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/system_alert.c"
HOST = ROOT / "tests/fixtures/system_alert_host.c"


class SystemAlertCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / "system_alert.so"
        subprocess.run(
            ["clang", "-std=c11", "-shared", "-fPIC", "-Wall", "-Wextra", "-Werror", str(HOST), "-o", str(library)],
            check=True,
            cwd=ROOT,
        )
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_test_system_alert_state.restype = ctypes.c_uint32
        cls.lib.open_cfw_test_system_alert_call_count.restype = ctypes.c_uint32
        cls.lib.open_cfw_test_system_alert_call_arg.restype = ctypes.c_size_t
        cls.lib.open_cfw_system_alert_common_data_handler.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32]
        cls.lib.open_cfw_system_alert_page_event_handler.argtypes = [ctypes.c_size_t, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p]
        cls.lib.open_cfw_system_alert_main_page_init.argtypes = [ctypes.c_size_t, ctypes.c_void_p, ctypes.c_uint32]
        cls.lib.open_cfw_system_alert_send_event_throttled.argtypes = [ctypes.c_uint8]
        cls.lib.open_cfw_system_alert_send_event_throttled.restype = ctypes.c_uint32
        cls.lib.open_cfw_system_alert_reflash_event_handler.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32]
        cls.lib.open_cfw_system_alert_ui_event_handler.argtypes = [ctypes.c_uint32, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_size_t]

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def setUp(self):
        self.lib.open_cfw_test_system_alert_reset()

    def inputs(self, role=0, active=0, tick=0, result=0):
        self.lib.open_cfw_test_system_alert_set_inputs(role, active, tick, result)

    def state(self, index):
        return self.lib.open_cfw_test_system_alert_state(index)

    def count(self, call_id):
        return self.lib.open_cfw_test_system_alert_call_count(call_id)

    def arg(self, call_id, occurrence, argument):
        return self.lib.open_cfw_test_system_alert_call_arg(call_id, occurrence, argument)

    def test_common_handler_validates_payload_and_posts_only_for_active_master(self):
        self.inputs(role=1, active=1)
        self.lib.open_cfw_system_alert_common_data_handler(0, None, 0)
        self.assertEqual((self.state(0), self.count(28)), (0, 0))
        payload = (ctypes.c_uint8 * 1)(2)
        self.lib.open_cfw_system_alert_common_data_handler(9, payload, 1)
        self.assertEqual((self.state(0), self.count(28)), (2, 1))
        self.assertEqual(tuple(self.arg(28, 0, i) for i in range(4)), (0x21, 0, 0, 200))

    def test_page_lifecycle_role_gates_exit_and_synchronizes_animation(self):
        self.inputs(role=2)
        self.assertEqual(self.lib.open_cfw_system_alert_page_event_handler(0, None, 0x0A, None), 1)
        self.assertEqual((self.state(4), self.count(29)), (0, 0))
        self.inputs(role=1)
        self.lib.open_cfw_system_alert_page_event_handler(0, None, 0x48, None)
        self.assertEqual((self.state(4), self.state(5), self.count(29)), (0, 180, 1))
        self.lib.open_cfw_system_alert_page_event_handler(0, None, 0x4D, None)
        self.assertEqual((self.state(4), self.state(5), self.count(28)), (1, 180, 1))
        self.assertEqual(tuple(self.arg(28, 0, i) for i in range(4)), (0x21, 5, 1, 3000))

    def test_main_page_initializes_root_content_and_stock_style_values(self):
        self.inputs(role=2)
        self.lib.open_cfw_system_alert_main_page_init(0x77, None, 0)
        self.assertEqual((self.state(1), self.state(2)), (0x1000, 0x2000))
        self.assertEqual((self.count(0), self.arg(0, 0, 0), self.arg(0, 1, 0)), (2, 0x77, 0x1000))
        self.assertEqual((self.count(12), self.count(13), self.count(14), self.count(15)), (2, 2, 2, 2))
        self.assertEqual(self.arg(16, 0, 1), 16)
        self.assertEqual((self.arg(18, 0, 1), self.arg(6, 0, 1)), (10, 12))

    def test_throttle_preserves_first_interval_and_nonascending_tick_behavior(self):
        self.inputs(tick=100, result=7)
        self.assertEqual(self.lib.open_cfw_system_alert_send_event_throttled(0x44), 7)
        self.assertEqual((self.state(3), self.count(30), self.arg(30, 0, 1)), (100, 1, 0x44))
        self.inputs(tick=9999, result=8)
        self.assertEqual(self.lib.open_cfw_system_alert_send_event_throttled(0x45), 0)
        self.assertEqual(self.count(30), 1)
        self.inputs(tick=10100, result=9)
        self.assertEqual(self.lib.open_cfw_system_alert_send_event_throttled(0x46), 9)
        self.assertEqual((self.state(3), self.count(30)), (10100, 2))
        self.inputs(tick=50, result=10)
        self.assertEqual(self.lib.open_cfw_system_alert_send_event_throttled(0x47), 10)
        self.assertEqual((self.state(3), self.count(30)), (10100, 3))

    def test_reflash_renders_both_alerts_and_handles_exit_message(self):
        self.inputs(role=1)
        self.lib.open_cfw_test_system_alert_set_type(1)
        self.lib.open_cfw_system_alert_reflash_event_handler(None, 0)
        self.assertEqual((self.count(21), self.count(22), self.count(24)), (1, 1, 1))
        self.assertEqual((self.arg(23, 0, 1), self.arg(26, 0, 0)), (0x7747E4, 1))
        self.assertEqual((self.count(3), self.arg(3, 0, 1), self.arg(3, 1, 1)), (2, 9, 2))
        self.lib.open_cfw_test_system_alert_reset()
        self.lib.open_cfw_test_system_alert_set_type(2)
        self.lib.open_cfw_system_alert_reflash_event_handler(None, 0)
        self.assertEqual((self.arg(23, 0, 1), self.arg(26, 0, 0)), (0x772928, 2))
        exit_event = (ctypes.c_uint8 * 1)(5)
        self.lib.open_cfw_system_alert_reflash_event_handler(exit_event, 1)
        self.assertEqual((self.state(4), self.state(5), self.count(29)), (0, 180, 1))

    def test_ui_dispatch_initializes_descriptor_reflashes_and_hides(self):
        self.inputs(role=1)
        self.lib.open_cfw_system_alert_ui_event_handler(2, None, 0, 0x55)
        self.assertEqual((self.state(1), self.state(6), self.state(4), self.state(5)), (0x1000, 0x1000, 1, 180))
        self.lib.open_cfw_test_system_alert_set_type(2)
        self.lib.open_cfw_system_alert_ui_event_handler(3, None, 0, 0)
        self.assertEqual(self.arg(23, 0, 1), 0x772928)
        self.lib.open_cfw_system_alert_ui_event_handler(4, None, 0, 0)
        self.assertEqual(self.state(4), 1)
        self.lib.open_cfw_system_alert_ui_event_handler(5, None, 0, 0)
        self.assertEqual((self.state(4), self.state(5)), (0, 180))

    def test_all_seven_cortex_m55_selectors_compile_to_one_global_leaf(self):
        selectors = {
            "PADDING": "open_cfw_system_alert_set_box_padding",
            "COMMON": "open_cfw_system_alert_common_data_handler",
            "PAGE_EVENT": "open_cfw_system_alert_page_event_handler",
            "INIT": "open_cfw_system_alert_main_page_init",
            "THROTTLED": "open_cfw_system_alert_send_event_throttled",
            "REFLASH": "open_cfw_system_alert_reflash_event_handler",
            "UI_EVENT": "open_cfw_system_alert_ui_event_handler",
        }
        flags = ["-target", "thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding", "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin", "-mno-unaligned-access", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra", "-Werror"]
        with tempfile.TemporaryDirectory() as directory:
            for selector, symbol in selectors.items():
                obj = Path(directory) / f"{selector}.o"
                subprocess.run(["clang", *flags, f"-DOPEN_CFW_SYSTEM_ALERT_{selector}_ONLY=1", "-c", str(SOURCE), "-o", str(obj)], check=True, cwd=ROOT)
                output = subprocess.run(["nm", str(obj)], check=True, capture_output=True, text=True).stdout
                entries = {parts[2] for line in output.splitlines() if len(parts := line.split()) == 3 and parts[1] == "T"}
                self.assertEqual(entries, {symbol}, selector)


if __name__ == "__main__":
    unittest.main()
