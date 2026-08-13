import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];S=importlib.util.spec_from_file_location('g2_conversate_comm_data',ROOT/'tools/analyze_g2_conversate_comm_data.py');M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_surface(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['ghidra_discovered_functions'],s['restored_functions']),(12,12,0));self.assertEqual((s['body_bytes'],s['physical_bytes'],s['noncode_bytes']),(2208,2560,352));self.assertEqual((s['direct_body_calls'],s['internal_direct_body_calls'],s['external_direct_body_calls']),(77,5,72));self.assertEqual((s['indirect_body_calls'],s['stored_function_entry_pointers'],s['strict_interior_ingress']),(0,0,0))
 def test_providers(self):self.assertEqual(tuple(self.r['provider_boundary'][x] for x in ('easylogger_calls','iar_dlib_calls','lvgl_calls')),(60,11,1));self.assertFalse(self.r['provider_boundary']['new_version_discriminator'])
 def test_boundary(self):self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[]);self.assertFalse(self.r['production']['production_routed'])
if __name__=='__main__':unittest.main()
