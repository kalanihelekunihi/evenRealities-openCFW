import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"tools/analyze_g2_npmx_main_driver.py";S=importlib.util.spec_from_file_location("g2_npmx_main_driver",P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class G2NpmxMainDriverTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_complete_object(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['restored_functions'],s['path_anchored_functions'],s['body_bytes'],s['physical_bytes'],s['noncode_bytes'],s['reachable_instructions']),(30,19,11,6560,7102,542,2281));self.assertEqual((s['direct_body_calls'],s['internal_direct_body_calls'],s['external_direct_body_calls'],s['indirect_body_calls'],s['direct_bl_entry_sites'],s['stored_function_entry_pointers'],s['strict_interior_ingress']),(420,17,403,0,35,4,0))
 def test_provider_closure(self):
  p=self.r['provider_boundary'];self.assertEqual((p['npmx_calls'],p['npmx_entry_targets'],p['easylogger_calls'],p['cmsis_freertos_calls'],p['iar_dlib_calls'],p['first_party_transport_delay_calls'],p['first_party_orientation_calls']),(72,42,310,2,2,9,8));self.assertTrue(p['new_version_discriminator']);self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[])
 def test_exact_public_candidate(self):
  p=self.r['provider_boundary'];self.assertTrue(p['exact_public_candidate']);self.assertFalse(p['exact_private_checkout_proven']);self.assertEqual(p['npmx_selected_commit'],'e1aaec53f456887a7d7b80d82f684d1ac3cb08c8');self.assertEqual(p['npmx_adjacent_excluded_commit'],'53de7af4394382e1a21008eaa18ed9e5e1809504')
 def test_behavior_and_routing(self):self.assertTrue(all(self.r['behavior'].values()));self.assertFalse(self.r['production']['production_routed']);self.assertEqual(len(self.r['production']['remaining_integration']),5)
if __name__=='__main__':unittest.main()
