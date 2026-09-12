"""Host contract and regression tests for the UART stage-1 mdelay leaf.

The full decoded stock/source differential lives in
tools/verify_gx8002_uart_stage1_mdelay.py (run by the candidate builder);
these tests pin the host behavior, the interpreter semantics, and the
placement/envelope regression on macOS.
"""
import ctypes
import json
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from verify_gx8002_uart_stage1_mdelay import (
    MDELAY_FLAGS, C_SOURCE, SPECS, LINKER_SCRIPT, CounterModel,
    execute, oracle, battery_cases, check_shape, outside_window,
    seed, Handoff, CTR_LO, CTR_HI, SP0)
from verify_gx8002_analog_source import sha
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA

BASELINE = ROOT / 'docs/research/gx8002-uart-stage1-mdelay-verification.json'

STUB_C = r'''
#include <stdint.h>
#include <setjmp.h>

static jmp_buf exit_env;
static uint32_t exit_r0;

void open_cfw_gx8002_uart_boot_stage1_46c_entry(uint32_t r0carry) {
    exit_r0 = r0carry;
    longjmp(exit_env, 1);
}

uint32_t open_cfw_gx8002_uart_stage1_mdelay(uint32_t msec);

int run_mdelay(uint32_t msec, uint32_t *out_r0) {
    if (setjmp(exit_env) == 0) {
        open_cfw_gx8002_uart_stage1_mdelay(msec);
        return -2;
    }
    *out_r0 = exit_r0;
    return 0;
}
'''


class HostBehavior(unittest.TestCase):
    """Exercise the C leaf on the host against a redirected counter."""

    @classmethod
    def setUpClass(cls):
        cls.cells = (ctypes.c_uint32 * 4)(0, 0, 0, 0)
        base = ctypes.addressof(cls.cells)
        directory = tempfile.mkdtemp(prefix='gx8002-stage1-mdelay-host-')
        cls.directory = Path(directory)
        (cls.directory / 'stub.c').write_text(STUB_C)
        cls.library = cls.directory / 'mdelay.dylib'
        subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                        '-O2', '-fno-builtin', '-shared', '-fPIC',
                        '-DGX8002_STAGE1_COUNTER_BASE=((uintptr_t)%#x)' % base,
                        '-DGX8002_STAGE1_MDELAY_HOST',
                        str(C_SOURCE), str(cls.directory / 'stub.c'),
                        '-o', str(cls.library)], check=True)
        lib = ctypes.CDLL(str(cls.library))
        cls.call_mdelay = lib.run_mdelay
        cls.call_mdelay.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32)]
        cls.call_mdelay.restype = ctypes.c_int
        cls.stop = threading.Event()

    def setUp(self):
        for index in range(4):
            self.cells[index] = 0
        self.stop.clear()

    # cells[1] is the counter VALUE (+0x04) and cells[2] the ACCSNAP
    # (+0x08); cells[0] is never touched by the leaf.
    def test_zero_milliseconds_hands_off_immediately(self):
        out = ctypes.c_uint32(0xdeadbeef)
        self.assertEqual(self.call_mdelay(0, ctypes.byref(out)), 0)
        self.assertEqual(out.value, 0xffffffff)
        self.assertEqual((self.cells[1], self.cells[2]), (0, 0))

    def test_waits_advance_then_hand_off(self):
        pumping = threading.Event()

        def advance():
            while not self.stop.is_set():
                self.cells[1] = (self.cells[1] + 200000) & 0xffffffff
                if self.cells[1] < 200000:
                    self.cells[2] = (self.cells[2] + 1) & 0xffffffff
                pumping.wait(0.001)

        worker = threading.Thread(target=advance, daemon=True)
        worker.start()
        outcome = {}

        def call():
            out = ctypes.c_uint32(0xdeadbeef)
            outcome['rc'] = self.call_mdelay(2, ctypes.byref(out))
            outcome['r0'] = out.value

        caller = threading.Thread(target=call, daemon=True)
        caller.start()
        try:
            caller.join(timeout=60)
            self.assertFalse(caller.is_alive(), 'mdelay did not hand off')
            self.assertEqual(outcome.get('rc'), 0)
            self.assertEqual(outcome.get('r0'), 0xffffffff)
            self.assertGreater(self.cells[1] | (self.cells[2] << 32), 2001)
        finally:
            self.stop.set()
            worker.join(timeout=30)


