"""Host contract and regression tests for UART stage-1 XIP leaves.

The full decoded stock/source differential lives in
tools/verify_gx8002_uart_stage1_xip.py (run by the candidate builder);
these tests pin the host behavior, the interpreter semantics, and the
placement/envelope regression on macOS.
"""
import ctypes
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from verify_gx8002_uart_stage1_xip import (
    XIP_FLAGS, C_SOURCE, SPECS, LINKER_SCRIPT, XipModel, battery_cases,
    execute, oracle, STATUS, DATA, RESIDUAL_READ, RESIDUAL_WRITE,
    XIP, UNLOCK, MASK)
from verify_gx8002_analog_source import sha
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA

BASELINE = ROOT / 'docs/research/gx8002-uart-stage1-xip-verification.json'

NWORDS = 32
STATUS_IDX = 0x0a
RESID_READ_IDX = 0x09
RESID_WRITE_IDX = 0x08
DATA_IDX = 0x18
UNLOCK_IDX = 31


class HostBehavior(unittest.TestCase):
    """Exercise the C leaves on the host against a redirected XIP block."""

    @classmethod
    def setUpClass(cls):
        cls.regs = (ctypes.c_uint32 * NWORDS)()
        base = ctypes.addressof(cls.regs)
        unlock = base + UNLOCK_IDX * 4
        directory = tempfile.mkdtemp(prefix='gx8002-stage1-xip-host-')
        cls.library = Path(directory) / 'xip.dylib'
        subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                        '-O2', '-fno-builtin', '-shared', '-fPIC',
                        '-DGX8002_STAGE1_XIP_BASE=((uintptr_t)%#x)' % base,
                        '-DGX8002_STAGE1_XIP_UNLOCK=((uintptr_t)%#x)' % unlock,
                        str(C_SOURCE), '-o', str(cls.library)], check=True)
        lib = ctypes.CDLL(str(cls.library))
        cls.read = lib.open_cfw_gx8002_uart_stage1_xip_read
        cls.read.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_ubyte),
                             ctypes.c_uint32]
        cls.read.restype = None
        cls.write = lib.open_cfw_gx8002_uart_stage1_xip_write
        cls.write.argtypes = [ctypes.c_uint32, ctypes.POINTER(ctypes.c_ubyte),
                              ctypes.c_uint32]
        cls.write.restype = None

    def setUp(self):
        for index in range(NWORDS):
            self.regs[index] = 0xdeadbeef

    def test_read_matches_oracle(self):
        # The host array aliases the DATA FIFO: the command word written
        # by the prologue is what the transfer loop reads back, so every
        # received byte is the narrowed command (this also pins the
        # narrowing on real compiled code).
        for length, cmd in ((0, 0x0000009f),
                            (1, 0x12345678),
                            (3, 0xffffff41)):
            self.regs[STATUS_IDX] = 0x08
            self.regs[RESID_READ_IDX] = 0
            self.regs[DATA_IDX] = 0xdeadbeef
            self.regs[UNLOCK_IDX] = 0xdeadbeef
            dst = (ctypes.c_ubyte * 4)(0xa5, 0xa5, 0xa5, 0xa5)
            self.read(cmd, dst, length)
            self.assertEqual(list(dst[:length]), [cmd & 0xff] * length)
            self.assertEqual(list(dst[length:]), [0xa5] * (4 - length))
            self.assertEqual(self.regs[0x00], 0xc07)
            self.assertEqual(self.regs[0x01], (length - 1) & 0xffffffff)
            self.assertEqual(self.regs[0x04], 1)
            self.assertEqual(self.regs[0x06], 0)
            self.assertEqual(self.regs[0x02], 1)
            self.assertEqual(self.regs[0x13], 0)
            self.assertEqual(self.regs[DATA_IDX], cmd)
            self.assertEqual(self.regs[UNLOCK_IDX], 0)

    def test_write_matches_oracle(self):
        for length, cmd, src in ((0, 0x0000009f, [0x11, 0x22, 0x33]),
                                 (1, 0x0000009f, [0x41, 0x22, 0x33]),
                                 (3, 0x12345678, [0x41, 0x80, 0xff])):
            self.regs[STATUS_IDX] = 0x02
            self.regs[RESID_WRITE_IDX] = 0
            self.regs[DATA_IDX] = 0xdeadbeef
            self.regs[UNLOCK_IDX] = 0xdeadbeef
            buf = (ctypes.c_ubyte * 3)(*src)
            self.write(cmd, buf, length)
            self.assertEqual(list(buf), src)
            self.assertEqual(self.regs[0x00], 0x407)
            self.assertEqual(self.regs[0x01], length)
            self.assertEqual(self.regs[0x04], 1)
            self.assertEqual(self.regs[0x06], (length << 16) & 0xffffffff)
            self.assertEqual(self.regs[0x02], 1)
            self.assertEqual(self.regs[0x13], 0)
            self.assertEqual(self.regs[DATA_IDX],
                             cmd if length == 0 else src[length - 1])
            self.assertEqual(self.regs[UNLOCK_IDX], 0)


