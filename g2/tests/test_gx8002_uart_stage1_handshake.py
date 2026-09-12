"""Host contract and regression tests for the UART stage-1 handshake leaf.

The full decoded stock/source differential lives in
tools/verify_gx8002_uart_stage1_handshake.py (run by the candidate builder);
these tests pin the prefix model, the executor semantics, and the
placement/envelope regression on macOS.

Native host execution of the assembly leaf past the chaining branch
is infeasible here: the leaf chains into the reviewed rail-configure
tail (which runs straight into the reviewed PMU dispatchers), whose
bodies live at stage-1 addresses. The interpreter tests below
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
from verify_gx8002_uart_stage1_handshake import (
    HANDSHAKE_FLAGS, S_SOURCE, NOTICE, SPECS, LINKER_SCRIPT, CHAINS,
    ENTRY, RAILCFG, GET0, SP0, POOLS, POOL_START,
    MASK, Model, ChainedOff, execute, oracle, battery_cases,
    config_ram, seed)
from verify_gx8002_analog_source import sha
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA
from build_transparent_image import Elf32

BASELINE = ROOT / 'docs/research/gx8002-uart-stage1-handshake-verification.json'


def run_until_chain(testcase, code, entry, args, ram, start=None, entry_sp=SP0):
    model = Model(dict(ram))
    with testcase.assertRaises(ChainedOff) as caught:
        execute(code, start if start is not None else entry,
                args, model, entry, entry_sp)
    return caught.exception


SNIPPET_START = 0x1000


def run_snippet(testcase, code, entry, args, ram):
    return run_until_chain(testcase, code, entry, args, ram,
                           start=SNIPPET_START)


ARGS0 = (0xaaaa0000, 0xbbbb0001, 0xcccc0004, 0xdddd0005,
         0xeeee0006, 0xffff0007, 0x11110008, 0x22220009)


class PrefixModel(unittest.TestCase):
    def test_chain_state_preserves_entry_regs(self):
        ram = config_ram(SP0)
        want = oracle(ENTRY, ARGS0, ram)
        self.assertEqual((want['outcome'], want['target']),
                         ('chain', RAILCFG))
        regs = want['regs']
        self.assertEqual(regs['r0'], 0xaaaa0000)
        self.assertEqual(regs['r1'], 0xbbbb0001)
        self.assertEqual(regs['r4'], 0xcccc0004)
        self.assertEqual(regs['r9'], 0x22220009)
        self.assertEqual(regs['r12'], seed('r12'))
        self.assertEqual(regs['r14'], SP0 - 28)
        self.assertEqual(regs['r15'], 0x100006de)
        trace = want['trace']
        self.assertEqual(len(trace), 7)
        self.assertEqual(trace[0], ('write', SP0 - 4, 4, 0xcccc0004))
        self.assertEqual(trace[-1], ('write', SP0 - 28, 4, seed('r15')))

    def test_chain_state_shifted_stack(self):
        entry_sp = SP0 - 64
        ram = config_ram(entry_sp)
        want = oracle(ENTRY, ARGS0, ram, entry_sp)
        self.assertEqual(want['target'], RAILCFG)
        self.assertEqual(want['regs']['r14'], entry_sp - 28)
        self.assertEqual(want['trace'][0],
                         ('write', entry_sp - 4, 4, 0xcccc0004))

    def test_oracle_rejects_unmapped_cell(self):
        with self.assertRaises(ValueError):
            oracle(ENTRY, ARGS0, {}, SP0)

    def test_oracle_rejects_unknown_entry(self):
        with self.assertRaises(ValueError):
            oracle(0x10000999, ARGS0, config_ram(SP0), SP0)


class ExecutorSemantics(unittest.TestCase):
    def test_push_spills_in_operand_order(self):
        code = {0x1000: ('push', 'r4-r9, r15', 2),
                0x1002: ('bsr', hex(RAILCFG), 4)}
        done = run_snippet(self, code, ENTRY, ARGS0,
                           {SP0 - 4 * i: 0 for i in range(1, 9)})
        self.assertEqual(done.target, RAILCFG)
        self.assertEqual([done.model.ram[SP0 - 4], done.model.ram[SP0 - 28]],
                         [0xcccc0004, seed('r15')])
        self.assertEqual(done.registers['r15'], 0x1006)
        self.assertEqual(done.registers['r14'], SP0 - 28)

    def test_foreign_call_rejected(self):
        code = {0x1000: ('bsr', hex(GET0), 4)}
        with self.assertRaises(ValueError):
            run_snippet(self, code, ENTRY, ARGS0, {})

    def test_unmapped_access_traps(self):
        code = {0x1000: ('push', 'r4-r9, r15', 2)}
        with self.assertRaises(ValueError):
            run_snippet(self, code, ENTRY, ARGS0, {})

    def test_post_call_ops_refused(self):
        # cmpnei lives only past the chain; the executor (like the
        # battery) never steps there.
        code = {0x1000: ('cmpnei', 'r0, 1', 2)}
        with self.assertRaises(ValueError):
            run_snippet(self, code, ENTRY, ARGS0, {})


class BatteryCoverage(unittest.TestCase):
    def test_battery_scale_and_entry_coverage(self):
        cases = battery_cases()
        kinds = [case[0] for case in cases]
        self.assertEqual(len(cases), 15)
        self.assertEqual(set(kinds), {'handshake'})
        sps = {case[2] for case in cases}
        self.assertEqual(sps, {SP0, SP0 - 32, SP0 - 64})

    def test_baseline_report_matches(self):
        report = json.loads(BASELINE.read_text())
        self.assertEqual(report['target_cases'], 15)
        self.assertTrue(report['source_admitted'])
        self.assertEqual([f['symbol'] for f in report['functions']],
                         ['open_cfw_gx8002_uart_stage1_handshake'])


class PlacementRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = Path(tempfile.mkdtemp(prefix='handshake-placement-'))
        prefix = ROOT / 'build/csky-macos/install/bin'
        obj = cls.directory / 'handshake_s.o'
        subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *HANDSHAKE_FLAGS,
                        '-c', str(S_SOURCE), '-o', str(obj)], check=True)
        script = cls.directory / 'handshake.ld'
        script.write_text(LINKER_SCRIPT)
        cls.elf_path = cls.directory / 'handshake.elf'
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

    def test_pool_words_match_stock(self):
        for symbol, entry, offset, size, _, _ in SPECS:
            section = next(s for s in self.elf.sections
                           if s['name'] == '.text.' + symbol)
            payload = self.elf.contents(section)
            words = tuple(int.from_bytes(payload[POOL_START - entry + 4 * i:
                                                 POOL_START - entry + 4 * i + 4],
                                         'little') for i in range(3))
            self.assertEqual(words, POOLS)


if __name__ == '__main__':
    unittest.main()
