import hashlib,importlib.util,sys,tempfile,unittest
from pathlib import Path
from unittest import mock
P=Path(__file__).resolve().parents[1]/"tools/analyze_g2_liblc3.py";S=importlib.util.spec_from_file_location("g2_liblc3",P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class G2Liblc3Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.r=M.analyze()
 def test_source_selection(self):
  s=self.r['selected'];self.assertEqual((s['version'],s['commit']),('v1.1.3','96a3af0beb5487aca3b98a4b992a539a1f6d80d1'));self.assertFalse(s['exact_public_commit_recoverable']);self.assertFalse(s['exact_private_checkout_recoverable'])
 def test_compatibility_interval(self):
  c=self.r['compatibility'];self.assertTrue(c['sns_flt_max_present']);self.assertTrue(c['pre_ltpf_bypass_layout']);self.assertEqual(c['first_excluded_successor'],'9f1e206b34546e858e11065151ae38ff4efc4c77')
 def test_stock_surface_and_snapshot(self):self.assertEqual(self.r['stock']['public_entries'],4);self.assertEqual(self.r['stock']['direct_public_entry_calls'],5);self.assertEqual(self.r['stock']['encoder_field_offsets'],{'dt':0,'sr':1,'sr_pcm':2});self.assertEqual(self.r['snapshot'],{'files':38,'byte_identical':True})
 def test_encoder_setup_stock_evidence_is_exact(self):
  e=self.r['stock']['encoder_setup']
  self.assertEqual(e['primary_span'],{'start':0x0059123A,'end_exclusive':0x00591374,'bytes':314,'sha256':'04f7f722ef30afdfae612d0f6622cb4811918c8a8f4dc30b1ee99f95f42572c8','authenticated':True})
  self.assertEqual(e['wrapper'],{'start':0x00591374,'end_exclusive':0x0059138A,'bytes':22,'sha256':'98ecf298571e96939bfefd863c514116a4e5ccf638b8023c395a465175da635d','callsite':0x00591382,'target':0x0059123A,'authenticated':True,'relationship':'direct-call-to-primary-entry'})
 def test_encoder_setup_primary_span_mutation_fails_closed(self):
  image=bytearray(M.IMAGE.read_bytes());image[M.SETUP_PRIMARY['start']-M.c.BASE]^=1
  with tempfile.TemporaryDirectory() as temporary:
   path=Path(temporary)/'mutated.bin';path.write_bytes(image)
   with mock.patch.object(M.c,'IMAGE_SHA256',hashlib.sha256(image).hexdigest()):
    with self.assertRaisesRegex(M.c.AuditError,'setup primary span changed'):M.analyze(path)
 def test_production_gate(self):self.assertFalse(self.r['production']['production_routed']);self.assertEqual(len(self.r['production']['remaining_gates']),4)
if __name__=='__main__':unittest.main()
