from __future__ import annotations
import ctypes,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"components/bootloader/core_overlay/runtime_mspi_device_configure_public_424be4.c";FIXTURE=ROOT/"tests/fixtures/bootloader_runtime_mspi_device_configure_public_host.c";sys.path.insert(0,str(ROOT/"tools"));import analyze_g2_bootloader_mspi_device_configure_public_424be4 as analyzer
H={3,5,7,9,11,13,15,17,19,21,23}
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.t=tempfile.TemporaryDirectory();o=Path(c.t.name)/("x.dylib" if sys.platform=="darwin" else "x.so");cmd=["/usr/bin/clang","-std=c11","-O2","-Wall","-Wextra","-Werror",str(FIXTURE)]+(["-dynamiclib"] if sys.platform=="darwin" else ["-shared","-fPIC"]);subprocess.run([*cmd,"-o",str(o)],check=True,capture_output=True,text=True);c.x=ctypes.CDLL(str(o));c.x.open_cfw_test_public_device_reset.argtypes=[ctypes.c_uint32]*9;c.x.open_cfw_test_public_device_run.argtypes=[ctypes.c_uint32];c.x.open_cfw_test_public_device_run.restype=ctypes.c_uint32;c.x.open_cfw_test_public_device_state.argtypes=[ctypes.c_uint32];c.x.open_cfw_test_public_device_state.restype=ctypes.c_uint32;c.x.open_cfw_test_public_device_trace.argtypes=[ctypes.c_uint32];c.x.open_cfw_test_public_device_trace.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(c):c.t.cleanup()
 def reset(s,m=0,p=0x01bebebe,cfg=1,src=99,tcb=1,f=14,d=4,rel=0,req=0):s.x.open_cfw_test_public_device_reset(m,p,cfg,src,tcb,f,d,rel,req)
 def st(s,n):return s.x.open_cfw_test_public_device_state(n)
 def tr(s,n):return s.x.open_cfw_test_public_device_trace(n)
 def test_audit(s):
    r=analyzer.audit();s.assertTrue(r["production"]["routed"]);s.assertEqual(r["production"]["boundary_status"],"source_compiled");s.assertEqual(r["production"]["compiled_bytes"],672);s.assertEqual(r["production"]["source_owned_bytes"]+r["production"]["retained_official_bytes"],147350);s.assertEqual(r["production"]["next_frontier"],0x424E84);s.assertEqual(r["next_code_frontier"],{"start":0x425066,"end":0x4250F0,"identity":"am_hal_mspi_enable","bytes":138,"status":"official_blob"});s.assertEqual(r["hardware_validation"],"blocked by unavailable physical evidence");s.assertEqual(r["hardware_operations"],[])
 def test_structured_source_has_no_raw_encoding(s):
  text=SOURCE.read_text();s.assertNotIn(".byte",text);s.assertNotIn("__asm__",text)
 def test_all_23_frequency_classes(s):
  for f in range(1,24):
   with s.subTest(f=f):
    s.reset(f=f);s.assertEqual(s.x.open_cfw_test_public_device_run(0),0);source=5 if f in H else 4;selector=10 if f in H else (7 if f==1 else 8);div=1 if f>=20 else 2 if f>=18 else 3 if f>=16 else 4 if f>=14 else 6 if f>=12 else 8 if f>=10 else 12 if f>=8 else 16 if f>=6 else 24 if f>=4 else 32;delay=8 if 6<=f<=9 else 4 if 10<=f<=13 else 2 if f in (14,15,18,19) else 1 if 20<=f<=23 else 99;s.assertEqual((s.st(0),s.st(1),s.st(2),s.st(3),s.st(4),s.st(5)),(source,4,0,f,10000,delay));s.assertEqual((s.tr(0),s.tr(3),s.tr(4),s.tr(5),s.tr(8),s.tr(9),s.tr(10),s.tr(11)),(2,selector,1,1,1,div,1 if f in (22,23) else 0,1 if f>=18 else 0))
 def test_module_restrictions(s):
  for m in (1,2):
   for f in (21,22,23):s.reset(m=m,f=f);s.assertEqual(s.x.open_cfw_test_public_device_run(0),5);s.assertEqual(s.tr(0),0)
   for d in (10,11):s.reset(m=m,d=d);s.assertEqual(s.x.open_cfw_test_public_device_run(0),5);s.assertEqual(s.tr(0),0)
 def test_clock_release_and_request_failures(s):
  s.reset(rel=37);s.assertEqual(s.x.open_cfw_test_public_device_run(0),37);s.assertEqual((s.tr(0),s.tr(4),s.tr(5),s.tr(8)),(1,1,0,0));s.reset(req=38);s.assertEqual(s.x.open_cfw_test_public_device_run(0),38);s.assertEqual((s.tr(0),s.tr(4),s.tr(5),s.tr(8)),(1,1,1,0))
 def test_same_clock_source_skips_lifecycle(s):
  s.reset(src=4,f=14);s.assertEqual(s.x.open_cfw_test_public_device_run(0),0);s.assertEqual((s.tr(4),s.tr(5),s.tr(0)),(0,0,2))
 def test_invalid_frequency_fails_after_clock_lifecycle(s):
  s.reset(f=0);s.assertEqual(s.x.open_cfw_test_public_device_run(0),5);s.assertEqual((s.tr(0),s.tr(4),s.tr(5),s.tr(8)),(1,1,1,0))
 def test_handle_and_configured_guards(s):
  s.reset(p=0);s.assertEqual(s.x.open_cfw_test_public_device_run(0),2);s.reset(cfg=0);s.assertEqual(s.x.open_cfw_test_public_device_run(0),7);s.reset();s.assertEqual(s.x.open_cfw_test_public_device_run(1),2)
if __name__=="__main__":unittest.main()
