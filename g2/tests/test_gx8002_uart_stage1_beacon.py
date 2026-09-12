"""Host contract and regression tests for the UART stage-1 beacon leaves.

The full decoded stock/source differential lives in
tools/verify_gx8002_uart_stage1_beacon.py (run by the candidate builder);
these tests pin the prefix model, the executor semantics, and the
placement/envelope regression on macOS.

Native host execution of the assembly leaves past the chaining branch
is infeasible here: both leaves chain into the PMU dispatcher cascade
or the reviewed beacon, whose bodies live at stage-1 addresses. The
interpreter tests below execute snippets plus the real linked sections
up to the chaining branch, which is the shipped code shape.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from verify_gx8002_uart_stage1_beacon import (
    BEACON_FLAGS, S_SOURCE, NOTICE, SPECS, LINKER_SCRIPT, CHAINS,
    ENTRY_BEACON, ENTRY_BRINGUP, D98, EA0, DIV, MOD, SP0,
    BASE_CELL, FLAG_CELL, UART_A, UART_B,
    MASK, Model, ChainedOff, execute, oracle, battery_cases,
    config_beacon_ram, config_bringup_ram, seed)
from verify_gx8002_analog_source import sha
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA
from build_transparent_image import Elf32

BASELINE = ROOT / 'docs/research/gx8002-uart-stage1-beacon-verification.json'


def run_until_chain(testcase, code, entry, args, ram, poll=(), start=None):
    model = Model(dict(ram), poll)
    with testcase.assertRaises(ChainedOff) as caught:
        execute(code, start if start is not None else entry,
                args, model, entry)
    return caught.exception


SNIPPET_START = 0x1000


def run_snippet(testcase, code, entry, args, ram):
    return run_until_chain(testcase, code, entry, args, ram,
                           start=SNIPPET_START)


class PrefixModel(unittest.TestCase):
    def test_beacon_chain_state_poll_path(self):
        ram = config_beacon_ram(UART_B, 0x33333333)
        script = [0x00000001, 0x00000000]
        want = oracle(ENTRY_BEACON, 0xaaaa0000, 0x00000001, 0xcccc0004,
                      0xdddd0005, 0xeeee0006, 0xffff0007, ram,
                      poll_script=script)
        self.assertEqual((want['outcome'], want['target']), ('chain', EA0))
        regs = want['regs']
        self.assertEqual(regs['r0'], 18)
        self.assertEqual(regs['r1'], UART_B + 12)
        self.assertEqual(regs['r2'], UART_B + 124)
        self.assertEqual(regs['r3'], UART_A)
        self.assertEqual(regs['r4'], 0xcccc0004)
        self.assertEqual(regs['r6'], 0xeeee0006)
        self.assertEqual(regs['r12'], UART_B)
        self.assertEqual(regs['r14'], SP0)
        self.assertEqual(regs['r15'], 0x10000516)
        trace = want['trace']
        self.assertEqual(trace[0], ('write', SP0 - 4, 4, 0xcccc0004))
        self.assertIn(('read', BASE_CELL, 4, UART_B), trace)
        self.assertIn(('write', UART_B + 0x4, 4, 0), trace)
        self.assertIn(('write', UART_B + 0x10, 4, 3), trace)
        self.assertIn(('read', UART_B + 124, 4, 1), trace)
        self.assertIn(('read', UART_B + 124, 4, 0), trace)
        self.assertIn(('write', UART_B + 12, 4, 3), trace)
        self.assertIn(('write', UART_B + 8, 4, 79), trace)

    def test_beacon_chain_state_skip_path_first_uart(self):
        ram = config_beacon_ram(UART_A, 0x00000000)
        want = oracle(ENTRY_BEACON, 0x11111111, 0x00000000, 0x22222222,
                      0x33333333, 0x44444444, 0x55555555, ram,
                      poll_script=[0])
        regs = want['regs']
        self.assertEqual(want['target'], EA0)
        # r1 == 0 skips the poll block and the pop: the frame stays.
        self.assertEqual(regs['r0'], 17)
        self.assertEqual(regs['r1'], 0)
        self.assertEqual(regs['r2'], seed('r2'))
        self.assertEqual(regs['r4'], 0x11111111)
        self.assertEqual(regs['r14'], SP0 - 20)
        self.assertEqual(regs['r15'], 0x1000057a)
        # No poll traffic and no block writes past the two setup stores.
        addrs = [(kind, address) for kind, address, _, _ in want['trace']]
        self.assertNotIn(('read', UART_A + 124), addrs)
        self.assertNotIn(('write', UART_A + 12), addrs)
        self.assertNotIn(('write', UART_A + 8), addrs)

    def test_bringup_flag_set_chains_to_beacon(self):
        ram = config_bringup_ram(0x00000001, 0x00000002)
        want = oracle(ENTRY_BRINGUP, 0xaaaa0000, 0xbbbb0000, 0xcccc0004,
                      0xdddd0005, 0xeeee0006, 0xffff0007, ram)
        self.assertEqual((want['outcome'], want['target']),
                         ('chain', ENTRY_BEACON))
        regs = want['regs']
        self.assertEqual(regs['r0'], 115200)
        self.assertEqual(regs['r1'], 0)
        self.assertEqual(regs['r2'], 1)
        self.assertEqual(regs['r3'], FLAG_CELL)
        self.assertEqual(regs['r4'], 0xbbbb0000)
        self.assertEqual(regs['r5'], 0xaaaa0000)
        self.assertEqual(regs['r14'], SP0 - 12)
        self.assertEqual(regs['r15'], 0x10000614)

    def test_bringup_flag_clear_selects_base(self):
        for select, base in ((0, UART_A), (1, UART_B), (2, UART_A),
                             (0xffffffff, UART_A)):
            ram = config_bringup_ram(0, select)
            want = oracle(ENTRY_BRINGUP, 0, 0, 0, 0, 0, 0, ram)
            self.assertEqual(want['target'], D98, hex(select))
            self.assertEqual(want['regs']['r0'], 16)
            self.assertEqual(want['regs']['r1'], 1)
            self.assertEqual(want['regs']['r3'], base, hex(select))
            self.assertEqual(want['regs']['r15'], 0x100005ee)
            self.assertIn(('write', BASE_CELL, 4, base), want['trace'])

    def test_oracle_rejects_unmapped_cell(self):
        with self.assertRaises(ValueError):
            oracle(ENTRY_BEACON, 0, 1, 0, 0, 0, 0, {}, poll_script=[0])

    def test_oracle_rejects_unknown_entry(self):
        with self.assertRaises(ValueError):
            oracle(0x10000999, 0, 0, 0, 0, 0, 0, {})


class ExecutorSemantics(unittest.TestCase):
    def test_push_spills_in_operand_order(self):
        code = {0x1000: ('push', 'r4-r7, r15', 2),
                0x1002: ('bsr', hex(EA0), 4)}
        done = run_snippet(self, code, ENTRY_BEACON,
                         (1, 2, 0x41, 0x42, 0x43, 0x44),
                         {SP0 - 4 * i: 0 for i in range(1, 7)})
        self.assertEqual(done.target, EA0)
        # The pushed r15 is the entry seed; the chaining branch then
        # overwrites the live r15 with the return address.
        self.assertEqual([done.model.ram[SP0 - 4 * i] for i in range(1, 6)],
                         [0x41, 0x42, 0x43, 0x44, seed('r15')])
        self.assertEqual(done.registers['r15'], 0x1006)

    def test_inct_follows_condition(self):
        # Taken path: r3 seed != 1, so r3 becomes r2 + 0.
        taken_code = {0x1000: ('cmpnei', 'r3, 1', 4),
                      0x1004: ('inct', 'r3, r2, 0', 4),
                      0x1008: ('bsr', hex(D98), 4)}
        done = run_snippet(self, dict(taken_code), ENTRY_BRINGUP,
                         (0, 0, 0, 0, 0, 0), {SP0 - 4: 0})
        self.assertEqual(done.registers['r3'],
                         (0x98760000 + 2 * 0x111111) & MASK)
        # Not-taken path: r3 == 1 keeps its value.
        skipped_code = {0x1000: ('movi', 'r3, 1', 2),
                        0x1002: ('cmpnei', 'r3, 1', 4),
                        0x1006: ('inct', 'r3, r2, 0', 4),
                        0x100a: ('bsr', hex(D98), 4)}
        done = run_snippet(self, dict(skipped_code), ENTRY_BRINGUP,
                         (0, 0, 0, 0, 0, 0), {SP0 - 4: 0})
        self.assertEqual(done.registers['r3'], 1)

    def test_bseti_sets_bit(self):
        code = {0x1000: ('movi', 'r0, 49664', 4),
                0x1004: ('bseti', 'r0, 16', 2),
                0x1006: ('bsr', hex(ENTRY_BEACON), 4)}
        done = run_snippet(self, code, ENTRY_BRINGUP,
                         (0, 0, 0, 0, 0, 0), {SP0 - 4: 0})
        self.assertEqual(done.registers['r0'], 115200)

    def test_foreign_call_rejected(self):
        code = {0x1000: ('bsr', hex(DIV), 4)}
        with self.assertRaises(ValueError):
            run_snippet(self, code, ENTRY_BRINGUP, (0,) * 6, {})

    def test_unmapped_access_traps(self):
        code = {0x1000: ('ld.w', 'r3, (r6, 0x0)', 4)}
        with self.assertRaises(ValueError):
            run_snippet(self, code, ENTRY_BEACON, (0,) * 6, {})

    def test_post_call_ops_refused(self):
        # mult/zext live only past the chain; the executor (like the
        # battery) never steps there.
        code = {0x1000: ('mult', 'r0, r7', 2)}
        with self.assertRaises(ValueError):
            run_snippet(self, code, ENTRY_BEACON, (0,) * 6, {})


class BatteryCoverage(unittest.TestCase):
    def test_battery_scale_and_entry_coverage(self):
        cases = battery_cases()
        kinds = [case[0] for case in cases]
        self.assertEqual(len(cases), 148)
        self.assertEqual(kinds.count('beacon'), 100)
        self.assertEqual(kinds.count('bringup'), 48)
        beacon_r1 = {case[1][1] for case in cases if case[0] == 'beacon'}
        self.assertIn(0, beacon_r1)
        self.assertTrue(any(v != 0 for v in beacon_r1))
        beacon_bases = {case[2] for case in cases if case[0] == 'beacon'}
        self.assertEqual(beacon_bases, {UART_A, UART_B})
        bringup_flags = {case[2] for case in cases if case[0] == 'bringup'}
        self.assertIn(0, bringup_flags)
        self.assertTrue(any(v != 0 for v in bringup_flags))
        bringup_selects = {case[3] for case in cases if case[0] == 'bringup'}
        self.assertIn(1, bringup_selects)
        self.assertTrue(any(v != 1 for v in bringup_selects))

    def test_baseline_report_matches(self):
        report = json.loads(BASELINE.read_text())
        self.assertEqual(report['target_cases'], 148)
        self.assertTrue(report['source_admitted'])
        self.assertEqual([f['symbol'] for f in report['functions']],
                         ['open_cfw_gx8002_uart_stage1_beacon',
                          'open_cfw_gx8002_uart_stage1_bringup'])


class PlacementRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = Path(tempfile.mkdtemp(prefix='beacon-placement-'))
        prefix = ROOT / 'build/csky-macos/install/bin'
        obj = cls.directory / 'beacon_s.o'
        subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *BEACON_FLAGS,
                        '-c', str(S_SOURCE), '-o', str(obj)], check=True)
        script = cls.directory / 'beacon.ld'
        script.write_text(LINKER_SCRIPT)
        cls.elf_path = cls.directory / 'beacon.elf'
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
