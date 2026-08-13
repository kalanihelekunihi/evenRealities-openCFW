import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/"tools/analyze_g2_liblc3.py";S=importlib.util.spec_from_file_location("g2_liblc3",P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class G2Liblc3Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_source_selection(self):
  s=self.r['selected'];self.assertEqual((s['version'],s['commit']),('v1.1.3','96a3af0beb5487aca3b98a4b992a539a1f6d80d1'));self.assertFalse(s['exact_public_commit_recoverable']);self.assertFalse(s['exact_private_checkout_recoverable'])
 def test_compatibility_interval(self):
  c=self.r['compatibility'];self.assertTrue(c['sns_flt_max_present']);self.assertTrue(c['pre_ltpf_bypass_layout']);self.assertEqual(c['first_excluded_successor'],'9f1e206b34546e858e11065151ae38ff4efc4c77')
 def test_stock_surface_and_snapshot(self):self.assertEqual(self.r['stock']['public_entries'],4);self.assertEqual(self.r['stock']['direct_public_entry_calls'],5);self.assertEqual(self.r['stock']['encoder_field_offsets'],{'dt':0,'sr':1,'sr_pcm':2});self.assertEqual(self.r['snapshot'],{'files':38,'byte_identical':True})
 def test_production_gate(self):self.assertFalse(self.r['production']['production_routed']);self.assertEqual(len(self.r['production']['remaining_gates']),4)
if __name__=='__main__':unittest.main()
