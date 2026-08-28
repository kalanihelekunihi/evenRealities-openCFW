from __future__ import annotations
import ctypes,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];SOURCE=ROOT/"research/admission/bootloader_mspi_clkgen_ctrl_4249a0/runtime_bootloader_mspi_clkgen_ctrl_candidate.c";FIXTURE=SOURCE.parent/"host_fixture.c";XIP=SOURCE.parent/"runtime_bootloader_mspi_xip_off_delay_candidate.c";sys.path.insert(0,str(ROOT/"tools"));import analyze_g2_bootloader_mspi_clkgen_ctrl_4249a0 as analyzer
class Tests(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.t=tempfile.TemporaryDirectory();o=Path(c.t.name)/("x.dylib" if sys.platform=="darwin" else "x.so");cmd=["/usr/bin/clang","-std=c11","-O2","-Wall","-Wextra","-Werror",str(SOURCE),str(XIP),str(FIXTURE)]+(["-dynamiclib"] if sys.platform=="darwin" else ["-shared","-fPIC"]);subprocess.run([*cmd,"-o",str(o)],check=True,capture_output=True,text=True);c.x=ctypes.CDLL(str(o));c.x.open_cfw_test_clkgen_reset.argtypes=[ctypes.c_uint32,ctypes.c_uint32];c.x.open_cfw_test_clkgen_run.argtypes=[ctypes.c_uint32]*4;c.x.open_cfw_test_clkgen_value.argtypes=[ctypes.c_uint32,ctypes.c_uint32];c.x.open_cfw_test_clkgen_value.restype=ctypes.c_uint32;c.x.open_cfw_bootloader_mspi_xip_off_delay_424a18.argtypes=[ctypes.c_uint8,ctypes.c_uint32];c.x.open_cfw_bootloader_mspi_xip_off_delay_424a18.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(c):c.t.cleanup()
 def v(s,a,i=0):return s.x.open_cfw_test_clkgen_value(a,i)
 def test_audit(s):
  r=analyzer.audit();s.assertTrue(r["production"]["routed"]);s.assertEqual(r["production"]["source_owned_bytes"]+r["production"]["retained_official_bytes"],147296);s.assertEqual(r["production"]["next_frontier"],0x424A5A);s.assertEqual(r["hardware_validation"],"deferred by project direction")
 def test_enable_configure_and_delay(s):
  s.x.open_cfw_test_clkgen_reset(0xffffffff,0xa5);s.x.open_cfw_test_clkgen_run(2,1,1,3);mask=0x1f<<10;configured=(0xffffffff&~mask)|(7<<10);s.assertEqual([s.v(i) for i in (0,1,2,3,5,6)],[configured,1,0xa5,2,1,10]);s.assertEqual([s.v(4,i) for i in range(2)],[(0xffffffff&~(0x1e<<10))|(6<<10),configured])
 def test_disable_clears_only_enable(s):
  s.x.open_cfw_test_clkgen_reset(0xffffffff,7);s.x.open_cfw_test_clkgen_run(1,0,1,2);s.assertEqual((s.v(0),s.v(3),s.v(5),s.v(2)),(0xffffffff&~(1<<5),1,0,7))
 def test_enable_without_config_has_one_write(s):
  s.x.open_cfw_test_clkgen_reset(0,9);s.x.open_cfw_test_clkgen_run(3,1,0,0xff);s.assertEqual((s.v(0),s.v(3),s.v(5)),(1<<15,1,1))
 def test_xip_delay_classes(s):
  expected={**{x:8 for x in range(6,10)},**{x:4 for x in range(10,14)},**{x:2 for x in (14,15,18,19)},**{x:1 for x in range(20,24)}}
  for value in range(32):s.assertEqual(s.x.open_cfw_bootloader_mspi_xip_off_delay_424a18(value,99),expected.get(value,99))
if __name__=="__main__":unittest.main()
