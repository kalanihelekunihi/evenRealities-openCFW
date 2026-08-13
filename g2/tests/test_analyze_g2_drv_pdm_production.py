import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"tools/analyze_g2_drv_pdm_production.py";S=importlib.util.spec_from_file_location("g2_drv_pdm_production",P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class G2DrvPdmProductionTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_object(self):
  s=self.r['surface'];self.assertEqual((s['linked_functions'],s['body_bytes'],s['physical_bytes']),(6,610,704));self.assertEqual((s['direct_body_calls'],s['internal_direct_body_calls'],s['external_direct_body_calls']),(41,3,38));self.assertEqual((s['indirect_body_calls'],s['strict_interior_ingress']),(0,0))
 def test_upstream_seam(self):
  p=self.r['provider_boundary'];self.assertEqual((p['ambiqsuite_pdm_calls'],p['ambiqsuite_pdm_apis']),(13,12));self.assertEqual(p['ambiqsuite_selected_commit'],'5efc0228528a8adce5eae0d226fac85d2551eb3b');self.assertEqual(p['ambiqsuite_source_git_blob'],'23a440bfd6121509b0586f0afe1990fcf59dd8fb')
 def test_embedded_cmsis_and_behavior(self):self.assertEqual(len(self.r['identity']['embedded_third_party_definitions']),3);self.assertEqual((self.r['behavior']['output_samples'],self.r['behavior']['output_bytes']),(1600,3200))
 def test_gate(self):self.assertFalse(self.r['provider_boundary']['private_generating_commit_recoverable']);self.assertFalse(self.r['production']['production_routed'])
if __name__=='__main__':unittest.main()
