import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'tools/analyze_g2_sync_info.py';S=importlib.util.spec_from_file_location('analyze_g2_sync_info',P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class SyncInfoTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_surface(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['restored_functions'],s['body_bytes'],s['physical_bytes'],s['noncode_bytes']),(3,0,780,860,80));self.assertEqual((s['direct_bl_entry_sites'],s['stored_aligned_function_entry_pointers'],s['strict_interior_ingress']),(8,1,0))
 def test_providers(self):
  p=self.r['provider_boundary'];self.assertEqual(tuple(p[x] for x in ('easylogger_calls','iar_dlib_calls','nanopb_calls','closed_first_party_calls')),(30,8,6,11));self.assertEqual(p['nanopb_commit'],'98bf4db69897b53434f3d0ba72e0a3ab1a902824');self.assertEqual(p['cmsis_freertos_seams'],[]);self.assertEqual(p['freertos_kernel_seams'],[]);self.assertIsNone(p['historical_sync_info_commit']);self.assertFalse(p['new_version_discriminator'])
 def test_claims(self):self.assertEqual(self.r['identity']['embedded_third_party_definitions'],[]);self.assertFalse(self.r['production']['production_routed'])
