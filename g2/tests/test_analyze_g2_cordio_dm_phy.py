import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class DmPhyTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  s=importlib.util.spec_from_file_location("dm_phy_audit",ROOT/"tools/analyze_g2_cordio_dm_phy.py"); assert s and s.loader; cls.m=importlib.util.module_from_spec(s); sys.modules[s.name]=cls.m; s.loader.exec_module(cls.m)
 def test_closure(self):
  r=self.m.analyze(); m=r["module"]; self.assertEqual((m["linked_function_count"],m["linked_function_bytes"],m["physical_bytes"]),(6,308,320)); self.assertEqual(len(m["source_only_functions"]),2); self.assertEqual((m["direct_bl_ingress_sites"],m["registered_function_pointers"],m["strict_interior_pointers"]),(5,1,0)); self.assertEqual(r["architecture"]["widened_feature_mask"],0x900); self.assertEqual(r["readiness"]["linked_unresolved_symbols"],0)
  p=r["production"]; self.assertEqual(p["status"],"production-routed"); self.assertEqual((p["redirected_stock_functions"],p["redirected_stock_bytes"]),(6,308)); self.assertEqual((p["source_owned_bytes_added"],p["alignment_bytes_added"],p["strict_relocations"]),(378,4,11)); self.assertEqual(len(p["source_only_target_compiled"]),2); self.assertEqual(p["manifest_regions"],14)
  counts=p["flash_plan_counts"]; self.assertEqual(len(counts),4); self.assertGreater(counts[0],0); self.assertEqual(counts[1],0)
if __name__=="__main__": unittest.main()
