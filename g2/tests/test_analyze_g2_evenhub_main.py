import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SPEC=importlib.util.spec_from_file_location("g2_evenhub_main",ROOT/"tools/analyze_g2_evenhub_main.py");MODULE=importlib.util.module_from_spec(SPEC);sys.modules[SPEC.name]=MODULE;SPEC.loader.exec_module(MODULE)
class EvenHubMainTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.report=MODULE.analyze()
 def test_complete_object(self):
  s=self.report["surface"];self.assertEqual((s["linked_functions"],s["ghidra_discovered_functions"],s["restored_functions"]),(5,4,1));self.assertEqual((s["body_bytes"],s["physical_bytes"],s["noncode_bytes"]),(3130,3450,320));self.assertEqual((s["direct_body_calls"],s["internal_direct_body_calls"],s["external_direct_body_calls"]),(181,1,180));self.assertEqual((s["indirect_body_calls"],s["strict_interior_ingress"]),(0,0));self.assertEqual((s["raw_noncode_pseudo_bl_sites"],s["raw_unaligned_interior_word_collisions"]),(1,1))
 def test_provider_boundary(self):
  p=self.report["provider_boundary"];self.assertEqual((p["easylogger_calls"],p["iar_runtime_calls"],p["lvgl_calls"],p["cmsis_freertos_calls"],p["nanopb_calls"],p["heap_wrapper_calls"],p["first_party_calls"]),(120,6,2,2,3,2,45));self.assertIsNone(p["historical_evenhub_main_commit"]);self.assertFalse(p["new_version_discriminator"])
 def test_no_embedded_dependency_or_routing(self):self.assertEqual(self.report["identity"]["embedded_third_party_definitions"],[]);self.assertFalse(self.report["production"]["production_routed"])
if __name__=="__main__":unittest.main()
