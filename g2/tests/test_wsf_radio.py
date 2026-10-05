"""Pinned source, stock identity and executable integration contracts."""
import csv,hashlib,json,pathlib,subprocess,unittest
ROOT=pathlib.Path(__file__).resolve().parents[2]
class WsfRadioEvidence(unittest.TestCase):
 def test_pinned_public_source_and_notice(self):
  p=json.loads((ROOT/'g2/components/foundation/wsf_radio/SOURCE_PROVENANCE.json').read_text())
  self.assertEqual(p['public_commit'],'3656312d6b73e2a2c1c8b33ee0385bc199dd97e6')
  for x in p['upstream_files']:
   file=ROOT/'g2/build/foundation/wsf-upstream'/pathlib.Path(x['path']).name if x['path']!='LICENSE.md' else ROOT/'g2/components/foundation/wsf_radio/LICENSE.md'
   if not file.exists():continue # public fetch cache is optional, manifest remains inspectable
   b=file.read_bytes();self.assertEqual(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest(),x['git_blob']);self.assertEqual(hashlib.sha256(b).hexdigest(),x['sha256'])
  source=(ROOT/'g2/components/foundation/wsf_radio/wsf_radio.c').read_text();self.assertIn('Copyright (c) 2009-2019 Arm Ltd.',source);self.assertIn('Copyright (c) 2019-2020 Packetcraft',source);self.assertTrue((ROOT/'g2/components/foundation/wsf_radio/LICENSE.md').is_file())
 def test_stock_bodies_match_authenticated_census(self):
  b=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();self.assertEqual(hashlib.sha256(b).hexdigest(),'36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863')
  rows={int(x['address'],16):x for x in csv.DictReader((ROOT/'g2/symbols/apollo_main.tsv').read_text().splitlines(),delimiter='\t')}
  for pc in [0x52b8a4,0x52b8b6,0x52b8d8,0x52b91e,0x52b95e,0x52b99e,0x52b9d0,0x4420bc]:
   x=rows[pc];n=int(x['size']);off=pc-0x438000+32;self.assertEqual(hashlib.sha256(b[off:off+n]).hexdigest(),x['stock_sha256'])
 def test_actual_wsf_and_radio_are_linked(self):
  p=ROOT/'g2/build/foundation/wsf-radio-simulator/wsf_radio.elf'
  if not p.exists():self.skipTest('WSF callable target not built')
  nm=subprocess.check_output(['arm-none-eabi-nm',str(p)],text=True)
  for n in ['opencfw_wsf_set_event','opencfw_wsf_dispatch','opencfw_wsf_wake','opencfw_wsf_cs_enter','opencfw_radio_scheduler_event','GPIO0_607F_IRQHandler','opencfw_radio_gpio_disable']:self.assertIn(' T '+n,nm)
  self.assertIn('wsf-radio-simulator-test: wsf-radio-simulator',(ROOT/'g2/Makefile').read_text())
 def test_optimized_verifier_is_rejected(self):
  p=subprocess.run(['python3','-O',str(ROOT/'g2/components/foundation/wsf_radio/simulator/verify.py')],capture_output=True,text=True);self.assertNotEqual(p.returncode,0);self.assertIn('optimized Python rejected',p.stderr)
