import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SPEC=importlib.util.spec_from_file_location("g2_dashboard_watchface_layout1",ROOT/"tools/analyze_g2_dashboard_watchface_layout1.py");MODULE=importlib.util.module_from_spec(SPEC);sys.modules[SPEC.name]=MODULE;SPEC.loader.exec_module(MODULE)
class DashboardWatchfaceLayout1Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.report=MODULE.analyze()
 def test_complete_object(self):
  s=self.report["surface"];self.assertEqual((s["linked_functions"],s["ghidra_discovered_functions"],s["restored_functions"]),(19,9,10));self.assertEqual((s["body_bytes"],s["physical_bytes"],s["noncode_bytes"]),(3500,3592,92));self.assertEqual((s["direct_body_calls"],s["internal_direct_body_calls"],s["external_direct_body_calls"]),(231,16,215));self.assertEqual((s["indirect_body_calls"],s["bounded_local_callback_targets"],s["strict_interior_ingress"]),(2,2,0))
 def test_provider_boundary(self):
  p=self.report["provider_boundary"];self.assertEqual((p["easylogger_calls"],p["lvgl_calls"],p["iar_dlib_calls"],p["mpaland_printf_calls"],p["first_party_calls"]),(20,154,13,10,18));self.assertFalse(p["new_version_discriminator"]);self.assertFalse(p["private_generating_commit_recoverable"])
 def test_no_embedded_dependency_or_routing(self):
  self.assertEqual(self.report["identity"]["embedded_third_party_definitions"],[]);self.assertFalse(self.report["production"]["production_routed"])
if __name__=="__main__":unittest.main()
