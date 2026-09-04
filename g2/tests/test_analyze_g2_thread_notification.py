import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ThreadNotificationTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  spec=importlib.util.spec_from_file_location("thread_notification",ROOT/"tools/analyze_g2_thread_notification.py");cls.m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=cls.m;spec.loader.exec_module(cls.m);cls.r=cls.m.analyze()
 def test_surface(self):
  expected={"linked_functions":12,"ghidra_discovered_functions":9,"restored_functions":3,"path_anchored_functions":3,"body_bytes":730,"physical_bytes":816,"outer_pool_bytes":86,"direct_body_calls":58,"internal_direct_body_calls":8,"external_direct_body_calls":50,"indirect_body_calls":0,"direct_bl_entry_sites":9,"stored_entry_pointers":2}
  for key,value in expected.items():self.assertEqual(self.r["surface"][key],value,key)
 def test_cmsis_seam(self):
  p=self.r["provider_boundary"];self.assertEqual((p["easylogger_calls"],p["cmsis_freertos_calls"],p["first_party_calls"]),(30,8,12));self.assertEqual(p["cmsis_freertos_commit"],"d213f261b5be6bb29a7cce8b84071706b72f4d53");self.assertEqual(set(p["cmsis_wrappers"]),{"osThreadNew","osThreadTerminate","osThreadFlagsSet","osThreadFlagsWait","osDelay","osMessageQueueNew","osMessageQueueGet","osMessageQueueDelete"});self.assertFalse(p["new_version_discriminator"])
 def test_production_route(self):
  p=self.r["production"];self.assertTrue(p["production_routed"]);self.assertFalse(p["software_functional_gap"]);self.assertEqual(p["source_functions"],12);self.assertEqual(p["compiled_text_bytes"],{"apple-clang":400,"linux-clang":400});self.assertEqual(p["in_place_source_bytes"],2);self.assertEqual(p["strict_relocations"],{"apple-clang":31,"linux-clang":31});self.assertEqual(p["stock_replaced_bytes"],730);self.assertEqual(p["retained_diagnostic_pool_bytes"],86);self.assertEqual(p["hardware_validation"],"blocked by unavailable physical evidence")
if __name__=="__main__":unittest.main()
