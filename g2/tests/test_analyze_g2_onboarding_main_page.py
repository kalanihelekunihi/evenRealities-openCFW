import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"tools/analyze_g2_onboarding_main_page.py";S=importlib.util.spec_from_file_location("g2_onboarding_main_page",P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class G2OnboardingMainPageTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_complete_object(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['ghidra_discovered_functions'],s['restored_functions'],s['body_bytes'],s['physical_bytes'],s['noncode_bytes'],s['reachable_instructions']),(52,37,15,9234,9776,542,3632));self.assertEqual((s['direct_body_calls'],s['internal_direct_body_calls'],s['external_direct_body_calls'],s['indirect_body_calls'],s['direct_bl_entry_sites'],s['stored_entry_pointers'],s['strict_interior_ingress']),(533,80,453,0,118,17,0))
 def test_provider_closure(self):
  p=self.r['provider_boundary'];self.assertEqual((p['lvgl_calls'],p['easylogger_calls'],p['cmsis_freertos_calls'],p['iar_dlib_calls'],p['mpaland_printf_calls'],p['closed_onboarding_protobuf_calls'],p['first_party_calls']),(264,45,23,17,4,1,99));self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[]);self.assertFalse(p['new_version_discriminator'] or p['private_generating_commit_recoverable'])
 def test_behavior_and_routing(self):
  self.assertTrue(all(self.r['behavior'].values()));self.assertFalse(self.r['production']['production_routed'])
if __name__=='__main__':unittest.main()
