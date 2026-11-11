# SPDX-License-Identifier: MIT
import importlib.util
import contextlib
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

spec = importlib.util.spec_from_file_location('sources', Path(__file__).with_name('sources.py'))
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)


class SourcesTest(unittest.TestCase):
    @unittest.skipUnless(shutil.which('clang') and shutil.which('arm-none-eabi-ld'), 'ARM tools not available')
    def test_retained_roots_keep_dependencies_and_drop_duplicate_provider(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path, args = self.build_fixture(root)
            (root / 'sample.c').write_text(
                'int state; extern int needed(int); extern int discarded(void);\n'
                'int helper(void) { return needed(++state); }\n'
                'int firmware_entry(void) { return helper(); }\n'
                'int duplicate(void) { return discarded(); }\n')
            (root / 'other.c').write_text('int duplicate(void) { return 7; }\n')
            manifest = json.loads(path.read_text())
            manifest['profiles']['arm'] += ['-ffunction-sections', '-fdata-sections']
            manifest['units'][0]['retain'] = {'linker': shutil.which('arm-none-eabi-ld'),
                                             'symbols': ['firmware_entry']}
            manifest['units'].append({'source': 'other.c', 'payload': 'fixture',
                                      'toolchain': 'clang', 'profile': 'arm'})
            manifest['payloads'] = {'fixture': {'compose': {'toolchain': 'clang',
                'ld': shutil.which('arm-none-eabi-ld')}}}
            path.write_text(json.dumps(manifest))
            with mock.patch.object(s, 'ROOT', root), contextlib.redirect_stdout(io.StringIO()):
                result = s.build(args)
            data = json.loads((args.out / 'report.json').read_text())['devices']['fixture']
            unit = next(u for u in data['units'] if u['source'] == 'sample.c')
            self.assertEqual(result, 0)
            self.assertIn('duplicate', unit['compiler_symbols']['strong'])
            self.assertNotIn('duplicate', unit['strong'])
            self.assertEqual(set(unit['strong']), {'firmware_entry', 'helper', 'state'})
            self.assertEqual(unit['undefined'], ['needed'])
            self.assertTrue(Path(unit['compiler_object']).is_file())
            self.assertNotEqual(unit['object'], unit['compiler_object'])
            self.assertEqual(data['payloads']['fixture']['compose']['undefined'], ['needed'])

    @unittest.skipUnless(shutil.which('clang') and shutil.which('arm-none-eabi-ld'), 'ARM tools not available')
    def test_retained_root_failure_never_publishes_full_object(self):
        for linker, symbols in [(shutil.which('arm-none-eabi-ld'), ['missing']),
                                ('/nonexistent/retained-root-linker', ['firmware_entry']),
                                (shutil.which('true'), ['firmware_entry'])]:
            with self.subTest(linker=linker, symbols=symbols), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                path, args = self.build_fixture(root)
                manifest = json.loads(path.read_text())
                manifest['units'][0]['retain'] = {'linker': linker, 'symbols': symbols}
                path.write_text(json.dumps(manifest))
                with mock.patch.object(s, 'ROOT', root), contextlib.redirect_stdout(io.StringIO()):
                    result = s.build(args)
                unit = json.loads((args.out / 'report.json').read_text())['devices']['fixture']['units'][0]
                self.assertEqual(result, 1)
                self.assertEqual(unit['returncode'], 125)
                self.assertNotIn('object', unit)
                self.assertEqual(unit['strong'], [])
                self.assertTrue(Path(unit['compiler_object']).is_file())

    @unittest.skipUnless(shutil.which('clang') and shutil.which('arm-none-eabi-ld'), 'ARM tools not available')
    def test_unresolved_count_uses_composed_symbols_after_linker_aliases(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path, args = self.build_fixture(root)
            (root / 'sample.c').write_text('extern int alias(void);\n'
                'int provider(void) { return 7; }\nint firmware_entry(void) { return alias(); }\n')
            manifest = json.loads(path.read_text())
            manifest['payloads'] = {'fixture': {'compose': {'toolchain': 'clang',
                'ld': shutil.which('arm-none-eabi-ld'), 'defsym': {'alias': 'provider'}}}}
            path.write_text(json.dumps(manifest))
            with mock.patch.object(s, 'ROOT', root), contextlib.redirect_stdout(io.StringIO()):
                result = s.build(args)
            payload = json.loads((args.out / 'report.json').read_text())['devices']['fixture']['payloads']['fixture']
            self.assertEqual(result, 0)
            self.assertEqual(payload['object_unresolved_symbols'], 1)
            self.assertEqual(payload['composed_unresolved_symbols'], 0)
            self.assertEqual(payload['unresolved_symbols'], 0)
            self.assertEqual(payload['unresolved_scope'], 'composed')

    @unittest.skipUnless(shutil.which('clang'), 'clang not available')
    def test_skipped_composition_reports_object_scope_not_resolved_aliases(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path, args = self.build_fixture(root)
            (root / 'sample.c').write_text('extern int missing(void);\nint firmware_entry(void) { return missing(); }\n')
            args.no_compose = True
            with mock.patch.object(s, 'ROOT', root), contextlib.redirect_stdout(io.StringIO()):
                result = s.build(args)
            payload = json.loads((args.out / 'report.json').read_text())['devices']['fixture']['payloads']['fixture']
            self.assertEqual(result, 0)
            self.assertEqual(payload['object_unresolved_symbols'], 1)
            self.assertIsNone(payload['composed_unresolved_symbols'])
            self.assertEqual(payload['unresolved_symbols'], 1)
            self.assertEqual(payload['unresolved_scope'], 'objects')

    def test_compiler_success_with_uninspectable_object_is_a_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source, obj = root / 'sample.c', root / 'sample.o'
            source.write_text('int sample;\n')
            obj.write_bytes(b'not an ELF32 object')
            unit = {'source': str(source), 'payload': 'fixture', 'toolchain': 'clang'}
            row = s.finish(unit, obj, ['clang'], 0, '', root)
            self.assertEqual(row['returncode'], 125)
            self.assertIn('ELF32', row['symbol_error'])

    def build_fixture(self, root, *, compose=False):
        source = root / 'sample.c'
        source.write_text('int firmware_entry(void) { return 7; }\n')
        manifest = {'toolchains': {'clang': {'cc': 'clang'}},
                    'profiles': {'arm': ['--target=arm-none-eabi', '-mcpu=cortex-m4', '-mthumb']},
                    'units': [{'source': 'sample.c', 'payload': 'fixture',
                               'toolchain': 'clang', 'profile': 'arm'}]}
        if compose:
            manifest['payloads'] = {'fixture': {'compose': {'toolchain': 'clang', 'ld': shutil.which('false')}}}
        path = root / 'fixture/src/sources.json'
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps(manifest))
        args = SimpleNamespace(devices=['fixture'], out=root / 'out', payload=None,
                               jobs=1, no_compose=False)
        return path, args

    @unittest.skipUnless(shutil.which('clang') and shutil.which('false'), 'clang/false not available')
    def test_compile_success_does_not_hide_relocatable_link_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _, args = self.build_fixture(root, compose=True)
            output = io.StringIO()
            with mock.patch.object(s, 'ROOT', root), contextlib.redirect_stdout(output):
                result = s.build(args)
            report = json.loads((args.out / 'report.json').read_text())
            payload = report['devices']['fixture']['payloads']['fixture']
            self.assertEqual(payload['compiled'], 1)
            self.assertEqual(payload['failed'], [])
            self.assertEqual(payload['compose']['returncode'], 1)
            self.assertEqual(result, 1)
            self.assertIn('relocatable link failed', output.getvalue())
            self.assertIn('unresolved: FAILED', output.getvalue())

    @unittest.skipUnless(shutil.which('clang'), 'clang not available')
    def test_manifest_change_fails_and_keeps_original_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path, args = self.build_fixture(root)
            original_hash = hashlib.sha256(path.read_bytes()).hexdigest()
            compile_host = s.compile_host
            def mutate_after_compile(*pos, **kwargs):
                result = compile_host(*pos, **kwargs)
                path.write_text(path.read_text() + '\n')
                return result
            with mock.patch.object(s, 'ROOT', root), mock.patch.object(s, 'compile_host', mutate_after_compile), \
                    contextlib.redirect_stdout(io.StringIO()):
                result = s.build(args)
            device = json.loads((args.out / 'report.json').read_text())['devices']['fixture']
            self.assertEqual(result, 1)
            self.assertEqual(device['manifest_sha256'], original_hash)
            self.assertTrue(device['manifest_changed_during_build'])

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
