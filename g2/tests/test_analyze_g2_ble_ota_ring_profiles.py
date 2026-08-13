from __future__ import annotations
import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'tools/analyze_g2_ble_ota_ring_profiles.py';S=importlib.util.spec_from_file_location('ble_ota_ring',P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class BleOtaRingTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_surface(self):self.assertEqual(self.r['aggregate'],{'modules':2,'linked_functions':14,'ambiq_skeleton_derived_stock_functions':4,'g2_local_stock_functions':10,'body_bytes':2066,'physical_bytes':2280})
 def test_ota_lineage(self):self.assertEqual(self.r['upstream']['selected_commit'],'de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f');self.assertEqual(self.r['upstream']['stable_release_imports'],4);self.assertIsNone(self.r['upstream']['historical_g2_generating_commit']);self.assertEqual(self.r['modules']['ota']['ownership_counts'],{'ambiq_skeleton_derived':4,'g2_local':3})
 def test_ring_boundary(self):self.assertIsNone(self.r['upstream']['ring_component']);self.assertEqual(self.r['upstream']['ring_exact_public_symbol_hits'],0);self.assertEqual(self.r['modules']['ring']['ownership_counts'],{'ambiq_skeleton_derived':0,'g2_local':7});self.assertEqual(self.r['modules']['ring']['protocol']['events'][-1],0xAC)
 def test_production_excluded(self):self.assertEqual(self.r['production'],{'source_oracle_admitted':True,'production_routed':False,'ownership_bytes':0})
if __name__=='__main__':unittest.main()
