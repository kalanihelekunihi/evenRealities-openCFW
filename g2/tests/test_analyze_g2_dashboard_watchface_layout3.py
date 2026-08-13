import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];S=importlib.util.spec_from_file_location('layout3',ROOT/'tools/analyze_g2_dashboard_watchface_layout3.py');M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_surface(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['ghidra_discovered_functions'],s['restored_functions']),(19,12,7));self.assertEqual((s['body_bytes'],s['physical_bytes'],s['noncode_bytes']),(3254,3648,394));self.assertEqual((s['direct_body_calls'],s['internal_direct_body_calls'],s['external_direct_body_calls']),(199,26,173));self.assertEqual((s['indirect_body_calls'],s['stored_function_entry_pointers'],s['raw_overlapping_pseudo_bl_sites']),(0,9,5))
 def test_providers(self):self.assertEqual(tuple(self.r['provider_boundary'][x] for x in ('easylogger_calls','lvgl_calls','iar_dlib_calls','mpaland_printf_calls','first_party_calls')),(20,125,10,2,16))
 def test_boundary(self):self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[]);self.assertFalse(self.r['production']['production_routed'])
if __name__=='__main__':unittest.main()
