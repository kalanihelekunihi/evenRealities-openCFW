import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class L2cMainTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  s=importlib.util.spec_from_file_location('l2c_main_audit',ROOT/'tools/analyze_g2_cordio_l2c_main.py');cls.m=importlib.util.module_from_spec(s);sys.modules[s.name]=cls.m;s.loader.exec_module(cls.m)
 def test_closure(self):
  r=self.m.analyze();m=r['module'];self.assertEqual((m['linked_function_count'],m['linked_function_bytes'],m['physical_bytes']),(11,1636,1736));self.assertEqual(m['source_only_functions'],[]);self.assertEqual((m['direct_bl_ingress_sites'],m['registered_function_pointers'],m['strict_interior_pointers']),(16,6,0));self.assertEqual(r['architecture']['control_block'],0x200737D8);self.assertFalse(r['lineage']['independent_release_discriminator'])
if __name__=='__main__':unittest.main()
