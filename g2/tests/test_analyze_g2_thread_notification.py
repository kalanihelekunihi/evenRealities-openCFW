import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ThreadNotificationTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  spec=importlib.util.spec_from_file_location("thread_notification",ROOT/"tools/analyze_g2_thread_notification.py");cls.m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=cls.m;spec.loader.exec_module(cls.m);cls.r=cls.m.analyze()
 def test_surface(self):
  expected={"linked_functions":11,"ghidra_discovered_functions":9,"restored_functions":2,"path_anchored_functions":3,"body_bytes":702,"physical_bytes":816,"outer_pool_bytes":114,"direct_body_calls":56,"internal_direct_body_calls":8,"external_direct_body_calls":48,"indirect_body_calls":0,"direct_bl_entry_sites":9,"stored_entry_pointers":2}
  for key,value in expected.items():self.assertEqual(self.r["surface"][key],value,key)
 def test_cmsis_seam(self):
  p=self.r["provider_boundary"];self.assertEqual((p["easylogger_calls"],p["cmsis_freertos_calls"],p["first_party_calls"]),(30,7,11));self.assertEqual(p["cmsis_freertos_commit"],"d213f261b5be6bb29a7cce8b84071706b72f4d53");self.assertEqual(set(p["cmsis_wrappers"]),{"osThreadNew","osThreadFlagsSet","osThreadFlagsWait","osDelay","osMessageQueueNew","osMessageQueueGet","osMessageQueueDelete"});self.assertFalse(p["new_version_discriminator"])
 def test_not_routed(self):self.assertFalse(self.r["production"]["production_routed"])
if __name__=="__main__":unittest.main()
