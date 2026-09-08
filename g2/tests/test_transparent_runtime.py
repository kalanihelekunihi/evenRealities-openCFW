# SPDX-License-Identifier: MIT
"""Execute recovered p-code scalar helpers against independent integer oracles."""
import ctypes
import importlib.util
import json
import random
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / 'tools/transparent'


def load_tool(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f'tools/{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TransparentRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.clang = shutil.which('clang')
        if cls.clang is None:
            raise unittest.SkipTest('clang unavailable')
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        cls.source = Path(cls.temp.name) / 'helpers.c'
        cls.source.write_text('''#include "openg2_decompiled_runtime.h"
unsigned carry(uint32_t a, uint32_t b) { return CARRY4(a, b); }
unsigned scarry(uint32_t a, uint32_t b) { return SCARRY4(a, b); }
unsigned sborrow(uint32_t a, uint32_t b) { return SBORROW4(a, b); }
uint64_t concat13(uint8_t a, uint32_t b) { return CONCAT13(a, b); }
uint64_t concat15(uint8_t a, uint64_t b) { return CONCAT15(a, b); }
uint64_t concat16(uint8_t a, uint64_t b) { return CONCAT16(a, b); }
uint64_t concat17(uint8_t a, uint64_t b) { return CONCAT17(a, b); }
uint64_t concat26(uint16_t a, uint64_t b) { return CONCAT26(a, b); }
''')
        library = Path(cls.temp.name) / 'helpers.so'
        subprocess.run([cls.clang, '-shared', '-fPIC', '-O2', '-std=c11',
                        '-ffreestanding', '-fno-builtin', '-Wall', '-Wextra',
                        '-Werror', '-I', str(HEADER), str(cls.source), '-o',
                        str(library)], check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(library))
        for name in ('carry', 'scarry', 'sborrow'):
            fn = getattr(cls.lib, name)
            fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
            fn.restype = ctypes.c_uint
        for name, high, low in (
            ('concat13', ctypes.c_uint8, ctypes.c_uint32),
            ('concat15', ctypes.c_uint8, ctypes.c_uint64),
            ('concat16', ctypes.c_uint8, ctypes.c_uint64),
            ('concat17', ctypes.c_uint8, ctypes.c_uint64),
            ('concat26', ctypes.c_uint16, ctypes.c_uint64),
        ):
            fn = getattr(cls.lib, name)
            fn.argtypes = [high, low]
            fn.restype = ctypes.c_uint64

    def test_overflow_predicates_match_unbounded_integer_arithmetic(self):
        edge = (0, 1, 0x7ffffffe, 0x7fffffff, 0x80000000,
                0x80000001, 0xfffffffe, 0xffffffff)
        rng = random.Random(0x4732)
        pairs = [(a, b) for a in edge for b in edge]
        pairs += [(rng.getrandbits(32), rng.getrandbits(32)) for _ in range(10000)]
        def signed(value):
            return value if value < 2**31 else value - 2**32
        for a, b in pairs:
            x, y = signed(a), signed(b)
            self.assertEqual(self.lib.carry(a, b), a + b >= 2**32)
            self.assertEqual(self.lib.scarry(a, b), not -2**31 <= x + y < 2**31)
            self.assertEqual(self.lib.sborrow(a, b), not -2**31 <= x - y < 2**31)

    def test_odd_width_concat_masks_low_operand(self):
        rng = random.Random(0xC015)
        for name, high_bytes, low_bytes in (
            ('concat13', 1, 3), ('concat15', 1, 5), ('concat16', 1, 6),
            ('concat17', 1, 7), ('concat26', 2, 6),
        ):
            fn = getattr(self.lib, name)
            for a, b in [(0, 2**64-1), (1, 2**64-1)] + [
                (rng.getrandbits(high_bytes*8), rng.getrandbits(64))
                for _ in range(1000)
            ]:
                self.assertEqual(fn(a, b), (a << (low_bytes*8)) |
                                 (b & (2**(low_bytes*8)-1)), name)

    def test_cortex_m55_helpers_have_no_external_runtime_imports(self):
        image = load_tool('build_transparent_image')
        obj = Path(self.temp.name) / 'helpers.o'
        subprocess.run([self.clang, '--target=armv8.1m.main-none-eabi',
                        '-mcpu=cortex-m55', '-mthumb', '-mfloat-abi=soft',
                        '-Oz', '-ffreestanding', '-fno-builtin', '-I', str(HEADER),
                        '-c', str(self.source), '-o', str(obj)],
                       check=True, capture_output=True)
        elf = image.Elf32(obj.read_bytes(), str(obj))
        self.assertEqual([s['name'] for s in elf.symbols()
                          if s['section'] == 0 and s['name']], [])

    def test_recovered_consumers_compile_and_fit_stock_envelopes(self):
        harvest = ROOT / 'research/corpus/apollo-main/ghidra/decomp'
        if not (harvest / 'functions.jsonl').is_file():
            self.skipTest('harvested corpus unavailable')
        gen = load_tool('generate_transparent_source')
        image = load_tool('build_transparent_image')
        records = [json.loads(line) for line in
                   (harvest / 'functions.jsonl').read_text().splitlines()]
        signatures = {r['name']: r['signature'] for r in records}
        addresses = {r['name']: int(r['entry'], 16) | 1 for r in records}
        bodies = gen.load_bundles(harvest / 'bundles')
        by_entry = {int(r['entry'], 16): r for r in records}
        # Actual recovered callers collectively exercise all five added helpers.
        for entry in (0x44e79e, 0x47d870, 0x58fad2, 0x590e6c):
            with self.subTest(entry=hex(entry)):
                record = dict(by_entry[entry], entry=entry, tier='decompiled')
                text, disposition = gen.render_unit(record, bodies[entry], signatures)
                self.assertEqual(disposition, 'decompiled')
                source = Path(self.temp.name) / f'fn_{entry:x}.c'
                obj = source.with_suffix('.o')
                source.write_text(text)
                ok, error = gen.compile_unit(self.clang, source, obj, HEADER)
                self.assertTrue(ok, error)
                low, high = next((int(a, 16), int(b, 16)+1)
                                 for a, b in record['ranges']
                                 if int(a, 16) <= entry <= int(b, 16))
                payload, _ = image.place_unit(
                    image.Elf32(obj.read_bytes(), str(obj)), low, high-low, addresses)
                self.assertGreater(len(payload), 0)
                self.assertLessEqual(len(payload), high-low)


if __name__ == '__main__':
    unittest.main()
