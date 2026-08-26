import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"tools/analyze_g2_lvgl_font_manager.py";S=importlib.util.spec_from_file_location("g2_lvgl_font_manager",P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class G2LvglFontManagerTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_complete_object(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['body_bytes'],s['physical_bytes'],s['noncode_bytes'],s['reachable_instructions']),(8,2590,2972,382,973));self.assertEqual((s['direct_body_calls'],s['internal_direct_body_calls'],s['external_direct_body_calls'],s['indirect_body_calls'],s['direct_bl_entry_sites'],s['stored_entry_pointers'],s['strict_interior_ingress']),(149,9,140,0,12,0,0))
 def test_provider_closure(self):
  p=self.r['provider_boundary'];self.assertEqual((p['easylogger_calls'],p['iar_dlib_calls'],p['g2_mspi_lock_calls'],p['source_owned_heap_wrapper_calls'],p['lvgl_freetype_adapter_calls']),(125,2,2,9,2));self.assertEqual((p['freetype_version'],p['freetype_commit']),("2.9.1","86bc8a95056c97a810986434a3f268cbe67f2902"));self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[])
 def test_behavior_and_routing(self):
  self.assertTrue(all(self.r['behavior'].values()))
  self.assertEqual(self.r['production'],{"production_routed":True,"source_files":1,"source_functions":8,"compiled_text_bytes":904,"alignment_bytes":10,"strict_relocations":19,"guarded_redirects":8,"routed_stock_bytes":2590,"retained_compatibility_bytes":382})
if __name__=='__main__':unittest.main()
