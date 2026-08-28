# SPDX-License-Identifier: MIT
"""Host and Cortex-M0+ tests for isolated touch source-admission adapters."""

import ctypes
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOUCH = ROOT / "components/shared/touch"
FIXTURE = ROOT / "tests/fixtures/touch_source_admission_host.c"
RUNTIME = TOUCH / "runtime_touch_runtime_adapters.c"
CAT2 = TOUCH / "runtime_touch_cat2_adapters.c"


class TouchSourceAdmissionRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        compiler = shutil.which("clang") or shutil.which("cc")
        if compiler is None:
            raise unittest.SkipTest("C compiler unavailable")
        cls.temp = tempfile.TemporaryDirectory()
        lib = Path(cls.temp.name) / "libtouch_admission.so"
        subprocess.run([
            compiler, "-std=c11", "-Wall", "-Wextra", "-Werror",
            "-shared", "-fPIC", "-I", str(TOUCH), str(RUNTIME), str(CAT2),
            str(FIXTURE), "-o", str(lib),
        ], check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(lib))
        cls.lib.touch_host_runtime_arrays.restype = ctypes.c_uint32
        cls.lib.touch_host_runtime_exit.argtypes = [ctypes.c_int]
        cls.lib.touch_host_halt_code.restype = ctypes.c_int
        cls.lib.touch_host_trace.restype = ctypes.c_uint32
        cls.lib.touch_host_delay.argtypes = [ctypes.c_uint16, ctypes.c_uint32]
        cls.lib.touch_host_delay.restype = ctypes.c_uint32
        cls.lib.touch_host_systick.restype = ctypes.c_uint32
        cls.lib.touch_host_syspm.argtypes = [ctypes.c_int]
        cls.lib.touch_host_syspm.restype = ctypes.c_int
        for name in ("touch_host_flash_route", "touch_host_gpio_route",
                     "touch_host_i2c_route", "touch_host_scb_read_route",
                     "touch_host_scb_write_route", "touch_host_scb_level_route",
                     "touch_host_gpio_value_route", "touch_host_msclp_route",
                     "touch_host_i2c_helper_route",
                     "touch_host_register_callback_route",
                     "touch_host_system_halt_route"):
            function = getattr(cls.lib, name)
            function.argtypes = [ctypes.c_int]
            function.restype = ctypes.c_int
        cls.lib.touch_host_sysclk_route.argtypes = [ctypes.c_int]
        cls.lib.touch_host_sysclk_route.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_runtime_array_order_and_null_skip(self):
        self.assertEqual(self.lib.touch_host_runtime_arrays(), 123)

    def test_exit_adapter_fails_closed_without_halt_provider(self):
        self.assertEqual(self.lib.touch_host_runtime_exit(0), -1)
        self.assertEqual(self.lib.touch_host_trace(), 0)
        self.assertEqual(self.lib.touch_host_runtime_exit(1), 0)
        self.assertEqual(self.lib.touch_host_trace(), 1)
        self.assertEqual(self.lib.touch_host_halt_code(), 7)

    def test_delay_us_exact_multiply_contract(self):
        self.assertEqual(self.lib.touch_host_delay(17, 24), 408)

    def test_systick_callback_order_and_reload(self):
        value = self.lib.touch_host_systick()
        self.assertEqual(value & 0xFF, 12)
        self.assertEqual(value >> 8, 999)

    def test_syspm_provider_contract_fails_closed(self):
        self.assertEqual(self.lib.touch_host_syspm(0), -1)
        self.assertEqual(self.lib.touch_host_syspm(1), 109)

    def test_flash_gpio_and_i2c_routes_fail_closed(self):
        self.assertEqual(self.lib.touch_host_flash_route(0), -1)
        self.assertEqual(self.lib.touch_host_flash_route(1), 17)
        self.assertEqual(self.lib.touch_host_gpio_route(0), -1)
        self.assertEqual(self.lib.touch_host_gpio_route(1), 6)
        self.assertEqual(self.lib.touch_host_i2c_route(0), -1)
        self.assertEqual(self.lib.touch_host_i2c_route(1), 0)
        self.assertEqual(self.lib.touch_host_trace(), 7)

    def test_scb_common_routes_fail_closed_without_mmio_provider(self):
        self.assertEqual(self.lib.touch_host_scb_read_route(0), 0)
        self.assertEqual(self.lib.touch_host_scb_read_route(1), 0x5A01)
        self.assertEqual(self.lib.touch_host_scb_write_route(0), 0)
        self.assertEqual(self.lib.touch_host_scb_write_route(1), 9)
        self.assertEqual(self.lib.touch_host_scb_level_route(0), -1)
        self.assertEqual(self.lib.touch_host_scb_level_route(1), 6)

    def test_gpio_and_sysclk_routes_fail_closed_without_mmio_provider(self):
        self.assertEqual(self.lib.touch_host_gpio_value_route(0), -1)
        self.assertEqual(self.lib.touch_host_gpio_value_route(1), 12)
        self.assertEqual(self.lib.touch_host_sysclk_route(0), 0xFFFF_FFFF)
        self.assertEqual(self.lib.touch_host_sysclk_route(1), 14)

    def test_final_cat2_routes_and_unavailable_halt_fail_closed(self):
        self.assertEqual(self.lib.touch_host_msclp_route(0), -1)
        self.assertEqual(self.lib.touch_host_msclp_route(1), 5)
        self.assertEqual(self.lib.touch_host_i2c_helper_route(0), -1)
        self.assertEqual(self.lib.touch_host_i2c_helper_route(1), 0)
        self.assertEqual(self.lib.touch_host_trace(), 9)
        self.assertEqual(self.lib.touch_host_register_callback_route(0), -1)
        self.assertEqual(self.lib.touch_host_register_callback_route(1), 1)
        self.assertEqual(self.lib.touch_host_system_halt_route(0), -1)
        self.assertEqual(self.lib.touch_host_system_halt_route(1), 7)

    def test_cortex_m0plus_compilation(self):
        clang = shutil.which("clang")
        if clang is None:
            self.skipTest("clang unavailable")
        for source in (RUNTIME, CAT2):
            out = Path(self.temp.name) / (source.stem + ".o")
            subprocess.run([
                clang, "--target=arm-none-eabi", "-mcpu=cortex-m0plus",
                "-mthumb", "-ffreestanding", "-std=c11", "-Wall", "-Wextra",
                "-Werror", "-I", str(TOUCH), "-c", str(source), "-o", str(out),
            ], check=True, capture_output=True, text=True)
            self.assertGreater(out.stat().st_size, 0)


if __name__ == "__main__":
    unittest.main()
