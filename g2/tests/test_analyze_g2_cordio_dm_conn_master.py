import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class DmConnMasterTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  s=importlib.util.spec_from_file_location("dm_conn_master_audit",ROOT/"tools/analyze_g2_cordio_dm_conn_master.py");assert s and s.loader;cls.m=importlib.util.module_from_spec(s);sys.modules[s.name]=cls.m;s.loader.exec_module(cls.m)
 def test_closure(self):
  r=self.m.analyze();m=r["module"];self.assertEqual((m["linked_function_count"],m["linked_function_bytes"],m["physical_bytes"]),(5,138,140));self.assertEqual(m["source_only_functions"],["DmConnSetAddrType"]);self.assertEqual((m["direct_bl_ingress_sites"],m["registered_function_pointers"],m["strict_interior_pointers"]),(2,3,0));self.assertEqual(r["architecture"]["l2c_update_event"],0x72);self.assertTrue(r["architecture"]["separate_update_executor"]);self.assertEqual(r["readiness"]["linked_unresolved_symbols"],0)
if __name__=="__main__":unittest.main()
