from __future__ import annotations
import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'third_party/ambiqsuite-amota-profile/verify_snapshot.py';S=importlib.util.spec_from_file_location('amota_snapshot_test',P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class AmbiqSuiteAmotaSnapshotTests(unittest.TestCase):
 def test_snapshot(self):
  r=M.verify();self.assertEqual(r['files'],3);self.assertEqual(r['selected_release'],'2.5.1');self.assertEqual(r['stable_release_imports'],4);self.assertIsNone(r['historical_g2_generating_commit'])
if __name__=='__main__':unittest.main()
