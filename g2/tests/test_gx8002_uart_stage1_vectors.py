"""Host contract and regression tests for the UART stage-1 vectors/traps.

The full linked-image byte-exact check lives in
tools/verify_gx8002_uart_stage1_vectors.py (run by the candidate builder);
these tests pin the source structure, the linked placement/envelope
regression, and the trap loop property on macOS.
"""
import json
import re
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from verify_gx8002_uart_stage1_vectors import (
    ASM_FLAGS, SOURCE, NOTICE, SPECS, LINKER_SCRIPT, VECTORS_ADDRESS,
    TRAPS_ADDRESS, RESET_ENTRY)
from verify_gx8002_analog_source import sha
from analyze_gx8002_upstream_objects import IMAGE, IMAGE_SHA
from build_transparent_image import Elf32
from verify_gx8002_memcpy_source import decode

BASELINE = ROOT / 'docs/research/gx8002-uart-stage1-vectors-verification.json'


class SourceStructure(unittest.TestCase):
    """The .S must stay a three-address derivation, not a pasted dump."""

    @classmethod
    def setUpClass(cls):
        cls.text = SOURCE.read_text()

    def test_table_is_one_reset_word_plus_repeats(self):
        code = self.text.rsplit('*/', 1)[1]
        words = re.findall(r'\.word\s+(\S+)', code)
        # Three directive lines only: the .rept bodies expand at assembly.
        self.assertEqual(words, ['open_cfw_gx8002_uart_stage1_reset_entry',
                                 'open_cfw_gx8002_uart_stage1_exc_trap',
                                 'open_cfw_gx8002_uart_stage1_irq_trap'])
        self.assertEqual(code.count('.rept 31'), 1)
        self.assertEqual(code.count('.rept 32'), 1)

    def test_no_numeric_address_literals_in_table(self):
        code = self.text.rsplit('*/', 1)[1].split(
            '.size open_cfw_gx8002_uart_stage1_vectors')[0]
        self.assertNotIn('0x10000100', code)
        self.assertNotIn('0x10000130', code)
        self.assertNotIn('0x10000134', code)

    def test_traps_are_branch_to_self(self):
        traps = self.text.split(
            '.size open_cfw_gx8002_uart_stage1_vectors', 1)[1]
        self.assertEqual(traps.count('br open_cfw_gx8002_uart_stage1_exc_trap'), 1)
        self.assertEqual(traps.count('br open_cfw_gx8002_uart_stage1_irq_trap'), 1)

    def test_notice_exists_and_names_no_upstream_text(self):
        notice = NOTICE.read_text()
        self.assertIn('No upstream file is adapted or reproduced', notice)


class TargetLink(unittest.TestCase):
    """Assemble/link placement, envelope fit, and loop property."""

    @classmethod
    def setUpClass(cls):
        prefix = ROOT / 'build/csky-macos/install/bin'
        if not (prefix / 'csky-unknown-elf-as').exists():
            raise unittest.SkipTest('csky toolchain unavailable')
        cls.directory = tempfile.TemporaryDirectory(
            prefix='gx8002-stage1-vectors-')
        directory = Path(cls.directory.name)
        obj = directory / 'vectors.o'
        subprocess.run([str(prefix / 'csky-unknown-elf-as'), *ASM_FLAGS,
                        str(SOURCE), '-o', str(obj)], check=True)
        script = directory / 'vectors.ld'
        script.write_text(LINKER_SCRIPT.format(vectors=VECTORS_ADDRESS,
                                               traps=TRAPS_ADDRESS,
                                               reset=RESET_ENTRY))
        cls.linked = directory / 'vectors.elf'
        subprocess.run([str(prefix / 'csky-unknown-elf-ld'), '-T', str(script),
                        str(obj), '-o', str(cls.linked)], check=True)
        cls.elf = Elf32(cls.linked.read_bytes(), str(cls.linked))
        cls.prefix = prefix

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def test_sections_fit_and_bind_nothing(self):
        self.assertFalse(any(s['name'] and s['section'] == 0
                             for s in self.elf.symbols()))
        for symbol, section_name, _, offset, size, ownership in SPECS:
            section = next(s for s in self.elf.sections
                           if s['name'] == section_name)
            self.assertEqual(len(self.elf.contents(section)), size, symbol)
            self.assertEqual(offset % section['align'], 0, symbol)
            self.assertEqual(self.elf.relocations(section['index']), [],
                             symbol)
            executable = bool(section['flags'] & 4)
            self.assertEqual(executable, ownership == 'compiled_assembly',
                             symbol)

    def test_table_words_are_link_symbol_values(self):
        values = {s['name']: s['value'] for s in self.elf.symbols()}
        section = next(s for s in self.elf.sections
                       if s['name'].endswith('vectors'))
        words = struct.unpack('<64I', self.elf.contents(section))
        self.assertEqual(words[0], values[
            'open_cfw_gx8002_uart_stage1_reset_entry'])
        self.assertTrue(all(w == values[
            'open_cfw_gx8002_uart_stage1_exc_trap'] for w in words[1:32]))
        self.assertTrue(all(w == values[
            'open_cfw_gx8002_uart_stage1_irq_trap'] for w in words[32:64]))

    def test_traps_decode_as_self_loops(self):
        decoded = decode(subprocess.check_output(
            [str(self.prefix / 'csky-unknown-elf-objdump'), '-d',
             '--start-address=%#x' % TRAPS_ADDRESS,
             '--stop-address=%#x' % (TRAPS_ADDRESS + 8),
             str(self.linked)], text=True))
        for cell in (TRAPS_ADDRESS, TRAPS_ADDRESS + 4):
            op, operand, width = decoded[cell]
            self.assertEqual((op, int(operand, 0), width), ('br', cell, 2))


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
        for symbol, _, _, offset, size, _ in SPECS:
            want = by_symbol[symbol]['stock_occurrences'][0]['sha256']
            self.assertEqual(sha(self.stock[offset:offset + size]), want,
                             symbol)

    def test_linked_payloads_byte_exact(self):
        prefix = ROOT / 'build/csky-macos/install/bin'
        if not (prefix / 'csky-unknown-elf-as').exists():
            raise unittest.SkipTest('csky toolchain unavailable')
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            obj = directory / 'vectors.o'
            subprocess.run([str(prefix / 'csky-unknown-elf-as'), *ASM_FLAGS,
                            str(SOURCE), '-o', str(obj)], check=True)
            script = directory / 'vectors.ld'
            script.write_text(LINKER_SCRIPT.format(vectors=VECTORS_ADDRESS,
                                                   traps=TRAPS_ADDRESS,
                                                   reset=RESET_ENTRY))
            linked = directory / 'vectors.elf'
            subprocess.run([str(prefix / 'csky-unknown-elf-ld'),
                            '-T', str(script), str(obj), '-o', str(linked)],
                           check=True)
            elf = Elf32(linked.read_bytes(), str(linked))
            for symbol, section_name, _, offset, size, _ in SPECS:
                section = next(s for s in elf.sections
                               if s['name'] == section_name)
                self.assertEqual(elf.contents(section),
                                 self.stock[offset:offset + size], symbol)


if __name__ == '__main__':
    unittest.main()
