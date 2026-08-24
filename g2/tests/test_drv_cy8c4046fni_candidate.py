from __future__ import annotations

import ctypes
import platform
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/drv_cy8c4046fni.c"
FIXTURE = ROOT / "tests/fixtures"


class DrvCy8c4046fniCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        cls.library_path = Path(cls.temp.name) / ("cy8c" + suffix)
        subprocess.run([
            "clang", "-std=c11", "-shared", "-fPIC", "-O1", "-include",
            str(FIXTURE / "drv_cy8c4046fni_host.h"), str(SOURCE),
            str(FIXTURE / "drv_cy8c4046fni_host.c"), "-o",
            str(cls.library_path),
        ], check=True, cwd=ROOT)
        cls.lib = ctypes.CDLL(str(cls.library_path))
        cls.lib.open_cfw_cy8c_read_proximity_baseline.restype = ctypes.c_uint16
        cls.lib.open_cfw_cy8c_write_gesture_cfg.argtypes = [
            ctypes.POINTER(ctypes.c_uint16)
        ]
        cls.lib.open_cfw_cy8c_read_gesture_cfg.argtypes = [
            ctypes.POINTER(ctypes.c_uint16)
        ]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def setUp(self) -> None:
        self.lib.open_cfw_test_cy8c_reset()

    def scalar(self, name: str, kind=ctypes.c_uint32):
        return kind.in_dll(self.lib, name)

    def register_data(self):
        return ((ctypes.c_uint8 * 32) * 256).in_dll(
            self.lib, "open_cfw_test_cy8c_register_data"
        )

    def register_status(self):
        return (ctypes.c_int32 * 256).in_dll(
            self.lib, "open_cfw_test_cy8c_register_status"
        )

    def test_hal_callbacks_bind_bus_address_command_and_size(self) -> None:
        data = (ctypes.c_uint8 * 3)(1, 2, 3)
        self.assertEqual(self.lib.open_cfw_cy8c_i2c_register_write(7, data, 3), 0)
        self.assertEqual(self.scalar("open_cfw_test_cy8c_hal_kind").value, 1)
        self.assertEqual(self.scalar("open_cfw_test_cy8c_hal_bus").value, 5)
        self.assertEqual(self.scalar("open_cfw_test_cy8c_hal_address").value, 12)
        self.assertEqual(self.scalar("open_cfw_test_cy8c_last_command").value, 7)
        self.assertEqual(self.scalar("open_cfw_test_cy8c_last_size").value, 3)
        self.lib.open_cfw_cy8c_i2c_register_read(8, data, 2)
        self.assertEqual(self.scalar("open_cfw_test_cy8c_hal_kind").value, 2)
        self.lib.open_cfw_cy8c_i2c_raw_write(data, 3)
        self.assertEqual(self.scalar("open_cfw_test_cy8c_hal_kind").value, 3)
        self.lib.open_cfw_cy8c_i2c_raw_read(data, 3)
        self.assertEqual(self.scalar("open_cfw_test_cy8c_hal_kind").value, 4)

    def test_reset_and_dfu_command(self) -> None:
        self.lib.open_cfw_cy8c_reset()
        board = ((ctypes.c_uint32 * 2) * 8).in_dll(
            self.lib, "open_cfw_test_cy8c_board_records"
        )
        delays = (ctypes.c_uint32 * 8).in_dll(
            self.lib, "open_cfw_test_cy8c_delay_records"
        )
        self.assertEqual([list(board[i]) for i in range(2)], [[10, 0], [10, 1]])
        self.assertEqual(list(delays)[:2], [10, 50])
        self.assertEqual(self.lib.open_cfw_cy8c_switch_to_dfu(), 0)
        self.assertEqual(self.scalar("open_cfw_test_cy8c_last_command").value, 2)
        self.register_status()[2] = -4
        self.assertEqual(self.lib.open_cfw_cy8c_switch_to_dfu(), -1)

    def test_touch_frame_and_difference_read_policy(self) -> None:
        for index in range(16):
            self.register_data()[3][index] = index + 1
        frame = (ctypes.c_uint8 * 16)()
        self.lib.open_cfw_cy8c_read_touch_frame(frame)
        self.assertEqual(list(frame), list(range(1, 17)))
        for index in range(10):
            self.register_data()[4][index] = 20 + index
        difference = (ctypes.c_uint8 * 10)(*([0xEE] * 10))
        self.assertEqual(self.lib.open_cfw_cy8c_read_difference(difference), 0)
        self.assertEqual(list(difference), list(range(20, 30)))
        self.register_status()[4] = -7
        difference = (ctypes.c_uint8 * 10)(*([0xEE] * 10))
        self.assertEqual(self.lib.open_cfw_cy8c_read_difference(difference), -7)
        self.assertEqual(list(difference), [0xEE] * 10)

    def test_proximity_baseline_prepare_save_and_read(self) -> None:
        self.register_data()[1][:4] = (1, 2, 3, 4)
        value = ctypes.c_uint32()
        self.assertEqual(
            self.lib.open_cfw_cy8c_prepare_proximity_baseline(ctypes.byref(value)),
            0,
        )
        self.assertEqual(value.value, 0x01020304)
        scratch = (ctypes.c_uint8 * 4).in_dll(
            self.lib, "open_cfw_test_cy8c_baseline_scratch"
        )
        self.assertEqual(list(scratch), [1, 2, 3, 4])
        self.assertEqual(self.lib.open_cfw_cy8c_save_proximity_baseline(), 0)
        self.assertEqual(self.scalar("open_cfw_test_cy8c_last_command").value, 5)
        self.register_status()[5] = 9
        self.assertEqual(self.lib.open_cfw_cy8c_save_proximity_baseline(), -1)
        self.register_data()[6][:2] = (0x34, 0x12)
        self.assertEqual(self.lib.open_cfw_cy8c_read_proximity_baseline(), 0x1234)
        self.register_data()[6][:2] = (0, 0)
        self.assertEqual(self.lib.open_cfw_cy8c_read_proximity_baseline(), 0xFFFF)
        self.register_status()[6] = -1
        self.assertEqual(self.lib.open_cfw_cy8c_read_proximity_baseline(), 0xFFFF)

    def test_gesture_configuration_ack_and_validation(self) -> None:
        threshold = ctypes.c_uint16(0x3456)
        raw = (ctypes.c_uint8 * 32).in_dll(
            self.lib, "open_cfw_test_cy8c_raw_read_data"
        )
        raw[:3] = (7, 0, 0x17)
        self.assertEqual(self.lib.open_cfw_cy8c_write_gesture_cfg(ctypes.byref(threshold)), 0)
        self.assertEqual(self.scalar("open_cfw_test_cy8c_last_command").value, 0x101)
        written = (ctypes.c_uint8 * 32).in_dll(
            self.lib, "open_cfw_test_cy8c_last_data"
        )
        self.assertEqual(list(written)[:2], [0x56, 0x34])
        raw[2] = 0
        self.assertEqual(self.lib.open_cfw_cy8c_write_gesture_cfg(ctypes.byref(threshold)), -1)
        zero = ctypes.c_uint16(0)
        self.assertEqual(self.lib.open_cfw_cy8c_write_gesture_cfg(ctypes.byref(zero)), -1)
        self.assertEqual(self.lib.open_cfw_cy8c_write_gesture_cfg(None), -1)

        self.register_data()[8][:2] = (0x78, 0x56)
        observed = ctypes.c_uint16()
        self.assertEqual(self.lib.open_cfw_cy8c_read_gesture_cfg(ctypes.byref(observed)), 0)
        self.assertEqual(observed.value, 0x5678)
        self.register_data()[8][:2] = (0, 0)
        self.assertEqual(self.lib.open_cfw_cy8c_read_gesture_cfg(ctypes.byref(observed)), -1)
        self.assertEqual(self.lib.open_cfw_cy8c_read_gesture_cfg(None), -1)

    def test_each_selector_is_one_thumb_function(self) -> None:
        selectors = {
            "I2C_REGISTER_WRITE": "open_cfw_cy8c_i2c_register_write",
            "I2C_REGISTER_READ": "open_cfw_cy8c_i2c_register_read",
            "I2C_RAW_WRITE": "open_cfw_cy8c_i2c_raw_write",
            "I2C_RAW_READ": "open_cfw_cy8c_i2c_raw_read",
            "COMMAND": "open_cfw_cy8c_command",
            "READ_COMMAND": "open_cfw_cy8c_read_command",
            "WRITE_COMMAND": "open_cfw_cy8c_write_command",
            "SAVE_COMMAND": "open_cfw_cy8c_save_command",
            "READ_BASELINE_COMMAND": "open_cfw_cy8c_read_baseline_command",
            "GESTURE_THRESHOLD_VALID": "open_cfw_cy8c_gesture_threshold_valid",
            "WRITE_GESTURE_PRIVATE": "open_cfw_cy8c_write_gesture_private",
            "READ_GESTURE_PRIVATE": "open_cfw_cy8c_read_gesture_private",
            "INSTALL_DEFAULT_OPS": "open_cfw_cy8c_install_default_ops",
            "SWITCH_TO_DFU": "open_cfw_cy8c_switch_to_dfu",
            "RESET": "open_cfw_cy8c_reset",
            "INITIALIZE": "open_cfw_cy8c_initialize",
            "READ_TOUCH_FRAME": "open_cfw_cy8c_read_touch_frame",
            "READ_DIFFERENCE": "open_cfw_cy8c_read_difference",
            "PREPARE_PROXIMITY_BASELINE": "open_cfw_cy8c_prepare_proximity_baseline",
            "SAVE_PROXIMITY_BASELINE": "open_cfw_cy8c_save_proximity_baseline",
            "READ_PROXIMITY_BASELINE": "open_cfw_cy8c_read_proximity_baseline",
            "WRITE_GESTURE_CFG": "open_cfw_cy8c_write_gesture_cfg",
            "READ_GESTURE_CFG": "open_cfw_cy8c_read_gesture_cfg",
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
                    "clang", *flags, f"-DOPEN_CFW_CY8C_{selector}_ONLY=1",
                    "-c", str(SOURCE), "-o", str(target),
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
