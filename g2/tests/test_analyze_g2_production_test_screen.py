import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'tools/analyze_g2_production_test_screen.py';S=importlib.util.spec_from_file_location('prod_screen',P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class ProductionScreenTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_surface(self):self.assertEqual(self.r['surface'],{'linked_functions':3,'body_bytes':286,'owned_noncode_bytes':30,'physical_bytes':316,'descriptor_bytes':16,'direct_bl_entry_sites':0,'direct_body_calls':20,'stored_entry_pointers':3,'raw_entry_or_interior_values':92,'excluded_instruction_byte_lookalikes':89,'strict_interior_ingress':0})
 def test_grid(self):self.assertEqual(self.r['behavior']['grid_dimensions'],[3,3]);self.assertEqual(self.r['behavior']['x_positions'],[66,266,466]);self.assertEqual(self.r['behavior']['y_positions'],[21,121,221])
 def test_boundary_and_status(self):
  self.assertEqual(self.r['boundary']['next_function'],'0x005cf8e4');p=self.r['production'];self.assertTrue(p['production_routed']);self.assertEqual(p['source_functions'],3);self.assertEqual(p['stock_body_bytes_displaced'],286);self.assertFalse(p['software_functional_gap']);self.assertEqual(p['hardware_validation'],'blocked by unavailable physical evidence')
if __name__=='__main__':unittest.main()
