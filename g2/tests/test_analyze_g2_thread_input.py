import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'tools/analyze_g2_thread_input.py';S=importlib.util.spec_from_file_location('analyze_g2_thread_input',P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class ThreadInputTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_surface(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['restored_functions'],s['body_bytes'],s['physical_bytes'],s['noncode_bytes']),(23,18,2090,2296,206));self.assertEqual((s['direct_bl_entry_sites'],s['stored_function_entry_pointers'],s['indirect_body_calls'],s['strict_interior_ingress']),(20,1,1,0))
 def test_providers(self):
  p=self.r['provider_boundary'];self.assertEqual(tuple(p[x] for x in ('easylogger_calls','iar_dlib_calls','cmsis_freertos_calls','source_owned_runtime_wrapper_calls','closed_thread_manager_calls','closed_first_party_calls','bounded_open_first_party_calls')),(90,3,10,1,3,9,11));self.assertEqual(p['freertos_kernel_direct_calls'],0);self.assertEqual(p['cmsis_wrappers'],['osThreadNew','osThreadTerminate','osThreadFlagsSet','osThreadFlagsWait','osDelay','osMessageQueueNew','osMessageQueuePut','osMessageQueueGet','osMessageQueueDelete']);self.assertFalse(p['new_version_discriminator'])
 def test_claims(self):self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[]);self.assertFalse(self.r['production']['production_routed'])
