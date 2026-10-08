import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import resource_metadata as rm

ROOT = Path(__file__).resolve().parents[5]

class ResourceMetadataTests(unittest.TestCase):
    def test_authenticates_and_exports_only_previously_mapped_ranges(self):
        payload = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / 'out'
            result = rm.export_metadata(payload, out)
            self.assertEqual(len(result['assets']), 6)
            self.assertTrue(all(a['classification_status'].startswith('prior evidence') for a in result['assets']))
            for asset in result['assets']:
                raw = (out / asset['file']).read_bytes()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), asset['sha256'])
                self.assertEqual(len(raw), asset['width'] * asset['height'])
            self.assertEqual(sum((out/a['file']).stat().st_size for a in result['assets']), 28872)

    def test_rejects_modified_source_bytes(self):
        spec = rm.load_l8_map()
        payload = bytearray(spec['payload_size'])
        with self.assertRaisesRegex(ValueError, 'payload identity mismatch'):
            rm.validate_payload(bytes(payload), spec)

    def test_map_records_dependency_and_license_claim_limits(self):
        deps = json.loads((Path(__file__).with_name('dependency-map.json')).read_text())['dependencies']
        by_name = {item['name']: item for item in deps}
        self.assertIn('hybrid 9.3-development', by_name['LVGL core']['source_status'])
        self.assertEqual(by_name['Ambiq LVGL draw backend']['source_pin'], '1e774257495fa43177e04fc5c8a42a77c2d7d619')
        self.assertEqual(by_name['Google liblc3']['source_pin'], '96a3af0beb5487aca3b98a4b992a539a1f6d80d1')
        self.assertIn('No complete proprietary C', by_name['NemaGFX/NemaVG SDK']['claim_limit'])
        self.assertIn('not supplied', by_name['Official resource payload']['source_status'])

if __name__ == '__main__':
    unittest.main()
