from __future__ import annotations

import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/system_close.c"
HOST = ROOT / "tests/fixtures/system_close_host.c"


class Point(ctypes.Structure):
    _fields_ = [("x", ctypes.c_int32), ("y", ctypes.c_int32)]


class PageEvent(ctypes.Structure):
    _fields_ = [("reserved", ctypes.c_uint8 * 16), ("point", ctypes.POINTER(Point))]


class SystemCloseCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / "system_close.so"
        subprocess.run(
            ["clang", "-std=c11", "-shared", "-fPIC", "-Wall", "-Wextra", "-Werror", str(HOST), "-o", str(library)],
            check=True,
            cwd=ROOT,
        )
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_system_close_fifo_push.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint16]
        cls.lib.open_cfw_system_close_fifo_push.restype = ctypes.c_int32
        cls.lib.open_cfw_system_close_fifo_pop.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint16]
        cls.lib.open_cfw_system_close_fifo_pop.restype = ctypes.c_int32
        cls.lib.open_cfw_system_close_fifo_empty.restype = ctypes.c_uint32
        cls.lib.open_cfw_system_close_common_data_handler.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32]
        cls.lib.open_cfw_system_close_common_data_handler.restype = ctypes.c_int32
        cls.lib.open_cfw_system_close_dispatch_page_action.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
        cls.lib.open_cfw_system_close_dispatch_page_action.restype = ctypes.c_uint32
        cls.lib.open_cfw_system_close_page_event_handler.argtypes = [ctypes.c_size_t, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p]
        cls.lib.open_cfw_system_close_page_event_handler.restype = ctypes.c_uint32
        cls.lib.open_cfw_system_close_main_page_init.argtypes = [ctypes.c_size_t, ctypes.c_void_p, ctypes.c_uint32]
        cls.lib.open_cfw_system_close_reflash_event_handler.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32]
        cls.lib.open_cfw_system_close_page_factory.argtypes = [ctypes.c_uint8, ctypes.c_uint32]
        cls.lib.open_cfw_system_close_page_factory.restype = ctypes.c_uint32
        cls.lib.open_cfw_system_close_ui_event_handler.argtypes = [ctypes.c_uint32, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_size_t]
        cls.lib.open_cfw_test_system_close_state.restype = ctypes.c_uint32
        cls.lib.open_cfw_test_system_close_call_count.restype = ctypes.c_uint32
        cls.lib.open_cfw_test_system_close_call_arg.restype = ctypes.c_size_t

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def setUp(self):
        self.lib.open_cfw_test_system_close_reset()

    def inputs(self, role=0, active=0, app=0, state=0, result=0):
        self.lib.open_cfw_test_system_close_inputs(role, active, app, state, result)

    def set_state(self, index, value):
        self.lib.open_cfw_test_system_close_set_state(index, value)

    def state(self, index):
        return self.lib.open_cfw_test_system_close_state(index)

    def count(self, call_id):
        return self.lib.open_cfw_test_system_close_call_count(call_id)

    def arg(self, call_id, occurrence, argument):
        return self.lib.open_cfw_test_system_close_call_arg(call_id, occurrence, argument)

    def test_bounded_fifo_preserves_order_wrap_and_stock_errors(self):
        self.assertEqual(self.lib.open_cfw_system_close_fifo_push(None, 1), -3)
        self.assertEqual(self.lib.open_cfw_system_close_fifo_pop(None, 1), -3)
        source = (ctypes.c_uint8 * 128)(*range(128))
        self.assertEqual(self.lib.open_cfw_system_close_fifo_push(source, 128), 0)
        self.assertEqual(self.lib.open_cfw_system_close_fifo_push(source, 1), -1)
        first = (ctypes.c_uint8 * 100)()
        self.assertEqual(self.lib.open_cfw_system_close_fifo_pop(first, 100), 100)
        self.assertEqual(list(first), list(range(100)))
        wrapped = (ctypes.c_uint8 * 20)(*range(200, 220))
        self.assertEqual(self.lib.open_cfw_system_close_fifo_push(wrapped, 20), 0)
        tail = (ctypes.c_uint8 * 48)()
        self.assertEqual(self.lib.open_cfw_system_close_fifo_pop(tail, 64), 48)
        self.assertEqual(list(tail), list(range(100, 128)) + list(range(200, 220)))
        self.assertEqual((self.lib.open_cfw_system_close_fifo_empty(), self.state(6)), (1, 0))

    def test_common_data_requires_five_bytes_and_role_display_allowlist(self):
        payload = (ctypes.c_uint8 * 5)(1, 0x78, 0x56, 0x34, 0x12)
        self.assertEqual(self.lib.open_cfw_system_close_common_data_handler(0, payload, 4), -1)
        self.inputs(role=1, active=1, app=8, state=0, result=9)
        self.assertEqual(self.lib.open_cfw_system_close_common_data_handler(0, payload, 5), 0)
        self.assertEqual((self.state(0), self.state(5), self.count(31)), (1, 0x12345678, 1))
        self.assertEqual(tuple(self.arg(31, 0, i) for i in range(4)), (0x22, 0, 0, 100))
        self.inputs(role=1, active=1, app=7, state=0)
        self.lib.open_cfw_system_close_common_data_handler(0, payload, 5)
        self.assertEqual(self.count(31), 1)

    def test_page_action_serializes_coordinates_and_respects_animation_gate(self):
        self.inputs(result=7)
        point = Point(0x1234, 0x5678)
        event = PageEvent(point=ctypes.pointer(point))
        self.assertEqual(self.lib.open_cfw_system_close_dispatch_page_action(0x44, ctypes.byref(event)), 7)
        self.assertEqual(tuple(self.arg(32, 0, i) for i in range(4)), (0x22, 0x12344400, 6, 0))
        self.set_state(3, 1)
        self.assertEqual(self.lib.open_cfw_system_close_dispatch_page_action(0x45, ctypes.byref(event)), 0)
        self.assertEqual(self.count(32), 1)

    def test_page_events_are_role_gated_and_click_is_local(self):
        self.inputs(role=2)
        self.assertEqual(self.lib.open_cfw_system_close_page_event_handler(0, None, 0x44, None), 1)
        self.assertEqual(self.count(32), 0)
        self.inputs(role=1)
        self.lib.open_cfw_system_close_page_event_handler(0, None, 0x44, None)
        self.assertEqual(self.count(32), 1)
        self.set_state(0, 2)
        self.set_state(1, 0)
        self.lib.open_cfw_system_close_page_event_handler(0, None, 0x0A, None)
        self.assertEqual(self.count(33), 1)

    def test_main_page_builds_centered_root_and_role_offset_content(self):
        self.inputs(role=2)
        self.lib.open_cfw_system_close_main_page_init(0x77, None, 0)
        self.assertNotEqual((self.state(7), self.state(8)), (0, 0))
        self.assertEqual((self.count(1), self.count(18), self.count(19), self.count(20), self.count(21)), (2, 2, 2, 2, 2))
        self.assertEqual((self.arg(5, 0, 1), self.arg(6, 0, 1)), (100, 40))
        self.assertEqual(self.arg(5, 1, 1), 16)

    def test_scroll_animation_queues_and_drains_next_event(self):
        self.inputs(role=1)
        self.set_state(0, 2)
        self.set_state(2, 3)
        self.lib.open_cfw_system_close_handle_scroll_up()
        self.assertEqual((self.state(1), self.state(3), self.count(39)), (1, 1, 1))
        packet = (ctypes.c_uint8 * 6)(0, 0x45, 0, 0, 0, 0)
        self.lib.open_cfw_system_close_reflash_event_handler(packet, 6)
        self.assertEqual(self.state(6), 5)
        self.lib.open_cfw_test_system_close_finish_animation()
        self.assertEqual((self.state(1), self.state(6)), (0, 0))

    def test_click_policy_distinguishes_cancel_minimize_and_confirm(self):
        self.inputs(role=1)
        self.set_state(0, 2)
        self.set_state(1, 0)
        self.lib.open_cfw_system_close_handle_click()
        self.assertEqual((self.count(33), self.count(37)), (1, 0))
        self.set_state(1, 1)
        self.lib.open_cfw_system_close_handle_click()
        self.assertEqual((self.count(33), self.count(37)), (2, 1))
        self.set_state(0, 3)
        self.set_state(1, 1)
        self.lib.open_cfw_system_close_handle_click()
        self.assertEqual((self.count(33), self.count(37)), (2, 1))
        self.set_state(1, 2)
        self.lib.open_cfw_system_close_handle_click()
        self.assertEqual((self.count(33), self.count(37)), (3, 2))

    def test_reflash_builds_confirmation_and_routes_peer_events(self):
        self.inputs(role=1)
        self.lib.open_cfw_system_close_ui_event_handler(2, None, 0, 0x55)
        self.set_state(0, 1)
        self.lib.open_cfw_system_close_reflash_event_handler(None, 0)
        self.assertEqual((self.state(4), self.state(2), self.count(24), self.count(25), self.count(27)), (1, 2, 1, 1, 3))
        self.assertNotEqual((self.state(9), self.state(10), self.state(11), self.state(12)), (0, 0, 0, 0))
        packet = (ctypes.c_uint8 * 6)(0, 0x48, 0, 0, 0, 0)
        self.lib.open_cfw_system_close_reflash_event_handler(packet, 6)
        self.assertEqual(self.count(33), 1)

    def test_factory_and_ui_lifecycle_preserve_wire_format_and_reset_state(self):
        self.inputs(result=11)
        self.assertEqual(self.lib.open_cfw_system_close_page_factory(3, 0x12345678), 11)
        self.assertEqual(tuple(self.arg(34, 0, i) for i in range(4)), (0x22, 0x34567803, 5, 0))
        self.lib.open_cfw_system_close_ui_event_handler(2, None, 0, 0x99)
        self.assertEqual((self.state(13), self.state(2), self.state(3)), (self.state(7), 2, 0))
        self.set_state(1, 2)
        self.lib.open_cfw_system_close_ui_event_handler(5, None, 0, 0)
        self.assertEqual((self.state(1), self.state(2), self.state(6), self.count(36)), (0, 2, 0, 1))

    def test_all_twenty_cortex_m55_selectors_compile_to_one_global_leaf(self):
        selectors = {
            "PADDING": "open_cfw_system_close_set_box_padding",
            "FIFO_PUSH": "open_cfw_system_close_fifo_push",
            "FIFO_EMPTY": "open_cfw_system_close_fifo_empty",
            "FIFO_POP": "open_cfw_system_close_fifo_pop",
            "FIFO_RESET": "open_cfw_system_close_fifo_reset",
            "COMMON": "open_cfw_system_close_common_data_handler",
            "PAGE_ACTION": "open_cfw_system_close_dispatch_page_action",
            "PAGE_EVENT": "open_cfw_system_close_page_event_handler",
            "INIT": "open_cfw_system_close_main_page_init",
            "POSITION": "open_cfw_system_close_option_position",
            "ANIM_READY": "open_cfw_system_close_selection_anim_ready",
            "ANIMATE": "open_cfw_system_close_start_selection_animation",
            "UPDATE": "open_cfw_system_close_update_selection",
            "SCROLL_UP": "open_cfw_system_close_handle_scroll_up",
            "SCROLL_DOWN": "open_cfw_system_close_handle_scroll_down",
            "CLICK": "open_cfw_system_close_handle_click",
            "OPTIONS": "open_cfw_system_close_create_options",
            "REFLASH": "open_cfw_system_close_reflash_event_handler",
            "FACTORY": "open_cfw_system_close_page_factory",
            "UI_EVENT": "open_cfw_system_close_ui_event_handler",
        }
        flags = ["-target", "thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding", "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin", "-mno-unaligned-access", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra", "-Werror"]
        with tempfile.TemporaryDirectory() as directory:
            for selector, symbol in selectors.items():
                obj = Path(directory) / f"{selector}.o"
                subprocess.run(["clang", *flags, f"-DOPEN_CFW_SYSTEM_CLOSE_{selector}_ONLY=1", "-c", str(SOURCE), "-o", str(obj)], check=True, cwd=ROOT)
                output = subprocess.run(["nm", str(obj)], check=True, capture_output=True, text=True).stdout
                entries = {parts[2] for line in output.splitlines() if len(parts := line.split()) == 3 and parts[1] == "T"}
                self.assertEqual(entries, {symbol}, selector)


if __name__ == "__main__":
    unittest.main()
