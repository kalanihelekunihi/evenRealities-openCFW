import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class SystemCloseTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  spec=importlib.util.spec_from_file_location('system_close',ROOT/'tools/analyze_g2_system_close.py');cls.m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=cls.m;spec.loader.exec_module(cls.m);cls.r=cls.m.analyze()
 def test_complete_surface(self):
  e={'linked_functions':20,'ghidra_discovered_functions':5,'restored_functions':15,'path_anchored_functions':10,'raw_path_references':27,'raw_path_referencing_functions':10,'body_bytes':4960,'physical_bytes':5368,'noncode_bytes':408,'reachable_instructions':1854,'direct_body_calls':296,'internal_direct_body_calls':25,'external_direct_body_calls':271,'indirect_body_calls':0,'direct_bl_entry_sites':40,'stored_entry_pointers':3,'raw_interior_word_collisions':8,'strict_interior_ingress':0}
  for k,v in e.items():self.assertEqual(self.r['surface'][k],v,k)
 def test_provider_boundary(self):
  p=self.r['provider_boundary'];self.assertEqual((p['easylogger_calls'],p['lvgl_calls'],p['iar_dlib_calls'],p['first_party_calls']),(130,99,5,37));self.assertEqual(p['direct_cmsis_freertos_calls'],0);self.assertEqual(p['lvgl_commit'],'344c7c318047b7348e1be8572a9fd4260c251cfa');self.assertIsNone(p['historical_system_close_commit']);self.assertFalse(p['new_version_discriminator'])
 def test_first_party_ui_policy(self):
  self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[]);self.assertTrue(all(self.r['behavior'].values()));self.assertFalse(self.r['production']['production_routed'])
if __name__=='__main__':unittest.main()
