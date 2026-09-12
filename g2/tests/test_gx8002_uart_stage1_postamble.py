"""Host contract and regression tests for the UART stage-1 postamble leaf.

The full decoded stock/source differential lives in
tools/verify_gx8002_uart_stage1_postamble.py (run by the candidate builder);
these tests pin the interpreter semantics, the oracle/prefix model, and
the placement/envelope regression on macOS.

Native host execution of the assembly leaf is infeasible here: the
body dereferences the 0x20002274 pointer cell and linked dispatcher
addresses, which truncate on the 64-bit host (the same truncation
test_gx8002_uart_stage1_pmudisp documents for desc[0]). The
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
from verify_gx8002_uart_stage1_postamble import (
    POST_FLAGS, PMUDISP_FLAGS, PMUFILL_FLAGS, S_SOURCE, DISP_SOURCE,
    FILL_SOURCE, SPECS, LINKER_SCRIPT, ENTRY, DISP, HANDOFF, PKG, SIZE,
    PTR, BASES, POLL_OFF, PUB_OFF, CTRL_OFF, SP0_POST,
    JT1, JT2, JT1_IDS, JT2_IDS, JT1_EXPECT, JT2_EXPECT,
    Model, execute, oracle, oracle_prefix, battery_cases, config_case,
    check_shape, check_tables, seed, signed, HandedOff,
    SP0, DESC, MASK)
from verify_gx8002_analog_source import sha
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA

BASELINE = ROOT / 'docs/research/gx8002-uart-stage1-postamble-verification.json'


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
    def test_push_single_r15(self):
        # The leaf pushes only the return address (no frame).
        code, start, term = tiny([('push', 'r15'),
                                  ('pop', 'r15')])
        ram = {SP0_POST - 4: 0}
        regs, trace = run(code, start, term, (0, 0, 0), dict(ram))
        self.assertEqual(regs['r14'], SP0_POST)
        self.assertEqual(regs['r15'], seed('r15'))
        self.assertEqual(trace[0], ('write', SP0_POST - 4, 4, seed('r15')))

    def test_poll_gate_shape(self):
        # bez on the masked poll bit loops; a set bit falls through.
        code, start, term = tiny([('andi', 'r3, r3, 1'),
                                  ('bez', 'r3, 0x1000')])
        regs, _ = run(code, start, term, (0, 0, 0), {})
        self.assertEqual(regs['r3'], seed('r3') & 1)
        spinning, spin_start, spin_term = tiny(
            [('movi', 'r3, 0'),
             ('bez', 'r3, 0x1000')])
        with self.assertRaises(ValueError):
            run(spinning, spin_start, spin_term, (0, 0, 0), {})

    def test_control_bit_ops(self):
        code, start, term = tiny([('ori', 'r3, r3, 257'),
                                  ('bclri', 'r3, 0'),
                                  ('bclri', 'r3, 8')])
        regs, _ = run(code, start, term, (0, 0, 0), {})
        want = (seed('r3') | 0x101) & ~(1 << 0) & ~(1 << 8) & MASK
        self.assertEqual(regs['r3'], want)

    def test_bsr_admits_fill_and_dispatch(self):
        # No DISP body is mapped here: the call itself is admitted and
        # the failure is the unmapped target, not the call.
        code, start, term = tiny([('bsr', hex(DISP))])
        model = Model({})
        with self.assertRaises(ValueError) as ctx:
            execute(code, start, (0, 0, 0), model, handoff=term)
        self.assertIn('unexpected pc', str(ctx.exception))

    def test_bsr_rejects_foreign_calls(self):
        code, start, term = tiny([('bsr', '0x10000ea0')])
        model = Model({})
        with self.assertRaises(ValueError):
            execute(code, start, (0, 0, 0), model, handoff=term)

    def test_bkpt_traps(self):
        code, start, term = tiny([('bkpt', '')])
        model = Model({})
        with self.assertRaises(ValueError):
            execute(code, start, (0, 0, 0), model, handoff=term)


class OraclePrefix(unittest.TestCase):
    def setUp(self):
        if not IMAGE.exists():
            raise unittest.SkipTest('authenticated codec oracle unavailable')
        stock = IMAGE.read_bytes()
        if sha(stock) != IMAGE_SHA:
            raise unittest.SkipTest('stock identity changed')

    def test_entry_regs_are_not_inputs(self):
        # r0/r1 are overwritten before any use: garbage in gives
        # identical traces and registers.
        built = config_case((0, 0), 0x600d600d, 0, 5, 3, 0xa5a5a500, 0,
                            BASES[0], 0, 1)
        self.assertIsNotNone(built)
        ram, table_words = built
        first = oracle((0, 0, 0x600d600d), dict(ram), dict(table_words))
        second = oracle((0xdeadbeef, 0xdeadbeef, 0x600d600d), dict(ram),
                        dict(table_words))
        self.assertEqual(first['trace'], second['trace'])
        self.assertEqual(first['regs'], second['regs'])
        self.assertEqual(first['ram'], second['ram'])

    def test_prefix_models_push_and_cells(self):
        ram = {SP0_POST - 4: 0, PTR: BASES[0],
               BASES[0] + CTRL_OFF: 0, BASES[0] + POLL_OFF: 1,
               BASES[0] + PUB_OFF: 0x5a5a5a5a}
        regs, trace, _, base = oracle_prefix((9, 9, 7), dict(ram))
        self.assertEqual(base, BASES[0])
        self.assertEqual(regs['r0'], 25)
        self.assertEqual(regs['r1'], 0)
        self.assertEqual(regs['r6'], 7)
        kinds = [kind for kind, _, _, _ in trace]
        self.assertEqual(kinds,
                         ['write', 'read', 'read', 'write', 'read', 'read',
                          'write', 'write'])

    def test_multi_pass_poll_excluded(self):
        ram = {SP0_POST - 4: 0, PTR: BASES[0],
               BASES[0] + CTRL_OFF: 0, BASES[0] + POLL_OFF: 0,
               BASES[0] + PUB_OFF: 0}
        with self.assertRaises(ValueError):
            oracle_prefix((0, 0, 0), dict(ram))

    def test_dump_matches_pinned_maps(self):
        stock = IMAGE.read_bytes()
        jt1, jt2 = check_tables(stock)
        self.assertEqual(len(jt1), len(JT1_IDS))
        self.assertEqual(len(jt2), len(JT2_IDS))

    def test_id25_passes_both_tables_through(self):
        # Id 25 is out of both table ranges, so corrupted retained
        # tables change nothing for this leaf; the tables are pinned
        # by check_tables above and exercised by the pmudispatch
        # battery, not here.
        built = config_case((0, 0), 0x600d600d, 0, 5, 3, 0xa5a5a500, 0,
                            BASES[0], 0, 1)
        self.assertIsNotNone(built)
        ram, table_words = built
        clean = oracle((0, 0, 0x600d600d), dict(ram), dict(table_words))
        ram[JT1] = 0xdeadbeef
        ram[JT2] = 0xdeadbeef
        dirty = oracle((0, 0, 0x600d600d), dict(ram), dict(table_words))
        self.assertEqual(clean['trace'], dirty['trace'])
        self.assertEqual(clean['regs'], dirty['regs'])

    def test_battery_scale(self):
        cases = battery_cases()
        self.assertGreaterEqual(len(cases), 200)
        self.assertTrue({case[7] for case in cases} >= set(BASES))
        self.assertTrue({case[8] for case in cases} >= {0x0, 0x101})


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
            post_obj = directory / 'postamble_s.o'
            subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *POST_FLAGS,
                            '-c', str(S_SOURCE), '-o', str(post_obj)], check=True)
            disp_obj = directory / 'pmudispatch_s.o'
            subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *PMUDISP_FLAGS,
                            '-c', str(DISP_SOURCE), '-o', str(disp_obj)], check=True)
            fill_obj = directory / 'fill_c.o'
            subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *PMUFILL_FLAGS,
                            '-c', str(FILL_SOURCE), '-o', str(fill_obj)], check=True)
            script = directory / 'postamble.ld'
            script.write_text(LINKER_SCRIPT)
            linked = directory / 'postamble.elf'
            subprocess.run([str(prefix / 'csky-unknown-elf-ld'), '-T', str(script),
                            str(post_obj), str(disp_obj), str(fill_obj),
                            '-o', str(linked)], check=True)
            elf = Elf32(linked.read_bytes(), str(linked))
            self.assertFalse(any(s['name'] and s['section'] == 0 for s in elf.symbols()))
            for symbol, _, offset, size, _, _ in SPECS:
                section = next(s for s in elf.sections if s['name'] == '.text.' + symbol)
                payload = elf.contents(section)
                self.assertEqual(len(payload), size, symbol)
                self.assertEqual(offset % section['align'], 0, symbol)
                self.assertEqual(elf.relocations(section['index']), [], symbol)
                self.assertEqual(sha(payload),
                                 sha(self.stock[offset:offset + size]), symbol)


if __name__ == '__main__':
    unittest.main()
