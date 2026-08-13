import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'tools/analyze_g2_device_mgr.py';S=importlib.util.spec_from_file_location('analyze_g2_device_mgr',P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class DeviceMgrTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_surface(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['restored_functions'],s['body_bytes'],s['physical_bytes'],s['noncode_bytes']),(20,16,2484,2756,272));self.assertEqual((s['direct_bl_entry_sites'],s['stored_aligned_function_entry_pointers'],s['strict_interior_ingress']),(18,4,0))
 def test_providers(self):
  p=self.r['provider_boundary'];self.assertEqual(tuple(p[x] for x in ('easylogger_calls','cmsis_freertos_calls','freertos_kernel_calls','iar_dlib_calls','closed_first_party_calls','bounded_first_party_calls')),(75,10,1,3,34,14));self.assertEqual(p['cmsis_freertos_seams'],['osThreadNew','osThreadTerminate','osDelay','osTimerNew','osTimerStart','osMessageQueueNew','osMessageQueuePut','osMessageQueueGet']);self.assertEqual(p['freertos_kernel_seams'],['xTaskGetTickCount']);self.assertIsNone(p['historical_device_mgr_commit']);self.assertFalse(p['new_version_discriminator'])
 def test_claims(self):self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[]);self.assertFalse(self.r['production']['production_routed'])
 def test_bounded_indirect(self):
  s=self.r['surface'];self.assertEqual((s['indirect_body_calls'],s['bounded_indirect_body_calls']),(1,1))
