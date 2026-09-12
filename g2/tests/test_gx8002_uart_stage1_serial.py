"""Host contract and regression tests for UART stage-1 polled-UART leaves.

The full decoded stock/source differential lives in
tools/verify_gx8002_uart_stage1_serial.py (run by the candidate builder);
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
from verify_gx8002_uart_stage1_serial import (
    SERIAL_FLAGS, C_SOURCE, S_SOURCE, SPECS, UartModel, battery_cases,
    execute, oracle, BASE_CELL, DST_CELL, MASK)
from verify_gx8002_analog_source import sha
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA

BASELINE = ROOT / 'docs/research/gx8002-uart-stage1-serial-verification.json'


class HostBehavior(unittest.TestCase):
    """Exercise the C leaves on the host against a redirected UART."""

    @classmethod
    def setUpClass(cls):
        cls.regs = (ctypes.c_uint32 * 8)()
        cls.cell = ctypes.c_ulonglong(ctypes.addressof(cls.regs))
        directory = tempfile.mkdtemp(prefix='gx8002-stage1-serial-host-')
        cls.library = Path(directory) / 'serial.dylib'
        subprocess.run(['cc', '-std=c11', '-Wall', '-Wextra', '-Werror',
                        '-O2', '-fno-builtin', '-shared', '-fPIC',
                        '-DGX8002_STAGE1_UART_BASE_CELL=((volatile uintptr_t *)%#x)'
                        % ctypes.addressof(cls.cell),
                        str(C_SOURCE), '-o', str(cls.library)], check=True)
        lib = ctypes.CDLL(str(cls.library))
        cls.put = lib.open_cfw_gx8002_uart_stage1_put
        cls.put.argtypes = [ctypes.c_int]
        cls.put.restype = None
        cls.try_get = lib.open_cfw_gx8002_uart_stage1_try_get
        cls.try_get.argtypes = [ctypes.POINTER(ctypes.c_ubyte)]
        cls.try_get.restype = ctypes.c_int
        cls.get_char = lib.open_cfw_gx8002_uart_stage1_get_char
        cls.get_char.argtypes = []
        cls.get_char.restype = ctypes.c_int

    def test_put_matches_oracle(self):
        for arg, base, _, lsr, _ in battery_cases('put'):
            del base
            self.regs[5] = lsr[-1]
            self.regs[0] = 0xdeadbeef
            self.put(arg & 0xffffffff if arg < 0x80000000 else
                     arg - 0x100000000)
            want, _, _, _ = oracle('put', arg, 0, 0, lsr, [0])
            self.assertEqual(self.regs[0], want & 0xffffffff)

    def test_try_get_matches_oracle(self):
        cell = ctypes.c_ubyte(0xaa)
        for _, _, dst_init, lsr, rbr in battery_cases('try_get'):
            del dst_init
            self.regs[5] = lsr[0]
            self.regs[0] = rbr[0]
            cell.value = 0xaa
            got = self.try_get(ctypes.byref(cell))
            want_r0, want_dst, _, _ = oracle('try_get', 0, 0, 0xaa, lsr, rbr)
            self.assertEqual(got, want_r0 if want_r0 != MASK else -1)
            self.assertEqual(cell.value, want_dst & 0xff)

    def test_get_char_matches_oracle(self):
        for _, _, _, lsr, rbr in battery_cases('get_char'):
            self.regs[5] = lsr[-1]
            self.regs[0] = rbr[0]
            want_r0, _, _, _ = oracle('get_char', 0, 0, 0, lsr, rbr)
            self.assertEqual(self.get_char(), want_r0)


class TargetInterpreter(unittest.TestCase):
    def test_poll_loop_and_word_store(self):
        code = {0x1000: ('movi', 'r3, 8192', 4),
                0x1004: ('bseti', 'r3, 29', 2),
                0x1006: ('ld.w', 'r3, (r3, 0x14)', 2),
                0x1008: ('addi', 'r12, r3, 20', 4),
                0x100c: ('ld.w', 'r1, (r12, 0x0)', 2),
                0x100e: ('andi', 'r2, r1, 64', 4),
                0x1012: ('bez', 'r2, 0x100c', 4),
                0x1016: ('st.w', 'r0, (r3, 0x0)', 2),
                0x1018: ('rts', '', 2)}
        model = UartModel(0xa0100000, 0, [0x00, 0xbf, 0x43], [0])
        result = execute(code, 0x1000, 0x47, model)
        self.assertEqual(result[:4], (0x47, 0, [0x47],
                                      [('read', BASE_CELL, 0xa0100000),
                                       ('read', 0xa0100014, 0x00),
                                       ('read', 0xa0100014, 0xbf),
                                       ('read', 0xa0100014, 0x43),
                                       ('write', 0xa0100000, 0x47)]))
        self.assertTrue(result[4])

    def test_byte_store_width_and_negative_return(self):
        code = {0: ('lrw', 'r3, 0xa0100000', 4),
                4: ('ld.w', 'r1, (r3, 0x14)', 2),
                6: ('andi', 'r2, r1, 1', 4),
                10: ('bez', 'r2, 0x1e', 4),
                14: ('ld.w', 'r3, (r3, 0x0)', 2),
                16: ('st.b', 'r3, (r0, 0x0)', 2),
                18: ('movi', 'r0, 0', 2),
                20: ('rts', '', 2),
                30: ('movi', 'r0, 0', 2),
                32: ('subi', 'r0, 1', 2),
                34: ('br', '0x14', 2)}
        model = UartModel(0xa0100000, 0xa5a5a5a5, [0x00], [0])
        result = execute(code, 0, DST_CELL, model)
        self.assertEqual(result[0], MASK)
        self.assertEqual(result[1], 0xa5a5a5a5)
        self.assertTrue(result[4])
        model = UartModel(0xa0100000, 0xa5a5a500, [0x01], [0x12345678])
        result = execute(code, 0, DST_CELL, model)
        self.assertEqual(result[:4], (0, 0xa5a5a578, [],
                                      [('read', 0xa0100014, 0x01),
                                       ('read', 0xa0100000, 0x12345678),
                                       ('write', DST_CELL, 0x78)]))
        self.assertTrue(result[4])

    def test_zextb_narrows_word_read(self):
        code = {0: ('lrw', 'r3, 0x20002000', 4),
                4: ('ld.w', 'r0, (r3, 0x0)', 2),
                6: ('zextb', 'r0, r0', 2),
                8: ('rts', '', 2)}
        model = UartModel(0xa0100000, 0x12345678, [0x40], [0])
        result = execute(code, 0, 0, model)
        self.assertEqual(result[0], 0x78)
        self.assertTrue(result[4])

    def test_unexpected_address_rejected(self):
        code = {0: ('ld.w', 'r0, (r3, 0x18)', 2), 2: ('rts', '', 2)}
        with self.assertRaises(ValueError):
            execute(code, 0, 0, UartModel(0xa0100000, 0, [0x40], [0]))


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
        from verify_gx8002_uart_stage1_serial import LINKER_SCRIPT
        prefix = ROOT / 'build/csky-macos/install/bin'
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            c_obj = directory / 'serial_c.o'
            s_obj = directory / 'putsync_s.o'
            subprocess.run([str(prefix / 'csky-unknown-elf-gcc'), *SERIAL_FLAGS,
                            '-c', str(C_SOURCE), '-o', str(c_obj)], check=True)
            subprocess.run([str(prefix / 'csky-unknown-elf-as'), '-mcpu=ck804ef',
                            '-mhard-float', str(S_SOURCE), '-o', str(s_obj)], check=True)
            script = directory / 'serial.ld'
            script.write_text(LINKER_SCRIPT)
            linked = directory / 'serial.elf'
            subprocess.run([str(prefix / 'csky-unknown-elf-ld'), '-T', str(script),
                            str(c_obj), str(s_obj), '-o', str(linked)], check=True)
            elf = Elf32(linked.read_bytes(), str(linked))
            self.assertFalse(any(s['name'] and s['section'] == 0 for s in elf.symbols()))
            for symbol, _, offset, size, _, _ in SPECS:
                section = next(s for s in elf.sections if s['name'] == '.text.' + symbol)
                self.assertLessEqual(section['size'], size, symbol)
                self.assertEqual(offset % section['align'], 0, symbol)
                self.assertEqual(elf.relocations(section['index']), [], symbol)

    def test_assembled_put_sync_is_byte_identical(self):
        from build_transparent_image import Elf32
        prefix = ROOT / 'build/csky-macos/install/bin'
        with tempfile.TemporaryDirectory() as directory:
            s_obj = Path(directory) / 'putsync_s.o'
            subprocess.run([str(prefix / 'csky-unknown-elf-as'), '-mcpu=ck804ef',
                            '-mhard-float', str(S_SOURCE), '-o', str(s_obj)], check=True)
            elf = Elf32(s_obj.read_bytes(), str(s_obj))
            section = next(s for s in elf.sections
                           if s['name'] == '.text.open_cfw_gx8002_uart_stage1_put_sync')
            self.assertEqual(elf.contents(section), self.stock[0x5f0:0x5f0 + 36])


if __name__ == '__main__':
    unittest.main()
