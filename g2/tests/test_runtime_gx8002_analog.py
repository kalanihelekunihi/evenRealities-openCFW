# SPDX-License-Identifier: MIT
"""Execute GX8002 analog updates against decoded register-transfer oracles."""
import ctypes
import random
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'components/shared/gx8002/runtime_gx8002_analog.c'


class AnalogRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        clang = shutil.which('clang')
        if not clang:
            raise unittest.SkipTest('host clang unavailable')
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        directory = Path(cls.temp.name)
        fixture = directory / 'registers.c'
        fixture.write_text('#include <stdint.h>\nvolatile uint32_t open_cfw_gx8002_analog_test_registers[6];\n')
        library = directory / 'analog.so'
        subprocess.run([clang, '-shared', '-fPIC', '-std=c11', '-O2',
                        '-DOPEN_CFW_GX8002_ANALOG_HOST_TEST=1', '-Wall', '-Wextra', '-Werror',
                        str(SOURCE), str(fixture), '-o', str(library)], check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.registers = (ctypes.c_uint32 * 6).in_dll(cls.lib, 'open_cfw_gx8002_analog_test_registers')

    def exercise(self, name, index, transfer):
        fn = getattr(self.lib, name)
        fn.argtypes = [ctypes.c_uint32]
        fn.restype = ctypes.c_int
        rng = random.Random(0x8002)
        pairs = [(old, value) for old in (0, 0xff, 0xa5, 0xffffffff, 0xdeadbeef)
                 for value in (0, 1, 2, 3, 31, 63, 64, 127, 255, 256, 0xffffffff)]
        pairs += [(rng.getrandbits(32), rng.getrandbits(32)) for _ in range(1000)]
        for old, value in pairs:
            initial = [0xa5a50000+i for i in range(6)]
            initial[index] = old
            self.registers[:] = initial
            self.assertEqual(fn(value), 0)
            expected = list(initial)
            expected[index] = transfer(old, value)
            self.assertEqual(list(self.registers), expected, (name, old, value))

    def test_trim_saturates_at_63_and_retains_control_bits(self):
        self.exercise('gx_analog_set_pga_itrim', 2,
                      lambda old, value: ((old & 0xc0) | min(value, 63)) & 0xff)

    def test_flag_updates_preserve_stock_shift_and_narrowing(self):
        for name, index, shift in (
            ('gx_analog_set_pga_bypass', 2, 6),
            ('gx_analog_set_pga_enable', 4, 6),
            ('gx_analog_set_adc_sample_clk_sel', 5, 0),
            ('gx_analog_set_adc_out_at_clk', 5, 1),
            ('gx_analog_set_adc_in_sel', 5, 2),
            ('gx_analog_set_adc_rstn', 5, 3),
        ):
            with self.subTest(name=name):
                self.exercise(name, index, lambda old, value, s=shift:
                              ((old & (0xff ^ (1 << s))) | (value << s)) & 0xff)


if __name__ == '__main__':
    unittest.main()
