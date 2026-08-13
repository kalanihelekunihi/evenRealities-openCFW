import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'tools/analyze_g2_pdt_gray_screen.py';S=importlib.util.spec_from_file_location('gray',P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class GrayTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_surface(self):self.assertEqual(self.r['surface'],{'linked_functions':3,'body_bytes':340,'literal_pool_bytes':32,'physical_bytes':372,'descriptor_bytes':16,'direct_bl_entry_sites':0,'direct_body_calls':23,'stored_entry_pointers':3,'strict_interior_ingress':0})
 def test_contract(self):
  self.assertEqual(self.r['registration']['screen_id'],'0x0000010f');self.assertEqual(self.r['behavior']['gray_values'],[17,34,68,136,136,68,34,17]);self.assertEqual(self.r['behavior']['band_dimensions'],[72,288])
 def test_boundary_and_status(self):self.assertEqual(self.r['boundary']['next_handler'],'0x005cf7a8');self.assertFalse(self.r['production']['production_routed']);self.assertIsNone(self.r['production']['candidate'])
if __name__=='__main__':unittest.main()
