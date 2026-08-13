import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_ui_health_page as h
class G2UIHealthPageTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=h.analyze()
 def test_surface(self):
  x=self.r['surface'];self.assertEqual((x['linked_functions'],x['ghidra_discovered_functions'],x['restored_non_anchor_functions'],x['body_bytes'],x['physical_bytes']),(12,11,1,9414,10054));self.assertEqual((x['direct_body_calls'],x['internal_direct_body_calls'],x['external_direct_body_calls']),(678,12,666))
 def test_ingress(self):
  x=self.r['surface'];self.assertEqual((x['direct_bl_entry_sites'],x['stored_function_pointers'],x['indirect_body_calls'],x['classified_noncode_pseudo_bl_sites']),(19,2,0,1))
 def test_providers(self):
  p=self.r['provider_boundary'];self.assertEqual((p['lvgl_calls'],p['easylogger_calls'],p['cmsis_freertos_calls'],p['runtime_calls'],p['mpaland_printf_calls'],p['first_party_calls']),(437,55,0,4,36,134));self.assertIsNone(p['historical_health_page_commit']);self.assertFalse(p['new_version_discriminator'])
 def test_boundary(self):self.assertFalse(self.r['production']['production_routed']);self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[])
if __name__=='__main__':unittest.main()
