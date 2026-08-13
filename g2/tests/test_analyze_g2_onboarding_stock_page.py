import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"tools/analyze_g2_onboarding_stock_page.py";S=importlib.util.spec_from_file_location("g2_onboarding_stock_page",P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class G2OnboardingStockPageTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_complete_object(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['ghidra_discovered_functions'],s['restored_functions'],s['body_bytes'],s['physical_bytes'],s['noncode_bytes'],s['reachable_instructions']),(17,17,0,7500,7864,364,2818));self.assertEqual((s['direct_body_calls'],s['internal_direct_body_calls'],s['external_direct_body_calls'],s['indirect_body_calls'],s['direct_bl_entry_sites'],s['stored_entry_pointers'],s['strict_interior_ingress']),(629,32,597,0,38,0,0))
 def test_provider_closure(self):
  p=self.r['provider_boundary'];self.assertEqual((p['lvgl_calls'],p['easylogger_calls'],p['cmsis_freertos_calls'],p['iar_dlib_calls'],p['first_party_calls']),(447,110,2,5,33));self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[]);self.assertFalse(p['new_version_discriminator'] or p['private_generating_commit_recoverable'])
 def test_behavior_and_routing(self):
  self.assertTrue(all(self.r['behavior'].values()));self.assertFalse(self.r['production']['production_routed'])
if __name__=='__main__':unittest.main()
