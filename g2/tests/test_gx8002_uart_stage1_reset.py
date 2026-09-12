"""Host contract and regression tests for the UART stage-1 reset entry.

The full link-and-decode qualification lives in
tools/verify_gx8002_uart_stage1_reset.py (run by the candidate builder);
these tests pin the interpreter semantics, the stock envelope, and the
byte-exact placement on macOS.
"""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from verify_gx8002_uart_stage1_reset import (
    ENTRY_ADDRESS,
    ENTRY_SIZE,
    INITIAL_STACK,
    INIT_ADDRESS,
    PACKAGE_OFFSET,
    STAGE2_ADDRESS,
    VECTORS_ADDRESS,
    execute,
    oracle,
    verify,
)
from verify_gx8002_memcpy_source import decode
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA, sha

BASELINE = ROOT / 'docs/research/gx8002-uart-stage1-reset-verification.json'
PREFIX = ROOT / 'build/csky-macos/install/bin'


def synthetic_body(calls=(INIT_ADDRESS, STAGE2_ADDRESS), stack=INITIAL_STACK,
                   vbr=VECTORS_ADDRESS):
    lines = [
        '%x: 1009 lrw r0, 0x80000200' % ENTRY_ADDRESS,
        '%x: c0006420 mtcr r0, cr<0, 0>' % (ENTRY_ADDRESS + 2),
        '%x: c01f6021 mfcr r1, cr<31, 0>' % (ENTRY_ADDRESS + 6),
        '%x: 3983 bclri r1, 3' % (ENTRY_ADDRESS + 10),
        '%x: c001643f mtcr r1, cr<31, 0>' % (ENTRY_ADDRESS + 12),
        '%x: 1006 lrw r0, %#x' % (ENTRY_ADDRESS + 16, vbr),
        '%x: c0006421 mtcr r0, cr<1, 0>' % (ENTRY_ADDRESS + 18),
        '%x: 1006 lrw r0, %#x' % (ENTRY_ADDRESS + 22, stack),
        '%x: 6f83 mov r14, r0' % (ENTRY_ADDRESS + 24),
    ]
    pc = ENTRY_ADDRESS + 26
    for target in calls:
        lines.append('%x: e0000000 bsr %#x' % (pc, target))
        pc += 4
    return decode('\n'.join(lines))


class InterpreterContract(unittest.TestCase):
    def test_happy_path_matches_oracle(self):
        for control in (0, 0xffffffff, 0x55555555, 0xa5a5a5a5):
            for seed in (0, 0x12345678):
                self.assertEqual(execute(synthetic_body(), control, seed),
                                 oracle(control))

    def test_wrong_vector_base_rejected(self):
        with self.assertRaisesRegex(ValueError, 'trace mismatch|unexpected'):
            trace = execute(synthetic_body(vbr=0x20000000), 0, 0)
            if trace != oracle(0):
                raise ValueError('trace mismatch')

    def test_wrong_stack_rejected(self):
        with self.assertRaisesRegex(ValueError, 'reset stack'):
            execute(synthetic_body(stack=0x20000000), 0, 0)

    def test_unknown_call_target_rejected(self):
        with self.assertRaisesRegex(ValueError, 'unexpected call target'):
            execute(synthetic_body(calls=(INIT_ADDRESS, 0x10002000)), 0, 0)

    def test_unexpected_instruction_rejected(self):
        code = synthetic_body()
        code[ENTRY_ADDRESS + 2] = ('ld.w', 'r0, (r1, 0x0)', 2)
        with self.assertRaisesRegex(ValueError, 'unexpected instruction'):
            execute(code, 0, 0)


class StockEnvelopeRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not IMAGE.exists():
            raise unittest.SkipTest('authenticated codec oracle unavailable')
        cls.stock = IMAGE.read_bytes()
        if sha(cls.stock) != IMAGE_SHA:
            raise unittest.SkipTest('stock identity changed')
        cls.baseline = json.loads(BASELINE.read_text())

    def test_stock_envelope_unchanged(self):
        want = self.baseline['functions'][0]['stock_occurrences'][0]['sha256']
        self.assertEqual(
            sha(self.stock[PACKAGE_OFFSET:PACKAGE_OFFSET + ENTRY_SIZE]), want)

    def test_envelope_layout(self):
        span = self.stock[PACKAGE_OFFSET:PACKAGE_OFFSET + ENTRY_SIZE]
        self.assertEqual(len(span), 48)
        # Literal pool: PSR value, vector base, initial stack.
        self.assertEqual(span[36:40].hex(), '00020080')
        self.assertEqual(span[40:44].hex(), '00000010')
        self.assertEqual(span[44:48].hex(), 'fc270020')


class PlacementRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not (PREFIX / 'csky-unknown-elf-gcc').exists():
            raise unittest.SkipTest('C-SKY toolchain unavailable')

    def test_linked_candidate_byte_exact(self):
        directory = Path(tempfile.mkdtemp(prefix='gx8002-stage1-reset-'))
        try:
            report = verify(output=directory)
        finally:
            shutil.rmtree(directory, ignore_errors=True)
        baseline = json.loads(BASELINE.read_text())
        self.assertEqual(report, baseline)
        occurrence = report['functions'][0]['stock_occurrences'][0]
        self.assertEqual((occurrence['package_offset'], occurrence['bytes']),
                         (PACKAGE_OFFSET, ENTRY_SIZE))
        self.assertEqual(PACKAGE_OFFSET % 4, 0)


if __name__ == '__main__':
    unittest.main()
