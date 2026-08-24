from __future__ import annotations

import ctypes
import platform
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/apollo_main/core_overlay/cb_ring_battery.c"
FIXTURES = ROOT / "tests/fixtures"


class CbRingBatteryCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        suffix = ".dylib" if platform.system() == "Darwin" else ".so"
        library = Path(cls.temp.name) / ("cb_ring_battery" + suffix)
        subprocess.run([
            "clang", "-std=c11", "-shared", "-fPIC", "-O1", "-Wall",
            "-Wextra", "-Werror", "-include",
            str(FIXTURES / "cb_ring_battery_host.h"), str(SOURCE),
            str(FIXTURES / "cb_ring_battery_host.c"), "-o", str(library),
        ], check=True, cwd=ROOT)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_test_ring_battery_word.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_test_ring_battery_word.restype = ctypes.c_uint32
        cls.lib.open_cfw_test_ring_battery_set.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.lib.open_cfw_cb_ring_battery_forward.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)]
        cls.lib.open_cfw_cb_ring_battery_register.argtypes = [ctypes.c_size_t]
        cls.lib.open_cfw_cb_ring_battery_register.restype = ctypes.c_uint32
        cls.lib.open_cfw_cb_ring_battery_notify.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.lib.open_cfw_cb_ring_battery_notify.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls): cls.temp.cleanup()

    def setUp(self): self.lib.open_cfw_test_ring_battery_reset()
    def word(self, index): return self.lib.open_cfw_test_ring_battery_word(index)

    def test_forwarder_preserves_in_out_pointer(self):
        self.lib.open_cfw_test_ring_battery_set(3, 5)
        value = ctypes.c_uint32(9)
        self.lib.open_cfw_cb_ring_battery_forward(2, ctypes.byref(value))
        self.assertEqual((value.value, self.word(0), self.word(1), self.word(2)), (14, 1, 2, 9))

    def test_lifecycle_and_identity(self):
        self.lib.open_cfw_cb_ring_battery_init()
        self.assertEqual(tuple(self.word(i) for i in range(4, 7)), (1, 1, 1))
        self.lib.open_cfw_cb_ring_battery_deinit()
        self.assertEqual((self.word(7), self.word(8)), (1, 1))

    def test_register_null_and_provider_return(self):
        self.lib.open_cfw_test_ring_battery_set(12, 0x45)
        self.assertEqual(self.lib.open_cfw_cb_ring_battery_register(0), 0)
        self.assertEqual(self.word(9), 0)
        self.assertEqual(self.lib.open_cfw_cb_ring_battery_register(0x1234), 0x45)
        self.assertEqual(tuple(self.word(i) for i in range(9, 12)), (1, 1, 0x1234))

    def test_notify_in_out_word(self):
        self.lib.open_cfw_test_ring_battery_set(3, 7)
        self.assertEqual(self.lib.open_cfw_cb_ring_battery_notify(1, 20), 27)
        self.assertEqual(tuple(self.word(i) for i in range(13, 16)), (1, 1, 20))

    def test_selector_builds(self):
        selectors = {
            "FORWARD": "open_cfw_cb_ring_battery_forward",
            "INIT": "open_cfw_cb_ring_battery_init",
            "DEINIT": "open_cfw_cb_ring_battery_deinit",
            "REGISTER": "open_cfw_cb_ring_battery_register",
            "NOTIFY": "open_cfw_cb_ring_battery_notify",
        }
        flags = ["-target", "thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding",
                 "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
                 "-mno-unaligned-access", "-fno-unwind-tables",
                 "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
                 "-fdata-sections", "-Wall", "-Wextra", "-Werror"]
        with tempfile.TemporaryDirectory() as directory:
            for selector, symbol in selectors.items():
                obj = Path(directory) / (selector + ".o")
                subprocess.run(["clang", *flags,
                    f"-DOPEN_CFW_CB_RING_BAT_{selector}_ONLY=1", "-c",
                    str(SOURCE), "-o", str(obj)], check=True, cwd=ROOT)
                output = subprocess.run(["nm", str(obj)], check=True,
                    capture_output=True, text=True).stdout
                text_symbols = {fields[2] for line in output.splitlines()
                    if len(fields := line.split()) == 3 and fields[1] == "T"}
                self.assertEqual(text_symbols, {symbol})


if __name__ == "__main__": unittest.main()
