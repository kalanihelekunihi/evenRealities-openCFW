import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class L2cMasterTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  s=importlib.util.spec_from_file_location('l2c_master_audit',ROOT/'tools/analyze_g2_cordio_l2c_master.py');cls.m=importlib.util.module_from_spec(s);sys.modules[s.name]=cls.m;s.loader.exec_module(cls.m)
 def test_closure(self):
  r=self.m.analyze();m=r['module'];self.assertEqual((m['linked_function_count'],m['linked_function_bytes'],m['physical_bytes']),(3,658,700));self.assertEqual(m['source_only_functions'],[]);self.assertEqual((m['direct_bl_ingress_sites'],m['registered_function_pointers'],m['strict_interior_pointers']),(3,1,0));self.assertFalse(r['lineage']['independent_release_discriminator'])
  self.assertEqual((r['production']['status'],r['production']['stock_bytes_replaced'],r['production']['compiled_text_bytes'],r['production']['alignment_bytes'],r['production']['strict_relocations']),('routed',658,286,2,5))
if __name__=='__main__':unittest.main()
