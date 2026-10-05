"""Pinned helper and actual omitted timer-daemon call-path identities."""
import hashlib,json,pathlib,re,subprocess,unittest
ROOT=pathlib.Path(__file__).resolve().parents[2]
COMP=ROOT/'g2/components/foundation/freertos_daemon'
class DaemonEvidence(unittest.TestCase):
 def test_pinned_copy_helper_and_license(self):
  p=json.loads((COMP/'SOURCE_PROVENANCE.json').read_text());raw=(COMP/'receive_copy.c').read_bytes();s=raw.decode()
  start=s.index('void prvCopyDataFromQueue(');i=s.index('{',start)+1;depth=1
  while depth:depth+=(s[i]=='{')-(s[i]=='}');i+=1
  self.assertEqual(hashlib.sha256(('static '+s[start:i]).encode()).hexdigest(),p['copied_helper_original_text_sha256'])
  self.assertIn(b'Copyright (C) 2021 Amazon.com',raw)
  self.assertEqual(p['upstream_commit'],'def7d2df2b0506d3d249334974f51e427c17a41c')
 def test_locked_receive_and_omitted_daemon(self):
  b=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes();self.assertEqual(hashlib.sha256(b).hexdigest(),'36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863')
  for a,n,h in [(0x441b0a,314,'f96de373691fb5d916ccbe25e0bc1d3474b918c16968b540b601fe6e36575560'),(0x441f5e,42,'d788663fd093a939ebf3f23edb08bf534bda42f1c31a181b9e7f20347db229cc'),(0x47e97a,278,'7b11858bca279a51a5b6b9565b9ba9b6c5da9eed337ef50206f57ac314f4257f'),(0x47e878,20,'9a7fd60775e97786baeb1ea1871423c63c5d744b5b8e1ce0c8176e8bb80d377a')]:
   off=a-0x438000+32;self.assertEqual(hashlib.sha256(b[off:off+n]).hexdigest(),h)
 def test_integrated_symbols_and_no_optimized_verification(self):
  elf=ROOT/'g2/build/foundation/timer-daemon-wsf-simulator/timer_daemon_wsf.elf'
  if elf.exists():
   nm=subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True)
   for n in ['opencfw_queue_receive_nowait','prvCopyDataFromQueue','opencfw_timer_callbacks_drain','opencfw_daemon_critical_enter','opencfw_daemon_critical_exit','xQueueGenericSendFromISR','vEventGroupSetBitsCallback','opencfw_wsf_dispatch']:self.assertIn(' T '+n,nm)
  p=subprocess.run(['python3','-O',str(COMP/'simulator/verify.py')],capture_output=True,text=True);self.assertNotEqual(p.returncode,0);self.assertIn('optimized Python rejected',p.stderr)
