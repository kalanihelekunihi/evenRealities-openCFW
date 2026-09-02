from __future__ import annotations
import ctypes,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_mspi_lifecycle_425066.c";FIXTURE=ROOT/"tests/fixtures/bootloader_runtime_mspi_lifecycle_host.c";sys.path.insert(0,str(ROOT/"tools"));import analyze_g2_bootloader_mspi_lifecycle_425066 as analyzer
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.t=tempfile.TemporaryDirectory();o=Path(c.t.name)/("x.dylib" if sys.platform=="darwin" else "x.so");cmd=["/usr/bin/clang","-std=c11","-O2","-Wall","-Wextra","-Werror",str(FIXTURE)]+(["-dynamiclib"] if sys.platform=="darwin" else ["-shared","-fPIC"]);subprocess.run([*cmd,"-o",str(o)],check=True,capture_output=True,text=True);c.x=ctypes.CDLL(str(o));c.x.open_cfw_test_lifecycle_reset.argtypes=[ctypes.c_uint32]*8;c.x.open_cfw_test_lifecycle_run.argtypes=[ctypes.c_uint32]*2;c.x.open_cfw_test_lifecycle_run.restype=ctypes.c_uint32;c.x.open_cfw_test_lifecycle_state.argtypes=[ctypes.c_uint32];c.x.open_cfw_test_lifecycle_state.restype=ctypes.c_uint32;c.x.open_cfw_test_lifecycle_trace.argtypes=[ctypes.c_uint32];c.x.open_cfw_test_lifecycle_trace.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(c):c.t.cleanup()
 def reset(s,p=0x01bebebe,cfg=1,tcb=0x20070000,cq=0,hp=0,xip=0,delay=8,status=0):s.x.open_cfw_test_lifecycle_reset(p,cfg,tcb,cq,hp,xip,delay,status)
 def st(s,n):return s.x.open_cfw_test_lifecycle_state(n)
 def tr(s,n):return s.x.open_cfw_test_lifecycle_trace(n)
 def test_audit(s):r=analyzer.audit();s.assertTrue(r["production"]["routed"]);s.assertEqual(r["production"]["boundary_status"],"source_compiled");s.assertEqual(r["production"]["compiled_bytes"],296);s.assertEqual(r["production"]["source_owned_bytes"]+r["production"]["retained_official_bytes"],146994);s.assertEqual(r["production"]["next_frontier"],0x4250E6);s.assertEqual(r["successor"]["start"],0x4251C0);s.assertEqual(r["hardware_validation"],"blocked by unavailable physical evidence");s.assertEqual(r["hardware_operations"],[])
 def test_production_source_is_structured_c(s):
  text=SOURCE.read_text(encoding="utf-8");s.assertNotIn(".byte",text);s.assertNotIn("__asm__",text);s.assertIn("open_cfw_bootloader_mspi_enable_425066",text);s.assertIn("open_cfw_bootloader_mspi_disable_4250f0",text);s.assertIn("open_cfw_bootloader_mspi_deinitialize_42516c",text)
 def test_enable_with_tcb_resets_queue_state(s):
  s.reset();s.assertEqual(s.x.open_cfw_test_lifecycle_run(0,0),0);s.assertEqual(s.st(0),0x03bebebe);s.assertEqual([s.st(i) for i in range(4,12)],[0,0,0,0,0,0,0,0]);s.assertEqual((s.st(14),s.st(15),s.st(16),s.tr(0),s.tr(5)),(0,0,1,1,0x00400080))
 def test_enable_without_tcb_preserves_queue_state(s):
  s.reset(tcb=0);s.assertEqual(s.x.open_cfw_test_lifecycle_run(0,0),0);s.assertEqual((s.st(4),s.st(14),s.tr(0)),(0xa5a5a5a5,0xa5,0))
 def test_enable_guards(s):
  s.reset(p=0);s.assertEqual(s.x.open_cfw_test_lifecycle_run(0,0),2);s.reset(cfg=0);s.assertEqual(s.x.open_cfw_test_lifecycle_run(0,0),7);s.reset();s.assertEqual(s.x.open_cfw_test_lifecycle_run(0,1),2)
 def test_disable_idempotent_and_busy(s):
  s.reset();s.assertEqual(s.x.open_cfw_test_lifecycle_run(1,0),0);s.assertEqual(s.tr(1),0);s.reset(p=0x03bebebe,cq=1);s.assertEqual(s.x.open_cfw_test_lifecycle_run(1,0),3);s.assertEqual(s.st(0),0x03bebebe);s.reset(p=0x03bebebe,hp=1);s.assertEqual(s.x.open_cfw_test_lifecycle_run(1,0),3)
 def test_disable_cq_error_and_success_xip_delay(s):
  s.reset(p=0x03bebebe,xip=1,status=44);s.assertEqual(s.x.open_cfw_test_lifecycle_run(1,0),44);s.assertEqual((s.tr(1),s.tr(2),s.tr(3),s.st(0)),(1,0,0,0x03bebebe));s.reset(p=0x03bebebe,xip=1,delay=4);s.assertEqual(s.x.open_cfw_test_lifecycle_run(1,0),0);s.assertEqual((s.tr(1),s.tr(2),s.tr(3),s.tr(4),s.st(0)),(1,1,1,4,0x01bebebe))
 def test_deinitialize_releases_even_when_nested_disable_is_busy(s):
  s.reset(p=0x03bebebe,cq=1);s.assertEqual(s.x.open_cfw_test_lifecycle_run(2,0),0);s.assertEqual((s.st(0),s.st(1)),(0x02bebebe,0))
 def test_deinitialize_normal(s):
  s.reset(p=0x03bebebe,tcb=0);s.assertEqual(s.x.open_cfw_test_lifecycle_run(2,0),0);s.assertEqual((s.st(0),s.st(1)),(0x00bebebe,0))
if __name__=="__main__":unittest.main()
