import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_ui_widget_news_page as n
class G2UIWidgetNewsPageTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=n.analyze()
 def test_complete_object(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['ghidra_discovered_functions'],s['restored_non_anchor_functions'],s['body_bytes'],s['physical_bytes']),(45,31,14,19058,20668));self.assertEqual((s['direct_body_calls'],s['internal_direct_body_calls'],s['external_direct_body_calls']),(1252,56,1196))
 def test_ingress(self):
  s=self.r['surface'];self.assertEqual((s['direct_bl_entry_sites'],s['stored_function_pointers'],s['indirect_body_calls'],s['classified_pseudo_bl'],s['classified_wide_interior_branches']),(70,12,0,7,8))
 def test_provider_boundary(self):
  p=self.r['provider_boundary'];self.assertEqual((p['lvgl_calls'],p['easylogger_calls'],p['cmsis_freertos_calls'],p['runtime_calls'],p['first_party_calls']),(508,565,8,36,79));self.assertFalse(p['new_version_discriminator']);self.assertIsNone(p['historical_news_page_commit'])
 def test_no_route_or_embedded_body(self):self.assertFalse(self.r['production']['production_routed']);self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[])
if __name__=='__main__':unittest.main()
