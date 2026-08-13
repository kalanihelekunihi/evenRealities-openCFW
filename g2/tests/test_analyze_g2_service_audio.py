import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"tools/analyze_g2_service_audio.py";S=importlib.util.spec_from_file_location("g2_service_audio",P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class G2ServiceAudioTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_complete_object(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['body_bytes'],s['physical_bytes']),(14,2676,2884));self.assertEqual((s['direct_body_calls'],s['internal_direct_body_calls'],s['external_direct_body_calls']),(113,9,104));self.assertEqual(s['strict_interior_ingress'],0)
 def test_indirect_callback_is_closed(self):
  s=self.r['surface'];self.assertEqual((s['indirect_body_calls'],s['resolved_indirect_body_calls']),(1,1));self.assertEqual((s['registered_external_callback_entries'],s['registered_external_callback_sites']),(2,3));self.assertEqual(self.r['provider_boundary']['registered_callback_entries'],['0x0058f4e4','0x0058f5e0'])
 def test_providers(self):
  p=self.r['provider_boundary'];self.assertEqual((p['easylogger_calls'],p['iar_dlib_calls'],p['cmsis_freertos_calls'],p['liblc3_calls']),(76,8,3,5));self.assertEqual((p['closed_service_algo_calls'],p['source_owned_file_runtime_calls'],p['littlefs_backend_adapter_calls'],p['first_party_notification_calls']),(2,7,2,1));self.assertEqual(p['liblc3_commit'],'96a3af0beb5487aca3b98a4b992a539a1f6d80d1')
 def test_no_embedded_dependency_or_routing(self):self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[]);self.assertFalse(self.r['provider_boundary']['new_version_discriminator']);self.assertFalse(self.r['production']['production_routed'])
if __name__=='__main__':unittest.main()
