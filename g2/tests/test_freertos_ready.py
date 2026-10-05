"""Pinned ready-provider text, original identities and linked ABI evidence."""
import hashlib,json,pathlib,subprocess,unittest
ROOT=pathlib.Path(__file__).resolve().parents[2]
COMP=ROOT/'g2/components/foundation/freertos_ready'
class ReadyEvidence(unittest.TestCase):
 def test_pinned_function_text_and_license(self):
  p=json.loads((COMP/'SOURCE_PROVENANCE.json').read_text())
  for name,expected in p['unchanged_function_text_sha256'].items():
   s=(COMP/('list_subset.c' if name in ['vListInsertEnd','uxListRemove'] else 'tasks_subset.c')).read_bytes().decode()
   # Select definition, not the earlier static forward declaration.
   begin=s.rindex(name+'(');begin=s.rfind('\n',0,begin)+1
   i=s.index('{',begin)+1;depth=1
   while depth:depth+=(s[i]=='{')-(s[i]=='}');i+=1
   self.assertEqual(hashlib.sha256(s[begin:i].encode()).hexdigest(),expected,name)
   self.assertIn('Copyright (C) 2021 Amazon.com',s)
 def test_original_body_identities(self):
  b=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
  self.assertEqual(hashlib.sha256(b).hexdigest(),'36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863')
  evidence=json.loads((ROOT/'g2/analysis/rtos-ready-wsf-2026-10-05/original/results.json').read_text())
  for address,f in evidence['functions'].items():
   offset=int(address,16)-0x438000+32
   self.assertEqual(hashlib.sha256(b[offset:offset+f['size']]).hexdigest(),f['sha256'])
 def test_linked_provider_and_optimized_rejection(self):
  elf=ROOT/'g2/build/foundation/rtos-ready-wsf-simulator/rtos_ready_wsf.elf'
  self.assertTrue(elf.exists(),'build ready simulator first')
  nm=subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True)
  for name in ['opencfw_ready_remove_event_list','xTaskRemoveFromEventList','uxTaskGetNumberOfTasks','vListInsertEnd','uxListRemove','opencfw_timer_callbacks_drain']:
   self.assertIn(' T '+name,nm)
  p=subprocess.run(['python3','-O',str(COMP/'simulator/verify.py')],capture_output=True,text=True)
  self.assertNotEqual(p.returncode,0);self.assertIn('optimized Python rejected',p.stderr)
