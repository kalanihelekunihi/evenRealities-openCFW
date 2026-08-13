import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class L2cCocTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  s=importlib.util.spec_from_file_location('l2c_coc_audit',ROOT/'tools/analyze_g2_cordio_l2c_coc.py');cls.m=importlib.util.module_from_spec(s);sys.modules[s.name]=cls.m;s.loader.exec_module(cls.m)
 def test_exclusion(self):
  r=self.m.analyze();m=r['module'];self.assertEqual((m['linked_function_count'],m['source_inventory_functions']),(0,67));self.assertEqual(len(m['source_only_functions']),67);self.assertEqual(r['exclusion']['coc_initializers'],0);self.assertEqual(r['exclusion']['dm_conn_register_callers'],[0x4B5140,0x4B7ED2,0x537CF2]);self.assertFalse(r['lineage']['stock_body_version_discriminated'])
if __name__=='__main__':unittest.main()
