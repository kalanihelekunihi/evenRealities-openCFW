from __future__ import annotations
import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'third_party/ambiqsuite-ancc-profile/verify_snapshot.py';S=importlib.util.spec_from_file_location('ancc_snapshot',P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class AmbiqSuiteAnccSnapshotTests(unittest.TestCase):
 def test_snapshot(self):
  r=M.verify();self.assertEqual(r['files'],2);self.assertEqual(r['upstream_source_definitions'],17);self.assertEqual(r['selected_release'],'2.5.1');self.assertIsNone(r['historical_g2_generating_commit'])
if __name__=='__main__':unittest.main()
