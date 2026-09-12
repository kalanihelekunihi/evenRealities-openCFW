"""Host contract and regression tests for the UART stage-1 railb leaf.

The full decoded stock/source differential lives in
tools/verify_gx8002_uart_stage1_railb.py (run by the candidate builder);
these tests pin the interpreter semantics, the oracle/check model, and
the placement/envelope regression on macOS.

Native host execution of the assembly leaf is infeasible here: the
body dereferences fill-provided 32-bit target addresses (entry,
selector, MMIO cells), which truncate on the 64-bit host (the same
truncation test_gx8002_uart_stage1_pmufill documents for desc[0]). The
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
from verify_gx8002_uart_stage1_railb import (
    RAILB_FLAGS, PMUFILL_FLAGS, S_SOURCE, FILL_SOURCE, SPECS, LINKER_SCRIPT,
    Model, execute, oracle, battery_cases, config_ram, skip_gate,
    check_shape, seed, signed, Looped,
    SP0, ENTRY, FILL, MASK)
from verify_gx8002_analog_source import sha
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA

BASELINE = ROOT / 'docs/research/gx8002-uart-stage1-railb-verification.json'


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
        execute(code, start, args, model, term, 0, None)
    except Looped as done:
        return done.registers, list(done.model.trace)
    raise AssertionError('expected Looped')


class TargetInterpreter(unittest.TestCase):
    def test_halfword_load_zero_extends(self):
        # ld.h is modeled zero-extending; only zero values occur on
        # fill-reachable paths, so sign semantics stay unqualified.
        ram = {0x2000: 0x8001fb04}
        code, start, term = tiny([('ld.h', 'r1, (r0, 0x0)'),
                                  ('ld.h', 'r2, (r0, 0x2)')])
        regs, trace = run(code, start, term, (0x2000, 0, 0), dict(ram))
        self.assertEqual(regs['r1'], 0xfb04)
        self.assertEqual(regs['r2'], 0x8001)
        self.assertEqual([e[2] for e in trace], [2, 2])

    def test_halfword_spanning_words_rejected(self):
        ram = {0x2000: 0x11223344}
        code, start, term = tiny([('ld.h', 'r1, (r0, 0x3)')])
        with self.assertRaises(ValueError):
            run(code, start, term, (0x2000, 0, 0), dict(ram))

    def test_zexth_narrows(self):
        code, start, term = tiny([('zexth', 'r1, r0')])
        regs, _ = run(code, start, term, (0xcafe0001, 0, 0), {})
        self.assertEqual(regs['r1'], 0x0001)

    def test_rotl(self):
        code, start, term = tiny([('mov', 'r1, r0'), ('rotl', 'r1, r1, r2'),
                                  ('rotl', 'r3, r0, r2')])
        regs, _ = run(code, start, term, (0xfffffffe, 0, 7), {})
        self.assertEqual(regs['r1'], ((0xfffffffe << 7) | (0xfffffffe >> 25)) & MASK)
        self.assertEqual(regs['r3'], regs['r1'])
        # Count wraps at 32 with the low 5 bits.
        code, start, term = tiny([('rotl', 'r1, r0, r2')])
        regs, _ = run(code, start, term, (0x80000001, 0, 33), {})
        self.assertEqual(regs['r1'], ((0x80000001 << 1) | 1) & MASK)

    def test_andn(self):
        code, start, term = tiny([('andn', 'r1, r0, r2'),
                                  ('andn', 'r0, r2')])
        regs, _ = run(code, start, term, (0xff00ff00, 0, 0x0f0f0f0f), {})
        self.assertEqual(regs['r1'], 0xf000f000)
        self.assertEqual(regs['r0'], 0xf000f000)

    def test_shifts_mask_register_counts(self):
        # Register counts use the low 5 bits (both sides share the
        # executor, so agreement holds by construction; hardware shift
        # semantics for negative counts remain unqualified).
        code, start, term = tiny([('lsl', 'r1, r0, r2'),
                                  ('lsr', 'r3, r0, r2'),
                                  ('mov', 'r4, r0'), ('lsl', 'r4, r2'),
                                  ('mov', 'r5, r0'), ('lsr', 'r5, r2')])
        regs, _ = run(code, start, term, (0x3, 0, 0xffffffff, 0), {})
        self.assertEqual(regs['r1'], (0x3 << 31) & MASK)
        self.assertEqual(regs['r3'], 0x3 >> 31)
        self.assertEqual(regs['r4'], (0x3 << 31) & MASK)
        self.assertEqual(regs['r5'], 0x3 >> 31)

    def test_blz_is_signed(self):
        setups = (([('movi', 'r4, 0'), ('bseti', 'r4, 31')], 7),
                  ([('movi', 'r4, 0'), ('bseti', 'r4, 30')], 0))
        for setup, want in setups:
            ops = setup + [('blz', 'r4, 0x100a'), ('movi', 'r3, 0'),
                           ('br', '0x100c'), ('movi', 'r3, 7')]
            code, start, term = tiny(ops)
            model = Model({})
            try:
                execute(code, start, (0, 0, 0), model, term, 0, None)
            except Looped as done:
                self.assertEqual(done.registers['r3'], want, setup)
            else:
                self.fail('expected Looped')
        self.assertEqual((signed(0xffffffff), signed(0x7fffffff)),
                         (-1, 0x7fffffff))

    def test_byte_loads_zero_and_sign_extend(self):
        ram = {0x2000: 0x5aa580fb}
        code, start, term = tiny([('ld.b', 'r1, (r0, 0x0)'),
                                  ('ld.bs', 'r2, (r0, 0x0)'),
                                  ('ld.bs', 'r3, (r0, 0x3)')])
        regs, trace = run(code, start, term, (0x2000, 0, 0), dict(ram))
        self.assertEqual(regs['r1'], 0xfb)
        self.assertEqual(regs['r2'], (0xfb - 0x100) & MASK)
        self.assertEqual(regs['r3'], 0x5a)
        self.assertEqual([e[2] for e in trace], [1, 1, 1])

    def test_inct_follows_condition(self):
        code, start, term = tiny([('cmpnei', 'r0, 0'), ('inct', 'r1, r1, 1')])
        regs, _ = run(code, start, term, (5, 9, 0), {})
        self.assertEqual(regs['r1'], 10)
        regs, _ = run(code, start, term, (0, 9, 0), {})
        self.assertEqual(regs['r1'], 9)

    def test_push_pop_round_trip(self):
        code, start, term = tiny([('push', 'r4-r5, r15'),
                                  ('movi', 'r4, 1'), ('movi', 'r5, 2'),
                                  ('pop', 'r4-r5, r15')])
        ram = {a: 0 for a in range(SP0 - 16, SP0 + 16, 4)}
        regs, _ = run(code, start, term, (0, 0, 0), dict(ram))
        self.assertEqual(regs['r4'], seed('r4'))
        self.assertEqual(regs['r5'], seed('r5'))
        self.assertEqual(regs['r15'], seed('r15'))
        self.assertEqual(regs['r14'], SP0)

    def test_bsr_rts_round_trip(self):
        code, start, term = tiny([('bsr', hex(FILL))])
        code[FILL] = ('movi', 'r0, 0', 2)
        code[FILL + 2] = ('rts', '', 2)
        regs, _ = run(code, start, term, (5, 6, 7), {})
        self.assertEqual(regs['r0'], 0)
        self.assertEqual(regs['r1'], 6)

    def test_foreign_call_rejected(self):
        code, start, term = tiny([('bsr', '0x10000ea0')])
        with self.assertRaises(ValueError):
            run(code, start, term, (0, 0, 0), {})

    def test_unmapped_access_rejected(self):
        code, start, term = tiny([('ld.w', 'r0, (r1, 0x0)')])
        with self.assertRaises(ValueError):
            run(code, start, term, (0, 0x30000000, 0), {})

    def test_shape_guard_rejects_drift(self):
        code, _, _ = tiny([('push', 'r4-r6, r15'), ('bsr', hex(FILL))],
                          start=ENTRY)
        with self.assertRaises(ValueError):
            check_shape(code, ENTRY, 8)


class OracleBehavior(unittest.TestCase):
    def base_case(self):
        return ('direct', 2, 0, 0xcafe0001, 3, 7, 4, 0, 0, 0, 1 << 7, 1 << 3)

    def base_ram(self):
        (mode, ident, arg2, arg1, b4, b6, b0, r18, r13,
         sel, m_init, d3_init) = self.base_case()
        ram, _ = config_ram(mode, ident, b4, b6, b0, r18, r13,
                            sel, m_init, d3_init)
        return ram

    def test_body_path_and_desc(self):
        (mode, ident, arg2, arg1, b4, b6, b0, r18, r13,
         sel, m_init, d3_init) = self.base_case()
        want = oracle(ident, arg1, arg2, self.base_ram())
        self.assertEqual(want['outcome'], 'looped')
        self.assertEqual(want['path'], 'body')
        self.assertEqual(want['desc'][0], 0x20002018 + 2 * 16)
        self.assertEqual(want['desc'][1], 0xa0010000)
        # The check bit is set (d3 bit 3). The latch word evolves
        # one 1<<x step per pass: 8 -> 256 -> 1 -> 2 -> 4.
        self.assertEqual(want['regs']['r20'], 1)
        self.assertEqual(want['regs']['r21'], 4)

    def test_skip_gate_math(self):
        # gated = ((sel >> r18) & r13) + 1 when nonzero.
        self.assertEqual(skip_gate(0, 0, 0xdeadbeef), 0)
        self.assertEqual(skip_gate(1, 1, 0xffffffff), 2)
        self.assertEqual(skip_gate(7, 0x1f, 0xffffffff),
                         (((0xffffffff >> 7) & 0x1f) + 1) & MASK)

    def test_skip_path_has_no_prediction(self):
        # r18=1, r13=1, sel_init=0xffffffff: gated = ((0xffffffff >> 1)
        # & 1) + 1 = 2; low16 == 2 hits the leftover skip arm. (sel is
        # desc[1] + b0 with desc[1] the domain base; sel_init is the
        # value stored there.)
        ram, _ = config_ram('direct', 2, 3, 7, 4, 1, 1, 0xffffffff,
                            1 << 7, 1 << 3)
        gated = skip_gate(1, 1, 0xffffffff)
        want = oracle(2, 0xcafe0000 | gated, 0, ram)
        self.assertEqual(want['path'], 'skip')

    def test_leftover_paths_have_no_prediction(self):
        ram = self.base_ram()
        self.assertEqual(oracle(26, 0, 0, ram)['path'], 'fill-fail')
        self.assertEqual(oracle(26, 0, 0, ram)['outcome'], 'leftover-dependent')

    def test_id_gate_arms_only_eq6_or_ge10(self):
        # ident 9 takes neither the rotl tail nor the fold-first entry;
        # ident 6 and 20 take both when the cell bit is set. The fold
        # merges bit 7 back, so the arm is pinned by access count, not
        # by the final cell value: armed paths touch the cell four
        # more times (rotl re-read, rotl write, fold-first read,
        # fold-first write).
        arg1 = 0xcafe0001
        counts = {}
        for ident in (2, 6, 9, 20):
            ram, _ = config_ram('direct', ident, 3, 7, 4, 0, 0, 0,
                                1 << 7, 1 << 3)
            want = oracle(ident, arg1, 0, ram)
            self.assertEqual(want['outcome'], 'looped', ident)
            cell = want['desc'][2]
            counts[ident] = sum(1 for e in want['trace'] if e[1] == cell)
        self.assertEqual(counts[2], counts[9])
        self.assertEqual(counts[6], counts[20])
        self.assertEqual(counts[6] - counts[2], 4)

    def test_arg2_is_dead(self):
        (mode, ident, _a2, arg1, b4, b6, b0, r18, r13,
         sel, m_init, d3_init) = self.base_case()
        for arg2 in (0, 1, 0xa5a5a5a5):
            ram, _ = config_ram(mode, ident, b4, b6, b0, r18, r13,
                                sel, m_init, d3_init)
            want = oracle(ident, arg1, arg2, ram)
            self.assertEqual(want['outcome'], 'looped')
            self.assertEqual(want['trace'], oracle(ident, arg1, 0,
                                                   self.base_ram())['trace'])

    def test_battery_covers_edges(self):
        cases = battery_cases()
        self.assertGreaterEqual(len(cases), 200)
        modes = {c[0] for c in cases}
        self.assertEqual(modes, {'direct', 'entry0', 'scan'})
        idents = {c[1] for c in cases}
        self.assertEqual(idents, {2, 6, 9, 20})
        b4s = {c[4] for c in cases}
        self.assertTrue(any(b < 0 for b in b4s))
        self.assertIn(31, b4s)
        r13s = {c[8] for c in cases}
        self.assertIn(0, r13s)
        self.assertIn(0xffff, r13s)
        # Every admitted case loops (no leftover path sneaks in).
        for case in cases:
            (mode, ident, arg2, arg1, b4, b6, b0, r18, r13,
             sel, m_init, d3_init) = case
            ram, _ = config_ram(mode, ident, b4, b6, b0, r18, r13,
                                sel, m_init, d3_init)
            self.assertEqual(oracle(ident, arg1, arg2, ram)['outcome'],
                             'looped', case)


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

    def test_linked_section_is_byte_identical(self):
        from build_transparent_image import Elf32
        prefix = ROOT / 'build/csky-macos/install/bin'
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            railb_obj = directory / 'railb_s.o'
            subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *RAILB_FLAGS,
                            '-c', str(S_SOURCE), '-o', str(railb_obj)], check=True)
            fill_obj = directory / 'fill_c.o'
            subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *PMUFILL_FLAGS,
                            '-c', str(FILL_SOURCE), '-o', str(fill_obj)], check=True)
            script = directory / 'railb.ld'
            script.write_text(LINKER_SCRIPT)
            linked = directory / 'railb.elf'
            subprocess.run([str(prefix / 'csky-unknown-elf-ld'), '-T', str(script),
                            str(railb_obj), str(fill_obj), '-o', str(linked)],
                           check=True)
            elf = Elf32(linked.read_bytes(), str(linked))
            self.assertFalse(any(s['name'] and s['section'] == 0 for s in elf.symbols()))
            for symbol, _, offset, size, _, _ in SPECS:
                section = next(s for s in elf.sections if s['name'] == '.text.' + symbol)
                payload = elf.contents(section)
                self.assertEqual(len(payload), size, symbol)
                self.assertEqual(offset % section['align'], 0, symbol)
                self.assertEqual(elf.relocations(section['index']), [], symbol)
                self.assertEqual(sha(payload), sha(self.stock[offset:offset + size]),
                                 symbol + ' byte identity')


if __name__ == '__main__':
    unittest.main()
