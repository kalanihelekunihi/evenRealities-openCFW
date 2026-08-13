import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class L2cSlaveTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  s=importlib.util.spec_from_file_location('l2c_slave_audit',ROOT/'tools/analyze_g2_cordio_l2c_slave.py');cls.m=importlib.util.module_from_spec(s);sys.modules[s.name]=cls.m;s.loader.exec_module(cls.m)
 def test_closure(self):
  r=self.m.analyze();m=r['module'];self.assertEqual((m['linked_function_count'],m['linked_function_bytes'],m['physical_bytes']),(6,1078,1148));self.assertEqual(m['source_only_functions'],['L2cDmSigReq']);self.assertEqual((m['direct_bl_ingress_sites'],m['registered_function_pointers'],m['strict_interior_pointers']),(4,2,0));self.assertEqual(r['architecture']['handle_validation'],'DmConnIdByHandle')
if __name__=='__main__':unittest.main()
