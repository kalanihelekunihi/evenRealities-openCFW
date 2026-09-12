"""Host contract and regression tests for the UART stage-1 announce leaf.

The full decoded stock/source differential lives in
tools/verify_gx8002_uart_stage1_announce.py (run by the candidate builder);
these tests pin the prefix model, the executor semantics, and the
placement/envelope regression on macOS.

Native host execution of the assembly leaf past the chaining branch
is infeasible here: the leaf chains into the retained rail-program
entry (which runs straight into the reviewed first PMU dispatcher),
whose body lives at stage-1 addresses. The interpreter tests below
execute snippets plus the real linked section up to the chaining
branch, which is the shipped code shape.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from verify_gx8002_uart_stage1_announce import (
    ANNOUNCE_FLAGS, S_SOURCE, NOTICE, SPECS, LINKER_SCRIPT, CHAINS,
    ENTRY, RAIL_PROG, POSTAMBLE, SP0,
    BASE_CELL, UART_A, UART_B,
    MASK, Model, ChainedOff, execute, oracle, battery_cases,
    config_ram, seed)
from verify_gx8002_analog_source import sha
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA
from build_transparent_image import Elf32

BASELINE = ROOT / 'docs/research/gx8002-uart-stage1-announce-verification.json'


def run_until_chain(testcase, code, entry, args, ram, start=None):
    model = Model(dict(ram))
    with testcase.assertRaises(ChainedOff) as caught:
        execute(code, start if start is not None else entry,
                args, model, entry)
    return caught.exception


SNIPPET_START = 0x1000


def run_snippet(testcase, code, entry, args, ram):
    return run_until_chain(testcase, code, entry, args, ram,
                           start=SNIPPET_START)


class PrefixModel(unittest.TestCase):
    def test_chain_state_first_uart_selects_six(self):
        ram = config_ram(UART_A, 0x00000000)
        want = oracle(ENTRY, 0xaaaa0000, 0xbbbb0001, 0xcccc0004,
                      0xdddd0005, ram)
        self.assertEqual((want['outcome'], want['target']),
                         ('chain', RAIL_PROG))
        regs = want['regs']
        self.assertEqual(regs['r0'], 0xaaaa0000)
        self.assertEqual(regs['r1'], UART_A)
        self.assertEqual(regs['r2'], 0xbbbb0001)
        self.assertEqual(regs['r3'], 6)
        self.assertEqual(regs['r4'], BASE_CELL)
        self.assertEqual(regs['r12'], UART_A)
        self.assertEqual(regs['r14'], SP0 - 8)
        self.assertEqual(regs['r15'], 0x10000680)
        trace = want['trace']
        self.assertEqual(trace[0], ('write', SP0 - 4, 4, 0xcccc0004))
        self.assertIn(('read', BASE_CELL, 4, UART_A), trace)
        self.assertIn(('write', UART_A + 0xa8, 4, 1), trace)

    def test_chain_state_second_uart_selects_four(self):
        ram = config_ram(UART_B, 0xffffffff)
        want = oracle(ENTRY, 0x11111111, 0x22222222, 0x33333333,
                      0x44444444, ram)
        self.assertEqual((want['outcome'], want['target']),
                         ('chain', RAIL_PROG))
        regs = want['regs']
        self.assertEqual(regs['r1'], UART_B)
        self.assertEqual(regs['r2'], 0x22222222)
        self.assertEqual(regs['r3'], 4)
        self.assertEqual(regs['r12'], UART_B)
        self.assertEqual(regs['r15'], 0x10000680)
        self.assertIn(('write', UART_B + 0xa8, 4, 1), want['trace'])

    def test_select_covers_both_arms_over_inits(self):
        for base, select in ((UART_A, 6), (UART_B, 4)):
            for init in (0x00000000, 0x00000001, 0xffffffff):
                ram = config_ram(base, init)
                want = oracle(ENTRY, 0, 0, 0, 0, ram)
                self.assertEqual(want['target'], RAIL_PROG, hex(base))
                self.assertEqual(want['regs']['r3'], select, hex(base))

    def test_oracle_rejects_unmapped_cell(self):
        with self.assertRaises(ValueError):
            oracle(ENTRY, 0, 0, 0, 0, {})

    def test_oracle_rejects_unknown_entry(self):
        with self.assertRaises(ValueError):
            oracle(0x10000999, 0, 0, 0, 0, {})


class ExecutorSemantics(unittest.TestCase):
    def test_push_spills_in_operand_order(self):
        code = {0x1000: ('push', 'r4, r15', 2),
                0x1002: ('bsr', hex(RAIL_PROG), 4)}
        done = run_snippet(self, code, ENTRY,
                           (1, 2, 0x41, 0x42),
                           {SP0 - 4: 0, SP0 - 8: 0})
        self.assertEqual(done.target, RAIL_PROG)
        self.assertEqual([done.model.ram[SP0 - 4], done.model.ram[SP0 - 8]],
                         [0x41, seed('r15')])
        self.assertEqual(done.registers['r15'], 0x1006)

    def test_inct_follows_condition(self):
        # Taken path: base seed != UART_A, so r3 becomes r2 + 0.
        taken_code = {0x1000: ('movi', 'r2, 4', 2),
                      0x1002: ('movi', 'r3, 6', 2),
                      0x1004: ('cmpne', 'r12, r3', 2),
                      0x1006: ('inct', 'r3, r2, 0', 4),
                      0x100a: ('bsr', hex(RAIL_PROG), 4)}
        done = run_snippet(self, dict(taken_code), ENTRY,
                           (0, 0, 0, 0),
                           {SP0 - 4: 0, SP0 - 8: 0})
        self.assertEqual(done.registers['r3'], 4)
        # Not-taken path: r12 == r3 keeps the preselected 6.
        skipped_code = {0x1000: ('movi', 'r2, 4', 2),
                        0x1002: ('movi', 'r3, 6', 2),
                        0x1004: ('mov', 'r12, r3', 2),
                        0x1006: ('cmpne', 'r12, r3', 2),
                        0x1008: ('inct', 'r3, r2, 0', 4),
                        0x100c: ('bsr', hex(RAIL_PROG), 4)}
        done = run_snippet(self, dict(skipped_code), ENTRY,
                           (0, 0, 0, 0),
                           {SP0 - 4: 0, SP0 - 8: 0})
        self.assertEqual(done.registers['r3'], 6)

    def test_movih_builds_uart_base(self):
        code = {0x1000: ('movih', 'r3, 40976', 4),
                0x1004: ('bsr', hex(RAIL_PROG), 4)}
        done = run_snippet(self, code, ENTRY, (0, 0, 0, 0),
                           {SP0 - 4: 0, SP0 - 8: 0})
        self.assertEqual(done.registers['r3'], UART_A)

    def test_foreign_call_rejected(self):
        code = {0x1000: ('bsr', hex(POSTAMBLE), 4)}
        with self.assertRaises(ValueError):
            run_snippet(self, code, ENTRY, (0,) * 4, {})

    def test_unmapped_access_traps(self):
        code = {0x1000: ('ld.w', 'r12, (r4, 0x0)', 4)}
        with self.assertRaises(ValueError):
            run_snippet(self, code, ENTRY, (0,) * 4, {})

    def test_post_call_ops_refused(self):
        # andi/bez live only past the chain; the executor (like the
        # battery) never steps there.
        code = {0x1000: ('andi', 'r2, r2, 64', 4)}
        with self.assertRaises(ValueError):
            run_snippet(self, code, ENTRY, (0,) * 4, {})


class BatteryCoverage(unittest.TestCase):
    def test_battery_scale_and_entry_coverage(self):
        cases = battery_cases()
        kinds = [case[0] for case in cases]
        self.assertEqual(len(cases), 30)
        self.assertEqual(set(kinds), {'announce'})
        bases = {case[2] for case in cases}
        self.assertEqual(bases, {UART_A, UART_B})
        inits = {case[3] for case in cases}
        self.assertEqual(inits, {0x00000000, 0x00000001, 0xffffffff})

    def test_baseline_report_matches(self):
        report = json.loads(BASELINE.read_text())
        self.assertEqual(report['target_cases'], 30)
        self.assertTrue(report['source_admitted'])
        self.assertEqual([f['symbol'] for f in report['functions']],
                         ['open_cfw_gx8002_uart_stage1_announce'])


class PlacementRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = Path(tempfile.mkdtemp(prefix='announce-placement-'))
        prefix = ROOT / 'build/csky-macos/install/bin'
        obj = cls.directory / 'announce_s.o'
        subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *ANNOUNCE_FLAGS,
                        '-c', str(S_SOURCE), '-o', str(obj)], check=True)
        script = cls.directory / 'announce.ld'
        script.write_text(LINKER_SCRIPT)
        cls.elf_path = cls.directory / 'announce.elf'
        subprocess.run([str(prefix / 'csky-unknown-elf-ld'), '-T', str(script),
                        str(obj), '-o', str(cls.elf_path)], check=True)
        cls.elf = Elf32(cls.elf_path.read_bytes(), str(cls.elf_path))
        cls.stock = IMAGE.read_bytes()
        assert sha(cls.stock) == IMAGE_SHA

    def test_stock_envelope_unchanged(self):
        report = json.loads(BASELINE.read_text())
        for _, entry, offset, size, _, _ in SPECS:
            self.assertEqual(sha(self.stock[offset:offset + size]),
                             report['stock_envelope_shas'][hex(entry)])

    def test_linked_sections_fill_placements_byte_identical(self):
        for symbol, _, offset, size, _, _ in SPECS:
            section = next(s for s in self.elf.sections
                           if s['name'] == '.text.' + symbol)
            payload = self.elf.contents(section)
            self.assertEqual(len(payload), size)
            self.assertEqual(payload, self.stock[offset:offset + size])
            self.assertFalse(self.elf.relocations(section['index']))
            self.assertEqual(offset % section['align'], 0)


if __name__ == '__main__':
    unittest.main()
