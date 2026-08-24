from __future__ import annotations

import ctypes
import platform
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/at_tp.c"
FIXTURE = ROOT / "tests/fixtures"


class AtTpCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        cls.library = Path(cls.temporary.name) / f"at_tp{suffix}"
        subprocess.run([
            "clang", "-std=c11", "-shared", "-fPIC", "-O1",
            "-include", str(FIXTURE / "at_tp_host.h"),
            str(SOURCE), str(FIXTURE / "at_tp_host.c"),
            "-o", str(cls.library),
        ], check=True, cwd=ROOT)
        cls.loaded = ctypes.CDLL(str(cls.library))
        cls.loaded.open_cfw_at_tp_test.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        cls.loaded.open_cfw_at_tp_test.restype = ctypes.c_int

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.loaded.open_cfw_test_at_tp_reset()

    def uint(self, name: str) -> int:
        return ctypes.c_uint.in_dll(self.loaded, name).value

    def ushort(self, name: str) -> int:
        return ctypes.c_ushort.in_dll(self.loaded, name).value

    def output(self) -> bytes:
        return bytes((ctypes.c_char * 2048).in_dll(
            self.loaded, "open_cfw_test_at_tp_output_log"
        )).split(b"\0", 1)[0]

    def call(self, first: bytes | None, second: bytes | None = None) -> int:
        return self.loaded.open_cfw_at_tp_test(first, second)

    def test_null_is_fail_closed_and_unknown_preserves_stock_ack(self) -> None:
        self.assertEqual(self.call(None), 0)
        self.assertEqual(self.output(), b"")
        self.assertEqual(self.call(b"unknown"), 1)
        self.assertEqual(self.output(), b"AT^TP+OK\r\n")

    def test_diff_stop_debug_and_baseline_operations(self) -> None:
        diff = (ctypes.c_ushort * 5).in_dll(self.loaded, "open_cfw_test_at_tp_diff")
        diff[:] = (1, 2, 3, 4, 5)
        self.assertEqual(self.call(b"1"), 1)
        self.assertEqual(self.output(), b"diff: 1, 2, 3, 4, 5\r\nAT^TP+OK\r\n")
        self.setUp()
        self.assertEqual(self.call(b"0"), 1)
        self.assertEqual(self.uint("open_cfw_test_at_tp_stop_count"), 1)
        self.setUp()
        self.assertEqual(self.call(b"debug1"), 1)
        self.assertEqual(ctypes.c_ubyte.in_dll(self.loaded, "open_cfw_test_at_tp_debug_flag").value, 1)
        self.assertEqual(self.call(b"debug0"), 1)
        self.assertEqual(ctypes.c_ubyte.in_dll(self.loaded, "open_cfw_test_at_tp_debug_flag").value, 0)
        ctypes.c_ushort.in_dll(self.loaded, "open_cfw_test_at_tp_baseline").value = 321
        self.setUp()
        ctypes.c_ushort.in_dll(self.loaded, "open_cfw_test_at_tp_baseline").value = 321
        self.assertEqual(self.call(b"bsln_read"), 1)
        self.assertEqual(self.output(), b"Proximity baseline: 321\r\nAT^TP+OK\r\n")
        self.setUp()
        self.assertEqual(self.call(b"bsln_set"), 1)
        self.assertEqual(self.uint("open_cfw_test_at_tp_stop_count"), 1)
        self.assertEqual(self.uint("open_cfw_test_at_tp_prepare_count"), 1)
        self.assertEqual(self.uint("open_cfw_test_at_tp_save_count"), 1)

    def test_gesture_read_success_and_failure(self) -> None:
        ctypes.c_ushort.in_dll(self.loaded, "open_cfw_test_at_tp_readback").value = 450
        self.assertEqual(self.call(b"gesture_cfg_read"), 1)
        self.assertEqual(self.output(), b"Gesture cfg: long_press_threshold_ms=450\r\nAT^TP+OK\r\n")
        self.setUp()
        ctypes.c_int.in_dll(self.loaded, "open_cfw_test_at_tp_read_status").value = 1
        self.assertEqual(self.call(b"gesture_cfg_read"), 0)
        self.assertEqual(self.output(), b"Gesture cfg read failed.\r\n")

    def test_gesture_set_validates_bounds_and_null(self) -> None:
        for value, expected in [
            (None, b"Usage: AT^TP=gesture_cfg_set,<threshold_ms>\r\n"),
            (b"", b"Invalid gesture cfg. Usage: AT^TP=gesture_cfg_set,<threshold_ms>\r\n"),
            (b"0", b"Invalid gesture cfg. Usage: AT^TP=gesture_cfg_set,<threshold_ms>\r\n"),
            (b"65536", b"Invalid gesture cfg. Usage: AT^TP=gesture_cfg_set,<threshold_ms>\r\n"),
            (b"12x", b"Invalid gesture cfg. Usage: AT^TP=gesture_cfg_set,<threshold_ms>\r\n"),
        ]:
            with self.subTest(value=value):
                self.setUp()
                self.assertEqual(self.call(b"gesture_cfg_set", value), 0)
                self.assertEqual(self.output(), expected)
                self.assertEqual(self.uint("open_cfw_test_at_tp_write_count"), 0)

    def test_gesture_set_provider_failures_mismatch_and_success(self) -> None:
        ctypes.c_int.in_dll(self.loaded, "open_cfw_test_at_tp_write_status").value = 1
        self.assertEqual(self.call(b"gesture_cfg_set", b"100"), 0)
        self.assertEqual(self.output(), b"Gesture cfg write failed.\r\n")
        self.setUp()
        ctypes.c_int.in_dll(self.loaded, "open_cfw_test_at_tp_read_status").value = 1
        self.assertEqual(self.call(b"gesture_cfg_set", b"65535"), 0)
        self.assertEqual(self.uint("open_cfw_test_at_tp_delay_ticks"), 100)
        self.assertEqual(self.output(), b"Gesture cfg write success, but readback failed.\r\n")
        self.setUp()
        ctypes.c_ushort.in_dll(self.loaded, "open_cfw_test_at_tp_readback").value = 99
        self.assertEqual(self.call(b"gesture_cfg_set", b"100"), 0)
        self.assertEqual(self.output(), b"Gesture cfg write mismatch: wrote threshold=100, read back threshold=99\r\n")
        self.setUp()
        ctypes.c_ushort.in_dll(self.loaded, "open_cfw_test_at_tp_readback").value = 100
        self.assertEqual(self.call(b"gesture_cfg_set", b"100"), 1)
        self.assertEqual(self.ushort("open_cfw_test_at_tp_written"), 100)
        self.assertEqual(self.uint("open_cfw_test_at_tp_delay_count"), 1)
        self.assertEqual(self.output(), b"Gesture cfg updated and verified successfully.\r\nGesture cfg: long_press_threshold_ms=100\r\nAT^TP+OK\r\n")

    def test_thumb_compile_has_exact_global_text_surface(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "at_tp.o"
            subprocess.run([
                "clang", "-target", "thumbv7em-none-eabi", "-mthumb", "-O2",
                "-ffreestanding", "-fno-jump-tables", "-fomit-frame-pointer",
                "-fno-builtin", "-mno-unaligned-access", "-fno-unwind-tables",
                "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
                "-fdata-sections", "-Wall", "-Wextra", "-Werror", "-c",
                str(SOURCE), "-o", str(target),
            ], check=True, cwd=ROOT)
            symbols = subprocess.run(
                ["nm", str(target)], check=True, capture_output=True, text=True
            ).stdout
            observed = {
                fields[2] for line in symbols.splitlines()
                if len(fields := line.split()) == 3 and fields[1] == "T"
            }
            self.assertEqual(observed, {
                "open_cfw_at_tp_print_gesture_cfg", "open_cfw_at_tp_test"
            })


if __name__ == "__main__":
    unittest.main()
