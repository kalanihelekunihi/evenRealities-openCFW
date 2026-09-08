# SPDX-License-Identifier: MIT
import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class WatchdogTimeoutTests(unittest.TestCase):
    def test_all_accepted_16bit_timeouts(self):
        source=(ROOT/'components/shared/gx8002/runtime_gx8002_watchdog_initialize.c').read_text()
        # Compile the actual selector statements, excluding MMIO side effects.
        selector=source[source.index('    unsigned seconds ='):source.index('    volatile uint32_t *watchdog =')]
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory);(p/'selector.c').write_text('#include <stdint.h>\nunsigned select_timeout(uint16_t level_ms) {\n'+selector+'return setting;\n}\n')
            subprocess.run(['clang','-O2','-shared','-fPIC',str(p/'selector.c'),'-o',str(p/'selector.dylib')],check=True)
            lib=ctypes.CDLL(str(p/'selector.dylib'));lib.select_timeout.argtypes=[ctypes.c_uint16];lib.select_timeout.restype=ctypes.c_uint
            for level in range(1000,65536):
                # Stock first truncates milliseconds to seconds, then selects
                # the first exponent whose signed quotient compares >= unsigned seconds.
                seconds=level//1000
                expected=next(i for i in range(16) if ((1<<(i+16))//1000000 if i<15 else (-2147)&0xffffffff)>=seconds)
                self.assertEqual(lib.select_timeout(level),expected,level)

if __name__=='__main__':unittest.main()
