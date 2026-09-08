# SPDX-License-Identifier: MIT
"""Named binary matches are evidence, never source ownership."""
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
import analyze_gx8002_upstream_objects as audit


class UpstreamObjectTests(unittest.TestCase):
    def test_matches_stay_within_authenticated_region(self):
        data = b'abcabcabc'
        self.assertEqual(list(audit.occurrences(data, b'abc', 1, 8)), [3])
        self.assertEqual(list(audit.occurrences(data, b'abc', 0, 9)), [0, 3, 6])

    def test_aliases_and_overlaps_do_not_inflate_byte_coverage(self):
        self.assertEqual(audit.covered_bytes([
            {'package_offset': 10, 'bytes': 20},
            {'package_offset': 10, 'bytes': 20},
            {'package_offset': 20, 'bytes': 30},
            {'package_offset': 60, 'bytes': 10},
        ]), 50)

    def test_mutated_upstream_object_is_rejected(self):
        data = b'reviewed test object'
        blob = hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'object.o'
            path.write_bytes(data)
            self.assertEqual(audit.authenticated_blob(path, blob), data)
            path.write_bytes(data + b'!')
            with self.assertRaises(audit.AuditError):
                audit.authenticated_blob(path, blob)

    def test_local_sdk_replays_checked_candidate_evidence(self):
        sdk = ROOT / 'build/upstream-nationalchip-lvp-kws'
        if not (sdk / '.git').is_dir() or not audit.IMAGE.is_file():
            self.skipTest('local SDK oracle or authenticated codec unavailable')
        actual = audit.analyze(sdk)
        checked = json.loads((ROOT / 'docs/research/gx8002-upstream-object-candidates.json').read_text())
        self.assertEqual(actual, checked)
        self.assertTrue(actual['candidate_only'])
        self.assertFalse(actual['source_admitted'])
        self.assertEqual(actual['firmware_bytes_emitted'], 0)
        self.assertEqual(actual['hardware_operations'], [])


if __name__ == '__main__':
    unittest.main()
