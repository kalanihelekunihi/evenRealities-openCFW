"""Pinned resume text, actual stock bodies and external-tick boundary."""
import hashlib,json,pathlib,subprocess,unittest
ROOT=pathlib.Path(__file__).resolve().parents[2]
COMP=ROOT/'g2/components/foundation/freertos_resume'
class ResumeEvidence(unittest.TestCase):
 def test_unchanged_function_text_and_license(self):
  provenance=json.loads((COMP/'SOURCE_PROVENANCE.json').read_text())
  s=(COMP/'tasks_resume.c').read_bytes().decode()
  for name,h in provenance['unchanged_function_text_sha256'].items():
   signature={'vTaskSuspendAll':'void vTaskSuspendAll( void )','xTaskResumeAll':'BaseType_t xTaskResumeAll( void )','prvResetNextTaskUnblockTime':'static void prvResetNextTaskUnblockTime( void )'}[name]
   start=s.rindex(signature);i=s.index('{',start)+1;depth=1
   while depth:depth+=(s[i]=='{')-(s[i]=='}');i+=1
   self.assertEqual(hashlib.sha256(s[start:i].encode()).hexdigest(),h,name)
  self.assertIn('Copyright (C) 2021 Amazon.com',s)
 def test_stock_suspend_resume_and_tick_literal(self):
  b=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
  self.assertEqual(hashlib.sha256(b).hexdigest(),'36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863')
  for a,n,h in [(0x454d7c,12,'3651c872be8fd55503df57fb49f5d0b7b94b0e784237141389a4b965b8edb6e2'),(0x454dcc,306,'548e05e1f8a2f498372dd1f4eb7c6536e093dbbfdb82fbe8f9b54231cedc8a09')]:
   offset=a-0x438000+32;self.assertEqual(hashlib.sha256(b[offset:offset+n]).hexdigest(),h)
  self.assertEqual(int.from_bytes(b[0x455a18-0x438000+32:0x455a1c-0x438000+32],'little'),0x20074a40)
 def test_linked_provider_and_explicit_tick_boundary(self):
  elf=ROOT/'g2/build/foundation/rtos-resume-wsf-simulator/rtos_resume_wsf.elf'
  self.assertTrue(elf.exists(),'build resume simulator first')
  nm=subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True)
  for n in ['vTaskSuspendAll','xTaskResumeAll','opencfw_resume_yield_request','opencfw_ready_remove_event_list']:self.assertIn(' T '+n,nm)
  s=(COMP/'simulator/verify.py').read_text();self.assertIn("0x45504c:'tick_boundary'",s)
  p=subprocess.run(['python3','-O',str(COMP/'simulator/verify.py')],capture_output=True,text=True)
  self.assertNotEqual(p.returncode,0);self.assertIn('optimized Python rejected',p.stderr)
