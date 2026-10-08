import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import candidate_descriptor as cd

class HeldOutDescriptorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = (cd.ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
        cls.candidate = cd.load_candidate()

    def test_real_held_out_firmware_candidate_is_bounded_and_authenticated(self):
        result = cd.validate_candidate(self.payload, self.candidate)
        self.assertEqual(result['descriptor_runtime'], '0x7682b0')
        self.assertEqual(result['dimensions'], [55, 48])
        self.assertEqual(result['pixel_payload_range'], [2373520, 2376160])
        self.assertEqual(result['pointer_references'], [{'payload_offset': 0x187944, 'runtime_address': '0x5bf924', 'value': '0x7682b0'}])
        self.assertIn('remains unresolved', result['coverage_effect'])
        self.assertEqual(result['pixel_sha256'], '4dd38f91cc1baedbaa1454f873f02d8931148b185d32c27dcb7d347d9f63b429')

    def test_wrong_descriptor_offset_rejected(self):
        candidate = copy.deepcopy(self.candidate)
        candidate['descriptor_payload_offset'] += 28
        with self.assertRaisesRegex(ValueError, 'descriptor address-domain mismatch'):
            cd.validate_candidate(self.payload, candidate)

    def test_wrong_pointer_reference_value_rejected(self):
        candidate = copy.deepcopy(self.candidate)
        candidate['pointer_reference_payload_offsets'] = [0x187940]
        with self.assertRaisesRegex(ValueError, 'pointer reference value mismatch'):
            cd.validate_candidate(self.payload, candidate)

    def test_wrong_layout_rejected(self):
        damaged = bytearray(self.payload)
        damaged[self.candidate['descriptor_payload_offset']+1] = 7
        with self.assertRaisesRegex(ValueError, 'unsupported descriptor layout'):
            cd.validate_descriptor(bytes(damaged), self.candidate)

    def test_wrong_extent_rejected(self):
        candidate = copy.deepcopy(self.candidate)
        candidate['data_payload_range'][1] -= 1
        with self.assertRaisesRegex(ValueError, 'descriptor extent/pointer mismatch'):
            cd.validate_candidate(self.payload, candidate)

    def test_wrong_candidate_address_rejected(self):
        candidate = copy.deepcopy(self.candidate)
        candidate['descriptor_runtime'] += 28
        with self.assertRaisesRegex(ValueError, 'candidate identity mismatch'):
            cd.validate_candidate(self.payload, candidate)

    def test_wrong_payload_rejected(self):
        damaged = bytearray(self.payload)
        damaged[0] ^= 1
        with self.assertRaisesRegex(ValueError, 'authenticated payload hash mismatch'):
            cd.validate_candidate(bytes(damaged), self.candidate)

if __name__ == '__main__':
    unittest.main()
