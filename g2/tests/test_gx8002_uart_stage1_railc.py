"""Host contract and regression tests for the UART stage-1 railc leaf.

The full decoded stock/source differential lives in
tools/verify_gx8002_uart_stage1_railc.py (run by the candidate builder);
these tests pin the interpreter semantics, the oracle/check model, and
the placement/envelope regression on macOS.

Native host execution of the C leaf is infeasible here: the body
dereferences fill-provided 32-bit target addresses (entry, selector,
MMIO cells), which truncate on the 64-bit host (the same truncation
test_gx8002_uart_stage1_pmufill documents for desc[0]). The
interpreter tests below execute the compiled target object instead,
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
from verify_gx8002_uart_stage1_railc import (
    RAILC_FLAGS, PMUFILL_FLAGS, C_SOURCE, FILL_SOURCE, SPECS, LINKER_SCRIPT,
    Model, execute, oracle, battery_cases, config_ram, predict_pops,
    check_shape, outside_window, seed, signed, Spinning,
    SP0, ENTRY, FILL, MASK)
from verify_gx8002_analog_source import sha
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA

BASELINE = ROOT / 'docs/research/gx8002-uart-stage1-railc-verification.json'


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
        execute(code, start, args, model, term, term + 2, -1, 0, None)
    except Spinning as done:
        return done.registers, list(done.model.trace)
    raise AssertionError('expected Spinning')


class TargetInterpreter(unittest.TestCase):
    def test_mvcv_moves_inverted_condition(self):
        # The railc cond depends on the inversion: cmpnei r5,0 then
        # mvcv must yield (r5 == 0), confirmed against stock stores.
        for r5, want in ((0, 1), (1, 0), (0xffffffff, 0)):
            code, start, term = tiny([('cmpnei', 'r5, 0'), ('mvcv', 'r2')])
            regs, _ = run(code, start, term, (0, 0, 0, r5), {})
            self.assertEqual(regs['r2'], want, r5)

    def test_blz_is_signed(self):
        # Values built with 2-byte insns (the executor seeds r4).
        setups = (([('movi', 'r4, 0'), ('bseti', 'r4, 31')], 7),
                  ([('movi', 'r4, 0'), ('bseti', 'r4, 30')], 0),
                  ([('movi', 'r4, 0'), ('mov', 'r0, r0')], 0))
        for setup, want in setups:
            ops = setup + [('blz', 'r4, 0x100a'), ('movi', 'r3, 0'),
                           ('br', '0x100c'), ('movi', 'r3, 7')]
            code, start, term = tiny(ops)
            model = Model({})
            try:
                execute(code, start, (0, 0, 0, 0), model, term, term + 2,
                        -1, 0, None)
            except Spinning as done:
                self.assertEqual(done.registers['r3'], want, setup)
            else:
                self.fail('expected Spinning')
        self.assertEqual((signed(0xffffffff), signed(0x7fffffff)),
                         (-1, 0x7fffffff))

    def test_byte_loads_zero_and_sign_extend(self):
        ram = {0x2000: 0x5aa580fb}
        code, start, term = tiny([('ld.b', 'r1, (r0, 0x0)'),
                                  ('ld.bs', 'r2, (r0, 0x0)'),
                                  ('ld.bs', 'r3, (r0, 0x3)')])
        regs, trace = run(code, start, term, (0x2000, 0, 0, 0), dict(ram))
        self.assertEqual(regs['r1'], 0xfb)
        self.assertEqual(regs['r2'], (0xfb - 0x100) & MASK)
        self.assertEqual(regs['r3'], 0x5a)
        self.assertEqual([e[2] for e in trace], [1, 1, 1])

    def test_sextb_zextb(self):
        code, start, term = tiny([('sextb', 'r1, r0'), ('zextb', 'r2, r0')])
        regs, _ = run(code, start, term, (0x80, 0, 0, 0), {})
        self.assertEqual(regs['r1'], 0xffffff80 & MASK)
        self.assertEqual(regs['r2'], 0x80)

    def test_shifts_mask_register_counts(self):
        # Negative counts use the low 5 bits (HW assumption shared by
        # both sides; pinned here, unqualified on hardware).
        code, start, term = tiny([('lsl', 'r1, r0, r2'),
                                  ('lsr', 'r3, r0, r2'),
                                  ('mov', 'r4, r0'), ('lsl', 'r4, r2'),
                                  ('mov', 'r5, r0'), ('lsr', 'r5, r2')])
        regs, _ = run(code, start, term, (0x3, 0, 0xffffffff, 9), {})
        self.assertEqual(regs['r1'], (0x3 << 31) & MASK)
        self.assertEqual(regs['r3'], 0x3 >> 31)
        self.assertEqual(regs['r4'], (0x3 << 31) & MASK)
        self.assertEqual(regs['r5'], 0x3 >> 31)

    def test_nor_xor_andi(self):
        code, start, term = tiny([('nor', 'r1, r0, r0'), ('xor', 'r2, r0'),
                                  ('andi', 'r3, r0, 1')])
        regs, _ = run(code, start, term,
                      (0x0f0f0f0f, 0xffffffff, 0xffffffff, 0), {})
        self.assertEqual(regs['r1'], 0xf0f0f0f0)
        self.assertEqual(regs['r2'], 0xf0f0f0f0)
        self.assertEqual(regs['r3'], 1)

    def test_push_pop_round_trip(self):
        code, start, term = tiny([('push', 'r4-r5, r15'),
                                  ('movi', 'r4, 1'), ('movi', 'r5, 2'),
                                  ('pop', 'r4-r5, r15')])
        ram = {a: 0 for a in range(SP0 - 16, SP0 + 16, 4)}
        regs, _ = run(code, start, term, (0, 0, 0, 7), dict(ram))
        self.assertEqual(regs['r4'], seed('r4'))
        self.assertEqual(regs['r5'], 7)
        self.assertEqual(regs['r15'], seed('r15'))
        self.assertEqual(regs['r14'], SP0)

    def test_bsr_rts_round_trip(self):
        code, start, term = tiny([('bsr', hex(FILL))])
        code[FILL] = ('movi', 'r0, 0', 2)
        code[FILL + 2] = ('rts', '', 2)
        regs, _ = run(code, start, term, (5, 6, 7, 8), {})
        self.assertEqual(regs['r0'], 0)
        self.assertEqual(regs['r1'], 6)

    def test_foreign_call_rejected(self):
        code, start, term = tiny([('bsr', '0x10000ea0')])
        with self.assertRaises(ValueError):
            run(code, start, term, (0, 0, 0, 0), {})

    def test_unmapped_access_rejected(self):
        code, start, term = tiny([('ld.w', 'r0, (r1, 0x0)')])
        with self.assertRaises(ValueError):
            run(code, start, term, (0, 0x30000000, 0, 0), {})

    def test_shape_guard_rejects_drift(self):
        code, _, _ = tiny([('push', 'r4-r6, r15'), ('bsr', hex(FILL))],
                          start=ENTRY)
        with self.assertRaises(ValueError):
            check_shape(code, ENTRY, 8)

    def test_window_traffic_excluded(self):
        trace = [('write', SP0 - 4, 4, 1), ('read', 0xa0010000, 4, 5),
                 ('read', SP0 + 8, 4, 6)]
        self.assertEqual(outside_window(trace), [('read', 0xa0010000, 4, 5)])


class OracleBehavior(unittest.TestCase):
    def base_ram(self):
        ram, _ = config_ram('direct', 2, 3, 7, 4, 0x12345678, 1 << 7, 1 << 3)
        return ram

    def test_body_set_path_and_pops(self):
        # d3 bit set, m bit set, arg2=0, caller 1: body-set, 2 pops.
        want = oracle(2, 0x0a345679, 0, 1, self.base_ram())
        self.assertEqual(want['path'], 'body-set')
        self.assertEqual(want['pops'], 2)
        self.assertEqual(want['desc'][0], 0x20002018 + 2 * 16)
        self.assertEqual(want['desc'][1], 0xa0010000)

    def test_body_clear_path(self):
        ram, _ = config_ram('direct', 2, 3, 7, 4, 0x12345678, 0, 1 << 3)
        want = oracle(2, 0x0a345679, 0, 1, ram)
        self.assertEqual(want['path'], 'body-clear')
        self.assertEqual(want['pops'], 2)

    def test_skip_path_observes_arg2(self):
        # Skip jumps to the check without popping: arg2 drives the
        # first decision, caller r5 the second.
        ram, _ = config_ram('direct', 2, 3, 7, 4, 0x1a2b3c4d, 1 << 7, 1 << 3)
        arg1 = 0x1a2b3c4d & 0x1ffffff
        self.assertEqual(oracle(2, arg1, 0, 0, ram)['pops'], 1)
        self.assertEqual(oracle(2, arg1, 1, 0, ram)['pops'], 0)
        self.assertEqual(oracle(2, arg1, 0, 1, ram)['pops'], 2)

    def test_d4_path_observes_address_bit(self):
        # The d4 reload repoints the checked word at base|0x1c.
        want = oracle(2, 0x0a345679, 0, 1, self.base_ram())
        self.assertEqual(want['pops'], 2)
        want0 = oracle(2, 0x0a345679, 0, 0, self.base_ram())
        self.assertEqual(want0['pops'], 1)

    def test_leftover_paths_have_no_prediction(self):
        ram = self.base_ram()
        self.assertEqual(oracle(26, 0, 0, 0, ram)['path'], 'fill-fail')
        self.assertIsNone(oracle(26, 0, 0, 0, ram)['pops'])

    def test_predict_agrees_with_oracle_on_battery(self):
        for case in battery_cases():
            (mode, ident, arg2, arg1, b4, b6, b0,
             sel, m_init, d3_init, _tag) = case
            ram, _ = config_ram(mode, ident, b4, b6, b0, sel, m_init, d3_init)
            is_body = (arg1 != (sel & 0x1ffffff))
            r0bit = bool(is_body and b4 >= 0 and ((d3_init >> b4) & 1))
            for c5 in (0, 1):
                want = oracle(ident, arg1, arg2, c5, ram)
                self.assertEqual(
                    predict_pops(ident, arg1, arg2, c5, r0bit, sel, is_body),
                    want['pops'], (case, c5))

    def test_battery_covers_edges(self):
        cases = battery_cases()
        tags = {c[-1] for c in cases}
        self.assertEqual(tags, {'body-a2z', 'body-a2o', 'skip'})
        modes = {c[0] for c in cases}
        self.assertEqual(modes, {'direct', 'entry0', 'scan'})
        idents = {c[1] for c in cases}
        self.assertEqual(idents, {2, 9, 10, 20})
        b4s = {c[4] for c in cases}
        self.assertTrue(any(b < 0 for b in b4s))
        self.assertIn(31, b4s)
        pops = set()
        for case in cases:
            (mode, ident, arg2, arg1, b4, b6, b0,
             sel, m_init, d3_init, _tag) = case
            ram, _ = config_ram(mode, ident, b4, b6, b0, sel, m_init, d3_init)
            is_body = (arg1 != (sel & 0x1ffffff))
            r0bit = bool(is_body and b4 >= 0 and ((d3_init >> b4) & 1))
            for c5 in (0, 1):
                pops.add(predict_pops(ident, arg1, arg2, c5, r0bit, sel,
                                      is_body))
        self.assertEqual(pops, {0, 1, 2})


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

    def test_linked_sections_fit_and_bind_nothing(self):
        from build_transparent_image import Elf32
        prefix = ROOT / 'build/csky-macos/install/bin'
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            railc_obj = directory / 'railc_c.o'
            subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *RAILC_FLAGS,
                            '-c', str(C_SOURCE), '-o', str(railc_obj)], check=True)
            fill_obj = directory / 'fill_c.o'
            subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *PMUFILL_FLAGS,
                            '-c', str(FILL_SOURCE), '-o', str(fill_obj)], check=True)
            script = directory / 'railc.ld'
            script.write_text(LINKER_SCRIPT)
            linked = directory / 'railc.elf'
            subprocess.run([str(prefix / 'csky-unknown-elf-ld'), '-T', str(script),
                            str(railc_obj), str(fill_obj), '-o', str(linked)],
                           check=True)
            elf = Elf32(linked.read_bytes(), str(linked))
            self.assertFalse(any(s['name'] and s['section'] == 0 for s in elf.symbols()))
            for symbol, _, offset, size, _, _ in SPECS:
                section = next(s for s in elf.sections if s['name'] == '.text.' + symbol)
                self.assertLessEqual(len(elf.contents(section)), size, symbol)
                self.assertEqual(offset % section['align'], 0, symbol)
                self.assertEqual(elf.relocations(section['index']), [], symbol)


if __name__ == '__main__':
    unittest.main()
