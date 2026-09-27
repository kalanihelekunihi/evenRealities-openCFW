# SPDX-License-Identifier: MIT
"""Container/ownership tests; artificial replacement bytes are never flashed."""
import copy
import json
import struct
import sys
import unittest
import zlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from build_gx8002_source_candidate import compose, reviewed_replacements
from analyze_gx8002_upstream_objects import IMAGE, sha


class CodecCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not IMAGE.exists():
            raise unittest.SkipTest('authenticated codec oracle unavailable')
        cls.stock = IMAGE.read_bytes()

    def replacement(self, offset=12772):
        original = self.stock[offset:offset+32]
        fixture = bytes([original[0] ^ 1]) + original[1:]
        return {'package_offset': offset, 'bytes': 32, 'sha256': sha(original),
                'payload': fixture, 'compiled_sha256': sha(fixture), 'symbol': 'test_fixture'}

    def test_rebuild_updates_nested_checksums_and_closes_ownership(self):
        output, ownership, totals = compose(self.stock, [self.replacement(), self.replacement(95704)])
        self.assertEqual(sum(totals.values()), len(output))
        self.assertEqual(totals, {'compiled_c':64, 'compiled_assembly':0, 'generated_source_data':4092, 'generated_container_metadata':88,
                                  'retained_stock':321848, 'generated_unreachable_fill':0})
        self.assertEqual(struct.unpack_from('>I', output, 68)[0], sum(output[0x2850:0x958c]) & 0xffffffff)
        for offset in (16, 32):
            _, size, start, crc = struct.unpack_from('<IIII', output, offset)
            self.assertEqual(crc, zlib.crc32(output[start:start+size]) & 0xffffffff)
        for row in ownership:
            if row['kind'] == 'retained_stock':
                lo, hi = row['offset'], row['offset'] + row['size']
                self.assertEqual(output[lo:hi], self.stock[lo:hi])

    def test_assembly_is_not_counted_as_c(self):
        item = self.replacement()
        item['ownership_kind'] = 'compiled_assembly'
        _, ownership, totals = compose(self.stock, [item])
        self.assertEqual(totals['compiled_c'], 0)
        self.assertEqual(totals['compiled_assembly'], 32)
        self.assertTrue(any(row['kind']=='compiled_assembly' for row in ownership))

    def test_smaller_source_has_separate_fill_ownership(self):
        item = self.replacement()
        item['compiled_bytes'] = 28
        item['payload'] = item['payload'][:28] + bytes(4)
        item['compiled_sha256'] = sha(item['payload'][:28])
        _, ownership, totals = compose(self.stock, [item])
        self.assertEqual(totals['compiled_c'], 28)
        self.assertEqual(totals['generated_unreachable_fill'], 4)
        self.assertEqual(sum(r['size'] for r in ownership), len(self.stock))
        item['payload'] = item['payload'][:-1] + b'x'
        with self.assertRaisesRegex(ValueError, 'fill changed'):
            compose(self.stock, [item])

    def test_generated_data_is_separate_from_code_and_cannot_have_code_fill(self):
        item = self.replacement()
        item['ownership_kind'] = 'generated_source_data'
        _, ownership, totals = compose(self.stock, [item])
        self.assertEqual(totals['compiled_c'], 0)
        self.assertEqual(totals['generated_source_data'], 4124)
        self.assertTrue(any(row['kind']=='generated_source_data' and row.get('symbol')=='test_fixture'
                            and row['size']==32 for row in ownership))
        self.assertEqual(totals['generated_unreachable_fill'], 0)
        item['compiled_bytes'] = 28
        with self.assertRaisesRegex(ValueError, 'data replacement'):
            compose(self.stock, [item])
        item['ownership_kind'] = 'unsupported'
        with self.assertRaisesRegex(ValueError, 'unsupported source ownership'):
            compose(self.stock, [item])

    def test_overlap_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'overlapping'):
            compose(self.stock, [self.replacement(), self.replacement()])

    def test_changed_stock_or_payload_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'baseline changed'):
            compose(bytes(len(self.stock)), [])
        item = self.replacement()
        item['payload'] = bytes(32)
        with self.assertRaisesRegex(ValueError, 'payload changed'):
            compose(self.stock, [item])

    def test_unreviewed_qualification_is_rejected_before_object_read(self):
        with self.assertRaisesRegex(ValueError, 'differs from reviewed'):
            reviewed_replacements({'source_sha256':'new'}, {'source_sha256':'old'}, Path('/absent'), 'analog')


if __name__ == '__main__':
    unittest.main()
