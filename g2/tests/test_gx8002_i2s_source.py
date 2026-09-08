# SPDX-License-Identifier: MIT
import ctypes
import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from verify_gx8002_i2s_source import scratch_renaming, SOURCE, NAMES


class InstructionEquivalenceTests(unittest.TestCase):
    def test_only_consistent_scratch_renaming_is_accepted(self):
        original = [('ld.w', 'r2, (r3, 0x0)'), ('ins', 'r2, r0, 26, 24'), ('st.w', 'r2, (r3, 0x0)')]
        compiled = [('ld.w', 'r3, (r2, 0x0)'), ('ins', 'r3, r0, 26, 24'), ('st.w', 'r3, (r2, 0x0)')]
        self.assertEqual(scratch_renaming(original, compiled)['r2'], 'r3')
        for bad in ([('ld.w', 'r3, (r2, 0x0)'), ('ins', 'r3, r1, 26, 24'), compiled[2]],
                    [compiled[0], ('ins', 'r3, r0, 25, 24'), compiled[2]],
                    list(reversed(compiled))):
            with self.assertRaisesRegex(ValueError, 'differs beyond'):
                scratch_renaming(original, bad)


class HostRegisterTests(unittest.TestCase):
    def test_field_truncation_and_unrelated_register_preservation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            fixture = root / 'registers.c'
            fixture.write_text('#include <stdint.h>\nvolatile uint32_t open_cfw_gx8002_i2s_registers[3];\n')
            library = root / 'i2s.so'
            subprocess.run(['/usr/bin/clang', '-O2', '-shared', '-fPIC', '-std=c11',
                            '-DOPEN_CFW_GX8002_I2S_HOST_TEST', '-Wall', '-Wextra', '-Werror',
                            str(SOURCE), str(fixture), '-o', str(library)], check=True, capture_output=True)
            lib = ctypes.CDLL(str(library))
            registers = (ctypes.c_uint32*3).in_dll(lib, 'open_cfw_gx8002_i2s_registers')
            rng = random.Random(0xa0a0)
            boundary = (0, 1, 2, 7, 8, 255, 0xffffffff)
            cases = [(v,o) for v in boundary for o in boundary]
            cases += [(rng.getrandbits(32),rng.getrandbits(32)) for _ in range(4096)]
            for index, (name, shift, mask) in enumerate(zip(NAMES, (24,16,4), (7,1,1))):
                fn = getattr(lib, name)
                fn.argtypes = [ctypes.c_uint32]
                fn.restype = ctypes.c_int
                for value, previous in cases:
                    expected = [0x12345678, 0x98765432, 0xabcdef01]
                    expected[index] = previous
                    registers[:] = expected
                    self.assertEqual(fn(value), 0)
                    expected[index] = (previous & ~(mask<<shift)) | ((value & mask)<<shift)
                    self.assertEqual(list(registers), expected, (name, value, previous))


if __name__ == '__main__':
    unittest.main()
