import importlib.util,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'tools/analyze_g2_efs_transport.py';S=importlib.util.spec_from_file_location('g2_efs_transport_test',P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class EfsTransportAuditTest(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_surface(self):self.assertEqual((self.r['surface']['linked_functions'],self.r['surface']['body_bytes'],self.r['surface']['physical_bytes'],self.r['surface']['indirect_body_calls']),(2,1990,2152,4));self.assertEqual(self.r['surface']['indirect_call_sites'],[0x4D0E6A,0x4D10C6,0x4D128A,0x4D14B0])
 def test_providers(self):
  p=self.r['provider_boundary'];self.assertEqual((p['easylogger_calls'],p['cmsis_freertos_calls'],p['runtime_calls'],p['efs_service_calls'],p['crc16_calls'],p['heap_wrapper_calls'],p['first_party_calls'],p['registered_callback_calls']),(60,1,8,5,4,6,3,4));self.assertEqual(p['callback_slots'],['0x2000096C','0x20000970']);self.assertIsNone(p['historical_efs_transport_commit'])
 def test_ownership(self):self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[]);self.assertTrue(self.r['production']['production_routed']);self.assertFalse(self.r['production']['software_functional_gap']);self.assertEqual(self.r['production']['hardware_validation'],'blocked')
if __name__=='__main__':unittest.main()
