from __future__ import annotations
import ctypes,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"research/admission/bootloader_mspi_configure_424af0/runtime_bootloader_mspi_configure_candidate.c";FIXTURE=SOURCE.parent/"host_fixture.c";sys.path.insert(0,str(ROOT/"tools"));import analyze_g2_bootloader_mspi_configure_424af0 as analyzer
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.t=tempfile.TemporaryDirectory();o=Path(c.t.name)/("x.dylib" if sys.platform=="darwin" else "x.so");cmd=["/usr/bin/clang","-std=c11","-O2","-Wall","-Wextra","-Werror",str(SOURCE),str(FIXTURE)]+(["-dynamiclib"] if sys.platform=="darwin" else ["-shared","-fPIC"]);subprocess.run([*cmd,"-o",str(o)],check=True,capture_output=True,text=True);c.x=ctypes.CDLL(str(o));c.x.open_cfw_test_mspi_configure_reset.argtypes=[ctypes.c_uint32]*8;c.x.open_cfw_test_mspi_configure_run.argtypes=[ctypes.c_uint32];c.x.open_cfw_test_mspi_configure_run.restype=ctypes.c_uint32;c.x.open_cfw_test_mspi_configure_state.argtypes=[ctypes.c_uint32]*3;c.x.open_cfw_test_mspi_configure_state.restype=ctypes.c_uint32;c.x.open_cfw_test_mspi_configure_register.argtypes=[ctypes.c_uint32]*2;c.x.open_cfw_test_mspi_configure_register.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(c):c.t.cleanup()
 def reset(s,module=1,prefix=0x01bebebe,size=80,tcb=0x20070000,d4=1,xip=0xffffffff,scr=0x12345678,axi=0x87654321):s.x.open_cfw_test_mspi_configure_reset(module,prefix,size,tcb,d4,xip,scr,axi)
 def st(s,o,w=4,m=1):return s.x.open_cfw_test_mspi_configure_state(m,o,w)
 def reg(s,i,m=1):return s.x.open_cfw_test_mspi_configure_register(m,i)
 def test_audit(s):
  r=analyzer.audit();s.assertFalse(r["production"]["routed"]);s.assertEqual(r["production"]["boundary_status"],"official_blob");s.assertEqual(r["production"]["source_owned_bytes"]+r["production"]["retained_official_bytes"],147296);s.assertEqual(r["production"]["next_frontier"],0x424BD4);s.assertEqual(r["next_code_frontier"],{"start":0x424BE4,"end":0x425066,"identity":"am_hal_mspi_device_configure","bytes":1154,"status":"official_blob"});s.assertEqual(r["hardware_validation"],"deferred by project direction");s.assertEqual(r["hardware_operations"],[])
 def test_success_and_mmio_defaults(s):
  s.reset();s.assertEqual(s.x.open_cfw_test_mspi_configure_run(0),0);s.assertEqual([s.reg(i) for i in range(3)],[0,0xfffffffe,0]);s.assertEqual((s.st(0x14),s.st(0x18),s.st(0x8c8,1),s.st(0x858),s.st(9,1),s.st(8,1),s.st(10,1)),(80,0x20070000,1,4,1,1,26))
 def test_tcm_boundary_is_strict(s):
  s.reset(size=4,tcb=0x2007fff0);s.assertEqual(s.x.open_cfw_test_mspi_configure_run(0),0);s.assertEqual(s.st(0x8c8,1),0)
 def test_null_tcb_leaves_derived_fields_untouched(s):
  s.reset(size=80,tcb=0,d4=0);s.assertEqual(s.x.open_cfw_test_mspi_configure_run(0),0);s.assertEqual((s.st(0x8c8,1),s.st(0x858),s.st(9,1)),(0xa5,0xa5a5a5a5,0))
 def test_unsigned_small_size_caps_capacity(s):
  s.reset(size=7,tcb=0x1000);s.assertEqual(s.x.open_cfw_test_mspi_configure_run(0),0);s.assertEqual(s.st(0x858),256)
 def test_large_capacity_caps_at_256(s):
  s.reset(size=10000,tcb=0x20090000);s.assertEqual(s.x.open_cfw_test_mspi_configure_run(0),0);s.assertEqual((s.st(0x858),s.st(0x8c8,1)),(256,0))
 def test_invalid_handle_is_non_mutating(s):
  s.reset(prefix=0x00bebebe);s.assertEqual(s.x.open_cfw_test_mspi_configure_run(0),2);s.assertEqual([s.reg(i) for i in range(3)],[0x87654321,0xffffffff,0x12345678]);s.assertEqual(s.st(8,1),0xa5)
 def test_null_handle(s):
  s.reset();s.assertEqual(s.x.open_cfw_test_mspi_configure_run(1),2);s.assertEqual(s.reg(1),0xffffffff)
 def test_enabled_handle_is_rejected(s):
  s.reset(prefix=0x03bebebe);s.assertEqual(s.x.open_cfw_test_mspi_configure_run(0),7);s.assertEqual(s.reg(1),0xffffffff)
if __name__=="__main__":unittest.main()
