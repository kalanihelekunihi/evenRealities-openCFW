"""Host contract and regression tests for the UART stage-1 traptails leaves.

The full decoded stock/source differential lives in
tools/verify_gx8002_uart_stage1_traptails.py (run by the candidate builder);
these tests pin the prefix model, the executor semantics, and the
placement/envelope regression on macOS.

Native host execution of the assembly leaves past the chaining branch
is infeasible here: both leaves chain into the retained PMU dispatcher
cascade, whose bodies live at retained stage-1 addresses. The
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
from verify_gx8002_uart_stage1_traptails import (
    TRAPTAILS_FLAGS, S_SOURCE, NOTICE, SPECS, LINKER_SCRIPT,
    ENTRY1, ENTRY2, CHAIN, SP0, CNT, BLK_A, BLK_B,
    MASK, Model, ChainedOff, execute, oracle, battery_cases, config_ram,
    seed)
from verify_gx8002_analog_source import sha
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA
from build_transparent_image import Elf32

BASELINE = ROOT / 'docs/research/gx8002-uart-stage1-traptails-verification.json'


def run_until_chain(testcase, code, entry, args, ram):
    model = Model(dict(ram))
    with testcase.assertRaises(ChainedOff) as caught:
        execute(code, entry, args, model, entry)
    return caught.exception


class PrefixModel(unittest.TestCase):
    def test_railcfg_chain_state(self):
        ram = config_ram(ENTRY1, 0x11111111, 0x22222222, 0x33333333)
        want = oracle(ENTRY1, 0xaaaa0000, 0xbbbb0001, 0xcccc0004,
                      0xdddd0005, 0xeeee0006, 0xffff0007, ram)
        self.assertEqual(want['outcome'], 'chain')
        regs = want['regs']
        self.assertEqual(regs['r0'], 23)
        self.assertEqual(regs['r1'], 1)
        self.assertEqual(regs['r4'], CNT)
        self.assertEqual(regs['r14'], SP0 - 12)
        self.assertEqual(regs['r15'], 0x1000047a)
        # Untouched registers pass through.
        self.assertEqual(regs['r6'], 0xeeee0006)
        self.assertEqual(regs['r7'], 0xffff0007)
        # Only the three frame pushes: no MMIO traffic before the chain.
        self.assertEqual(want['trace'],
                         [('write', SP0 - 4, 4, 0xcccc0004),
                          ('write', SP0 - 8, 4, 0xdddd0005),
                          ('write', SP0 - 12, 4, seed('r15'))])

    def test_blkclr_chain_state(self):
        status_a, status_b = 0xa5a5a5a5, 0x5a5a5a5a
        ram = config_ram(ENTRY2, status_a, status_b, 0x99999999)
        want = oracle(ENTRY2, 0x11110000, 0x22220001, 0x33330004,
                      0x44440005, 0x55550006, 0x66660007, ram)
        self.assertEqual(want['outcome'], 'chain')
        regs = want['regs']
        self.assertEqual(regs['r0'], 20)
        self.assertEqual(regs['r1'], 0)
        self.assertEqual(regs['r2'], status_b)
        self.assertEqual(regs['r3'], BLK_B)
        self.assertEqual(regs['r4'], 0)
        self.assertEqual(regs['r14'], SP0 - 8)
        self.assertEqual(regs['r15'], 0x100004c4)
        self.assertEqual(want['trace'],
                         [('write', SP0 - 4, 4, 0x33330004),
                          ('write', SP0 - 8, 4, seed('r15')),
                          ('read', BLK_A + 0x40, 4, status_a),
                          ('write', BLK_A + 0x30, 4, 0),
                          ('write', BLK_A + 0x6c, 4, 0),
                          ('read', BLK_B + 0x40, 4, status_b),
                          ('write', BLK_B + 0x30, 4, 0),
                          ('write', BLK_B + 0x6c, 4, 0)])

    def test_oracle_rejects_unmapped_status(self):
        ram = config_ram(ENTRY2, 0, 0, 0)
        del ram[BLK_B + 0x40]
        with self.assertRaises(ValueError):
            oracle(ENTRY2, 0, 0, 0, 0, 0, 0, ram)

    def test_oracle_rejects_unknown_entry(self):
        ram = config_ram(ENTRY1, 0, 0, 0)
        with self.assertRaises(ValueError):
            oracle(0x10000999, 0, 0, 0, 0, 0, 0, ram)


class ExecutorSemantics(unittest.TestCase):
    def test_push_spills_in_operand_order(self):
        code = {ENTRY1: ('push', 'r4-r5, r15', 2),
                ENTRY1 + 2: ('bsr', hex(CHAIN), 4)}
        ram = config_ram(ENTRY1, 0, 0, 0)
        done = run_until_chain(self, code, ENTRY1,
                               (1, 2, 0x44444444, 0x55555555, 6, 7), ram)
        self.assertEqual(done.model.trace,
                         [('write', SP0 - 4, 4, 0x44444444),
                          ('write', SP0 - 8, 4, 0x55555555),
                          ('write', SP0 - 12, 4, seed('r15'))])
        self.assertEqual(done.registers['r14'], SP0 - 12)
        self.assertEqual(done.registers['r15'], ENTRY1 + 6)

    def test_foreign_call_rejected(self):
        code = {ENTRY1: ('bsr', '0x10000ea0', 4)}
        with self.assertRaises(ValueError):
            run_until_chain(self, code, ENTRY1, (0, 0, 0, 0, 0, 0),
                            config_ram(ENTRY1, 0, 0, 0))

    def test_unmapped_access_traps(self):
        code = {ENTRY1: ('st.w', 'r0, (r4, 0x10)', 2),
                ENTRY1 + 2: ('bsr', hex(CHAIN), 4)}
        model = Model(config_ram(ENTRY1, 0, 0, 0))
        with self.assertRaises(ValueError):
            execute(code, ENTRY1, (0xdead, 0, CNT, 0, 0, 0), model, ENTRY1)

    def test_post_call_ops_unsupported(self):
        # The post-chain tail (rotli/divs) is admitted by byte
        # identity, never by execution: reaching one is a failure.
        code = {ENTRY1: ('rotli', 'r3, r3, 4', 4),
                ENTRY1 + 4: ('bsr', hex(CHAIN), 4)}
        model = Model(config_ram(ENTRY1, 0, 0, 0))
        with self.assertRaises(ValueError):
            execute(code, ENTRY1, (0, 0, 0, 0, 0, 0), model, ENTRY1)
        with self.assertRaises(ValueError):
            execute({ENTRY1: ('bkpt', '', 2)}, ENTRY1,
                    (0, 0, 0, 0, 0, 0), Model(config_ram(ENTRY1, 0, 0, 0)),
                    ENTRY1)


class BatteryCoverage(unittest.TestCase):
    def test_battery_scale_and_entry_coverage(self):
        cases = battery_cases()
        self.assertGreaterEqual(len(cases), 200)
        entries = {case[0] for case in cases}
        self.assertEqual(entries, {ENTRY1, ENTRY2})
        rail = [case for case in cases if case[0] == ENTRY1]
        blk = [case for case in cases if case[0] == ENTRY2]
        self.assertEqual(len(rail), len(blk))
        # Register seeds vary (frame-word independence); status and
        # clear cells sweep zero/all-ones/pattern.
        self.assertGreater(len({case[1:7] for case in cases}), 1)
        self.assertIn(0xffffffff, {case[7] for case in cases})
        self.assertIn(0xffffffff, {case[9] for case in cases})


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

    def test_linked_sections_fill_placements_byte_identical(self):
        prefix = ROOT / 'build/csky-macos/install/bin'
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            traptails_obj = directory / 'traptails_s.o'
            subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *TRAPTAILS_FLAGS,
                            '-c', str(S_SOURCE), '-o', str(traptails_obj)], check=True)
            script = directory / 'traptails.ld'
            script.write_text(LINKER_SCRIPT)
            linked = directory / 'traptails.elf'
            subprocess.run([str(prefix / 'csky-unknown-elf-ld'), '-T', str(script),
                            str(traptails_obj), '-o', str(linked)],
                           check=True)
            elf = Elf32(linked.read_bytes(), str(linked))
            self.assertFalse(any(s['name'] and s['section'] == 0 for s in elf.symbols()))
            for symbol, _, offset, size, _, _ in SPECS:
                section = next(s for s in elf.sections if s['name'] == '.text.' + symbol)
                payload = elf.contents(section)
                self.assertEqual(len(payload), size, symbol)
                self.assertEqual(offset % section['align'], 0, symbol)
                self.assertEqual(elf.relocations(section['index']), [], symbol)
                self.assertEqual(payload, self.stock[offset:offset + size], symbol)


if __name__ == '__main__':
    unittest.main()
