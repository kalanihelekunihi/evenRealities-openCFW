import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_ui_stock_page as s
class G2UIStockPageTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=s.analyze()
 def test_complete_object(self):
  x=self.r['surface'];self.assertEqual((x['linked_functions'],x['ghidra_discovered_functions'],x['restored_non_anchor_functions'],x['body_bytes'],x['physical_bytes']),(34,32,2,13892,14852));self.assertEqual((x['direct_body_calls'],x['internal_direct_body_calls'],x['external_direct_body_calls']),(958,106,852))
 def test_ingress(self):
  x=self.r['surface'];self.assertEqual((x['direct_bl_entry_sites'],x['stored_function_pointers'],x['indirect_body_calls'],x['classified_wide_interior_branches']),(116,2,0,3))
 def test_provider_boundary(self):
  p=self.r['provider_boundary'];self.assertEqual((p['lvgl_calls'],p['easylogger_calls'],p['cmsis_freertos_calls'],p['runtime_calls'],p['first_party_calls']),(454,355,0,10,33));self.assertIsNone(p['historical_stock_page_commit']);self.assertFalse(p['new_version_discriminator'])
 def test_no_route_or_embedded_body(self):self.assertFalse(self.r['production']['production_routed']);self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[])
if __name__=='__main__':unittest.main()
