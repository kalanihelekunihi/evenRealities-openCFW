# SPDX-License-Identifier: MIT
"""Reviewed source admission, CMSIS ordering, and fail-closed image contracts."""
import copy
import ctypes
import hashlib
import importlib.util
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_tool(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f'tools/{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReviewedSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gen = load_tool('generate_transparent_source')
        cls.image = load_tool('build_transparent_image')
        cls.ledger = load_tool('report_transparent_coverage')
        cls.manifest = json.loads(cls.gen.REVIEWED_SOURCES.read_text())
        cls.database = {'image': {'path': 'blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin',
                                  'load_base': 0x437fe0},
                        'functions': [{'entry': r['entry'], 'ranges': [[r['entry'], r['end']]],
                                       'ghidra_name': r['function']}
                                      for r in cls.manifest['functions']]}
        cls.clang = shutil.which('clang')
        if not cls.clang:
            raise unittest.SkipTest('clang unavailable')
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        cls.directory = Path(cls.temp.name)
        # Host simulation models only CMSIS's observable operation boundaries.
        (cls.directory / 'cmsis_gcc.h').write_text('''#include <stdint.h>
extern uint32_t test_word, test_ipsr, test_psp, test_snapshot, test_barriers;
static inline void __DMB(void) {
    test_snapshot = test_word;
    test_word = 0x11223344;
    ++test_barriers;
}
static inline uint32_t __get_IPSR(void) { return test_ipsr; }
static inline uint32_t __get_PSP(void) { return test_psp; }
''')
        glue = cls.directory / 'glue.c'
        glue.write_text('#include <stdint.h>\nuint32_t test_word, test_ipsr, test_psp, test_snapshot, test_barriers;\n')
        lib = cls.directory / 'reviewed.so'
        subprocess.run([cls.clang, '-shared', '-fPIC', '-std=c11', '-O2',
                        '-Wall', '-Wextra', '-Werror', '-I', str(cls.directory),
                        *(str(ROOT / r['source']['path']) for r in cls.manifest['functions']),
                        str(glue), '-o', str(lib)], check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(lib))
        cls.word = ctypes.c_uint32.in_dll(cls.lib, 'test_word')
        cls.ipsr = ctypes.c_uint32.in_dll(cls.lib, 'test_ipsr')
        cls.psp = ctypes.c_uint32.in_dll(cls.lib, 'test_psp')
        cls.snapshot = ctypes.c_uint32.in_dll(cls.lib, 'test_snapshot')
        cls.barriers = ctypes.c_uint32.in_dll(cls.lib, 'test_barriers')
        cls.lib.FUN_004488f4.argtypes = [ctypes.POINTER(ctypes.c_uint32)]
        cls.lib.FUN_004488f4.restype = ctypes.c_uint32
        cls.lib.FUN_004488ec.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.c_uint32]
        cls.lib.FUN_004488ec.restype = None
        cls.lib.FUN_00442228.argtypes = []
        cls.lib.FUN_00442228.restype = ctypes.c_bool
        cls.lib.FUN_005939a0.argtypes = []
        cls.lib.FUN_005939a0.restype = ctypes.c_uint32

    def test_atomic_load_occurs_before_barrier(self):
        self.word.value = 0xaabbccdd
        self.barriers.value = 0
        self.assertEqual(self.lib.FUN_004488f4(ctypes.byref(self.word)), 0xaabbccdd)
        self.assertEqual(self.snapshot.value, 0xaabbccdd)
        self.assertEqual(self.word.value, 0x11223344)
        self.assertEqual(self.barriers.value, 1)

    def test_atomic_store_occurs_before_barrier(self):
        self.word.value = 0
        self.barriers.value = 0
        self.lib.FUN_004488ec(ctypes.byref(self.word), 0x12345678)
        self.assertEqual(self.snapshot.value, 0x12345678)
        self.assertEqual(self.barriers.value, 1)

    def test_exception_check_keeps_all_ipsr_bits(self):
        for value in range(512):
            self.ipsr.value = value
            self.assertEqual(self.lib.FUN_00442228(), value != 0, value)

    def test_psp_is_read_without_truncation_or_mutation(self):
        for value in (0, 0x20000000, 0x20003ff8, 0xfffffff8):
            self.psp.value = value
            self.assertEqual(self.lib.FUN_005939a0(), value)
            self.assertEqual(self.psp.value, value)

    def test_source_dependencies_and_stock_intervals_authenticate(self):
        blob = ROOT / self.database['image']['path']
        if not blob.is_file():
            self.skipTest('authenticated firmware unavailable')
        reviewed, dependencies = self.gen.load_reviewed_sources(self.database)
        self.assertEqual(len(reviewed), 4)
        self.assertIn('CMSIS_LICENSE.txt', dependencies)
        raw = blob.read_bytes()
        for entry, row in reviewed.items():
            obj = self.directory / f'{entry:x}.o'
            ok, error = self.gen.compile_unit(self.clang, ROOT / row['source']['path'], obj,
                                             ROOT / 'third_party/cmsis-core/CMSIS/Core/Include')
            self.assertTrue(ok, error)
            payload, _ = self.image.place_unit(self.image.Elf32(obj.read_bytes(), str(obj)),
                                               entry, row['end']-entry, {})
            unit = {'entry': entry, 'disposition': 'reviewed-source', 'reviewed_source': row}
            self.assertTrue(self.image.validate_reviewed_payload(unit, payload))
            if entry != 0x442228:
                self.assertEqual(payload, raw[entry-0x437fe0:row['end']-0x437fe0])

    def test_changed_source_dependency_firmware_or_boundary_is_rejected(self):
        if not (ROOT / self.database['image']['path']).is_file():
            self.skipTest('authenticated firmware unavailable')
        for kind in ('source', 'dependency', 'firmware', 'boundary', 'duplicate', 'escape'):
            with self.subTest(kind=kind):
                manifest = copy.deepcopy(self.manifest)
                if kind == 'source':
                    manifest['functions'][0]['source']['sha256'] = '0'*64
                elif kind == 'dependency':
                    manifest['dependencies'][0]['sha256'] = '0'*64
                elif kind == 'firmware':
                    manifest['firmware_sha256'] = '0'*64
                elif kind == 'boundary':
                    manifest['functions'][0]['end'] += 2
                elif kind == 'duplicate':
                    manifest['functions'].append(manifest['functions'][0])
                else:
                    manifest['dependencies'][0]['output'] = '../escape.h'
                path = self.directory / 'bad.json'
                path.write_text(json.dumps(manifest))
                with self.assertRaises(self.gen.GenerateError):
                    self.gen.load_reviewed_sources(self.database, path)

    def test_reviewed_text_cannot_silently_become_a_trap_or_changed_code(self):
        payload = b'\x70\x47'
        unit = {'entry': 0x1234, 'disposition': 'reviewed-source', 'reviewed_source': {
            'expected_text': {'size': 2, 'sha256': hashlib.sha256(payload).hexdigest()}}}
        self.assertTrue(self.image.validate_reviewed_payload(unit, payload))
        for bad in (None, b'\x00\xbe', payload + b'\x00\x00'):
            with self.assertRaises(self.image.ImageError):
                self.image.validate_reviewed_payload(unit, bad)

    def test_compilation_without_behavior_review_does_not_pass_readiness(self):
        summary = {'opaque_bytes': 0, 'trapped_bytes': 0, 'declared_data_bytes': 0,
                   'units_compiled': 10, 'units_total': 10, 'units_placed': 10}
        self.assertTrue(any('unreviewed' in x for x in
                            self.ledger.release_readiness_blockers(summary)))
        summary['unreviewed_code_units'] = 0
        self.assertEqual(self.ledger.release_readiness_blockers(summary), [])


if __name__ == '__main__':
    unittest.main()
