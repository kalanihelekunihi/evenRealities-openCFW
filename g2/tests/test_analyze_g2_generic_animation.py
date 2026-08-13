import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'tools/analyze_g2_generic_animation.py';S=importlib.util.spec_from_file_location('analyze_g2_generic_animation',P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class GenericAnimationTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_surface(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['restored_functions'],s['body_bytes'],s['physical_bytes']),(17,13,1622,1736));self.assertEqual((s['direct_bl_entry_sites'],s['indirect_body_calls'],s['strict_interior_ingress'],s['stored_function_entry_pointers']),(90,0,0,4));self.assertEqual((s['unaligned_start_word_collisions'],s['raw_instruction_word_interior_collisions']),(5,32))
 def test_providers(self):
  p=self.r['provider_boundary'];self.assertEqual(tuple(p[x] for x in ('easylogger_calls','iar_dlib_calls','cmsis_freertos_calls','source_owned_heap_calls','lvgl_calls','first_party_calls')),(40,4,3,3,27,3));self.assertEqual(p['cmsis_freertos_seams'],['osKernelGetTickCount']);self.assertEqual(p['freertos_kernel_seams'],[]);self.assertIsNone(p['historical_generic_animation_commit']);self.assertFalse(p['new_version_discriminator'])
 def test_claims(self):self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[]);self.assertFalse(self.r['production']['production_routed'])
if __name__=='__main__':unittest.main()
