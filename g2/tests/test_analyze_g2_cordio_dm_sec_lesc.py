from __future__ import annotations
import importlib.util, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class CordioDmSecLescAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path=ROOT/"tools/analyze_g2_cordio_dm_sec_lesc.py"; spec=importlib.util.spec_from_file_location("dm_sec_lesc_audit",path); assert spec and spec.loader
        cls.module=importlib.util.module_from_spec(spec); sys.modules[spec.name]=cls.module; spec.loader.exec_module(cls.module)
    def test_stock_dm_sec_lesc_closure(self):
        r=self.module.analyze(); m=r["module"]
        self.assertEqual((m["linked_function_count"],m["linked_function_bytes"],m["physical_bytes"]),(7,222,248))
        self.assertEqual((m["source_inventory_functions"],len(m["source_only_functions"])),(11,4))
        self.assertEqual((m["direct_bl_ingress_sites"],m["registered_function_pointers"],m["strict_interior_pointers"]),(10,1,0))
        self.assertEqual(r["architecture"]["message_events"],[0x40,0x41]); self.assertEqual(r["readiness"]["linked_unresolved_symbols"],0)
        self.assertTrue(r["production"]["production_routed"])
        self.assertEqual((r["production"]["live_functions"],r["production"]["compiled_leaf_bytes"],r["production"]["stock_bytes_replaced"]),(7,278,222))
        self.assertEqual(len(r["production"]["dead_stripped_public_apis"]),4)
if __name__=="__main__": unittest.main()
