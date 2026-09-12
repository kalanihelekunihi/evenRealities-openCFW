"""Host contract and regression tests for UART stage-1 div/mod/noop leaves.

The full decoded stock/source differential lives in
tools/verify_gx8002_uart_stage1_divmod.py (run by the candidate builder);
these tests pin the host behavior, the interpreter semantics, and the
placement/envelope regression on macOS.
"""
import ctypes
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from verify_gx8002_uart_stage1_divmod import (
    DIVMOD_FLAGS, SOURCE, SPECS, STUB, battery_cases, decode, execute, oracle)
from verify_gx8002_analog_source import sha
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA

BASELINE = ROOT / 'docs/research/gx8002-uart-stage1-divmod-verification.json'


class HostContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        directory = tempfile.mkdtemp(prefix='gx8002-stage1-divmod-')
        cls.library = Path(directory) / 'divmod.dylib'
        subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                        '-O2', '-fno-builtin', '-shared', '-fPIC',
                        str(SOURCE), '-o', str(cls.library)], check=True)
        lib = ctypes.CDLL(str(cls.library))
        cls.udiv = lib.open_cfw_gx8002_uart_stage1_udiv
        cls.udiv.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.udiv.restype = ctypes.c_uint32
        cls.umod = lib.open_cfw_gx8002_uart_stage1_umod
        cls.umod.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.umod.restype = ctypes.c_uint32

    def test_div_matches_oracle(self):
        for num, den in battery_cases():
            self.assertEqual(self.udiv(num, den), oracle(num, den, False),
                             'udiv(%#x, %#x)' % (num, den))

    def test_mod_matches_oracle(self):
        for num, den in battery_cases():
            self.assertEqual(self.umod(num, den), oracle(num, den, True),
                             'umod(%#x, %#x)' % (num, den))

    def test_divide_by_zero_convention(self):
        self.assertEqual(self.udiv(0, 0), 1)
        self.assertEqual(self.udiv(7, 0), 0)
        self.assertEqual(self.umod(7, 0), 7)
        self.assertEqual(self.umod(0, 0), 0)


class TargetInterpreter(unittest.TestCase):
    def test_unsigned_compare_and_branch(self):
        code = {0: ('cmphs', 'r1, r0', 2), 2: ('bt', '0x8', 2),
                4: ('movi', 'r0, 0', 2), 6: ('rts', '', 2),
                8: ('movi', 'r0, 1', 2), 10: ('rts', '', 2)}
        self.assertEqual(execute(code, 0, 3, 5)[0], 1)
        self.assertEqual(execute(code, 0, 5, 3)[0], 0)

    def test_signed_branch_and_two_operand_or(self):
        code = {0: ('blz', 'r1, 0x8', 4), 4: ('or', 'r0, r1', 2),
                6: ('rts', '', 2), 8: ('movi', 'r0, 0', 2), 10: ('rts', '', 2)}
        self.assertEqual(execute(code, 0, 0xa5, 0x80000001)[0], 0)
        self.assertEqual(execute(code, 0, 0xa5, 7)[0], 0xa5 | 7)

    def test_conditional_increment_and_subi(self):
        code = {0: ('cmphs', 'r0, r1', 2), 2: ('inct', 'r0, r2, 0', 4),
                6: ('subi', 'r2, 1', 2), 8: ('rts', '', 2)}
        result, preserved, accesses = execute(code, 0, 9, 4)
        self.assertEqual((result, preserved, accesses), (0x98760002, True, []))
        result, _, _ = execute({0: ('cmphs', 'r0, r1', 2), 2: ('inct', 'r0, r2, 0', 4),
                               6: ('rts', '', 2)}, 0, 3, 4)
        self.assertEqual(result, 3)


class PlacementRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not IMAGE.exists():
            raise unittest.SkipTest('authenticated codec oracle unavailable')
        cls.stock = IMAGE.read_bytes()
        if sha(cls.stock) != IMAGE_SHA:
            raise unittest.SkipTest('stock identity changed')
        cls.baseline = json.loads(BASELINE.read_text())

    def test_stock_envelopes_unchanged(self):
        by_symbol = {f['symbol']: f for f in self.baseline['functions']}
        specs = [(s[0], s[1], s[2]) for s in SPECS] + [STUB]
        for symbol, offset, size in specs:
            want = by_symbol[symbol]['stock_occurrences'][0]['sha256']
            self.assertEqual(sha(self.stock[offset:offset + size]), want, symbol)

    def test_compiled_sections_fit_and_bind_nothing(self):
        from build_transparent_image import Elf32
        prefix = ROOT / 'build/csky-macos/install/bin'
        with tempfile.TemporaryDirectory() as directory:
            obj = Path(directory) / 'divmod.o'
            subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *DIVMOD_FLAGS,
                            '-c', str(SOURCE), '-o', str(obj)], check=True)
            elf = Elf32(obj.read_bytes(), str(obj))
            self.assertFalse(any(s['name'] and s['section'] == 0 for s in elf.symbols()))
            specs = [(s[0], s[1], s[2]) for s in SPECS] + [STUB]
            for symbol, offset, size in specs:
                section = next(s for s in elf.sections if s['name'] == '.text.' + symbol)
                self.assertLessEqual(section['size'], size, symbol)
                self.assertEqual(offset % section['align'], 0, symbol)
                self.assertEqual(elf.relocations(section['index']), [], symbol)


if __name__ == '__main__':
    unittest.main()
