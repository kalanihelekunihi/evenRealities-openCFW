import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'tools/analyze_g2_sensor_hub.py';S=importlib.util.spec_from_file_location('analyze_g2_sensor_hub',P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class SensorHubTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_surface(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['restored_functions'],s['body_bytes'],s['physical_bytes'],s['noncode_bytes']),(31,26,4026,4408,382));self.assertEqual((s['direct_bl_entry_sites'],s['stored_function_entry_pointers'],s['indirect_body_calls'],s['strict_interior_ingress'],s['raw_interior_word_collisions']),(61,3,1,0,4))
 def test_providers(self):
  p=self.r['provider_boundary'];self.assertEqual(tuple(p[x] for x in ('easylogger_calls','admitted_lvgl_calls','closed_first_party_calls','cmsis_freertos_calls','translation_lookup_calls','nanopb_calls','bounded_open_first_party_calls')),(130,69,36,9,8,1,1));self.assertEqual(p['freertos_kernel_direct_calls'],0);self.assertIsNone(p['embedded_sensor_fusion_library']);self.assertEqual(p['cmsis_wrappers'],['osKernelGetTickCount','osThreadNew','osThreadTerminate','osTimerNew','osTimerStart','osTimerStop','osMessageQueueNew','osMessageQueuePut','osMessageQueueGet']);self.assertFalse(p['new_version_discriminator'])
 def test_claims(self):self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[]);self.assertFalse(self.r['production']['production_routed'])
