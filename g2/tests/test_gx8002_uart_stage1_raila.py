"""Host contract and regression tests for the UART stage-1 raila leaf.

The full decoded stock/source differential lives in
tools/verify_gx8002_uart_stage1_raila.py (run by the candidate builder);
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
from verify_gx8002_uart_stage1_raila import (
    RAILA_FLAGS, PMUFILL_FLAGS, S_SOURCE, FILL_SOURCE, SPECS, LINKER_SCRIPT,
    Model, execute, oracle, battery_cases, config_ram, check_shape, seed,
    signed, trunc_div, Stopped, MemFault, trap_pc_ok, BLOCK_PCS,
    deep_tables, pass_shift,
    SP0, ENTRY, FILL, FAILRE, MASK, FAIL_VISITS, FILL_CALLS, MAX_ID,
    FILL_TABLE_BASE)
from verify_gx8002_analog_source import sha
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA

BASELINE = ROOT / 'docs/research/gx8002-uart-stage1-raila-verification.json'


def tiny(ops, start=0x1000):
    """Hand-built snippet plus a branch-to-self loop-top address.

    The executor stops at FAILRE visits, so tests use FAILRE as the
    terminator address.
    """
    code = {}
    pc = start
    for op, operand in ops:
        code[pc] = (op, operand, 2)
        pc += 2
    return code, start, FAILRE


def run(code, start, args, ram):
    model = Model(ram)
    try:
        execute(code, start, args, model, None)
    except Stopped as done:
        return done
    raise AssertionError('expected Stopped')


class TargetInterpreter(unittest.TestCase):
    def test_divs_truncates_toward_zero(self):
        code, start, _ = tiny([('divs', 'r1, r0, r2'), ('br', hex(FAILRE))])
        done = run(code, start, (12, 0, 6), {})
        self.assertEqual(done.registers['r1'], 2)
        done = run(code, start, (0xfffffffe, 0, 6), {})
        self.assertEqual(done.registers['r1'], 0)
        # -12 / 6 == -2 (truncated, not floored).
        done = run(code, start, (0xfffffff4, 0, 6), {})
        self.assertEqual(done.registers['r1'], (-2) & MASK)
        # 12 / -6 == -2.
        done = run(code, start, (12, 0, 0xfffffffa), {})
        self.assertEqual(done.registers['r1'], (-2) & MASK)
        self.assertEqual(trunc_div(-7, 2), (-3) & MASK)

    def test_divs_by_zero_raises(self):
        code, start, _ = tiny([('divs', 'r1, r0, r2'), ('br', hex(FAILRE))])
        with self.assertRaises(ValueError):
            run(code, start, (12, 0, 0), {})

    def test_asri_sign_extends(self):
        code, start, _ = tiny([('asri', 'r1, r0, 2'), ('br', hex(FAILRE))])
        done = run(code, start, (0xfffffffc, 0, 0), {})
        self.assertEqual(done.registers['r1'], (0xffffffff) & MASK)
        done = run(code, start, (12, 0, 0), {})
        self.assertEqual(done.registers['r1'], 3)

    def test_cmplti_is_signed(self):
        code, start, _ = tiny([('cmplti', 'r0, 3'), ('mvcv', 'r1'),
                               ('br', hex(FAILRE))])
        # mvcv writes 1 when the condition is false.
        done = run(code, start, (2, 0, 0), {})
        self.assertEqual(done.registers['r1'], 0)
        done = run(code, start, (3, 0, 0), {})
        self.assertEqual(done.registers['r1'], 1)
        done = run(code, start, (0xffffffff, 0, 0), {})
        self.assertEqual(done.registers['r1'], 0)

    def test_two_operand_shifts(self):
        # Two-form shifts move Rd by Rs (the 0x966 check idiom:
        # tlsl r3, r0 with r3 == 1 isolates bit r0 of the retry
        # mask; r0 == 0 retries, which the battery confirms against
        # stock on both sides of the addressed fill).
        code, start, _ = tiny([('lsr', 'r1, r0'), ('movi', 'r3, 1'),
                               ('tlsl', 'r3, r2'), ('br', hex(FAILRE))])
        done = run(code, start, (7, 0xffffff80, 1), {})
        self.assertEqual(done.registers['r1'], (0xffffff80 >> 7) & MASK)
        self.assertEqual(done.registers['r3'], (1 << 1) & MASK)
        done = run(code, start, (0, 0, 0), {})
        self.assertEqual(done.registers['r3'], (1 << 0) & MASK)

    def test_nor_two_form_complements(self):
        code, start, _ = tiny([('nor', 'r1, r0'), ('br', hex(FAILRE))])
        done = run(code, start, (0x5a5a5a5a, 0, 0), {})
        self.assertEqual(done.registers['r1'], (~0x5a5a5a5a) & MASK)

    def test_unmapped_access_traps_with_pc_and_address(self):
        code, start, _ = tiny([('ld.w', 'r0, (r1, 0x0)')])
        done = run(code, start, (0, 0x30000000, 0), {})
        self.assertEqual(done.kind, 'trap')
        self.assertEqual(done.trap_pc, start)
        self.assertEqual(done.trap_addr, 0x30000000)
        self.assertIsInstance(done, Stopped)

    def test_failre_loop_counts_visits(self):
        code, start, _ = tiny([('br', hex(FAILRE))], start=FAILRE)
        done = run(code, start, (0, 0, 0), {})
        self.assertEqual(done.kind, 'fail-cycle')

    def test_fill_cap_bounds_retry_chains(self):
        code = {0x1000: ('movi', 'r0, 70', 2),
                0x1002: ('bsr', hex(FILL), 4),
                0x1006: ('bnezad', 'r0, 0x1002', 2),
                0x1008: ('br', hex(FAILRE), 2),
                FILL: ('rts', '', 2)}
        done = run(code, 0x1000, (0, 0, 0), {})
        self.assertEqual(done.kind, 'fill-cap')
        self.assertEqual(len(done.fill_bases), FILL_CALLS)

    def test_foreign_call_rejected(self):
        code, start, _ = tiny([('bsr', '0x10000ea0')])
        with self.assertRaises(ValueError):
            run(code, start, (0, 0, 0), {})

    def test_push_pop_round_trip(self):
        code, start, _ = tiny([('push', 'r4-r5, r15'),
                               ('movi', 'r4, 1'), ('movi', 'r5, 2'),
                               ('pop', 'r4-r5, r15')])
        ram = {a: 0 for a in range(SP0 - 16, SP0 + 16, 4)}
        done = run(code, start, (0, 0, 0), dict(ram))
        self.assertEqual(done.registers['r4'], seed('r4'))
        self.assertEqual(done.registers['r5'], seed('r5'))
        self.assertEqual(done.registers['r15'], seed('r15'))
        self.assertEqual(done.registers['r14'], SP0)

    def test_shape_guard_rejects_drift(self):
        code, _, _ = tiny([('push', 'r4-r6, r15'), ('bsr', hex(FILL))],
                          start=ENTRY)
        with self.assertRaises(ValueError):
            check_shape(code, ENTRY, 8)

    def test_trap_pc_sets(self):
        self.assertIn(0x1000089a, BLOCK_PCS['bitest'])
        self.assertIn(0x10000934, BLOCK_PCS['poll2'])
        self.assertEqual(BLOCK_PCS['idtable'], set())
        self.assertTrue(trap_pc_ok('poll2', 0x10000934))
        self.assertFalse(trap_pc_ok('poll2', 0x10000946))
        self.assertTrue(trap_pc_ok('fill', 0x10000780))
        self.assertFalse(trap_pc_ok('fill', 0x10000860))
        self.assertFalse(trap_pc_ok('nope', 0x1000089a))

    def test_signed_helper(self):
        self.assertEqual((signed(0xffffffff), signed(0x7fffffff)),
                         (-1, 0x7fffffff))


class OracleBehavior(unittest.TestCase):
    def base_case(self):
        # ident 9: owned entry bytes survive the fixed-entry
        # overrides (slots 2/7/8), so b6 == 7 agrees with m_init.
        return ('direct', 9, 0, 0, 3, 0x5a, 7,
                ((0, 0), (0, 0)), ((0, 0), (0, 0), (0, 0)),
                1 << 7, 1 << 3)

    def base_ram(self):
        (mode, ident, arg2, arg1, b4, b5, b6, neigh, fixed,
         m_init, d3_init) = self.base_case()
        ram, _ = config_ram(mode, ident, b4, b5, b6, neigh, fixed,
                            m_init, d3_init)
        return ram

    def test_first_pass_arms_then_fail_loop_traps(self):
        # ident 2, arg1 0: fill, merge path, pop/dispatch, fail tail,
        # then the fail loop traps on a drifted descriptor read.
        (mode, ident, arg2, arg1, b4, b5, b6, neigh, fixed,
         m_init, d3_init) = self.base_case()
        want = oracle(ident, arg1, arg2, self.base_ram())
        self.assertEqual(want['outcome'], 'trap')
        kinds = [e for e in want['trace'] if e[0] == 'write'
                 and e[1] == (0xa0010000 | 0x8c)]
        self.assertTrue(kinds, 'expected an m-cell store on the body path')

    def test_leftover_paths_have_no_prediction(self):
        ram = self.base_ram()
        self.assertEqual(oracle(MAX_ID + 1, 0, 0, ram)['path'], 'id-range')
        self.assertEqual(oracle(MAX_ID + 1, 0, 0, ram)['outcome'],
                         'leftover-dependent')
        # Entry byte 6 == 0xFF fails with unset address registers
        # (ident 9 keeps owned bytes out of the fixed slots).
        (mode, ident, arg2, arg1, _b4, b5, _b6, neigh, fixed,
         m_init, d3_init) = self.base_case()
        ram2, _ = config_ram(mode, ident, 3, b5, 0xff, neigh, fixed,
                             m_init, d3_init)
        self.assertEqual(oracle(ident, arg1, arg2, ram2)['path'],
                         'entry6-ff')

    def test_retry_fill_uses_popped_id(self):
        # After the first body pass the retry fill sees the popped
        # caller seed (out of range) and fast-fails into the fail
        # tail: at most two fill calls carry descriptor traffic.
        (mode, ident, arg2, arg1, b4, b5, b6, neigh, fixed,
         m_init, d3_init) = self.base_case()
        ram, _ = config_ram(mode, ident, b4, b5, b6, neigh, fixed,
                            m_init, d3_init)
        want = oracle(ident, arg1, arg2, ram)
        desc_writes = [e for e in want['trace'] if e[0] == 'write'
                       and e[1] in (0x20002800 - 36, 0x20002800)]
        self.assertTrue(desc_writes)

    def test_arg2_is_dead(self):
        (mode, ident, _a2, arg1, b4, b5, b6, neigh, fixed,
         m_init, d3_init) = self.base_case()
        traces = []
        for arg2 in (0, 1, 0xa5a5a5a5):
            ram, _ = config_ram(mode, ident, b4, b5, b6, neigh, fixed,
                                m_init, d3_init)
            want = oracle(ident, arg1, arg2, ram)
            self.assertNotEqual(want['outcome'], 'leftover-dependent')
            traces.append(want['trace'])
        self.assertEqual(traces[0], traces[1])
        self.assertEqual(traces[0], traces[2])

    def test_deep_tables_hit_stored5(self):
        # Crafted table bytes pass the tpoll chain to the desc[5]
        # latch: the domain 0x20 cell is written. The merge clears
        # the tested m-cell bit, so m carries a second bit that
        # survives into the polls (f7b6 keeps owned b6 == 7 for the
        # bit test; f2/f8 select the surviving bits).
        m_init, d3_init = (1 << 7) | (1 << 5), 1 << 3
        neigh = ((0, 0), (0, 0))
        fixed = ((3, 5), (4, 7), (4, 9))
        ram, _ = config_ram('direct', 7, 3, 0x5a, 7, neigh, fixed,
                            m_init, d3_init)
        want = oracle(7, 0, 0, ram)
        self.assertNotEqual(want['outcome'], 'leftover-dependent')
        self.assertIn((0xa0010000 | 0x20),
                      {e[1] for e in want['trace'] if e[0] == 'write'})

    def test_pass_shift(self):
        self.assertEqual(pass_shift(0), 0)
        self.assertEqual(pass_shift(1 << 7), 8)
        self.assertEqual(pass_shift(1 << 31), 0)

    def test_battery_covers_edges(self):
        cases = battery_cases()
        self.assertGreaterEqual(len(cases), 200)
        modes = {c[0] for c in cases}
        self.assertEqual(modes, {'direct', 'entry0', 'scan'})
        idents = {c[1] for c in cases}
        self.assertTrue({7, 8} <= idents)
        self.assertTrue({16, 19, 22} <= idents)
        self.assertTrue({23, 25} <= idents)
        arg1s = {c[3] for c in cases}
        self.assertTrue({0, 1, 2, 3, 12} <= arg1s)
        # Every admitted case stops (no leftover path sneaks in).
        for case in cases:
            (mode, ident, arg2, arg1, b4, b5, b6, neigh, fixed,
             m_init, d3_init) = case
            ram, _ = config_ram(mode, ident, b4, b5, b6, neigh, fixed,
                                m_init, d3_init)
            self.assertNotEqual(oracle(ident, arg1, arg2, ram)['outcome'],
                                'leftover-dependent', case)


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
            raila_obj = directory / 'raila_s.o'
            subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *RAILA_FLAGS,
                            '-c', str(S_SOURCE), '-o', str(raila_obj)], check=True)
            fill_obj = directory / 'fill_c.o'
            subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *PMUFILL_FLAGS,
                            '-c', str(FILL_SOURCE), '-o', str(fill_obj)], check=True)
            script = directory / 'raila.ld'
            script.write_text(LINKER_SCRIPT)
            linked = directory / 'raila.elf'
            subprocess.run([str(prefix / 'csky-unknown-elf-ld'), '-T', str(script),
                            str(raila_obj), str(fill_obj), '-o', str(linked)],
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
