import ctypes,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; FIX=ROOT/'tests/fixtures/service_kvdb_host.c'
class ServiceKvdbCandidateTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.t=tempfile.TemporaryDirectory(); out=Path(cls.t.name)/'x.so'
  subprocess.run(['clang','-shared','-fPIC','-std=c11','-Wall','-Wextra','-Werror',str(FIX),'-o',str(out)],check=True); cls.l=ctypes.CDLL(str(out)); cls.l.open_cfw_service_kvdb_init.argtypes=[ctypes.c_void_p,ctypes.c_void_p]; cls.l.open_cfw_service_kvdb_init.restype=ctypes.c_int
 def setUp(self): self.l.host_reset()
 def test_valid_mount_counter_migrations_and_read_all(self):
  self.assertEqual(self.l.open_cfw_service_kvdb_init(1,2),0); self.assertEqual(self.l.host_controls(),2); self.assertEqual(self.l.host_boot(),5); self.assertEqual(self.l.host_migrations(),11); self.assertEqual(self.l.host_writes(),1); self.assertEqual(self.l.host_reads(),14)
 def test_magic_mismatch_and_missing_fail_without_write(self):
  self.l.host_magic(7,1); self.assertEqual(self.l.open_cfw_service_kvdb_init(None,None),9); self.assertEqual(self.l.host_writes(),0)
  self.l.host_reset(); self.l.host_magic(0,0); self.assertEqual(self.l.open_cfw_service_kvdb_init(None,None),9); self.assertEqual(self.l.host_writes(),0)
 def test_init_failure_and_invalidate_are_safe(self):
  self.l.host_init_rc(3); self.assertEqual(self.l.open_cfw_service_kvdb_init(None,None),8); self.assertEqual(self.l.open_cfw_service_kvdb_invalidate_magic(),9); self.assertEqual(self.l.host_writes(),0)
if __name__=='__main__':unittest.main()
