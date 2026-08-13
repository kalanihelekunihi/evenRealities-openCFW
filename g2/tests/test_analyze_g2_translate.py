import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];S=importlib.util.spec_from_file_location('g2_translate',ROOT/'tools/analyze_g2_translate.py');M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_surface(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['ghidra_discovered_functions'],s['restored_functions']),(11,9,2));self.assertEqual((s['body_bytes'],s['physical_bytes'],s['noncode_bytes']),(2504,2862,358));self.assertEqual((s['direct_body_calls'],s['internal_direct_body_calls'],s['external_direct_body_calls']),(168,12,156));self.assertEqual(s['indirect_body_calls'],0)
 def test_providers(self):self.assertEqual(tuple(self.r['provider_boundary'][x] for x in ('easylogger_calls','iar_runtime_calls','lvgl_calls','cmsis_freertos_calls','nanopb_calls','first_party_calls')),(105,7,2,7,3,32))
 def test_boundary(self):self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[]);self.assertFalse(self.r['production']['production_routed'])
if __name__=='__main__':unittest.main()
