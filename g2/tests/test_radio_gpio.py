"""Consumer evidence contracts; source build and actual instructions tested separately."""
import hashlib,json,pathlib,subprocess,unittest
ROOT=pathlib.Path(__file__).resolve().parents[2]
class RadioGPIOEvidence(unittest.TestCase):
 def test_reference_ranges_are_authenticated(self):
  p=json.loads((ROOT/'g2/analysis/radio-gpio-consumer-2026-10-05/dependency-provenance.json').read_text());b=(ROOT/p['stock_image']).read_bytes()
  self.assertEqual(hashlib.sha256(b).hexdigest(),p['stock_sha256'])
  for x in p['ranges']:
   off=int(x['start'],16)-int(p['base'],16)+p['preamble_bytes'];self.assertEqual(hashlib.sha256(b[off:off+x['bytes']]).hexdigest(),x['sha256'])
 def test_consumer_is_build_integrated(self):
  m=(ROOT/'g2/Makefile').read_text();self.assertIn('radio-gpio-simulator-test: radio-gpio-simulator',m);self.assertIn('test_radio_gpio',m)
  elf=ROOT/'g2/build/foundation/radio-gpio-simulator/radio_gpio.elf'
  if not elf.exists():self.skipTest('consumer callable ELF not built')
  nm=subprocess.check_output(['arm-none-eabi-nm',str(elf)],text=True)
  for n in ['GPIO0_607F_IRQHandler','opencfw_radio_gpio_callback','opencfw_radio_gpio_register','am_hal_gpio_interrupt_service','am_hal_interrupt_master_disable']:self.assertIn(' T '+n,nm)
 def test_optimized_verifier_is_rejected(self):
  v=ROOT/'g2/components/foundation/radio_gpio/simulator/verify.py';p=subprocess.run(['python3','-O',str(v)],capture_output=True,text=True);self.assertNotEqual(p.returncode,0);self.assertIn('optimized Python rejected',p.stderr)
