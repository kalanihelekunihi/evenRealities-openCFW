import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'tools/analyze_g2_service_box_detect.py';S=importlib.util.spec_from_file_location('analyze_g2_service_box_detect',P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class ServiceBoxDetectTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_surface(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['restored_functions'],s['body_bytes'],s['physical_bytes']),(34,31,3584,3912));self.assertEqual((s['direct_bl_entry_sites'],s['indirect_body_calls'],s['strict_interior_ingress'],s['stored_function_entry_pointers']),(65,0,0,4))
 def test_providers(self):
  p=self.r['provider_boundary'];self.assertEqual(tuple(p[x] for x in ('easylogger_calls','iar_dlib_calls','cmsis_freertos_calls','first_party_calls')),(130,7,13,22));self.assertEqual(tuple(p['cmsis_freertos_seams'][x] for x in ('osTimerNew','osTimerStart','osTimerStop','osTimerIsRunning','osTimerDelete')),(2,2,6,1,2));self.assertIsNone(p['historical_box_detect_commit']);self.assertFalse(p['new_version_discriminator'])
 def test_claims(self):
  self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[])
  self.assertEqual(self.r['production'],{'production_routed':True,'source_functions':34,'compiled_text_bytes':1626,'alignment_bytes':36,'strict_relocations':77,'replaced_stock_body_bytes':3584,'hardware_validation':'deferred by project direction'})
