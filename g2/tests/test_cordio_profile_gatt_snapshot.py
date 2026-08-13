import importlib.util,sys,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'third_party/packetcraft-gatt-profile/verify_snapshot.py';S=importlib.util.spec_from_file_location('cg',P);M=importlib.util.module_from_spec(S);sys.modules[S.name]=M;S.loader.exec_module(M)
class SnapshotTests(unittest.TestCase):
 def test_snapshot(self):
  r=M.verify();self.assertEqual(r['source_functions'],6);self.assertEqual(r['selected_commit'],'3656312d6b73e2a2c1c8b33ee0385bc199dd97e6');self.assertIsNone(r['historical_g2_generating_commit'])
if __name__=='__main__':unittest.main()
