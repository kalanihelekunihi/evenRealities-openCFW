import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'tools/analyze_g2_ota_transport.py';S=importlib.util.spec_from_file_location('g2_ota_transport_test',P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class OtaTransportAuditTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_surface(self):self.assertEqual((self.r['surface']['linked_functions'],self.r['surface']['body_bytes'],self.r['surface']['physical_bytes'],self.r['surface']['indirect_body_calls']),(3,2004,2292,4));self.assertEqual(self.r['surface']['indirect_call_sites'],[0x48D9CA,0x48DC26,0x48DDEC,0x48E012])
 def test_providers(self):
  p=self.r['provider_boundary'];self.assertEqual((p['easylogger_calls'],p['runtime_calls'],p['ota_service_calls'],p['crc16_calls'],p['heap_wrapper_calls'],p['first_party_calls'],p['registered_callback_calls']),(60,8,5,4,6,3,4));self.assertEqual(p['callback_slots'],['0x20003058','0x2000305C']);self.assertIsNone(p['historical_ota_transport_commit'])
 def test_ownership(self):self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[]);self.assertFalse(self.r['production']['production_routed'])
if __name__=='__main__':unittest.main()
