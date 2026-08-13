import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'tools/analyze_g2_terminal_data.py';S=importlib.util.spec_from_file_location('analyze_g2_terminal_data',P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class TerminalDataTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_surface(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['restored_functions'],s['body_bytes'],s['physical_bytes'],s['noncode_bytes']),(44,40,2902,3012,110));self.assertEqual((s['direct_bl_entry_sites'],s['stored_function_entry_pointers'],s['stored_interior_pointers'],s['indirect_body_calls'],s['strict_interior_ingress'],s['raw_noncode_pseudo_bl']),(180,0,1,0,1,1))
 def test_providers(self):
  p=self.r['provider_boundary'];self.assertEqual(tuple(p[x] for x in ('easylogger_calls','iar_dlib_calls','closed_time_service_calls')),(30,13,2));self.assertEqual((p['cmsis_freertos_calls'],p['freertos_kernel_calls']),(0,0));self.assertFalse(p['new_version_discriminator'])
 def test_claims(self):self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[]);self.assertFalse(self.r['production']['production_routed'])
