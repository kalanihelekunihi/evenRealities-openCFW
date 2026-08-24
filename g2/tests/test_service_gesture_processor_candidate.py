from __future__ import annotations

import ctypes
import platform
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/service_gesture_processor.c"
FIXTURE = ROOT / "tests/fixtures"


class GestureProcessorCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        cls.library_path = Path(cls.temp.name) / ("gesture" + suffix)
        subprocess.run([
            "clang", "-std=c11", "-shared", "-fPIC", "-O1", "-include",
            str(FIXTURE / "service_gesture_processor_host.h"), str(SOURCE),
            str(FIXTURE / "service_gesture_processor_host.c"), "-o",
            str(cls.library_path),
        ], check=True, cwd=ROOT)
        cls.lib = ctypes.CDLL(str(cls.library_path))
        cls.lib.open_cfw_gesture_production_click.argtypes = [
            ctypes.c_uint8, ctypes.c_uint8,
        ]
        cls.lib.open_cfw_gesture_get_proximity.restype = ctypes.c_uint8
        cls.lib.open_cfw_gesture_event_name.argtypes = [ctypes.c_uint8]
        cls.lib.open_cfw_gesture_event_name.restype = ctypes.c_char_p
        cls.lib.open_cfw_gesture_format_mask.argtypes = [ctypes.c_uint8]
        cls.lib.open_cfw_gesture_format_mask.restype = ctypes.c_char_p

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def setUp(self) -> None:
        self.lib.open_cfw_test_gesture_reset()

    def scalar(self, name: str) -> ctypes.c_uint32:
        return ctypes.c_uint32.in_dll(self.lib, name)

    def frame(self):
        return (ctypes.c_uint8 * 16).in_dll(
            self.lib, "open_cfw_test_gesture_frame"
        )

    def records(self):
        return ((ctypes.c_uint32 * 4) * 32).in_dll(
            self.lib, "open_cfw_test_gesture_publish_records"
        )

    def test_accessors_mask_formatter_and_production_click(self) -> None:
        ctypes.c_uint8.in_dll(self.lib, "open_cfw_test_gesture_proximity").value = 7
        self.assertEqual(self.lib.open_cfw_gesture_get_proximity(), 7)
        self.assertEqual(self.lib.open_cfw_gesture_event_name(1), b"ON")
        self.assertEqual(
            self.lib.open_cfw_gesture_format_mask(0xA5),
            b"PRESS|SINGLE|SLIDE_L|ERROR",
        )
        self.lib.open_cfw_gesture_production_click(4, 1)
        self.assertEqual(self.scalar("open_cfw_test_gesture_buzzer_count").value, 1)
        self.assertEqual(self.scalar("open_cfw_test_gesture_buzzer_type").value, 3)
        self.lib.open_cfw_gesture_production_click(4, 2)
        self.lib.open_cfw_gesture_production_click(2, 1)
        self.assertEqual(self.scalar("open_cfw_test_gesture_buzzer_count").value, 1)

    def test_proximity_update_and_no_slider_event(self) -> None:
        self.frame()[0] = 1
        self.lib.open_cfw_gesture_process()
        self.assertEqual(
            ctypes.c_uint8.in_dll(self.lib, "open_cfw_test_gesture_proximity").value,
            1,
        )
        self.assertEqual(self.scalar("open_cfw_test_gesture_notify_count").value, 1)
        self.assertEqual(self.scalar("open_cfw_test_gesture_notify_selector").value, 3)
        self.assertEqual(self.scalar("open_cfw_test_gesture_notify_value").value, 1)
        self.assertEqual(self.scalar("open_cfw_test_gesture_publish_count").value, 0)

    def test_production_mode_consumes_slider_mask(self) -> None:
        self.frame()[1] = 4
        self.frame()[2] = 1
        self.scalar("open_cfw_test_gesture_product_mode").value = 1
        self.lib.open_cfw_gesture_process()
        self.assertEqual(self.scalar("open_cfw_test_gesture_buzzer_count").value, 1)
        self.assertEqual(self.scalar("open_cfw_test_gesture_publish_count").value, 0)

    def test_error_resets_touch_and_preempts_events(self) -> None:
        self.frame()[1] = 0xFF
        self.lib.open_cfw_gesture_process()
        self.assertEqual(self.scalar("open_cfw_test_gesture_touch_stop_count").value, 1)
        self.assertEqual(self.scalar("open_cfw_test_gesture_baseline_count").value, 1)
        self.assertEqual(self.scalar("open_cfw_test_gesture_publish_count").value, 0)

    def test_all_event_bits_and_single_thresholds(self) -> None:
        frame = self.frame()
        frame[1] = 0x7B
        frame[2] = 7
        frame[3] = 9
        self.lib.open_cfw_gesture_process()
        self.assertEqual(self.scalar("open_cfw_test_gesture_publish_count").value, 6)
        rows = self.records()
        self.assertEqual([rows[i][1] for i in range(6)], [0x0D, 1, 3, 5, 4, 0x0E])
        self.assertEqual(list(rows[3])[2:], [7, 9])
        self.assertEqual(list(rows[4])[2:], [7, 9])
        for difference, expected in ((1, 0), (2, None), (9, None), (10, 0x1010)):
            self.setUp()
            self.frame()[1] = 4
            self.frame()[2] = difference
            self.lib.open_cfw_gesture_process()
            count = self.scalar("open_cfw_test_gesture_publish_count").value
            self.assertEqual(count, 0 if expected is None else 1)
            if expected is not None:
                self.assertEqual(self.records()[0][1], expected)

    def test_each_selector_is_one_thumb_function(self) -> None:
        selectors = {
            "OPEN_CFW_GESTURE_PRODUCTION_CLICK_ONLY": "open_cfw_gesture_production_click",
            "OPEN_CFW_GESTURE_GET_PROXIMITY_ONLY": "open_cfw_gesture_get_proximity",
            "OPEN_CFW_GESTURE_EVENT_NAME_ONLY": "open_cfw_gesture_event_name",
            "OPEN_CFW_GESTURE_FORMAT_MASK_ONLY": "open_cfw_gesture_format_mask",
            "OPEN_CFW_GESTURE_PROCESS_ONLY": "open_cfw_gesture_process",
        }
        flags = [
            "-target", "thumbv7em-none-eabi", "-mthumb", "-O2",
            "-ffreestanding", "-fno-jump-tables", "-fomit-frame-pointer",
            "-fno-builtin", "-mno-unaligned-access", "-fno-unwind-tables",
            "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
            "-fdata-sections", "-Wall", "-Wextra", "-Werror",
        ]
        with tempfile.TemporaryDirectory() as directory:
            for selector, expected in selectors.items():
                target = Path(directory) / (selector + ".o")
                subprocess.run([
                    "clang", *flags, f"-D{selector}=1", "-c", str(SOURCE),
                    "-o", str(target),
                ], check=True, cwd=ROOT)
                symbols = subprocess.run(
                    ["nm", str(target)], check=True, capture_output=True, text=True
                ).stdout
                observed = {
                    fields[2] for line in symbols.splitlines()
                    if len(fields := line.split()) == 3 and fields[1] == "T"
                }
                self.assertEqual(observed, {expected})


if __name__ == "__main__":
    unittest.main()
