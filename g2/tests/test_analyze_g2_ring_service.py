import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_ring_service as r
class G2RingServiceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=r.analyze()
 def test_surface(self):
  x=self.r['surface'];self.assertEqual((x['linked_functions'],x['body_bytes'],x['physical_bytes'],x['direct_body_calls'],x['external_direct_body_calls']),(18,2412,2616,125,121))
 def test_ingress(self):
  x=self.r['surface'];self.assertEqual((x['direct_bl_entry_sites'],x['stored_function_pointers'],x['indirect_body_calls']),(27,2,0))
 def test_providers(self):
  p=self.r['provider_boundary'];self.assertEqual((p['easylogger_calls'],p['cmsis_freertos_calls'],p['runtime_calls'],p['nanopb_calls'],p['cordio_calls'],p['first_party_calls']),(76,2,8,1,0,34));self.assertIsNone(p['historical_ring_service_commit']);self.assertFalse(p['new_version_discriminator'])
 def test_boundary(self):self.assertTrue(self.r['production']['production_routed']);self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[]);self.assertEqual((self.r['production']['ownership_bytes'],self.r['production']['compiled_text_bytes'],self.r['production']['generated_alignment_bytes'],self.r['production']['strict_relocations'],self.r['production']['guarded_redirects']),(2412,952,18,38,18));self.assertEqual(self.r['production']['hardware_validation'],'blocked_unavailable_physical_evidence')
if __name__=='__main__':unittest.main()
