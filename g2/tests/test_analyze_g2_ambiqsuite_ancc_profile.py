from __future__ import annotations
import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'tools/analyze_g2_ambiqsuite_ancc_profile.py';S=importlib.util.spec_from_file_location('ancc_profile',P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class AmbiqSuiteAnccProfileTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_source_identity(self):self.assertEqual(self.r['upstream']['selected_commit'],'de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f');self.assertEqual(self.r['upstream']['earliest_authenticated_same_implementation_commit'],'ca79fc6e140d25b0c596a5c87c3d311cd2710ad9');self.assertEqual(self.r['upstream']['compatible_release_count'],4);self.assertIsNone(self.r['upstream']['historical_g2_generating_commit'])
 def test_surface(self):self.assertEqual(self.r['surface'],{'linked_functions':21,'source_derived_stock_functions':12,'g2_local_stock_functions':9,'body_bytes':3712,'physical_bytes':3980,'direct_bl_entry_sites':26,'direct_body_calls':155,'stored_entry_pointers':2,'strict_interior_ingress':0})
 def test_delta_and_admission(self):self.assertEqual(len(self.r['functions']),21);self.assertEqual(self.r['upstream']['upstream_source_definitions'],17);self.assertTrue(all(self.r['local_delta'].values()));p=self.r['production'];self.assertTrue(p['source_admitted']);self.assertTrue(p['production_routed']);self.assertEqual((p['ownership_bytes'],p['relocations']),(11760,69));self.assertEqual(p['hardware_validation'],'blocked');self.assertIn('No authorized responsive G2/ANCS peer',p['hardware_blocker'])
if __name__=='__main__':unittest.main()
