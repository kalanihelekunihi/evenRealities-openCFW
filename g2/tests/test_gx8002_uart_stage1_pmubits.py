"""Host contract and regression tests for UART stage-1 PMU trim-bit leaves.

The full decoded stock/source differential lives in
tools/verify_gx8002_uart_stage1_pmubits.py (run by the candidate builder);
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
from verify_gx8002_uart_stage1_pmubits import (
    PMUBITS_FLAGS, C_SOURCE, S_SOURCE, SPECS, battery_cases, execute, oracle)
from verify_gx8002_analog_source import sha
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA

BASELINE = ROOT / 'docs/research/gx8002-uart-stage1-pmubits-verification.json'


class HostBehavior(unittest.TestCase):
    """Exercise the C leaves on the host against a redirected register."""

    @classmethod
    def setUpClass(cls):
        cls.reg = ctypes.c_uint32(0)
        address = ctypes.addressof(cls.reg)
        directory = tempfile.mkdtemp(prefix='gx8002-stage1-pmubits-host-')
        cls.library = Path(directory) / 'pmubits.dylib'
        subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                        '-O2', '-fno-builtin', '-shared', '-fPIC',
                        '-DGX8002_UART_STAGE1_PMU_POR1=%#x' % address,
                        str(C_SOURCE), '-o', str(cls.library)], check=True)
        lib = ctypes.CDLL(str(cls.library))
        cls.set_bit0 = lib.open_cfw_gx8002_uart_stage1_pmu_set_bit0
        cls.set_bit0.argtypes = [ctypes.c_uint32]
        cls.set_bit0.restype = None
        cls.get_bit0 = lib.open_cfw_gx8002_uart_stage1_pmu_get_bit0
        cls.get_bit0.argtypes = []
        cls.get_bit0.restype = ctypes.c_uint32
        cls.get_bit1 = lib.open_cfw_gx8002_uart_stage1_pmu_get_bit1
        cls.get_bit1.argtypes = []
        cls.get_bit1.restype = ctypes.c_uint32

    def test_set_bit0_matches_oracle(self):
        for arg, reg_init in battery_cases('set0'):
            self.reg.value = reg_init
            self.set_bit0(arg)
            want_reg, _, _ = oracle('set0', arg, reg_init)
            self.assertEqual(self.reg.value, want_reg, 'set0(%#x) from %#x'
                             % (arg, reg_init))

    def test_get_bits_match_oracle(self):
        for _, reg_init in battery_cases('get0'):
            self.reg.value = reg_init
            self.assertEqual(self.get_bit0(), reg_init & 1)
            self.assertEqual(self.get_bit1(), (reg_init >> 1) & 1)


class TargetInterpreter(unittest.TestCase):
    def test_bit_clear_and_masked_or(self):
        code = {0: ('movih', 'r3, 40961', 4),
                4: ('ld.w', 'r2, (r3, 0x30)', 2),
                6: ('bclri', 'r2, 1', 2),
                8: ('st.w', 'r2, (r3, 0x30)', 2),
                10: ('ld.w', 'r2, (r3, 0x30)', 2),
                12: ('andi', 'r0, r0, 2', 4),
                16: ('or', 'r0, r2', 2),
                18: ('st.w', 'r0, (r3, 0x30)', 2),
                20: ('rts', '', 2)}
        _, reg, trace, preserved = execute(code, 0, 0x3, 0xf0)
        self.assertEqual(reg, 0xf2)
        self.assertEqual(trace, [('read', 0xa0010030, 0xf0),
                                 ('write', 0xa0010030, 0xf0),
                                 ('read', 0xa0010030, 0xf0),
                                 ('write', 0xa0010030, 0xf2)])
        self.assertTrue(preserved)

    def test_zext_single_bit_extract(self):
        leaf = {0: ('ld.w', 'r0, (r3, 0x30)', 2),
                2: ('zext', 'r0, r0, 1, 1', 4),
                6: ('rts', '', 2)}
        # Provide the base register the load expects.
        code = {0: ('movih', 'r3, 40961', 4)}
        code.update({address + 4: item for address, item in leaf.items()})
        result, _, _, _ = execute(code, 0, 0, 0b10)
        self.assertEqual(result, 1)

    def test_unexpected_address_rejected(self):
        code = {0: ('ld.w', 'r0, (r3, 0x34)', 2), 2: ('rts', '', 2)}
        with self.assertRaises(ValueError):
            execute(code, 0, 0, 0)


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
        for symbol, offset, size, _, _ in SPECS:
            want = by_symbol[symbol]['stock_occurrences'][0]['sha256']
            self.assertEqual(sha(self.stock[offset:offset + size]), want, symbol)

    def test_compiled_sections_fit_and_bind_nothing(self):
        from build_transparent_image import Elf32
        prefix = ROOT / 'build/csky-macos/install/bin'
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            c_obj = directory / 'pmubits_c.o'
            s_obj = directory / 'pmusbit_s.o'
            subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *PMUBITS_FLAGS,
                            '-c', str(C_SOURCE), '-o', str(c_obj)], check=True)
            subprocess.run([str(prefix / 'csky-unknown-elf-as'), '-mcpu=ck804ef',
                            '-mhard-float', str(S_SOURCE), '-o', str(s_obj)], check=True)
            linked = directory / 'pmubits.o'
            subprocess.run([str(prefix / 'csky-unknown-elf-ld'), '-r',
                            str(c_obj), str(s_obj), '-o', str(linked)], check=True)
            elf = Elf32(linked.read_bytes(), str(linked))
            self.assertFalse(any(s['name'] and s['section'] == 0 for s in elf.symbols()))
            for symbol, offset, size, _, _ in SPECS:
                section = next(s for s in elf.sections if s['name'] == '.text.' + symbol)
                self.assertLessEqual(section['size'], size, symbol)
                self.assertEqual(offset % section['align'], 0, symbol)
                self.assertEqual(elf.relocations(section['index']), [], symbol)

    def test_assembled_set_bit1_is_byte_identical(self):
        from build_transparent_image import Elf32
        prefix = ROOT / 'build/csky-macos/install/bin'
        with tempfile.TemporaryDirectory() as directory:
            s_obj = Path(directory) / 'pmusbit_s.o'
            subprocess.run([str(prefix / 'csky-unknown-elf-as'), '-mcpu=ck804ef',
                            '-mhard-float', str(S_SOURCE), '-o', str(s_obj)], check=True)
            elf = Elf32(s_obj.read_bytes(), str(s_obj))
            section = next(s for s in elf.sections
                           if s['name'] == '.text.open_cfw_gx8002_uart_stage1_pmu_set_bit1')
            self.assertEqual(elf.contents(section), self.stock[0x3dc:0x3dc + 24])


if __name__ == '__main__':
    unittest.main()
