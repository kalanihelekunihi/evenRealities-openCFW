import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_ui_health_page as h
import integrate_g2_ui_health_page_overlay as integration


class G2UIHealthPageIntegrationMetadataTests(unittest.TestCase):
 def test_component_description_retains_stock_imu_boundary(self):
  description=integration.COMPONENT_FUNCTION_DESCRIPTION
  self.assertIn('retained authenticated stock ICM45608 donor object',description)
  self.assertNotIn('TDK ICM45608',description)
  self.assertNotIn('clean-room ICM45608',description)


class G2UIHealthPageTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=h.analyze()
 def test_surface(self):
  x=self.r['surface'];self.assertEqual((x['linked_functions'],x['ghidra_discovered_functions'],x['restored_non_anchor_functions'],x['body_bytes'],x['physical_bytes']),(12,11,1,9414,10054));self.assertEqual((x['direct_body_calls'],x['internal_direct_body_calls'],x['external_direct_body_calls']),(678,12,666))
 def test_ingress(self):
  x=self.r['surface'];self.assertEqual((x['direct_bl_entry_sites'],x['stored_function_pointers'],x['indirect_body_calls'],x['classified_noncode_pseudo_bl_sites']),(19,2,0,1))
 def test_providers(self):
  p=self.r['provider_boundary'];self.assertEqual((p['lvgl_calls'],p['easylogger_calls'],p['cmsis_freertos_calls'],p['runtime_calls'],p['mpaland_printf_calls'],p['first_party_calls']),(437,55,0,4,36,134));self.assertIsNone(p['historical_health_page_commit']);self.assertFalse(p['new_version_discriminator'])
 def test_boundary(self):
  self.assertTrue(self.r['production']['production_routed']);self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[]);p=self.r['production'];self.assertEqual(tuple(p[x] for x in ('source_functions','compiled_text_bytes','compiled_rodata_bytes','generated_alignment_bytes','guarded_redirects','stock_function_bytes_redirected','generated_redirect_bytes','repurposed_liblc3_source_rodata_bytes','repurposed_generated_cave_bytes','retained_compatibility_bytes','strict_relocations')),(12,3978,328,10,12,9414,5000,1980,2434,640,269));self.assertEqual(p['generated_redirect_bytes']+p['repurposed_liblc3_source_rodata_bytes']+p['repurposed_generated_cave_bytes']+p['retained_compatibility_bytes'],self.r['surface']['physical_bytes']);self.assertEqual(p['hardware_validation'],'blocked by unavailable physical evidence');self.assertIn('blocked by unavailable physical evidence',p['hardware_blocker'])
if __name__=='__main__':unittest.main()
