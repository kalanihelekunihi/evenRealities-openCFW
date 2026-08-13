import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'tools/analyze_g2_general_configure.py';S=importlib.util.spec_from_file_location('analyze_g2_general_configure',P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class GeneralConfigureTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_surface(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['restored_functions'],s['body_bytes'],s['physical_bytes']),(10,6,2376,2616));self.assertEqual((s['direct_bl_entry_sites'],s['indirect_body_calls'],s['strict_interior_ingress'],s['stored_function_entry_pointers']),(10,0,2,1));self.assertEqual(s['merged_body_secondary_entries'],2)
 def test_providers(self):
  p=self.r['provider_boundary'];self.assertEqual(tuple(p[x] for x in ('easylogger_calls','iar_dlib_calls','cmsis_freertos_calls','nanopb_calls','first_party_calls')),(110,13,3,8,7));self.assertEqual(p['cmsis_freertos_seams']['osEventFlagsSet'],3);self.assertIsNone(p['historical_general_configure_commit']);self.assertFalse(p['new_version_discriminator'])
 def test_claims(self):self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[]);self.assertFalse(self.r['production']['production_routed'])
