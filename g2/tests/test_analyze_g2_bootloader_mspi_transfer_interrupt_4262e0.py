from __future__ import annotations
import ctypes,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"research/admission/bootloader_mspi_transfer_interrupt_4262e0/runtime_bootloader_mspi_transfer_interrupt_candidate.c";FIXTURE=SOURCE.parent/"host_fixture.c";sys.path.insert(0,str(ROOT/"tools"));import analyze_g2_bootloader_mspi_transfer_interrupt_4262e0 as analyzer
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.t=tempfile.TemporaryDirectory();o=Path(c.t.name)/("x.dylib" if sys.platform=="darwin" else "x.so");cmd=["/usr/bin/clang","-std=c11","-O2","-Wall","-Wextra","-Werror",str(SOURCE),str(FIXTURE)]+(["-dynamiclib"] if sys.platform=="darwin" else ["-shared","-fPIC"]);subprocess.run([*cmd,"-o",str(o)],check=True,capture_output=True,text=True);c.x=ctypes.CDLL(str(o));c.x.open_cfw_test_transfer_reset.argtypes=[ctypes.c_uint32]*12;c.x.open_cfw_test_transfer_run.argtypes=[ctypes.c_uint32]*3;c.x.open_cfw_test_transfer_run.restype=ctypes.c_uint32;c.x.open_cfw_test_transfer_state.argtypes=[ctypes.c_uint32];c.x.open_cfw_test_transfer_state.restype=ctypes.c_uint32;c.x.open_cfw_test_transfer_trace.argtypes=[ctypes.c_uint32];c.x.open_cfw_test_transfer_trace.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(c):c.t.cleanup()
 def reset(s,p=0x01bebebe,d=4,a=0,dr=0,cont=0,cq=0,hp=0,seq=0,inten=0xa5,intstat=0x3c,fifo=0,status=0):s.x.open_cfw_test_transfer_reset(p,d,a,dr,cont,cq,hp,seq,inten,intstat,fifo,status)
 def st(s,n):return s.x.open_cfw_test_transfer_state(n)
 def tr(s,n):return s.x.open_cfw_test_transfer_trace(n)
 def test_audit(s):r=analyzer.audit();s.assertFalse(r["production"]["routed"]);s.assertEqual(r["production"]["boundary_status"],"official_blob");s.assertEqual(r["production"]["source_owned_bytes"]+r["production"]["retained_official_bytes"],147350);s.assertEqual(r["production"]["next_frontier"],0x426506);s.assertFalse(r["bounded_mspi_code_closed"]);s.assertTrue(r["candidate_semantics_closed"]);s.assertEqual(r["adjacent_control"]["status"],"official_blob");s.assertEqual(r["hardware_validation"],"blocked by unavailable physical evidence");s.assertEqual(r["hardware_operations"],[])
 def test_rx_tx_and_interrupt_restore(s):
  for direction in (0,1):s.reset(dr=direction);s.assertEqual(s.x.open_cfw_test_transfer_run(0,100,0),0);s.assertEqual((s.tr(0),s.tr(1)),(1,0) if direction==0 else (0,1));s.assertEqual((s.tr(2),s.tr(3),s.tr(4),s.tr(5),s.st(0)),(1,2,0xa5,0xa5,0xa5))
 def test_transfer_guards(s):
  for kw in ({"d":10,"a":1},{"cont":1},{"cq":1},{"hp":1},{"seq":2}):s.reset(**kw);s.assertEqual(s.x.open_cfw_test_transfer_run(0,1,0),7);s.assertEqual(s.tr(3),0)
  s.reset(p=0);s.assertEqual(s.x.open_cfw_test_transfer_run(0,1,0),2);s.reset();s.assertEqual(s.x.open_cfw_test_transfer_run(0,1,1),2)
 def test_fifo_and_completion_errors_restore(s):
  s.reset(fifo=33);s.assertEqual(s.x.open_cfw_test_transfer_run(0,1,0),33);s.assertEqual((s.tr(2),s.tr(3),s.st(0)),(0,2,0xa5));s.reset(status=34);s.assertEqual(s.x.open_cfw_test_transfer_run(0,1,0),34);s.assertEqual((s.tr(2),s.tr(3),s.st(0)),(1,2,0xa5))
 def test_interrupt_apis(s):
  s.reset(inten=0x0f,intstat=0x3c);s.assertEqual(s.x.open_cfw_test_transfer_run(1,0x30,0),0);s.assertEqual(s.st(0),0x3f);s.assertEqual(s.x.open_cfw_test_transfer_run(2,0x0c,0),0);s.assertEqual(s.st(0),0x33);s.assertEqual(s.x.open_cfw_test_transfer_run(3,1,0),0);s.assertEqual(s.st(2),0x30);s.assertEqual(s.x.open_cfw_test_transfer_run(3,0,0),0);s.assertEqual(s.st(2),0x3c)
if __name__=="__main__":unittest.main()
