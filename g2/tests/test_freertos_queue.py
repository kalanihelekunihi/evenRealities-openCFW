"""Pinned queue producer lineage and integrated ARM32 executable evidence."""
import hashlib,json,pathlib,re,subprocess,unittest
ROOT=pathlib.Path(__file__).resolve().parents[2]
COMP=ROOT/'g2/components/foundation/freertos_queue'
class QueueEvidence(unittest.TestCase):
 def test_exact_pinned_source_text(self):
  p=json.loads((COMP/'SOURCE_PROVENANCE.json').read_text());raw=(COMP/'queue_subset.c').read_bytes();s=raw.decode()
  self.assertIn(b'Copyright (C) 2021 Amazon.com',raw)
  for name,h in p['unchanged_function_text_sha256'].items():
   start=list(re.finditer(r'(?:static )?BaseType_t '+name+r'\(',s))[-1].start();brace=s.index('{',start);depth=1;i=brace+1
   while depth:depth+=(s[i]=='{')-(s[i]=='}');i+=1
   self.assertEqual(hashlib.sha256(s[start:i].encode()).hexdigest(),h)
  upstream=ROOT/'g2/build/foundation/freertos-upstream/queue.c'
  if upstream.exists():
   b=upstream.read_bytes();self.assertEqual(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest(),p['queue_c_git_blob'])
 def test_locked_queue_instruction_identities(self):
  raw=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
  self.assertEqual(hashlib.sha256(raw).hexdigest(),'36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863')
  for pc,n,h in [(0x441952,240,'09caa940da5c5337919aec35f7e3f4e2068558df48ca9ce430daaddf1e9deb08'),(0x441ed8,134,'35c79bf50852c5f61d579981278509aa156ab8e18f57b4b6d6b7a88563682e36'),(0x5fa0a4,22,'f6bd0708e653c8e8880e33e298f9dc8ede1305c9386ea4ca5ff554d4022dc323'),(0x5fa0ba,14,'97532a7902b38e1551198dd647d0fcdc3a6f19315b6491058a813c7643e0028a')]:
   off=pc-0x438000+32;self.assertEqual(hashlib.sha256(raw[off:off+n]).hexdigest(),h)
 def test_integrated_symbols_and_assertions_enabled(self):
  elf=ROOT/'g2/build/foundation/timer-queue-wsf-simulator/timer_queue_wsf.elf'
  if elf.exists():
   nm=subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True)
   for n in ['xQueueGenericSendFromISR','opencfw_queue_memcpy','opencfw_queue_mask_set','opencfw_queue_mask_restore','xEventGroupSetBitsFromISR','opencfw_wsf_set_event','GPIO0_607F_IRQHandler']:self.assertIn(' T '+n,nm)
  p=subprocess.run(['python3','-O',str(COMP/'simulator/verify.py')],capture_output=True,text=True);self.assertNotEqual(p.returncode,0);self.assertIn('optimized Python rejected',p.stderr)
