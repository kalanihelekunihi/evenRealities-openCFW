import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class AttsDynTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  s=importlib.util.spec_from_file_location('atts_dyn_audit',ROOT/'tools/analyze_g2_cordio_atts_dyn.py');cls.m=importlib.util.module_from_spec(s);sys.modules[s.name]=cls.m;s.loader.exec_module(cls.m);cls.r=cls.m.analyze()
 def test_exclusion(self):
  m=self.r['module'];self.assertEqual((m['linked_function_count'],m['source_inventory_functions']),(0,7));self.assertEqual(len(m['source_only_functions']),7);self.assertEqual(self.r['exclusion']['dynamic_group_provider_callers'],0);self.assertEqual(self.r['exclusion']['dynamic_heap_bytes_not_instantiated'],1280)
 def test_group_provider_closure(self):
  e=self.r['exclusion'];self.assertEqual(e['atts_add_group_callers'],[0x52DC10,0x52DC16,0x5361A8,0x5361C0,0x5361D8,0x5361F0,0x536208,0x536220]);self.assertEqual(e['atts_remove_group_callers'],[0x534DB8])
if __name__=='__main__':unittest.main()
