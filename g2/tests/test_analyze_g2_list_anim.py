import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'tools/analyze_g2_list_anim.py';S=importlib.util.spec_from_file_location('analyze_g2_list_anim',P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class ListAnimTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_surface(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['restored_functions'],s['body_bytes'],s['physical_bytes']),(11,4,1348,1460));self.assertEqual((s['direct_bl_entry_sites'],s['indirect_body_calls'],s['strict_interior_ingress'],s['stored_function_entry_pointers']),(37,0,0,1))
 def test_providers(self):
  p=self.r['provider_boundary'];self.assertEqual(tuple(p[x] for x in ('easylogger_calls','iar_dlib_calls','cmsis_freertos_calls','lvgl_calls','closed_fade_anim_calls')),(40,2,2,27,2));self.assertEqual(p['cmsis_freertos_seams'],['osKernelGetTickCount']);self.assertEqual(p['freertos_kernel_seams'],[]);self.assertIsNone(p['historical_list_anim_commit']);self.assertFalse(p['new_version_discriminator'])
 def test_claims(self):self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[]);self.assertFalse(self.r['production']['production_routed'])
if __name__=='__main__':unittest.main()
