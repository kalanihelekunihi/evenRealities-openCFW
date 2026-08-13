import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class TranslateUiTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  s=importlib.util.spec_from_file_location('translate_ui',ROOT/'tools/analyze_g2_translate_ui.py');cls.m=importlib.util.module_from_spec(s);sys.modules[s.name]=cls.m;s.loader.exec_module(cls.m);cls.r=cls.m.analyze()
 def test_complete_surface(self):
  self.assertEqual(self.r['surface'],{'linked_functions':29,'ghidra_discovered_functions':7,'restored_functions':22,'path_anchored_functions':7,'body_bytes':5288,'physical_bytes':5730,'noncode_bytes':442,'reachable_instructions':1942,'direct_body_calls':367,'internal_direct_body_calls':21,'external_direct_body_calls':346,'indirect_body_calls':1,'direct_bl_entry_sites':41,'stored_entry_pointers':13,'strict_interior_ingress':0})
 def test_provider_boundary(self):
  p=self.r['provider_boundary'];self.assertEqual(tuple(p[x] for x in ('easylogger_calls','lvgl_calls','iar_dlib_calls','cmsis_freertos_calls','first_party_calls','bounded_first_party_indirect_calls')),(175,125,10,2,34,1));self.assertEqual(p['cmsis_freertos_commit'],'d213f261b5be6bb29a7cce8b84071706b72f4d53');self.assertIsNone(p['historical_translate_ui_commit']);self.assertFalse(p['new_version_discriminator'])
 def test_no_embedded_dependency_or_production_claim(self):
  self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[]);self.assertFalse(self.r['production']['production_routed'])
if __name__=='__main__':unittest.main()
