"""Host contract and regression tests for UART stage-1 ID/bit leaves.

The full decoded stock/source differential lives in
tools/verify_gx8002_uart_stage1_idbit.py (run by the candidate builder);
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
from verify_gx8002_uart_stage1_idbit import (
    IDBIT_FLAGS, C_SOURCE, SPECS, LINKER_SCRIPT, IdBitModel,
    battery_cases, execute, oracle, ID_CELL, PMU_SOURCE_SEL0, MASK)
from verify_gx8002_analog_source import sha
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA

BASELINE = ROOT / 'docs/research/gx8002-uart-stage1-idbit-verification.json'


class HostBehavior(unittest.TestCase):
    """Exercise the C leaves on the host against redirected cells."""

    @classmethod
    def setUpClass(cls):
        cls.cell = ctypes.c_uint32(0)
        cls.reg = ctypes.c_uint32(0)
        cls.desc = (ctypes.c_uint32 * 2)(0, 0)
        directory = tempfile.mkdtemp(prefix='gx8002-stage1-idbit-host-')
        cls.library = Path(directory) / 'idbit.dylib'
        subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                        '-O2', '-fno-builtin', '-shared', '-fPIC',
                        '-DGX8002_STAGE1_ID_CELL=((volatile uint32_t *)%#x)'
                        % ctypes.addressof(cls.cell),
                        '-DGX8002_STAGE1_PMU_SOURCE_SEL0=((volatile uint32_t *)%#x)'
                        % ctypes.addressof(cls.reg),
                        str(C_SOURCE), '-o', str(cls.library)], check=True)
        lib = ctypes.CDLL(str(cls.library))
        cls.get_id = lib.open_cfw_gx8002_uart_stage1_get_stored_id
        cls.get_id.argtypes = []
        cls.get_id.restype = ctypes.c_uint32
        cls.bit_modify = lib.open_cfw_gx8002_uart_stage1_pmu_bit_modify
        cls.bit_modify.argtypes = [ctypes.POINTER(ctypes.c_uint32)]
        cls.bit_modify.restype = None

    def test_get_id_matches_oracle(self):
        for _, ram in battery_cases('get_id'):
            self.cell.value = ram[ID_CELL]
            self.assertEqual(self.get_id(), ram[ID_CELL])

    def test_bit_modify_matches_oracle(self):
        for desc_base, ram in battery_cases('bit_modify'):
            self.desc[0] = ram[desc_base]
            self.desc[1] = ram[(desc_base + 4) & ~0x3]
            self.reg.value = ram[PMU_SOURCE_SEL0]
            self.bit_modify(self.desc)
            _, want_ram, _ = oracle('bit_modify', desc_base, dict(ram))
            self.assertEqual(self.reg.value, want_ram[PMU_SOURCE_SEL0])
            self.assertEqual(self.desc[0], ram[desc_base])
            self.assertEqual(self.desc[1], ram[(desc_base + 4) & ~0x3])


class TargetInterpreter(unittest.TestCase):
    def test_rotl_mask_and_bit_set(self):
        code = {0: ('movih', 'r1, 40961', 4),
                4: ('bseti', 'r1, 7', 2),
                6: ('movi', 'r3, 0', 2),
                8: ('ld.w', 'r12, (r0, 0x0)', 4),
                12: ('subi', 'r3, 2', 2),
                14: ('ld.w', 'r2, (r1, 0xc)', 2),
                16: ('rotl', 'r3, r12', 2),
                18: ('and', 'r3, r2', 2),
                20: ('ld.b', 'r2, (r0, 0x4)', 2),
                22: ('lsl', 'r2, r12', 2),
                24: ('or', 'r3, r2', 2),
                26: ('st.w', 'r3, (r1, 0xc)', 2),
                28: ('rts', '', 2)}
        model = IdBitModel({0x2000: 3, 0x2004: 0xa5a501,
                            PMU_SOURCE_SEL0: 0x00000000})
        result = execute(code, 0, 0x2000, model)
        self.assertEqual(result[0], 0x2000)
        self.assertEqual(model.ram[PMU_SOURCE_SEL0], 0x08)
        self.assertEqual(model.ram[0x2000], 3)
        self.assertEqual(model.ram[0x2004], 0xa5a501)
        self.assertTrue(result[2])

    def test_stock_getter_shape_uses_literal_pool(self):
        code = {0: ('lrw', 'r3, 0x20002008', 4),
                4: ('ld.w', 'r0, (r3, 0x0)', 2),
                6: ('rts', '', 2)}
        model = IdBitModel({ID_CELL: 0x0d})
        result = execute(code, 0, 0x99, model)
        self.assertEqual(result[:2], (0x0d, [('read', ID_CELL, 4, 0x0d)]))
        self.assertTrue(result[2])

    def test_getter_trace_is_single_cell_read(self):
        code = {0: ('movi', 'r3, 8192', 4),
                4: ('bseti', 'r3, 29', 2),
                6: ('ld.w', 'r0, (r3, 0x8)', 2),
                8: ('rts', '', 2)}
        model = IdBitModel({ID_CELL: 0x09})
        result = execute(code, 0, 0xabcdef, model)
        self.assertEqual(result[:2], (0x09, [('read', ID_CELL, 4, 0x09)]))
        self.assertTrue(result[2])

    def test_unexpected_address_rejected(self):
        code = {0: ('ld.w', 'r0, (r3, 0x18)', 2), 2: ('rts', '', 2)}
        with self.assertRaises(ValueError):
            execute(code, 0, 0, IdBitModel({ID_CELL: 0}))


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
        for symbol, _, offset, size, _, _ in SPECS:
            want = by_symbol[symbol]['stock_occurrences'][0]['sha256']
            self.assertEqual(sha(self.stock[offset:offset + size]), want, symbol)

    def test_linked_sections_fit_and_bind_nothing(self):
        from build_transparent_image import Elf32
        prefix = ROOT / 'build/csky-macos/install/bin'
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            c_obj = directory / 'idbit_c.o'
            subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *IDBIT_FLAGS,
                            '-c', str(C_SOURCE), '-o', str(c_obj)], check=True)
            script = directory / 'idbit.ld'
            script.write_text(LINKER_SCRIPT)
            linked = directory / 'idbit.elf'
            subprocess.run([str(prefix / 'csky-unknown-elf-ld'), '-T', str(script),
                            str(c_obj), '-o', str(linked)], check=True)
            elf = Elf32(linked.read_bytes(), str(linked))
            self.assertFalse(any(s['name'] and s['section'] == 0 for s in elf.symbols()))
            for symbol, _, offset, size, _, _ in SPECS:
                section = next(s for s in elf.sections if s['name'] == '.text.' + symbol)
                self.assertLessEqual(section['size'], size, symbol)
                self.assertEqual(offset % section['align'], 0, symbol)
                self.assertEqual(elf.relocations(section['index']), [], symbol)

    def test_compiled_bit_modify_is_byte_identical(self):
        from build_transparent_image import Elf32
        prefix = ROOT / 'build/csky-macos/install/bin'
        with tempfile.TemporaryDirectory() as directory:
            c_obj = Path(directory) / 'idbit_c.o'
            subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *IDBIT_FLAGS,
                            '-c', str(C_SOURCE), '-o', str(c_obj)], check=True)
            elf = Elf32(c_obj.read_bytes(), str(c_obj))
            section = next(s for s in elf.sections
                           if s['name'] == '.text.open_cfw_gx8002_uart_stage1_pmu_bit_modify')
            self.assertEqual(elf.contents(section), self.stock[0x890:0x890 + 30])


if __name__ == '__main__':
    unittest.main()
