import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'tools/analyze_g2_drv_cy8c4046fni.py';S=importlib.util.spec_from_file_location('analyze_g2_drv_cy8c4046fni',P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class DrvCy8c4046fniTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_surface(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['ghidra_discovered_functions'],s['restored_functions'],s['path_anchored_functions'],s['body_bytes'],s['physical_bytes'],s['noncode_bytes']),(23,20,3,7,1754,1924,170));self.assertEqual((s['direct_bl_entry_sites'],s['stored_entry_pointers'],s['indirect_body_calls'],s['strict_interior_ingress']),(50,4,9,0))
 def test_providers(self):
  p=self.r['provider_boundary'];self.assertEqual(tuple(p[x] for x in ('easylogger_calls','iar_dlib_calls','cmsis_freertos_calls','closed_hal_i2c_calls','bounded_first_party_calls')),(60,9,2,4,2));self.assertEqual(p['cmsis_wrappers'],['osDelay']);self.assertIsNone(p['public_cypress_source_candidate']);self.assertIsNone(p['historical_drv_cy8c4046fni_commit']);self.assertFalse(p['new_version_discriminator'])
 def test_claims(self):
  self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[])
  p=self.r['production'];self.assertTrue(p['production_routed']);self.assertFalse(p['software_functional_gap']);self.assertEqual((p['source_functions'],p['compiled_text_bytes'],p['alignment_bytes'],p['stock_replaced_bytes'],p['strict_relocations'],p['retained_callback_pool_bytes']),(23,1122,18,1754,19,170));self.assertEqual(p['hardware_validation'],'deferred by project direction');self.assertIn('required for future qualification',p['hardware_blocker'])
if __name__=='__main__':unittest.main()
