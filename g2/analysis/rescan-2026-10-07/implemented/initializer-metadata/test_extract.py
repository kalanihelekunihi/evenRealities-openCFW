import unittest
from pathlib import Path
import extract
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.blob=(extract.ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin').read_bytes()
 def test_real_table(self):
  d=extract.extract(self.blob);self.assertEqual(d['runner_capped_count'],4);self.assertEqual({int(r['callback_thumb_address'],16) for r in d['records']},set(extract.KNOWN));self.assertTrue(all(r['target_present_in_ota'] for r in d['records']))
 def test_changed_image(self):
  b=bytearray(self.blob);b[0]^=1
  with self.assertRaisesRegex(ValueError,'identity'):extract.extract(b)
 def test_bad_record_stride(self):
  with self.assertRaisesRegex(ValueError,'extent'):extract.extract(self.blob,end=0x43345f)
 def test_outside_image(self):
  with self.assertRaisesRegex(ValueError,'extent'):extract.extract(self.blob,end=0x500000)
 def test_runner_cap(self):self.assertEqual(extract.extract(self.blob,0x433440,0x433440+257*8)['runner_capped_count'],256)
if __name__=='__main__':unittest.main()
