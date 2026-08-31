import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'tools/analyze_g2_cordio_gatt_profile.py';S=importlib.util.spec_from_file_location('gp',P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class GattProfileTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_source_identity(self):self.assertEqual(self.r['upstream']['selected_commit'],'3656312d6b73e2a2c1c8b33ee0385bc199dd97e6');self.assertEqual(self.r['upstream']['compatible_release_count'],4);self.assertIsNone(self.r['upstream']['historical_g2_generating_commit'])
 def test_surface(self):self.assertEqual(self.r['surface'],{'linked_functions':6,'source_owned_functions':6,'body_bytes':322,'physical_bytes':356,'direct_bl_entry_sites':8,'direct_body_calls':14,'stored_entry_pointers':2,'strict_interior_ingress':0})
 def test_functions_and_delta(self):self.assertEqual(self.r['functions'],['GattDiscover','GattValueUpdate','GattSetSvcChangedIdx','GattSendServiceChangedInd','GattReadCback','GattWriteCback']);self.assertEqual(self.r['local_delta']['upstream_terminal_call'],'AppDiscFindService');self.assertTrue(self.r['production']['source_admitted']);self.assertTrue(self.r['production']['production_routed'])
 def test_production_closure(self):
  p=self.r['production'];self.assertFalse(p['software_functional_gap']);self.assertEqual((p['source_functions'],p['compiled_text_bytes'],p['alignment_bytes'],p['stock_replaced_bytes'],p['strict_relocations'],p['retained_literal_pool_bytes']),(6,254,8,322,10,34));self.assertEqual(p['hardware_validation'],'blocked by unavailable physical evidence');self.assertIn('required for future qualification',p['hardware_blocker'])
if __name__=='__main__':unittest.main()
