import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tools'))
import analyze_g2_navigation_ui as n
class G2NavigationUITests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=n.analyze()
 def test_complete_object(self):
  x=self.r['surface'];self.assertEqual((x['linked_functions'],x['ghidra_discovered_functions'],x['restored_non_anchor_functions'],x['body_bytes'],x['physical_bytes']),(61,32,29,36612,39056));self.assertEqual((x['direct_body_calls'],x['internal_direct_body_calls'],x['external_direct_body_calls']),(2376,139,2237))
 def test_ingress(self):
  x=self.r['surface'];self.assertEqual((x['direct_bl_entry_sites'],x['stored_function_start_pointers'],x['stored_interior_entry_pointers'],x['indirect_body_calls']),(152,14,5,0));self.assertEqual((x['classified_noncode_pseudo_bl_sites'],x['classified_wide_interior_branches']),(2,19))
 def test_provider_boundary(self):
  p=self.r['provider_boundary'];self.assertEqual((p['lvgl_calls'],p['easylogger_calls'],p['cmsis_freertos_calls'],p['runtime_calls'],p['nanopb_calls'],p['mpaland_printf_calls'],p['first_party_calls']),(702,1245,20,67,22,2,179));self.assertIsNone(p['historical_navigation_ui_commit']);self.assertFalse(p['new_version_discriminator'])
 def test_no_route_or_embedded_body(self):self.assertFalse(self.r['production']['production_routed']);self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[])
if __name__=='__main__':unittest.main()
