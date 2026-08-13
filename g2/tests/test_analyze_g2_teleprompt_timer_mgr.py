import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];S=importlib.util.spec_from_file_location('g2_teleprompt_timer_mgr',ROOT/'tools/analyze_g2_teleprompt_timer_mgr.py');M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_surface(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['ghidra_discovered_functions'],s['restored_functions'],s['path_anchored_functions']),(13,9,4,5));self.assertEqual((s['body_bytes'],s['physical_bytes'],s['noncode_bytes']),(1498,1660,162));self.assertEqual((s['direct_body_calls'],s['internal_direct_body_calls'],s['external_direct_body_calls']),(74,9,65));self.assertEqual((s['indirect_body_calls'],s['bounded_timer_callback_table_entries'],s['stored_function_entry_pointers'],s['strict_interior_ingress']),(2,3,4,0))
 def test_providers(self):self.assertEqual(tuple(self.r['provider_boundary'][x] for x in ('easylogger_calls','cmsis_freertos_calls','first_party_calls')),(55,3,7));self.assertEqual(self.r['provider_boundary']['cmsis_freertos_seams'],['osKernelGetTickCount']);self.assertFalse(self.r['provider_boundary']['new_version_discriminator'])
 def test_boundary(self):self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[]);self.assertFalse(self.r['production']['production_routed'])
if __name__=='__main__':unittest.main()
