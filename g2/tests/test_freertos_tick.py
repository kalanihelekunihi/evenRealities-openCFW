"""Pinned tick text, stock body and actual provider/configuration evidence."""
import hashlib,json,pathlib,subprocess,unittest
ROOT=pathlib.Path(__file__).resolve().parents[2]
COMP=ROOT/'g2/components/foundation/freertos_tick'
class TickEvidence(unittest.TestCase):
 def test_unchanged_function_text_and_license(self):
  provenance=json.loads((COMP/'SOURCE_PROVENANCE.json').read_text());s=(COMP/'tasks_tick.c').read_bytes().decode()
  for name,h in provenance['unchanged_function_text_sha256'].items():
   signature={'xTaskIncrementTick':'BaseType_t xTaskIncrementTick( void )','prvResetNextTaskUnblockTime':'static void prvResetNextTaskUnblockTime( void )'}[name]
   a=s.rindex(signature);i=s.index('{',a)+1;depth=1
   while depth:depth+=(s[i]=='{')-(s[i]=='}');i+=1
   self.assertEqual(hashlib.sha256(s[a:i].encode()).hexdigest(),h,name)
  self.assertIn('Copyright (C) 2021 Amazon.com',s)
 def test_stock_tick_and_rollover_counter_identity(self):
  b=(ROOT/'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin').read_bytes()
  self.assertEqual(hashlib.sha256(b).hexdigest(),'36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863')
  a=0x45504c-0x438000+32;self.assertEqual(hashlib.sha256(b[a:a+338]).hexdigest(),'438ad4e9e1a7b439671463b2bbfd13616ebb6de32bd2aad53b802d31f11cc050')
  a=0x455af8-0x438000+32;self.assertEqual(int.from_bytes(b[a:a+4],'little'),0x20074a48)
 def test_actual_provider_and_unoptimized_simulator_profile(self):
  elf=ROOT/'g2/build/foundation/rtos-tick-wsf-simulator/rtos_tick_wsf.elf';self.assertTrue(elf.exists(),'build tick simulator first')
  nm=subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True)
  for n in ['xTaskIncrementTick','xTaskResumeAll','opencfw_ready_remove_event_list','opencfw_timer_callbacks_drain']:self.assertIn(' T '+n,nm)
  self.assertNotIn('BaseType_t xTaskIncrementTick(void){',(COMP/'simulator/providers.c').read_text())
  self.assertIn('TICK_SIM_CFLAGS ?= $(GPIO_SIM_CFLAGS) -O0',(ROOT/'g2/Makefile').read_text())
  p=subprocess.run(['python3','-O',str(COMP/'simulator/verify.py')],capture_output=True,text=True)
  self.assertNotEqual(p.returncode,0);self.assertIn('optimized Python rejected',p.stderr)
