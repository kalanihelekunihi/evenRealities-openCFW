import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'tools/analyze_g2_service_even_ai.py';S=importlib.util.spec_from_file_location('analyze_g2_service_even_ai',P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class ServiceEvenAiTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_surface(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['restored_functions'],s['body_bytes'],s['physical_bytes'],s['noncode_bytes']),(9,3,1984,2126,142));self.assertEqual((s['direct_bl_entry_sites'],s['stored_aligned_function_entry_pointers'],s['raw_interior_word_collisions'],s['strict_interior_ingress']),(30,1,3,0))
 def test_providers(self):
  p=self.r['provider_boundary'];self.assertEqual(tuple(p[x] for x in ('easylogger_calls','iar_dlib_calls','cmsis_freertos_calls','closed_first_party_calls','bounded_first_party_calls')),(55,9,2,23,35));self.assertEqual(p['cmsis_freertos_seams'],['osKernelGetTickCount']);self.assertIsNone(p['historical_service_even_ai_commit']);self.assertFalse(p['new_version_discriminator'])
 def test_no_ai_nn_library(self):
  p=self.r['provider_boundary'];self.assertFalse(p['embedded_ai_nn_library']);self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[])
 def test_claims(self):self.assertFalse(self.r['production']['production_routed'])