class TargetInterpreter(unittest.TestCase):
    def test_add64_carries(self):
        for (lo, hi), (want_lo, want_hi) in (
                ((10, 20), (1011, 20)),
                ((0xffffffff, 7), (1000, 8)),
                ((0xffffffff, 0xffffffff), (1000, 0))):
            code = {0x1000: ('movi', 'r2, %d' % lo, 4),
                    0x1004: ('movi', 'r3, %d' % hi, 2),
                    0x1006: ('movi', 'r4, 1001', 4),
                    0x100a: ('movi', 'r5, 0', 2),
                    0x100c: ('add.64', 'r2, r2, r4', 4),
                    0x1010: ('bsr', '0x1000046c', 4)}
            try:
                execute(code, 0x1000, 0, CounterModel(0, 0))
            except Handoff as done:
                self.assertEqual(done.registers['r2'], want_lo, (lo, hi))
                self.assertEqual(done.registers['r3'], want_hi, (lo, hi))
            else:
                self.fail('expected handoff')

    def test_push_pop_round_trip(self):
        code = {0x1000: ('push', 'r4-r5, r15', 2),
                0x1002: ('movi', 'r4, 1', 2),
                0x1004: ('movi', 'r5, 2', 2),
                0x1006: ('pop', 'r4-r5, r15', 2),
                0x1008: ('bsr', '0x1000046c', 4)}
        model = CounterModel(0, 0)
        try:
            execute(code, 0x1000, 0, model)
        except Handoff as done:
            for reg in ('r4', 'r5', 'r15', 'r14'):
                self.assertEqual(done.registers[reg], seed(reg), reg)
        else:
            self.fail('expected handoff')

    def test_chaining_branch_stops_before_clobber(self):
        code = {0x1000: ('movi', 'r0, 7', 2),
                0x1002: ('bsr', '0x1000046c', 4)}
        model = CounterModel(0, 0)
        try:
            execute(code, 0x1000, 0, model)
        except Handoff as done:
            self.assertEqual(done.registers['r0'], 7)
            self.assertEqual(done.registers['r15'], seed('r15'))
        else:
            self.fail('expected handoff')

    def test_foreign_call_rejected(self):
        code = {0x1000: ('bsr', '0x10000780', 4)}
        with self.assertRaises(ValueError):
            execute(code, 0x1000, 0, CounterModel(0, 0))

    def test_unexpected_address_rejected(self):
        code = {0: ('ld.w', 'r0, (r3, 0x18)', 2), 2: ('bsr', '0x1000046c', 4)}
        with self.assertRaises(ValueError):
            execute(code, 0, 0, CounterModel(0, 0))

    def test_shape_guard_rejects_drift(self):
        code = {0x100003fc: ('push', 'r4-r6', 2),
                0x100003fe: ('bsr', '0x1000046c', 4)}
        with self.assertRaises(ValueError):
            check_shape(code, 0x100003fc, 8)

    def test_oracle_counts_waits(self):
        want_r0, ram, trace = oracle(2, 0, 0)
        self.assertEqual(want_r0, 0xffffffff)
        reads = [entry for entry in trace if entry[0] == 'read']
        # One deadline snapshot plus polls per millisecond; every snapshot
        # is a LO/HI pair and the counter visibly advances.
        self.assertTrue(len(reads) >= 6)
        self.assertEqual(reads[0], ('read', CTR_LO, 4, 0))
        self.assertEqual(reads[1], ('read', CTR_HI, 4, 0))
        self.assertGreater(ram[CTR_LO] | (ram[CTR_HI] << 32), 2002)
        want_r0, _, trace0 = oracle(0, 0x1234, 0x56)
        self.assertEqual(want_r0, 0xffffffff)
        self.assertEqual(trace0, [])

    def test_window_traffic_excluded(self):
        trace = [('write', SP0 - 4, 4, 1), ('read', CTR_LO, 4, 5),
                 ('read', SP0 + 8, 4, 6), ('read', CTR_HI, 4, 7)]
        self.assertEqual(outside_window(trace),
                         [('read', CTR_LO, 4, 5), ('read', CTR_HI, 4, 7)])

    def test_battery_covers_edges(self):
        cases = battery_cases()
        counts = sorted({msec for msec, _, _ in cases})
        self.assertIn(0, counts)
        self.assertIn(255, counts)
        self.assertTrue(any(lo >= 0xfffff000 for _, lo, _ in cases))
        self.assertTrue(any(hi == 0xffffffff for _, _, hi in cases))


class PlacementRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not IMAGE.exists():
            raise unittest.SkipTest('authenticated codec oracle unavailable')
        cls.stock = IMAGE.read_bytes()
        if sha(cls.stock) != IMAGE_SHA:
            raise unittest.SkipTest('stock identity changed')
        cls.baseline = json.loads(BASELINE.read_text())

    def test_stock_envelopes_unchanged(self):
        by_symbol = {f['symbol']: f for f in self.baseline['functions']}
        for symbol, _, offset, size, _, _ in SPECS:
            want = by_symbol[symbol]['stock_occurrences'][0]['sha256']
            self.assertEqual(sha(self.stock[offset:offset + size]), want, symbol)

    def test_linked_sections_fit_and_bind_nothing(self):
        from build_transparent_image import Elf32
        prefix = ROOT / 'build/csky-macos/install/bin'
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            c_obj = directory / 'mdelay_c.o'
            subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *MDELAY_FLAGS,
                            '-c', str(C_SOURCE), '-o', str(c_obj)], check=True)
            script = directory / 'mdelay.ld'
            script.write_text(LINKER_SCRIPT)
            linked = directory / 'mdelay.elf'
            subprocess.run([str(prefix / 'csky-unknown-elf-ld'), '-T', str(script),
                            str(c_obj), '-o', str(linked)], check=True)
            elf = Elf32(linked.read_bytes(), str(linked))
            self.assertFalse(any(s['name'] and s['section'] == 0 for s in elf.symbols()))
            for symbol, _, offset, size, _, _ in SPECS:
                section = next(s for s in elf.sections if s['name'] == '.text.' + symbol)
                self.assertLessEqual(len(elf.contents(section)), size, symbol)
                self.assertEqual(offset % section['align'], 0, symbol)
                self.assertEqual(elf.relocations(section['index']), [], symbol)


if __name__ == '__main__':
    unittest.main()
