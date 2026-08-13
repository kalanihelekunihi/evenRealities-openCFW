import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SPEC=importlib.util.spec_from_file_location("g2_health_data_manager",ROOT/"tools/analyze_g2_health_data_manager.py");MODULE=importlib.util.module_from_spec(SPEC);sys.modules[SPEC.name]=MODULE;SPEC.loader.exec_module(MODULE)
class HealthDataManagerTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.report=MODULE.analyze()
 def test_complete_object(self):
  s=self.report["surface"];self.assertEqual((s["linked_functions"],s["ghidra_discovered_functions"],s["restored_functions"]),(10,9,1));self.assertEqual((s["body_bytes"],s["physical_bytes"],s["noncode_bytes"]),(2644,2912,268));self.assertEqual((s["direct_body_calls"],s["internal_direct_body_calls"],s["external_direct_body_calls"]),(149,13,136));self.assertEqual((s["indirect_body_calls"],s["stored_function_entry_pointers"],s["strict_interior_ingress"]),(0,0,0))
 def test_provider_boundary(self):
  p=self.report["provider_boundary"];self.assertEqual((p["easylogger_calls"],p["iar_runtime_calls"],p["closed_health_lock_calls"],p["direct_cmsis_freertos_calls"]),(120,6,10,0));self.assertIsNone(p["historical_health_manager_commit"]);self.assertFalse(p["new_version_discriminator"])
 def test_no_embedded_dependency_or_routing(self):self.assertEqual(self.report["identity"]["embedded_third_party_definitions"],[]);self.assertFalse(self.report["production"]["production_routed"])
if __name__=="__main__":unittest.main()
