import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];S=importlib.util.spec_from_file_location('g2_teleprompt_controller',ROOT/'tools/analyze_g2_teleprompt_controller.py');M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_surface(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['ghidra_discovered_functions'],s['restored_functions']),(10,8,2));self.assertEqual((s['body_bytes'],s['physical_bytes'],s['noncode_bytes']),(2408,3900,1492));self.assertEqual((s['direct_body_calls'],s['internal_direct_body_calls'],s['external_direct_body_calls']),(162,13,149));self.assertEqual((s['indirect_body_calls'],s['stored_function_entry_pointers'],s['strict_interior_ingress']),(0,3,0))
 def test_providers(self):self.assertEqual(tuple(self.r['provider_boundary'][x] for x in ('easylogger_calls','iar_runtime_calls','lvgl_calls','cmsis_freertos_calls','nanopb_calls','first_party_calls')),(90,4,2,7,3,43))
 def test_boundary(self):self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[]);self.assertFalse(self.r['production']['production_routed'])
if __name__=='__main__':unittest.main()
