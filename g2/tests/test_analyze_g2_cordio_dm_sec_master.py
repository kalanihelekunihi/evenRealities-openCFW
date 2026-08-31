import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class DmSecMasterTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  s=importlib.util.spec_from_file_location("dm_sec_master_audit",ROOT/"tools/analyze_g2_cordio_dm_sec_master.py");assert s and s.loader;cls.m=importlib.util.module_from_spec(s);sys.modules[s.name]=cls.m;s.loader.exec_module(cls.m)
 def test_closure(self):
  r=self.m.analyze();m=r["module"];self.assertEqual((m["linked_function_count"],m["linked_function_bytes"],m["physical_bytes"]),(3,144,152));self.assertEqual(m["source_only_functions"],[]);self.assertEqual(m["direct_bl_ingress_sites"],4);self.assertEqual(r["architecture"]["encrypt_request_event"],0x28);self.assertEqual(r["abi"]["calc128_zeros"],0x7856B0);self.assertEqual(r["readiness"]["linked_unresolved_symbols"],0);self.assertTrue(r["production"]["production_routed"]);self.assertEqual((r["production"]["live_functions"],r["production"]["compiled_leaf_bytes"],r["production"]["source_owned_bytes_added"],r["production"]["stock_bytes_replaced"]),(3,172,174,144));self.assertIn("blocked by unavailable physical evidence",r["production"]["hardware_validation"])
if __name__=="__main__":unittest.main()
