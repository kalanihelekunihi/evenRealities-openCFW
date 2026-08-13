import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"tools/analyze_g2_service_em9305_dfu.py";S=importlib.util.spec_from_file_location("g2_em9305_dfu",P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class G2Em9305DfuTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_complete_object(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['restored_functions'],s['path_anchored_functions'],s['body_bytes'],s['physical_bytes'],s['noncode_bytes'],s['reachable_instructions']),(7,1,6,2802,2826,24,1062));self.assertEqual((s['direct_body_calls'],s['internal_direct_body_calls'],s['external_direct_body_calls'],s['indirect_body_calls'],s['direct_bl_entry_sites'],s['strict_interior_ingress']),(156,4,152,0,7,0))
 def test_provider_closure_and_vendor_negative(self):
  p=self.r['provider_boundary'];self.assertEqual((p['easylogger_calls'],p['source_owned_file_heap_calls'],p['iar_dlib_calls'],p['shared_nanopb_initializer_calls'],p['first_party_calls'],p['direct_em9305_packetcraft_calls']),(125,18,4,1,4,0));self.assertFalse(p['new_version_discriminator']);self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[])
 def test_behavior_and_routing(self):self.assertTrue(all(self.r['behavior'].values()));self.assertFalse(self.r['production']['production_routed'])
if __name__=='__main__':unittest.main()
