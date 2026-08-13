import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SPEC=importlib.util.spec_from_file_location("g2_even_ai_animation",ROOT/"tools/analyze_g2_even_ai_animation.py");MODULE=importlib.util.module_from_spec(SPEC);sys.modules[SPEC.name]=MODULE;SPEC.loader.exec_module(MODULE)
class EvenAiAnimationTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.report=MODULE.analyze()
 def test_complete_object(self):
  s=self.report["surface"];self.assertEqual((s["linked_functions"],s["ghidra_discovered_functions"],s["restored_functions"]),(5,2,3));self.assertEqual((s["body_bytes"],s["physical_bytes"],s["noncode_bytes"]),(2036,2228,192));self.assertEqual((s["direct_body_calls"],s["internal_direct_body_calls"],s["external_direct_body_calls"]),(80,1,79));self.assertEqual((s["direct_bl_entry_sites"],s["indirect_body_calls"],s["strict_interior_ingress"]),(28,0,0))
 def test_provider_boundary(self):
  p=self.report["provider_boundary"];self.assertEqual((p["easylogger_calls"],p["iar_dlib_calls"],p["lvgl_calls"],p["first_party_calls"]),(60,1,2,15));self.assertEqual(p["cmsis_freertos_calls"],1);self.assertEqual(p["cmsis_freertos_seams"],["osKernelGetTickCount"]);self.assertEqual(p["freertos_kernel_calls"],0);self.assertIsNone(p["historical_even_ai_animation_commit"]);self.assertFalse(p["new_version_discriminator"])
 def test_no_embedded_dependency_or_routing(self):self.assertEqual(self.report["identity"]["embedded_third_party_definitions"],[]);self.assertFalse(self.report["production"]["production_routed"])
if __name__=="__main__":unittest.main()
