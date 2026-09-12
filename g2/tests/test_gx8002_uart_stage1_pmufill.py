"""Host contract and regression tests for the UART stage-1 PMU fill leaf.

The full decoded stock/source differential lives in
tools/verify_gx8002_uart_stage1_pmufill.py (run by the candidate builder);
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
from verify_gx8002_uart_stage1_pmufill import (
    PMUFILL_FLAGS, C_SOURCE, SPECS, LINKER_SCRIPT, FillModel,
    execute, oracle, table_ram, TABLE_BASE, ENTRY_STRIDE, TABLE_ENTRIES,
    PMU_BASE, MCU_BASE, MASK)
from verify_gx8002_analog_source import sha
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA

BASELINE = ROOT / 'docs/research/gx8002-uart-stage1-pmufill-verification.json'

TABLE_WORDS = TABLE_ENTRIES * 4


class HostBehavior(unittest.TestCase):
    """Exercise the C leaf on the host against a redirected table."""

    @classmethod
    def setUpClass(cls):
        cls.table = (ctypes.c_uint32 * TABLE_WORDS)()
        base = ctypes.addressof(cls.table)
        directory = tempfile.mkdtemp(prefix='gx8002-stage1-pmufill-host-')
        cls.library = Path(directory) / 'pmufill.dylib'
        subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                        '-O2', '-fno-builtin', '-shared', '-fPIC',
                        '-DGX8002_STAGE1_DESC_TABLE_BASE=((uintptr_t)%#x)' % base,
                        str(C_SOURCE), '-o', str(cls.library)], check=True)
        lib = ctypes.CDLL(str(cls.library))
        cls.fill = lib.open_cfw_gx8002_uart_stage1_pmu_fill_desc
        cls.fill.argtypes = [ctypes.c_uint32,
                             ctypes.POINTER(ctypes.c_uint32)]
        cls.fill.restype = ctypes.c_uint32

    def setUp(self):
        for index in range(TABLE_WORDS):
            self.table[index] = 0xdeadbeef

    def set_table(self, words):
        for slot, word in enumerate(words):
            self.table[slot * 4] = word & 0xffffffff

    def call(self, ident, words):
        self.set_table(words)
        desc = (ctypes.c_uint32 * 6)(0xa5a5a5a5, 0xa5a5a5a5, 0xa5a5a5a5,
                                     0xa5a5a5a5, 0xa5a5a5a5, 0xa5a5a5a5)
        result = self.fill(ident, desc)
        return result, list(desc)

    def test_direct_hit_selects_domain(self):
        words = list(range(TABLE_ENTRIES))
        result, desc = self.call(3, words)
        # The 32-bit target truncates the entry address to 32 bits; the
        # 64-bit host keeps the full pointer, so mask before comparing.
        base = ctypes.addressof(self.table) & 0xffffffff
        self.assertEqual(result, 0)
        self.assertEqual(desc[0], (base + 3 * ENTRY_STRIDE) & 0xffffffff)
        self.assertEqual(desc[1:], [PMU_BASE, PMU_BASE | 0x8c,
                                    PMU_BASE | 0x18, PMU_BASE | 0x1c,
                                    PMU_BASE | 0x20])
        result, desc = self.call(17, words)
        self.assertEqual(result, 0)
        self.assertEqual(desc[0], (base + 17 * ENTRY_STRIDE) & 0xffffffff)
        self.assertEqual(desc[1:], [MCU_BASE, MCU_BASE | 0x88,
                                    MCU_BASE | 0x18, MCU_BASE | 0x1c,
                                    MCU_BASE | 0x20])

    def test_entry_zero_and_scan_priority(self):
        words = [0x77777777] * TABLE_ENTRIES
        words[0] = 9
        words[9] = 0x77777777
        words[20] = 9
        result, desc = self.call(9, words)
        base = ctypes.addressof(self.table) & 0xffffffff
        self.assertEqual(result, 0)
        self.assertEqual(desc[0], base)
        words[0] = 0x77777777
        result, desc = self.call(9, words)
        self.assertEqual(result, 0)
        self.assertEqual(desc[0], (base + 20 * ENTRY_STRIDE) & 0xffffffff)

    def test_rejections(self):
        words = list(range(TABLE_ENTRIES))
        desc = (ctypes.c_uint32 * 6)(1, 2, 3, 4, 5, 6)
        self.assertEqual(self.fill(26, desc), 0xffffffff)
        self.assertEqual(self.fill(0xffffffff, desc), 0xffffffff)
        self.assertEqual(list(desc), [1, 2, 3, 4, 5, 6])
        self.assertEqual(self.fill(4, None), 0xffffffff)
        words[4] = 0x01010101
        words[0] = 0x02020202
        result, _ = self.call(4, words)
        self.assertEqual(result, 0xffffffff)


class TargetInterpreter(unittest.TestCase):
    def test_bnezad_counts_down(self):
        code = {0x1000: ('bnezad', 'r3, 0x1000', 4),
                0x1004: ('rts', '', 2)}
        model = FillModel({})
        with self.assertRaises(ValueError):
            execute(code, 0x1000, 0, 0, model)

    def test_bnezad_loop_and_branch(self):
        code = {0x0ff0: ('movi', 'r3, 3', 2),
                0x0ff2: ('br', '0x1000', 2),
                0x1000: ('ld.w', 'r2, (r1, 0x0)', 2),
                0x1002: ('addi', 'r1, 4', 2),
                0x1004: ('bnezad', 'r3, 0x1000', 4),
                0x1008: ('rts', '', 2)}
        arena = 0x20001000
        model = FillModel({arena: 1, arena + 4: 2, arena + 8: 3})
        registers_run = execute(code, 0x0ff0, 0, arena, model)
        self.assertEqual(model.trace,
                         [('read', arena, 4, 1), ('read', arena + 4, 4, 2),
                          ('read', arena + 8, 4, 3)])
        self.assertTrue(registers_run[2])

    def test_incf_selects_on_condition(self):
        code = {0x1000: ('cmphsi', 'r0, 10', 2),
                0x1002: ('movi', 'r2, 136', 2),
                0x1004: ('movi', 'r3, 140', 2),
                0x1006: ('incf', 'r2, r3, 0', 4),
                0x100a: ('mov', 'r0, r2', 2),
                0x100c: ('rts', '', 2)}
        for ident, want in ((3, 140), (10, 136), (25, 136)):
            got, _, preserved = execute(code, 0x1000, ident, 0, FillModel({}))
            self.assertEqual(got, want, ident)
            self.assertTrue(preserved)

    def test_ldr_index_and_three_operand_bseti(self):
        code = {0x1000: ('movi', 'r12, 8216', 4),
                0x1004: ('bseti', 'r12, r12, 29', 4),
                0x1008: ('ldr.w', 'r2, (r12, r0 << 0)', 4),
                0x100c: ('mov', 'r0, r2', 2),
                0x100e: ('rts', '', 2)}
        words = table_ram(list(range(TABLE_ENTRIES)))
        # The index register carries a byte offset (slot * stride), matching
        # the stock `tlsli`-scaled addressing feeding `ldr.w .. << 0`.
        got, trace, preserved = execute(code, 0x1000, 5 * ENTRY_STRIDE, 0,
                                        FillModel(dict(words)))
        self.assertEqual(got, 5)
        self.assertEqual(trace, [('read', TABLE_BASE + 5 * ENTRY_STRIDE, 4, 5)])
        self.assertTrue(preserved)

    def test_cmpnei_and_ori(self):
        code = {0x1000: ('cmpnei', 'r0, 25', 2),
                0x1002: ('bt', '0x1008', 2),
                0x1004: ('movi', 'r0, 7', 2),
                0x1006: ('rts', '', 2),
                0x1008: ('ori', 'r0, r0, 32', 2),
                0x100a: ('rts', '', 2)}
        got, _, _ = execute(code, 0x1000, 25, 0, FillModel({}))
        self.assertEqual(got, 7)
        got, _, _ = execute(code, 0x1000, 4, 0, FillModel({}))
        self.assertEqual(got, 4 | 32)

    def test_unexpected_address_rejected(self):
        code = {0: ('ld.w', 'r0, (r3, 0x18)', 2), 2: ('rts', '', 2)}
        with self.assertRaises(ValueError):
            execute(code, 0, 0, 0, FillModel({}))


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
            c_obj = directory / 'pmufill_c.o'
            subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *PMUFILL_FLAGS,
                            '-c', str(C_SOURCE), '-o', str(c_obj)], check=True)
            script = directory / 'pmufill.ld'
            script.write_text(LINKER_SCRIPT)
            linked = directory / 'pmufill.elf'
            subprocess.run([str(prefix / 'csky-unknown-elf-ld'), '-T', str(script),
                            str(c_obj), '-o', str(linked)], check=True)
            elf = Elf32(linked.read_bytes(), str(linked))
            self.assertFalse(any(s['name'] and s['section'] == 0 for s in elf.symbols()))
            for symbol, _, offset, size, _, _ in SPECS:
                section = next(s for s in elf.sections if s['name'] == '.text.' + symbol)
                self.assertLessEqual(len(elf.contents(section)), size, symbol)
                self.assertEqual(offset % section['align'], 0, symbol)
                self.assertEqual(elf.relocations(section['index']), [], symbol)


if __name__ == '__main__':
    unittest.main()
