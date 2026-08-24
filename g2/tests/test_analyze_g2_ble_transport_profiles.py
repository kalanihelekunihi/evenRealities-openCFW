from __future__ import annotations
import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'tools/analyze_g2_ble_transport_profiles.py';S=importlib.util.spec_from_file_location('ble_transport_profiles',P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class BleTransportProfileTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_complete_partition(self):self.assertEqual(self.r['aggregate'],{'modules':4,'linked_functions':25,'body_bytes':2698,'physical_bytes':3000,'production_routed':True});self.assertEqual(set(self.r['modules']),{'eus','ess','efs','nus'})
 def test_protocol_family(self):
  for n,(event,handle) in {'eus':(0xA8,0x844),'ess':(0xA9,0x864),'efs':(0xAA,0x884),'nus':(0xAB,0x8A4)}.items():
   p=self.r['modules'][n]['protocol'];self.assertEqual(p['control_block_bytes'],4);self.assertEqual((p['send_event'],p['provider_handle']),(event,handle))
 def test_first_party_boundary(self):
  s=self.r['upstream_sweep'];self.assertEqual(s['exact_public_symbol_hits'],0);self.assertFalse(s['ambiqsuite_contains_any_module']);self.assertFalse(s['nordic_nus_api_match']);self.assertFalse(s['third_party_source_dependency_identified']);self.assertIsNone(s['historical_g2_generating_commit']);self.assertEqual({x['ownership'] for x in self.r['modules'].values()},{'g2_local_cordio_adapter'})
 def test_production_closure(self):
  self.assertEqual(self.r['production'],{'source_admitted':True,'production_routed':True,'source_functions':25,'compiled_text_bytes':1240,'alignment_bytes':10,'stock_replaced_bytes':2698,'retained_literal_pool_bytes':302,'strict_relocations':45,'software_functional_gap':False,'hardware_validation':'blocked','hardware_blocker':'No authorized responsive G2/EM9305 peer or captured dual-device CCC/RX/TX timing evidence is available.'})
if __name__=='__main__':unittest.main()
