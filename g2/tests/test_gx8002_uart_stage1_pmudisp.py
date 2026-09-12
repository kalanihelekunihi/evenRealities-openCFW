"""Host contract and regression tests for the UART stage-1 pmudispatch leaf.

The full decoded stock/source differential lives in
tools/verify_gx8002_uart_stage1_pmudisp.py (run by the candidate builder);
these tests pin the interpreter semantics, the oracle/table model, and
the placement/envelope regression on macOS.

Native host execution of the assembly leaf is infeasible here: the
body dereferences fill-provided 32-bit target addresses (entry,
selector, cells) and retained jump-table addresses, which truncate on
the 64-bit host (the same truncation
test_gx8002_uart_stage1_pmufill documents for desc[0]). The
interpreter tests below execute the assembled target object instead,
which is the shipped code shape.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from verify_gx8002_uart_stage1_pmudisp import (
    PMUDISP_FLAGS, PMUFILL_FLAGS, S_SOURCE, FILL_SOURCE, SPECS,
    LINKER_SCRIPT, JT1, JT2, JT1_IDS, JT2_IDS, JT1_MAP, JT1_PASS,
    JT1_TARGET_FILL, JT2_CHECK, JT2_TARGET_BIT, JT1_EXPECT, JT2_EXPECT,
    Model, execute, oracle, battery_cases, config_ram, table_ram_for,
    check_shape, check_tables, seed, signed, HandedOff,
    SP0, DESC, ENTRY, FILL, HANDOFF, MASK)
from verify_gx8002_analog_source import sha
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA

BASELINE = ROOT / 'docs/research/gx8002-uart-stage1-pmudisp-verification.json'


def tiny(ops, start=0x1000):
    """Hand-built snippet plus a branch-to-self terminator address."""
    code = {}
    pc = start
    for op, operand in ops:
        code[pc] = (op, operand, 2)
        pc += 2
    term = pc
    code[term] = ('br', hex(term), 2)
    return code, start, term


def run(code, start, term, args, ram):
    model = Model(ram)
    try:
        execute(code, start, args, model, handoff=term)
    except HandedOff as done:
        return done.registers, list(done.model.trace)
    raise AssertionError('expected HandedOff')


class TargetInterpreter(unittest.TestCase):
    def test_jmp_indirect(self):
        # A jump to a mapped address transfers control.
        code = {0x1000: ('jmp', 'r0', 2), 0x1002: ('br', '0x1002', 2)}
        model = Model({})
        try:
            execute(code, 0x1000, (0x1002, 0, 0), model, handoff=0x1002)
        except HandedOff as done:
            self.assertEqual(done.registers['r0'], 0x1002)
        else:
            raise AssertionError('expected HandedOff')
        # A jump into unmapped code is a hard failure, not a silent exit.
        code, start, term = tiny([('jmp', 'r2')])
        model = Model({})
        with self.assertRaises(ValueError):
            execute(code, start, (0x5000, 0, 0), model, handoff=term)

    def test_bclri_clears_bit(self):
        code, start, term = tiny([('mov', 'r1, r0'),
                                  ('bclri', 'r1, 0'),
                                  ('bclri', 'r2, 2')])
        regs, _ = run(code, start, term, (0xffffffff, 0, 0), {})
        self.assertEqual(regs['r1'], 0xfffffffe)
        self.assertEqual(regs['r2'], seed('r2') & ~(1 << 2) & MASK)

    def test_three_operand_shifts_execute_reversed(self):
        # The stock body proves printed (rd, rx, ry) executes as
        # ry OP rx (see the audit doc): tlsl r5,r3,r5 with r3=1 and
        # r5=fill computes fill<<1, not 1<<fill.
        code, start, term = tiny([('mov', 'r3, r0'),
                                  ('lsl', 'r5, r3, r5')])
        regs, _ = run(code, start, term, (1, 0, 0), {})
        r5seed = seed('r5')
        self.assertEqual(regs['r5'], (r5seed << 1) & MASK)
        code, start, term = tiny([('mov', 'r3, r0'),
                                  ('lsr', 'r0, r3, r0')])
        regs, _ = run(code, start, term, (0xa5a5a502, 0, 1), {})
        self.assertEqual(regs['r0'],
                         (0xa5a5a502 >> (0xa5a5a502 & 31)) & MASK)

    def test_two_operand_shifts_are_standard(self):
        # Note: execute takes (r0, r1, caller_r6); r2 keeps its seed,
        # so the count comes from r6 via mov.
        code, start, term = tiny([('mov', 'r3, r0'), ('mov', 'r4, r0'),
                                  ('mov', 'r2, r6'),
                                  ('lsl', 'r3, r1'),
                                  ('lsr', 'r4, r2')])
        regs, _ = run(code, start, term, (0x100, 3, 4), {})
        self.assertEqual(regs['r3'], 0x800)
        self.assertEqual(regs['r4'], 0x10)

    def test_bkpt_traps(self):
        code, start, term = tiny([('bkpt', '')])
        model = Model({})
        with self.assertRaises(ValueError):
            execute(code, start, (0, 0, 0), model, handoff=term)

    def test_push_pop_round_trip(self):
        code, start, term = tiny([('push', 'r4-r6, r15'),
                                  ('subi', 'r14, r14, 24'),
                                  ('addi', 'r14, r14, 24'),
                                  ('pop', 'r4-r6, r15')])
        ram = {SP0 - 64 + 4 * i: 0 for i in range(64)}
        regs, trace = run(code, start, term, (0, 0, 0x12345678), dict(ram))
        self.assertEqual(regs['r6'], 0x12345678)
        self.assertEqual(regs['r14'], SP0)

    def test_bsr_rejects_foreign_calls(self):
        code, start, term = tiny([('bsr', '0x10000ea0')])
        model = Model({})
        with self.assertRaises(ValueError):
            execute(code, start, (0, 0, 0), model, handoff=term)


class OracleTables(unittest.TestCase):
    def test_dump_matches_pinned_maps(self):
        if not IMAGE.exists():
            raise unittest.SkipTest('authenticated codec oracle unavailable')
        stock = IMAGE.read_bytes()
        if sha(stock) != IMAGE_SHA:
            raise unittest.SkipTest('stock identity changed')
        jt1, jt2 = check_tables(stock)
        self.assertEqual(len(jt1), len(JT1_IDS))
        self.assertEqual(len(jt2), len(JT2_IDS))

    def test_reverse_maps_encode_logistics_map(self):
        # The pinned dump, the battery logistics map, and the oracle
        # reverse maps must tell the same story.
        for ident, fill in JT1_MAP.items():
            slot = ident - JT1_IDS[0]
            target = JT1_EXPECT[slot]
            if fill == ident:
                self.assertEqual(target, JT1_PASS)
            else:
                self.assertEqual(JT1_TARGET_FILL[target], fill)
        for slot, target in enumerate(JT2_EXPECT):
            ident = JT2_IDS[0] + slot
            bit_arms = {6: 0x8000, 14: 0x8000, 11: 8, 13: 0x2000,
                        17: 1 << 16, 18: 1 << 17, 20: 1 << 18,
                        21: 1 << 19, 23: 1 << 20, 24: 1 << 21}
            if ident in bit_arms:
                self.assertEqual(JT2_TARGET_BIT[target], bit_arms[ident])
            else:
                self.assertEqual(target, JT2_CHECK)

    def test_oracle_rejects_unknown_table_targets(self):
        if not IMAGE.exists():
            raise unittest.SkipTest('authenticated codec oracle unavailable')
        stock = IMAGE.read_bytes()
        if sha(stock) != IMAGE_SHA:
            raise unittest.SkipTest('stock identity changed')
        ram, table_words, _ = config_ram('direct', 7, 1, 0, 0, 0,
                                         0xa5a5a500, 0)
        self.assertIsNotNone(ram)
        ram[JT1] = 0xdeadbeef
        with self.assertRaises(ValueError):
            oracle(7, 1, 0x600d600d, ram, table_words)

    def test_battery_scale(self):
        cases = battery_cases()
        self.assertGreaterEqual(len(cases), 200)
        idents = {case[1] for case in cases}
        self.assertTrue(set(range(26)) <= idents)


class PlacementRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not IMAGE.exists():
            raise unittest.SkipTest('authenticated codec oracle unavailable')
        cls.stock = IMAGE.read_bytes()
        if sha(cls.stock) != IMAGE_SHA:
            raise unittest.SkipTest('stock identity changed')
        cls.baseline = json.loads(BASELINE.read_text())

    def test_stock_envelope_unchanged(self):
        by_symbol = {f['symbol']: f for f in self.baseline['functions']}
        for symbol, _, offset, size, _, _ in SPECS:
            want = by_symbol[symbol]['stock_occurrences'][0]['sha256']
            self.assertEqual(sha(self.stock[offset:offset + size]), want, symbol)

    def test_linked_section_fills_placement(self):
        from build_transparent_image import Elf32
        prefix = ROOT / 'build/csky-macos/install/bin'
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            disp_obj = directory / 'pmudisp_s.o'
            subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *PMUDISP_FLAGS,
                            '-c', str(S_SOURCE), '-o', str(disp_obj)], check=True)
            fill_obj = directory / 'fill_c.o'
            subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *PMUFILL_FLAGS,
                            '-c', str(FILL_SOURCE), '-o', str(fill_obj)], check=True)
            script = directory / 'pmudisp.ld'
            script.write_text(LINKER_SCRIPT)
            linked = directory / 'pmudisp.elf'
            subprocess.run([str(prefix / 'csky-unknown-elf-ld'), '-T', str(script),
                            str(disp_obj), str(fill_obj), '-o', str(linked)],
                           check=True)
            elf = Elf32(linked.read_bytes(), str(linked))
            self.assertFalse(any(s['name'] and s['section'] == 0 for s in elf.symbols()))
            for symbol, _, offset, size, _, _ in SPECS:
                section = next(s for s in elf.sections if s['name'] == '.text.' + symbol)
                payload = elf.contents(section)
                self.assertEqual(len(payload), size, symbol)
                self.assertEqual(offset % section['align'], 0, symbol)
                self.assertEqual(elf.relocations(section['index']), [], symbol)


if __name__ == '__main__':
    unittest.main()
