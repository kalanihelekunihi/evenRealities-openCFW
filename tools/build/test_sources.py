# SPDX-License-Identifier: MIT
import importlib.util
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('sources', Path(__file__).with_name('sources.py'))
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)


class SourcesTest(unittest.TestCase):
    def test_generate_patches_exactly_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            vendor = root / 'vendor.h'
            vendor.write_text('ldr r12, =%0\n')
            rel = str(vendor.relative_to(s.ROOT)) if vendor.is_relative_to(s.ROOT) else str(vendor)
            manifest = {'generated': [{'output': 'patched.h', 'from': rel,
                                       'replace': [['ldr r12, =%0', 'ldr r12, =%c0']]}]}
            rows = s.generate(manifest, root / 'gen')
            self.assertEqual((root / 'gen/patched.h').read_text(), 'ldr r12, =%c0\n')
            self.assertEqual(rows[0]['output'], 'patched.h')
            vendor.write_text('no anchor here\n')
            with self.assertRaises(RuntimeError):
                s.generate(manifest, root / 'gen')

    def test_generated_sources_resolve_under_gen(self):
        unit = {'source': '{gen}/app.c'}
        self.assertEqual(s.source_path(unit, Path('/x/gen')), Path('/x/gen/app.c'))
        self.assertEqual(s.source_path({'source': 'g2/src/a.c'}, Path('/x')), s.ROOT / 'g2/src/a.c')
        self.assertEqual(s.object_name('{gen}/app.c'), 'generated__app.c.o')

    def test_units_inherit_payload_defaults(self):
        manifest = {'defaults': {'p': {'link': False}}, 'units': [
            {'source': 'a.c', 'payload': 'p'}, {'source': 'b.c', 'payload': 'q', 'link': True}]}
        units = list(s.units_of(manifest))
        self.assertFalse(units[0]['link'])
        self.assertTrue(units[1]['link'])
        self.assertEqual([u['source'] for u in s.units_of(manifest, 'q')], ['b.c'])

    @unittest.skipUnless(shutil.which('clang'), 'clang not available')
    def test_elf_symbols_split_strong_weak_and_undefined(self):
        with tempfile.TemporaryDirectory() as tmp:
            src, obj = Path(tmp) / 'u.c', Path(tmp) / 'u.o'
            src.write_text('extern int ext(void);\n__attribute__((weak)) int w(void){return 1;}\n'
                           'int strong(void){return ext();}\nstatic int local(void){return 2;}\n'
                           'int use_local(void){return local();}\n')
            done = subprocess.run(['clang', '--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb', '-O1',
                                   '-c', str(src), '-o', str(obj)], capture_output=True)
            if done.returncode:
                self.skipTest('clang lacks the ARM target')
            symbols = s.elf_symbols(obj)
            self.assertEqual(symbols['strong'], ['strong', 'use_local'])
            self.assertEqual(symbols['weak'], ['w'])
            self.assertEqual(symbols['undefined'], ['ext'])


if __name__ == '__main__':
    unittest.main()