class TargetInterpreter(unittest.TestCase):
    def test_lsli_rotli_synthesize_addresses(self):
        code = {0x1000: ('movi', 'r3, 162', 2),
                0x1002: ('lsli', 'r3, r3, 24', 2),
                0x1004: ('movi', 'r18, 32930', 4),
                0x1008: ('rotli', 'r18, r18, 24', 4),
                0x100c: ('st.w', 'r18, (r3, 0x0)', 2),
                0x100e: ('rts', '', 2)}
        model = XipModel({STATUS: [0], RESIDUAL_READ: [0],
                          RESIDUAL_WRITE: [0], DATA: [0]}, {})
        trace, _, preserved = execute(code, 0x1000, 0, 0, 0, model)
        self.assertEqual(trace, [('write', XIP, 4, 0xa2000080)])
        self.assertTrue(preserved)

    def test_countdown_copy_pins_trace_and_ram(self):
        arena = 0x20001000
        code = {0x1000: ('ldbi.b', 'r0, (r1)', 2),
                0x1002: ('stbi.b', 'r0, (r3)', 2),
                0x1004: ('subi', 'r2, 1', 2),
                0x1006: ('bnez', 'r2, 0x1000', 4),
                0x100a: ('rts', '', 2)}
        # Point r3 at the destination explicitly via a prefix move.
        code = {0x0ff0: ('mov', 'r3, r1', 2),
                0x0ff2: ('br', '0x1000', 2),
                **code}
        ram = {arena: 0x41, arena + 1: 0x80, arena + 2: 0xff}
        model = XipModel({STATUS: [0], RESIDUAL_READ: [0],
                          RESIDUAL_WRITE: [0], DATA: [0]}, ram)
        trace, final, preserved = execute(code, 0x0ff0, 0, arena, 3, model)
        self.assertEqual([final[arena + i] for i in range(3)], [0x41, 0x80, 0xff])
        self.assertEqual(trace,
                         [('read', arena, 1, 0x41), ('write', arena, 1, 0x41),
                          ('read', arena + 1, 1, 0x80),
                          ('write', arena + 1, 1, 0x80),
                          ('read', arena + 2, 1, 0xff),
                          ('write', arena + 2, 1, 0xff)])
        self.assertTrue(preserved)

    def test_cmpne_branch_and_callee_saved(self):
        code = {0x1000: ('cmpne', 'r1, r2', 2),
                0x1002: ('bt', '0x1008', 2),
                0x1004: ('movi', 'r4, 7', 2),
                0x1006: ('rts', '', 2),
                0x1008: ('rts', '', 2)}
        model = XipModel({STATUS: [0], RESIDUAL_READ: [0],
                          RESIDUAL_WRITE: [0], DATA: [0]}, {})
        _, _, preserved = execute(code, 0x1000, 0, 5, 5, model)
        self.assertFalse(preserved)
        model = XipModel({STATUS: [0], RESIDUAL_READ: [0],
                          RESIDUAL_WRITE: [0], DATA: [0]}, {})
        trace, _, preserved = execute(code, 0x1000, 0, 5, 6, model)
        self.assertEqual(trace, [])
        self.assertTrue(preserved)

    def test_unexpected_address_rejected(self):
        code = {0: ('ld.w', 'r0, (r3, 0x18)', 2), 2: ('rts', '', 2)}
        with self.assertRaises(ValueError):
            execute(code, 0, 0, 0, 0,
                    XipModel({STATUS: [0], RESIDUAL_READ: [0],
                              RESIDUAL_WRITE: [0], DATA: [0]}, {}))


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
        for symbol, _, offset, size, _ in SPECS:
            want = by_symbol[symbol]['stock_occurrences'][0]['sha256']
            self.assertEqual(sha(self.stock[offset:offset + size]), want, symbol)

    def test_linked_sections_fit_and_bind_nothing(self):
        from build_transparent_image import Elf32
        prefix = ROOT / 'build/csky-macos/install/bin'
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            c_obj = directory / 'xip_c.o'
            subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *XIP_FLAGS,
                            '-c', str(C_SOURCE), '-o', str(c_obj)], check=True)
            script = directory / 'xip.ld'
            script.write_text(LINKER_SCRIPT)
            linked = directory / 'xip.elf'
            subprocess.run([str(prefix / 'csky-unknown-elf-ld'), '-T', str(script),
                            str(c_obj), '-o', str(linked)], check=True)
            elf = Elf32(linked.read_bytes(), str(linked))
            self.assertFalse(any(s['name'] and s['section'] == 0 for s in elf.symbols()))
            for symbol, _, offset, size, _ in SPECS:
                section = next(s for s in elf.sections if s['name'] == '.text.' + symbol)
                self.assertLessEqual(len(elf.contents(section)), size, symbol)
                self.assertEqual(offset % section['align'], 0, symbol)
                self.assertEqual(elf.relocations(section['index']), [], symbol)


if __name__ == '__main__':
    unittest.main()
