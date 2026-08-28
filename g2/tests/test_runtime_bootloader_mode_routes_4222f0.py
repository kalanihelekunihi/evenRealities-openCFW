from __future__ import annotations
import ctypes,hashlib,os,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OFFICIAL=ROOT/"blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin";SOURCE=ROOT/"components/bootloader/core_overlay/runtime_mode_routes_4222f0.c";FIXTURE=ROOT/"tests/fixtures/bootloader_runtime_mode_routes_host.c"
class BootloaderModeRouteTests(unittest.TestCase):
 @classmethod
 def setUpClass(c):
  c.tmp=tempfile.TemporaryDirectory();c.libpath=Path(c.tmp.name)/("routes.dylib" if sys.platform=="darwin" else "routes.so");subprocess.run([os.environ.get("CC","/usr/bin/clang"),"-std=c11","-O2","-Wall","-Wextra","-Werror",str(FIXTURE),*(["-dynamiclib"] if sys.platform=="darwin" else ["-shared","-fPIC"]),"-o",str(c.libpath)],check=True,capture_output=True);c.lib=ctypes.CDLL(str(c.libpath));c.en=c.lib.open_cfw_bootloader_mode_enable_route_4222f0;c.dis=c.lib.open_cfw_bootloader_mode_disable_route_422364;c.clear=c.lib.open_cfw_bootloader_mode_clear_all_4223d8;c.copy=c.lib.open_cfw_bootloader_mode_configuration_copy_422416;c.en.argtypes=c.dis.argtypes=[ctypes.c_uint32,ctypes.c_uint32];c.en.restype=c.dis.restype=ctypes.c_uint32;c.clear.argtypes=[ctypes.c_uint32];c.clear.restype=ctypes.c_uint32;c.copy.argtypes=[ctypes.c_void_p];c.copy.restype=ctypes.c_uint32
 @classmethod
 def tearDownClass(c):c.tmp.cleanup()
 def setUp(s):s.lib.open_cfw_route_fixture_reset()
 def arr(s,n):return (ctypes.c_uint32*7).in_dll(s.lib,n)
 def bitmap(s):return ((ctypes.c_uint8*64)*7).in_dll(s.lib,"open_cfw_route_fixture_bitmap")
 def test_authenticated_bodies_and_successor(s):
  b=OFFICIAL.read_bytes();spans=((0x122F0,0x12364,"53cfb358989e68ae979d2814964a3e779ae0f0eba76836f99d409393d0e78d51"),(0x12364,0x123D8,"6a131868a276083764d4714178857124ccb4209a5f3e7552d874aba7f7c1a54e"),(0x123D8,0x12416,"97df45d0a88884e084088713a4325d6ce4b653e934a9c60ff72b13db31996fa1"),(0x12416,0x12430,"4d1631a1cd2b6aeb1ee196dd1039c51e339eb82c19bf0845a285f98839a00a8d"));
  for a,z,h in spans:s.assertEqual(hashlib.sha256(b[a:z]).hexdigest(),h)
  s.assertEqual(b[0x12430:0x12434].hex(),"04700220")
 def test_enable_disable_routes_and_bounds(s):
  for row in range(7):s.assertEqual(s.en(row,0x101+row),0x10+row);s.assertEqual(s.dis(row,1+row),0x20+row)
  s.assertEqual(tuple(s.arr("open_cfw_route_fixture_enable_calls")),(1,)*7);s.assertEqual(s.en(7,1),6);s.assertEqual(s.en(0,57),6);s.assertEqual(s.dis(8,2),6)
 def test_clear_all_only_routes_present_rows(s):
  for row in (0,2,6):s.bitmap()[row][9]=1
  s.assertEqual(s.clear(9),0);s.assertEqual(tuple(s.arr("open_cfw_route_fixture_disable_calls")),(1,0,1,0,0,0,1));s.assertEqual(s.clear(57),6)
 def test_configuration_copy_and_null(s):
  src=(ctypes.c_uint8*20)(*range(20));s.assertEqual(s.copy(src),0);dst=(ctypes.c_uint8*20).in_dll(s.lib,"open_cfw_route_host_configuration");s.assertEqual(bytes(dst),bytes(range(20)));s.assertEqual(s.copy(None),6)
 def test_source_cross_compiles(s):
  for cc in ("/usr/bin/clang","/opt/homebrew/opt/llvm@22/bin/clang"):
   if Path(cc).exists():subprocess.run([cc,"-target","arm-none-eabi","-mcpu=cortex-m55","-mthumb","-Oz","-ffreestanding","-fno-builtin","-ffunction-sections","-fdata-sections","-fno-unwind-tables","-fno-asynchronous-unwind-tables","-Wall","-Wextra","-Werror","-fno-ident","-c",str(SOURCE),"-o",str(Path(s.tmp.name)/(Path(cc).parent.name+"-routes.o"))],check=True,capture_output=True)
if __name__=="__main__":unittest.main()
