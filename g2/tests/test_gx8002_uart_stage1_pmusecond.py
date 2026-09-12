"""Host contract and regression tests for the UART stage-1 pmusecond leaf.

The full decoded stock/source differential lives in
tools/verify_gx8002_uart_stage1_pmusecond.py (run by the candidate builder);
these tests pin the dispatch-slot model, the oracle/table model, and
the placement/envelope regression on macOS.

Native host execution of the assembly leaf is infeasible here: the
body dereferences fill-provided 32-bit target addresses (entry,
selector, cells) and retained jump-table addresses, which truncate on
the 64-bit host (the same truncation
test_gx8002_uart_stage1_pmufill documents for desc[0]). The
interpreter tests below execute snippets of the assembled target
object shape instead, which is the shipped code shape.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from verify_gx8002_uart_stage1_pmusecond import (
    PMUSECOND_FLAGS, PMUFILL_FLAGS, S_SOURCE, FILL_SOURCE, SPECS,
    LINKER_SCRIPT, JT, JT_IDS, JT_TARGET, JT_EXPECT,
    UART_TUPLES, Model, execute, oracle, battery_cases, config_ram,
    check_tables, first_fill_id)
from verify_gx8002_analog_source import sha
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA
from build_transparent_image import Elf32

BASELINE = ROOT / 'docs/research/gx8002-uart-stage1-pmusecond-verification.json'


def dispatch_snippet():
    """Materialize JT, select the r0 slot, load it, trap: the stock dispatch idiom."""
    return {
        0x1000: ('movih', 'r2, 4096', 2),
        0x1002: ('ori', 'r2, r2, 7924', 2),
        0x1004: ('mov', 'r3, r0', 2),
        0x1006: ('ldr.w', 'r3, (r2, r3 << 2)', 4),
        0x100a: ('bkpt', '', 2),
    }


def run_until_trap(testcase, code, args, ram):
    model = Model(dict(ram))
    with testcase.assertRaises(ValueError):
        execute(code, 0x1000, args, model)
    return model


class DispatchSlotModel(unittest.TestCase):
    def test_ident_keyed_map_matches_slot_order(self):
        # The retained dispatch reads slot id-7 (stock 0xEAE ldr.w);
        # the ident-keyed arm map must agree with the slot-ordered
        # pinned dump, including the id-25 last slot.
        self.assertEqual(JT_IDS, tuple(range(7, 26)))
        self.assertEqual(len(JT_EXPECT), 19)
        for ident, target in JT_TARGET.items():
            self.assertEqual(target, JT_EXPECT[ident - 7], ident)

    def test_dump_matches_pinned_table(self):
        if not IMAGE.exists():
            raise unittest.SkipTest('authenticated codec oracle unavailable')
        stock = IMAGE.read_bytes()
        if sha(stock) != IMAGE_SHA:
            raise unittest.SkipTest('stock identity changed')
        self.assertEqual(check_tables(stock), JT_EXPECT)

    def test_oracle_rejects_unknown_table_targets(self):
        if not IMAGE.exists():
            raise unittest.SkipTest('authenticated codec oracle unavailable')
        stock = IMAGE.read_bytes()
        if sha(stock) != IMAGE_SHA:
            raise unittest.SkipTest('stock identity changed')
        jt = check_tables(stock)
        ram, table_words = config_ram(7, 'direct', 0, 0, 0, (0, 0, 0),
                                      0, 0, 0, UART_TUPLES[0], jt)
        ram[JT] = 0xdeadbeef
        with self.assertRaises(ValueError):
            oracle(7, 0x600d600d, ram, table_words)
        ram, table_words = config_ram(25, 'direct', 0, 0, 0, (0, 0, 0),
                                      0, 0, 0, UART_TUPLES[0], jt)
        ram[JT + 4 * 18] = 0xdeadbeef
        with self.assertRaises(ValueError):
            oracle(25, 0x600d600d, ram, table_words)

    def test_first_fill_ids(self):
        self.assertEqual(first_fill_id(6), 6)
        self.assertEqual(first_fill_id(7), 19)
        self.assertEqual(first_fill_id(8), 19)
        self.assertEqual(first_fill_id(16), 16)
        self.assertEqual(first_fill_id(17), 16)
        self.assertEqual(first_fill_id(19), 19)
        self.assertEqual(first_fill_id(20), 19)
        self.assertEqual(first_fill_id(21), 19)
        self.assertEqual(first_fill_id(22), 22)
        self.assertEqual(first_fill_id(24), 22)
        self.assertEqual(first_fill_id(25), 10)


class ExecutorDispatch(unittest.TestCase):
    def test_ldr_w_reads_slot_base_plus_index(self):
        # Slot 0 (id 7) reads the table base word itself.
        model = run_until_trap(self, dispatch_snippet(), (0, 0),
                               {JT: 0x10000eb8})
        self.assertEqual(model.trace,
                         [('read', JT, 4, 0x10000eb8)])
        # Slot 18 (id 25) reads the last in-bounds slot.
        model = run_until_trap(self, dispatch_snippet(), (18, 0),
                               {JT + 4 * 18: 0x10000f84})
        self.assertEqual(model.trace,
                         [('read', JT + 4 * 18, 4, 0x10000f84)])

    def test_jmp_is_plain_indirect(self):
        code = {0x1000: ('jmp', 'r0', 2), 0x1002: ('bkpt', '', 2)}
        model = Model({})
        with self.assertRaises(ValueError):
            execute(code, 0x1000, (0x1002, 0), model)
        code = {0x1000: ('jmp', 'r2', 2)}
        model = Model({})
        with self.assertRaises(ValueError):
            execute(code, 0x1000, (0x5000, 0), model)

    def test_bkpt_traps(self):
        model = Model({})
        with self.assertRaises(ValueError):
            execute({0x1000: ('bkpt', '', 2)}, 0x1000, (0, 0), model)


class BatteryCoverage(unittest.TestCase):
    def test_battery_scale_and_dispatch_coverage(self):
        cases = battery_cases()
        self.assertGreaterEqual(len(cases), 500)
        idents = {case[0] for case in cases}
        self.assertIn(25, idents)
        modes6 = {case[2] for case in cases if case[0] == 6}
        self.assertIn('miss1', modes6)
        modes7 = {case[2] for case in cases if case[0] == 7}
        self.assertIn('missloop', modes7)


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
        prefix = ROOT / 'build/csky-macos/install/bin'
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            body_obj = directory / 'pmusecond_s.o'
            subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *PMUSECOND_FLAGS,
                            '-c', str(S_SOURCE), '-o', str(body_obj)], check=True)
            fill_obj = directory / 'fill_c.o'
            subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *PMUFILL_FLAGS,
                            '-c', str(FILL_SOURCE), '-o', str(fill_obj)], check=True)
            script = directory / 'pmusecond.ld'
            script.write_text(LINKER_SCRIPT)
            linked = directory / 'pmusecond.elf'
            subprocess.run([str(prefix / 'csky-unknown-elf-ld'), '-T', str(script),
                            str(body_obj), str(fill_obj), '-o', str(linked)],
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
