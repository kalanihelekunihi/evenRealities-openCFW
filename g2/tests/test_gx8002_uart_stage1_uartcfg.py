"""Host contract and regression tests for the UART stage-1 uartcfg leaf.

The full decoded stock/source differential lives in
tools/verify_gx8002_uart_stage1_uartcfg.py (run by the candidate builder);
these tests pin the interpreter semantics, the oracle/battery model, and
the placement/envelope regression on macOS.

Native host execution of the assembly leaf is infeasible here: the
body dereferences a 32-bit descriptor address and 0xA0005000-block
MMIO addresses, which truncate on the 64-bit host. The interpreter
tests below execute the assembled target object instead, which is the
shipped code shape.
"""
import json
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from verify_gx8002_uart_stage1_uartcfg import (
    UARTCFG_FLAGS, S_SOURCE, SPECS, LINKER_SCRIPT, CHAIN, ENTRY, PKG,
    SIZE, MMIO, DESC, SP0, WINDOW_LO, WINDOW_HI, LIVE_REGS,
    Model, execute, oracle, battery_cases, config_ram, check_shape,
    seed, in_window, ChainedOff, MASK)
from verify_gx8002_analog_source import sha
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA

BASELINE = ROOT / 'docs/research/gx8002-uart-stage1-uartcfg-verification.json'


def tiny(ops, start=0x1000):
    """Hand-built snippet plus a self-targeting chain terminator."""
    code = {}
    pc = start
    for op, operand in ops:
        code[pc] = (op, operand, 2)
        pc += 2
    term = pc
    code[term] = ('bsr', hex(term), 4)
    return code, start, term


def run(code, start, term, args, ram, entry_sp=SP0):
    model = Model(ram)
    try:
        execute(code, start, args, model, chain=term, entry_sp=entry_sp)
    except ChainedOff as done:
        return done.registers, list(done.model.trace)
    raise AssertionError('expected ChainedOff')


class TargetInterpreter(unittest.TestCase):
    def test_movih_ori_materialize_base(self):
        code, start, term = tiny([('movih', 'r3, 40960'),
                                  ('ori', 'r3, r3, 20480')])
        regs, _ = run(code, start, term, (0, 0, 0)[:2], {})
        self.assertEqual(regs['r3'], MMIO)

    def test_zext_selects_bit_field(self):
        # zext rd, rs, 12, 8 keeps bits 8..12 (the 0x24 program).
        code, start, term = tiny([('mov', 'r2, r0'),
                                  ('zext', 'r2, r2, 12, 8')])
        regs, _ = run(code, start, term, (0x12341f00, 0), {})
        self.assertEqual(regs['r2'], 0x1f)
        regs, _ = run(code, start, term, (0x000000ff, 0), {})
        self.assertEqual(regs['r2'], 0x0)

    def test_lsli_and_bclri(self):
        code, start, term = tiny([('mov', 'r2, r0'),
                                  ('tlsli', 'r2, r2, 4'),
                                  ('bclri', 'r2, 5')])
        regs, _ = run(code, start, term, (0x0f, 0), {})
        self.assertEqual(regs['r2'], (0x0f << 4) & ~(1 << 5) & MASK)

    def test_subi_negative_mask(self):
        # movi/subi mask pairs build small negative masks.
        code, start, term = tiny([('movi', 'r1, 0'),
                                  ('subi', 'r1, 64')])
        regs, _ = run(code, start, term, (0, 0), {})
        self.assertEqual(regs['r1'], (0 - 64) & MASK)

    def test_ld_b_reads_lane(self):
        code, start, term = tiny([('ld.b', 'r2, (r0, 0x14)')])
        ram = {0x1014: 0xa5ff00c3}
        regs, trace = run(code, start, term, (0x1000, 0), dict(ram))
        self.assertEqual(regs['r2'], 0xc3)
        self.assertIn(('read', 0x1014, 1, 0xc3), trace)
        regs, _ = run(code, start, term, (0x1001, 0), dict(ram))
        self.assertEqual(regs['r2'], 0x00)

    def test_push_pop_round_trip(self):
        code, start, term = tiny([('push', 'r4-r6, r15'),
                                  ('pop', 'r4-r6, r15')])
        ram = {SP0 - 64 + 4 * i: 0 for i in range(64)}
        regs, _ = run(code, start, term, (0, 0), dict(ram))
        self.assertEqual(regs['r14'], SP0)
        self.assertEqual(regs['r6'], seed('r6'))

    def test_chain_sets_link_register(self):
        code, start, term = tiny([('movi', 'r0, 0')])
        model = Model({})
        try:
            execute(code, start, (0, 0), model, chain=term)
        except ChainedOff as done:
            self.assertEqual(done.registers['r15'], term + 4)
        else:
            raise AssertionError('expected ChainedOff')

    def test_bsr_rejects_foreign_calls(self):
        code, start, term = tiny([('bsr', '0x10000d98')])
        model = Model({})
        with self.assertRaises(ValueError):
            execute(code, start, (0, 0), model, chain=term)

    def test_bkpt_traps(self):
        code, start, term = tiny([('bkpt', '')])
        model = Model({})
        with self.assertRaises(ValueError):
            execute(code, start, (0, 0), model, chain=term)


