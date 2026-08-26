import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/ui_health_page_host.c"
SOURCE = ROOT / "components/apollo_main/core_overlay/ui_health_page.c"


class Point(ctypes.Structure):
    _fields_ = [("x", ctypes.c_int32), ("y", ctypes.c_int32)]


class EventContext(ctypes.Structure):
    _fields_ = [("reserved", ctypes.c_uint8 * 16), ("point", ctypes.POINTER(Point))]


class UIHealthPageCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        cls.library_path = Path(cls.temp.name) / "ui_health_page_host.dylib"
        subprocess.run(
            [
                "clang",
                "-std=c11",
                "-O2",
                "-Wall",
                "-Wextra",
                "-Werror",
                "-shared",
                "-fPIC",
                str(FIXTURE),
                "-o",
                str(cls.library_path),
            ],
            check=True,
            cwd=ROOT,
        )
        cls.lib = ctypes.CDLL(str(cls.library_path))
        cls.lib.open_cfw_health_page_init.argtypes = [ctypes.c_size_t]
        cls.lib.open_cfw_health_page_init.restype = ctypes.c_int32
        cls.lib.open_cfw_health_page_deinit.restype = ctypes.c_uint32
        cls.lib.open_cfw_health_page_switch.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_health_page_switch.restype = ctypes.c_uint32
        cls.lib.open_cfw_health_page_input_event.argtypes = [ctypes.c_uint32, ctypes.c_void_p]
        cls.lib.open_cfw_health_page_input_event.restype = ctypes.c_uint32
        cls.lib.open_cfw_health_page_external_event.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        cls.lib.open_cfw_health_page_external_event.restype = ctypes.c_uint32
        cls.lib.open_cfw_health_page_widget_event.restype = ctypes.c_int32
        cls.lib.open_cfw_health_page_reflash.restype = ctypes.c_uint32
        cls.lib.open_cfw_health_page_host_set_u32.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.lib.open_cfw_health_page_host_set_float.argtypes = [ctypes.c_uint32, ctypes.c_float]
        cls.lib.open_cfw_health_page_host_set_animating.argtypes = [ctypes.c_uint32]
        for name in (
            "selected",
            "initialized",
            "animating",
            "notify_value",
            "notify_count",
            "fifo_count",
            "action_count",
            "exit_count",
            "post_count",
            "minimize_count",
            "common_count",
            "delete_count",
            "lock_count",
            "scroll_x",
        ):
            getattr(cls.lib, f"open_cfw_health_page_host_{name}").restype = ctypes.c_uint32
        cls.lib.open_cfw_health_page_host_action_byte.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_health_page_host_action_byte.restype = ctypes.c_uint32
        cls.lib.open_cfw_health_page_host_indicator_color.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_health_page_host_indicator_color.restype = ctypes.c_uint32
        cls.lib.open_cfw_health_page_host_label.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_health_page_host_label.restype = ctypes.c_char_p

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def setUp(self) -> None:
        self.lib.open_cfw_health_page_host_reset()
        self.lib.open_cfw_health_page_host_set_u32(0x08, 10000)
        self.lib.open_cfw_health_page_host_set_float(0x0C, 3456.0)
        self.lib.open_cfw_health_page_host_set_u32(0x20, 2000)
        self.lib.open_cfw_health_page_host_set_float(0x24, 789.0)
        self.lib.open_cfw_health_page_host_set_u32(0x44, 5400)
        self.lib.open_cfw_health_page_host_set_float(0x54, 72.0)
        self.lib.open_cfw_health_page_host_set_float(0x58, 68.0)
        self.lib.open_cfw_health_page_host_set_float(0x6C, 54.0)
        self.lib.open_cfw_health_page_host_set_float(0xB4, 88.0)

    def test_init_builds_two_page_health_view_and_formats_live_metrics(self) -> None:
        self.assertEqual(self.lib.open_cfw_health_page_init(99), 0)
        self.assertEqual(self.lib.open_cfw_health_page_host_initialized(), 1)
        self.assertEqual(self.lib.open_cfw_health_page_host_selected(), 0)
        self.assertEqual(self.lib.open_cfw_health_page_host_notify_value(), 1)
        self.assertGreaterEqual(self.lib.open_cfw_health_page_host_lock_count(), 1)
        self.assertIn(b"3456", self.lib.open_cfw_health_page_host_label(3))
        self.assertIn(b"789", self.lib.open_cfw_health_page_host_label(5))
        self.assertEqual(
            self.lib.open_cfw_health_page_host_indicator_color(0),
            0x00FFFFFF,
        )
        self.assertEqual(
            self.lib.open_cfw_health_page_host_indicator_color(1),
            0x00444444,
        )

    def test_switch_updates_indicator_notifies_and_completes_animation(self) -> None:
        self.assertEqual(self.lib.open_cfw_health_page_init(99), 0)
        self.assertEqual(self.lib.open_cfw_health_page_switch(1), 1)
        self.assertEqual(self.lib.open_cfw_health_page_host_selected(), 1)
        self.assertEqual(self.lib.open_cfw_health_page_host_notify_value(), 2)
        self.assertEqual(self.lib.open_cfw_health_page_host_animating(), 0)
        self.assertEqual(self.lib.open_cfw_health_page_host_scroll_x(), 0x100)
        self.assertEqual(
            self.lib.open_cfw_health_page_host_indicator_color(0),
            0x00444444,
        )
        self.assertEqual(
            self.lib.open_cfw_health_page_host_indicator_color(1),
            0x00FFFFFF,
        )
        self.assertEqual(self.lib.open_cfw_health_page_switch(2), 0)

    def test_input_event_encodes_touch_coordinates_for_peer_action(self) -> None:
        self.assertEqual(self.lib.open_cfw_health_page_init(99), 0)
        point = Point(0x1234, 0x5678)
        context = EventContext()
        context.point = ctypes.pointer(point)
        self.lib.open_cfw_health_page_input_event(0x44, ctypes.byref(context))
        self.assertEqual(self.lib.open_cfw_health_page_host_action_count(), 1)
        self.assertEqual(
            [self.lib.open_cfw_health_page_host_action_byte(i) for i in range(6)],
            [0, 0x44, 0x34, 0x12, 0x78, 0x56],
        )

    def test_external_events_defer_during_animation_then_preserve_order(self) -> None:
        self.assertEqual(self.lib.open_cfw_health_page_init(99), 0)
        packet = (ctypes.c_uint8 * 6)(0, 0x44, 0, 0, 0, 0)
        self.lib.open_cfw_health_page_host_set_animating(1)
        self.lib.open_cfw_health_page_external_event(packet, 6)
        self.assertEqual(self.lib.open_cfw_health_page_host_selected(), 0)
        self.assertEqual(self.lib.open_cfw_health_page_host_fifo_count(), 1)
        self.lib.open_cfw_health_page_widget_event()
        self.assertEqual(self.lib.open_cfw_health_page_host_selected(), 1)
        self.assertEqual(self.lib.open_cfw_health_page_host_fifo_count(), 0)
        exit_packet = (ctypes.c_uint8 * 6)(0, 0x48, 0, 0, 0, 0)
        self.lib.open_cfw_health_page_external_event(exit_packet, 6)
        self.assertEqual(self.lib.open_cfw_health_page_host_exit_count(), 1)
        self.assertEqual(self.lib.open_cfw_health_page_host_post_count(), 1)

    def test_refresh_common_data_minimize_and_teardown_are_bounded(self) -> None:
        self.assertEqual(self.lib.open_cfw_health_page_init(99), 0)
        # The stock page manager constructs the compact summary separately from
        # the full-screen detail initializer.  Reflash is intentionally a no-op
        # until that summary has been initialized.
        self.lib.open_cfw_health_page_build_summary(0)
        before = self.lib.open_cfw_health_page_host_delete_count()
        self.lib.open_cfw_health_page_reflash()
        self.assertGreater(self.lib.open_cfw_health_page_host_delete_count(), before)
        common = (ctypes.c_uint8 * 3)(1, 0xAA, 0xBB)
        self.lib.open_cfw_health_page_external_event(common, 3)
        self.assertEqual(self.lib.open_cfw_health_page_host_common_count(), 1)
        minimize = (ctypes.c_uint8 * 6)(0, 0x49, 0, 0, 0, 0)
        self.lib.open_cfw_health_page_external_event(minimize, 6)
        self.assertEqual(self.lib.open_cfw_health_page_host_minimize_count(), 1)
        self.assertEqual(self.lib.open_cfw_health_page_host_initialized(), 0)
        self.lib.open_cfw_health_page_deinit()
        self.assertEqual(self.lib.open_cfw_health_page_host_initialized(), 0)

    def test_all_twelve_cortex_m55_selectors_compile_strictly(self) -> None:
        selectors = (
            "INDICATOR",
            "SWITCH",
            "WIDGET_EVENT",
            "ANIM_EXEC",
            "ANIMATE",
            "REFLASH",
            "SUMMARY",
            "INPUT",
            "EXTERNAL",
            "DETAIL",
            "INIT",
            "DEINIT",
        )
        for selector in selectors:
            subprocess.run(
                [
                    "clang",
                    "--target=thumbv7em-none-eabi",
                    "-mthumb",
                    "-mcpu=cortex-m55",
                    "-O2",
                    "-ffreestanding",
                    "-fno-builtin",
                    "-Wall",
                    "-Wextra",
                    "-Werror",
                    "-fsyntax-only",
                    f"-DOPEN_CFW_HEALTH_PAGE_{selector}_ONLY=1",
                    str(SOURCE),
                ],
                check=True,
                cwd=ROOT,
            )


if __name__ == "__main__":
    unittest.main()