class OracleBattery(unittest.TestCase):
    def test_battery_scale(self):
        cases = battery_cases()
        self.assertGreaterEqual(len(cases), 200)
        entries = {case[0] for case in cases}
        self.assertEqual(entries, {DESC, 0})

    def test_battery_covers_chain_and_program(self):
        outcomes = set()
        for case in battery_cases():
            entry_r0, word0_entry, d14, dmisc, mmio, r1seed = case
            ram, _ = config_ram(entry_r0, word0_entry, d14, dmisc, mmio)
            desc = 0 if word0_entry == 0 else entry_r0
            outcomes.add((entry_r0 == 0, word0_entry == 0,
                          ram.get(desc, ram.get(0)) == 0))
        # (entry-at-zero, entry-word-zero, gate-word-zero) corners:
        # direct chains with both bases plus programmed bodies.
        self.assertIn((False, False, False), outcomes)
        self.assertIn((False, True, False), outcomes)
        self.assertIn((True, False, False), outcomes)
        self.assertIn((True, True, True), outcomes)

    def test_entry_registers_do_not_shape_traces(self):
        # Entry r1/r4-r6 are never read by the body: two cases
        # differing only in r1seed must produce identical traces.
        from verify_gx8002_uart_stage1_uartcfg import DESC_WORDS, MMIO_OFFSETS
        dmisc = {0x10: 0x1, 0x18: 0x2, 0x1c: 0x3, 0x20: 0x4,
                 0x24: 0x5, 0x28: 0x6, 0x2c: 0x7}
        mmio = {offset: 0xa5a5a5a5 for offset in MMIO_OFFSETS}
        traces = []
        for r1seed in (0x600d600d, 0x0):
            ram, _ = config_ram(DESC, 0x12345678, 0x1f00, dmisc, mmio)
            want = oracle(DESC, r1seed, ram)
            traces.append([e for e in want['trace'] if not in_window(e[1])])
        self.assertEqual(traces[0], traces[1])

    def test_retained_chain_target_saves_frame_first(self):
        # The r4 implementation-defined exclusion rests on retained
        # 0x1000046C saving r4/r5 before any read. Pin the stock
        # entry shape directly against the authenticated image.
        if not IMAGE.exists():
            raise unittest.SkipTest('authenticated codec oracle unavailable')
        stock = IMAGE.read_bytes()
        if sha(stock) != IMAGE_SHA:
            raise unittest.SkipTest('stock identity changed')
        prefix = ROOT / 'build/csky-macos/install/bin'
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            (directory / 'slice.bin').write_bytes(stock[0x50:0x2050])
            wrapper = directory / 'wrap.elf'
            subprocess.run(
                [str(prefix / 'csky-unknown-elf-objcopy'), '-I', 'binary',
                 '-O', 'elf32-csky-little', '-B', 'csky',
                 '--set-section-flags', '.data=alloc,code,load',
                 str(directory / 'slice.bin'), str(wrapper)], check=True)
            data = bytearray(wrapper.read_bytes())
            struct.pack_into('<I', data, 36, 0x21006009)
            wrapper.write_bytes(data)
            adjusted = directory / 'vma.elf'
            subprocess.run(
                [str(prefix / 'csky-unknown-elf-objcopy'),
                 '--adjust-vma=0x10000000', str(wrapper), str(adjusted)],
                check=True)
            text = subprocess.check_output(
                [str(prefix / 'csky-unknown-elf-objdump'), '-D',
                 '--start-address=0x1000046c', '--stop-address=0x10000472',
                 str(adjusted)], text=True)
        lines = [line for line in text.splitlines() if '1000046c:' in line]
        self.assertEqual(len(lines), 1)
        self.assertIn('push', lines[0])
        self.assertIn('r4-r5, r15', lines[0])


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
            cfg_obj = directory / 'uartcfg_s.o'
            subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *UARTCFG_FLAGS,
                            '-c', str(S_SOURCE), '-o', str(cfg_obj)], check=True)
            script = directory / 'uartcfg.ld'
            script.write_text(LINKER_SCRIPT)
            linked = directory / 'uartcfg.elf'
            subprocess.run([str(prefix / 'csky-unknown-elf-ld'), '-T', str(script),
                            str(cfg_obj), '-o', str(linked)], check=True)
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
